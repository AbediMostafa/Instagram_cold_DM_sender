import traceback
from datetime import timedelta

from script.extra.helper import tehran_now
from script.extra.exceptions import RetryableError
from script.extra.mobile.base.BaseMobileEvent import BaseMobileEvent
from script.extra.mobile.base.BaseDuoPlus import DeviceCommandError
from script.extra.mobile.base.LinkParser import LinkParser
from script.models.Setting import Setting
from script.models.Order import Order
from script.models.OrderAction import OrderAction

from script.extra.mobile.actions.share.ShareMechanics import ShareMechanics


class SharePrepareEvent(BaseMobileEvent):
    """
    Mobile mirror of BaseOrderPreparer for the share service.

    For each claimed order it proves the whole pipeline works by doing ONE
    real send, then creates EVERY OrderAction upfront (the counts are fully
    determined by total_count, so nothing is left to compute at execution
    time — the execute phase becomes a plain claim loop, exactly like web).

    Error contract (identical to the web preparer):
      RetryableError / TimeoutError / DeviceCommandError
          -> is_prepared back to 0, another account retries.
      any other Exception
          -> order Canceled with a description, no actions created.
          (share is balance-exempt: no charge on cancel, ever.)
    """

    def init(self):
        self._reset_stuck_orders()

        batch_size = int(Setting.get_value('mobile_share_prepare_batch', 3))
        per_group = int(Setting.get_value('mobile_share_per_group', 250))
        groups_per_send = int(Setting.get_value('mobile_share_groups_per_send', 20))

        mechanics = ShareMechanics(self.device)

        # Mark the account 'processing' in the panel while it holds orders —
        # the same app_state the web workers use, so it's a valid enum value
        # and the panel treats a busy mobile account like any other. Always
        # restored, even when a device call blows up mid-order.
        previous_app_state = self.account.app_state
        self._set_account_state('processing')

        try:
            for index in range(batch_size):
                self.log(f'claim attempt {index + 1}/{batch_size}')
                order = self._claim_next_order()

                if not order:
                    if index == 0:
                        self.log('no share orders to prepare')
                    else:
                        self.log(f'no more orders to claim (prepared {index})')
                    break

                self.log(
                    f'preparing order #{order.id} '
                    f'({order.total_count}): {order.target_link}'
                )

                try:
                    self._process_order(order, mechanics, per_group, groups_per_send)
                except (RetryableError, TimeoutError, DeviceCommandError) as e:
                    self._handle_retryable(order, str(e))
                except Exception as e:
                    self._handle_permanent(order, str(e))
                    self.account.add_log(traceback.format_exc())
                finally:
                    # Fresh, known state before the next order (or module).
                    self.log('returning to Home before next order')
                    try:
                        self.device.go_home()
                    except Exception as e:
                        self.log(f'go_home after order failed: {e}')
        finally:
            self.log(f'restoring account app_state -> {previous_app_state or "idle"}')
            self._set_account_state(previous_app_state or 'idle')

    # ── claiming (mirror of web _reset_stuck_orders / _claim_next_order) ────
    def _reset_stuck_orders(self):
        """
        is_prepared=1 older than the timeout means the claiming worker died;
        reset to 0 so anyone can retry. Lock keeps the UPDATE from running on
        every session; the conditional UPDATE itself is already race-safe.
        """
        timeout = int(Setting.get_value('mobile_share_stuck_timeout', 120))

        try:
            from script.models.Lock import Lock
            if not Lock.acquire('mobile_share_stuck_reset', duration_seconds=60):
                return
            acquired = True
        except ImportError:
            acquired = False

        try:
            cutoff = tehran_now() - timedelta(seconds=timeout)

            updated = Order.update(
                is_prepared=0
            ).where(
                (Order.is_prepared == 1) &
                (Order.service_type == 'share') &
                (Order.updated_at < cutoff)
            ).execute()

            if updated:
                self.log(f'reset {updated} stuck share order(s)')
        finally:
            if acquired:
                from script.models.Lock import Lock
                Lock.release('mobile_share_stuck_reset')

    def _claim_next_order(self):
        """Multi-candidate atomic claim: is_prepared 0 -> 1."""
        candidates = list(
            Order
            .select(Order.id)
            .where(
                (Order.service_type == 'share') &
                (Order.is_prepared == 0) &
                (Order.status == 'Pending')
            )
            .order_by(Order.id.asc())
            .limit(5)
        )

        for candidate in candidates:
            updated = Order.update(
                is_prepared=1,
                updated_at=tehran_now()
            ).where(
                (Order.id == candidate.id) &
                (Order.is_prepared == 0)
            ).execute()

            if updated > 0:
                return Order.get_by_id(candidate.id)

        return None

    # ── processing one order ────────────────────────────────────────────────
    def _process_order(self, order, mechanics, per_group, groups_per_send):
        parsed = LinkParser.parse(order.target_link)
        target_type = parsed.get('type')
        self.log(
            f'parsed link -> type={target_type} '
            f'code={parsed.get("post_code")} user={parsed.get("username")}'
        )

        if target_type == LinkParser.TYPE_HIGHLIGHT:
            raise Exception('Highlights are not supported')
        if target_type not in (LinkParser.TYPE_POST,
                               LinkParser.TYPE_REEL,
                               LinkParser.TYPE_STORY):
            raise Exception(f'link is not a post, reel or story ({target_type})')

        # Opens and validates; raises RetryableError / Exception per contract.
        self.log('opening + validating target')
        mechanics.open_target(parsed)
        self.log('target validated OK')

        existing_actions = order.actions().count()

        if existing_actions == 0:
            self.log('fresh prepare (no existing actions)')
            self._prepare_fresh(order, mechanics, parsed,
                                per_group, groups_per_send)
        else:
            self.log(f're-prepare ({existing_actions} existing action(s))')
            self._prepare_again(order, mechanics, parsed, per_group)

        self._finalize(order, parsed)
        self.log(f'order #{order.id} prepared (is_prepared=2)')

    def _prepare_fresh(self, order, mechanics, parsed, per_group, groups_per_send):
        """
        First-ever prepare: one proving send, then every action upfront.
        The proving send IS the first action (status=sent, this account).
        """
        plan = ShareMechanics.build_send_plan(
            order.total_count, per_group, groups_per_send
        )

        # The proving send uses the first entry's group count (real groups to
        # tick), while completed_count grows by its capped customer count.
        first = plan[0]
        mechanics.perform_send(parsed['type'], first['groups'])

        rows = []
        now = tehran_now()
        for index, entry in enumerate(plan):
            rows.append({
                'order': order.id,
                'account': self.account.id if index == 0 else None,
                'type': 'share',
                # content carries the real group count for this send, so the
                # execution module ticks the right number regardless of the
                # (capped) customer count. count = customer amount for this send.
                'content': str(entry['groups']),
                'count': entry['count'],
                'status': 'sent' if index == 0 else 'free',
                'updated_at': now,
            })

        # Rows differ (groups and the last count vary), so each carries its own
        # values; insert_many still batches them fine.
        OrderAction.insert_many(rows).execute()

        Order.update(
            completed_count=Order.completed_count + first['count']
        ).where(
            Order.id == order.id
        ).execute()

        self.log(
            f'order #{order.id}: created {len(rows)} action(s) '
            f'{[(e["groups"], e["count"]) for e in plan]}, '
            f'first send counted ({first["count"]})'
        )

    def _prepare_again(self, order, mechanics, parsed, per_group):
        """
        Re-prepare: actions already exist, so never rebuild them. The proving
        send consumes one FREE action (completed_count += its count, exactly
        like the web free_action path).
        """
        first_free = (
            OrderAction
            .select()
            .where(
                (OrderAction.order == order.id) &
                (OrderAction.status == 'free')
            )
            .order_by(OrderAction.id.asc())
            .first()
        )

        if not first_free:
            self.log(f'order #{order.id}: re-prepare with no free actions, finalizing only')
            return

        groups = self._action_groups(first_free, per_group)
        mechanics.perform_send(parsed['type'], groups)

        claimed = OrderAction.update(
            status='sent',
            account=self.account,
            updated_at=tehran_now()
        ).where(
            (OrderAction.id == first_free.id) &
            (OrderAction.status == 'free')
        ).execute()

        if claimed > 0:
            Order.update(
                completed_count=Order.completed_count + first_free.count
            ).where(
                Order.id == order.id
            ).execute()

            self.log(
                f'order #{order.id}: re-prepare send counted ({first_free.count})'
            )

    @staticmethod
    def _action_groups(action, per_group):
        """
        Real group count for an action. Stored in `content` at creation time;
        falls back to a ceil of the (uncapped) count for any legacy row that
        predates the content field.
        """
        if action.content:
            try:
                return max(1, int(action.content))
            except (TypeError, ValueError):
                pass
        return max(1, (action.count + per_group - 1) // per_group)

    def _finalize(self, order, parsed):
        """action_data + is_prepared=2 + completion check, all conditional."""
        Order.update(
            is_prepared=2,
            action_data={
                'type': parsed.get('type'),
                'post_code': parsed.get('post_code'),
                'username': parsed.get('username'),
                'story_id': parsed.get('story_id'),
            },
            updated_at=tehran_now()
        ).where(
            Order.id == order.id
        ).execute()

        Order.update(
            status='Completed'
        ).where(
            (Order.id == order.id) &
            (Order.completed_count >= Order.total_count) &
            (Order.status != 'Completed')
        ).execute()

    # ── error handling ──────────────────────────────────────────────────────
    def _handle_retryable(self, order, message):
        """Temporary issue: release the claim so another account tries."""
        self.log(f'order #{order.id} retryable: {message}')

        Order.update(
            is_prepared=0,
            updated_at=tehran_now()
        ).where(
            (Order.id == order.id) &
            (Order.is_prepared == 1)
        ).execute()

    def _handle_permanent(self, order, message):
        """
        Permanent target issue (private, deleted, expired story, bad link):
        cancel with the reason. Share is balance-exempt, so unlike the web
        preparer there is NO charge here.
        """
        self.log(f'order #{order.id} failed permanently: {message}')

        Order.update(
            status='Canceled',
            is_prepared=0,
            description=message,
            updated_at=tehran_now()
        ).where(
            Order.id == order.id
        ).execute()

    # ── misc ────────────────────────────────────────────────────────────────
    def _set_account_state(self, state):
        from script.models.Account import Account

        try:
            Account.update(app_state=state).where(
                Account.id == self.account.id
            ).execute()
            self.account.app_state = state
        except Exception as e:
            self.log(f'could not set account app_state: {e}')