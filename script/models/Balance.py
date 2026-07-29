from peewee import *
from decimal import Decimal
from .BaseWithTimeZoneModel import BaseWithTimeZoneModel


# Rate per action type
ACTION_RATES = {
    'comment': Decimal('0.0003'),             # $0.30 / 1000
    'view_story': Decimal('0.00005'),         # $0.05 / 1000
    'view_all_stories': Decimal('0.00005'),   # $0.05 / 1000
    'save_post': Decimal('0.00004'),          # $0.04 / 1000
}

# Types with no balance operations at all (never charged, never refunded).
# Explicit guard so an exempt type can't hit the default-rate fallback.
BALANCE_EXEMPT_TYPES = ('share', 'comment_and_reply')


class Balance(BaseWithTimeZoneModel):
    customer = CharField()
    balance = DecimalField(max_digits=12, decimal_places=6)

    class Meta:
        table_name = 'balances'

    @classmethod
    def deduct_for_actions(cls, action_type, count=1):
        """
        Deduct balance for one or more actions.

        Args:
            action_type: Type of action (comment, view_story, save_post, etc.)
            count: Number of actions to charge for

        Returns:
            Decimal: Total amount deducted
        """
        if count <= 0:
            return Decimal('0')

        if action_type in BALANCE_EXEMPT_TYPES:
            return Decimal('0')

        rate = ACTION_RATES.get(action_type, Decimal('0.00005'))
        total = rate * Decimal(count)

        cls.update(
            balance=cls.balance - total
        ).where(
            cls.customer == 'sadeghi'
        ).execute()

        return total