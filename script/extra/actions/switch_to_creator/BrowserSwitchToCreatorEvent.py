import random


class BrowserSwitchToCreatorEvent:
    """
    Handles switching an Instagram account to a Creator professional account.

    Flow:
      1. Navigate to Settings page
      2. Check if already professional via DOM
      3. Use scrollIntoView on the target span, then click by text
      4. Click 'Switch to professional account' by text
      5. Select Creator, Next x2, pick category, Done
      6. Handle remaining steps, navigate home
    """

    PERSONAL_BLOG_WEIGHT = 0.70

    ALREADY_PROFESSIONAL_JS = """
        () => !!document.querySelector('a[href="/accounts/professional_account_settings/"]')
    """

    SCROLL_INTO_VIEW_JS = """
        () => {
            const spans = Array.from(document.querySelectorAll('span'));
            const target = spans.find(s => s.textContent.trim() === 'Account type and tools');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return true;
            }
            return false;
        }
    """

    IN_VIEWPORT_JS = """
        () => {
            const spans = Array.from(document.querySelectorAll('span'));
            const target = spans.find(s => s.textContent.trim() === 'Account type and tools');
            if (!target) return false;
            const rect = target.getBoundingClientRect();
            return rect.top >= 0 && rect.bottom <= window.innerHeight;
        }
    """

    def __init__(self, ig):
        self.ig = ig
        self.account = ig.account

    def init(self):
        try:
            self._go_to_settings()

            if self._is_already_professional():
                self.account.add_cli('[SwitchToCreator] Account is already a professional account, skipping...')
                return

            self._scroll_sidebar_and_click_account_type_and_tools()
            self._click_switch_to_professional()
            self._select_creator()
            self._click_next_first()
            self._click_next_second()
            self._select_category()
            self._handle_remaining_steps()

            self.account.add_cli('[SwitchToCreator] Successfully switched to Creator account')

        except Exception as e:
            self.account.add_cli(f'[SwitchToCreator] Failed: {str(e)}')
            raise

        finally:
            self.account.add_cli('[SwitchToCreator] Navigating back to Instagram home...')
            try:
                self.ig.page.goto('https://www.instagram.com/', timeout=60000)
                self.ig.pause(6000, 10000)
            except Exception:
                self.account.add_cli('[SwitchToCreator] Failed to navigate back to Instagram home')

    def _go_to_settings(self):
        self.account.add_cli('[SwitchToCreator] Navigating to Settings...')
        self.ig.page.goto('https://www.instagram.com/accounts/edit/', timeout=60000)
        self.ig.pause(6000, 10000)

    def _is_already_professional(self):
        """
        Query DOM directly since the link may be below the viewport.
        professional_account_settings replaces account_type_and_tools once switched.
        """
        result = self.ig.page.evaluate(self.ALREADY_PROFESSIONAL_JS)
        self.account.add_cli(f'[SwitchToCreator] Already professional: {result}')
        return result

    def _scroll_sidebar_and_click_account_type_and_tools(self):
        """
        Use scrollIntoView to bring the target span into the visible viewport,
        then verify it is visible before clicking.
        """
        self.account.add_cli('[SwitchToCreator] Scrolling to Account type and tools...')

        found = self.ig.page.evaluate(self.SCROLL_INTO_VIEW_JS)

        if not found:
            raise Exception('Account type and tools span not found in DOM')

        self.ig.pause(6000, 10000)

        in_viewport = self.ig.page.evaluate(self.IN_VIEWPORT_JS)
        self.account.add_cli(f'[SwitchToCreator] In viewport after scrollIntoView: {in_viewport}')

        if not in_viewport:
            raise Exception('Account type and tools not visible after scrollIntoView')

        self.account.add_cli('[SwitchToCreator] Clicking Account type and tools...')
        self.ig.page.get_by_text('Account type and tools', exact=True).first.click(timeout=10000)
        self.ig.pause(6000, 10000)

        current_url = self.ig.page.url
        self.account.add_cli(f'[SwitchToCreator] Current URL: {current_url}')

        if 'account_type_and_tools' not in current_url:
            raise Exception(f'Expected account_type_and_tools page but got: {current_url}')

    def _click_switch_to_professional(self):
        self.account.add_cli('[SwitchToCreator] Clicking Switch to professional account...')
        self.ig.page.get_by_text('Switch to professional account', exact=True).first.click(timeout=10000)
        self.ig.pause(6000, 10000)
        self.account.add_cli(f'[SwitchToCreator] Current URL: {self.ig.page.url}')

    def _select_creator(self):
        if self.ig.is_visible_by_text('Creator'):
            self.account.add_cli('[SwitchToCreator] Selecting Creator account type...')
            self.ig.page.get_by_role('button', name='Creator').first.click(timeout=10000)
            self.ig.pause(6000, 10000)

    def _click_next_first(self):
        if self.ig.is_visible_by_text('Next'):
            self.account.add_cli('[SwitchToCreator] Clicking Next (1)...')
            self.ig.page.get_by_role('button', name='Next').click(timeout=10000)
            self.ig.pause(6000, 10000)

    def _click_next_second(self):
        if self.ig.is_visible_by_text('Next'):
            self.account.add_cli('[SwitchToCreator] Clicking Next (2)...')
            self.ig.page.get_by_role('button', name='Next').click(timeout=10000)
            self.ig.pause(6000, 10000)

    def _select_category(self):
        if not self.ig.is_visible_by_text('Suggested'):
            self.account.add_cli('[SwitchToCreator] Category screen not detected, skipping...')
            return

        self.account.add_cli('[SwitchToCreator] Category selection screen detected...')

        show_category_checkbox = self.ig.page.locator('input[aria-label="Show category on profile"]')
        if show_category_checkbox.is_visible():
            show_category_checkbox.click(timeout=10000)
            self.ig.pause(6000, 10000)
            self.account.add_cli('[SwitchToCreator] Checked Show category on profile')

        category_buttons = self.ig.page.locator('[role="radiogroup"][name="category"] [role="button"]')
        count = category_buttons.count()

        if count == 0:
            self.account.add_cli('[SwitchToCreator] No categories found in list')
        else:
            selected_index = self._pick_category_index(category_buttons, count)
            selected = category_buttons.nth(selected_index)
            category_name = selected.inner_text()
            selected.click(timeout=10000)
            self.ig.pause(6000, 10000)
            self.account.add_cli(f'[SwitchToCreator] Selected category: {category_name}')

        if self.ig.is_visible_by_text('Done'):
            self.account.add_cli('[SwitchToCreator] Clicking Done (category)...')
            self.ig.page.get_by_role('button', name='Done').click(timeout=10000)
            self.ig.pause(6000, 10000)

    def _pick_category_index(self, category_buttons, count):
        """
        70% chance: pick Personal Blog if it exists.
        30% chance (or fallback if Personal Blog not found): pick a random category.
        """
        if random.random() < self.PERSONAL_BLOG_WEIGHT:
            for i in range(count):
                text = category_buttons.nth(i).inner_text()
                if 'personal blog' in text.lower():
                    self.account.add_cli('[SwitchToCreator] Picking Personal Blog')
                    return i

            self.account.add_cli('[SwitchToCreator] Personal Blog not found, picking random category')

        return random.randint(0, count - 1)

    def _handle_remaining_steps(self):
        if self.ig.is_visible_by_text('Continue'):
            self.account.add_cli('[SwitchToCreator] Clicking Continue...')
            self.ig.page.get_by_role('button', name='Continue').click(timeout=10000)
            self.ig.pause(6000, 10000)

        if self.ig.is_visible_by_text("Don't use my contact info"):
            self.account.add_cli("[SwitchToCreator] Clicking Don't use my contact info...")
            self.ig.page.get_by_role('button', name="Don't use my contact info").click(timeout=10000)
            self.ig.pause(6000, 10000)

        if self.ig.is_visible_by_text('Done'):
            self.account.add_cli('[SwitchToCreator] Clicking final Done...')
            self.ig.page.get_by_role('button', name='Done').click(timeout=10000)
            self.ig.pause(6000, 10000)