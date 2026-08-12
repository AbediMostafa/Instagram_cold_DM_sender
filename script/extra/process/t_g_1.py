```
import logging
from peewee import fn

from script.extra.exceptions import CantPerformAction
from script.extra.helper import go_to_page

from script.models.Account import Account
from script.models.AccountGroup import AccountGroup
from script.models.InternalFollowing import InternalFollowing
from script.models.Setting import Setting
from script.models.Command import Command
from script.extra.playwright.base_actions.DirectlyGoToAccountPageAction import DirectlyGoToAccountPageAction
from script.extra.playwright.base_actions.ClickOnFollowingAction import ClickOnFollowingAction


class MakeInstagramGroupContext:
    def __init__(self):
        pass

    def execute(self):
        max = Setting.get_value('maximum group count per account')

        # if max resached and all groups are full:
        #     raise
        #


class MakeInstagramGroup:

    def __init__(self):
        pass

    def init(self):
        self.create_group()
        self.add_member_to_group()

        pass


    def create_group(self):

        # if max reaache return


        created_groups_by_me = "query ---> 6"
        allowed_group_count = Setting.get_value('maximum group count per account')  # 10

        allowed_number = allowed_group_count - created_groups_by_me  # 7

        batch_size = Setting.get_value('batch size')  # 4

        final_number = min(allowed_number, batch_size)

        for _ in range(final_number):
            account_batch_size = Setting.get_value('account batch')
            lead_batch_size = Setting.get_value('lead batch')

            # Get accounts that have less account_group records order by id limit by account batch --> all
            # a,b,c
            # a --> 1
            # b --> 1
            # c --> 1
            # d,e,f
            # g,h,i
            #

            # Get leads that are not in any group

            accounts = []
            leads = []

            # usernames = account_usernames + lead_usernames

            # Group creattion script
            # Set group title --> acc_{account_id}_{uuid()}


          # Create account_group_record

    def add_member_to_group(self):

        # Get me batch limit of groups that are not filled

        groups = []

        for group in groups:

            max_group_memeber = Setting.get_value('maximum group memeber') #250
            this_group_memeber= 188#query()

            allowed_number = max_group_memeber - this_group_memeber #62
            group_member_batch = Setting.get_value('group batch size') # 15

            final = min(allowed_number, group_member_batch) #15

            account_batch = Setting.get_value('account batch size') # 4
            lead_size = final - account_batch # 11

            # Get accounts that have less account_group records order by id limit 4 --> all -> linmit 4
            # a,b,c
            # a --> 1
            # b --> 1
            # c --> 1
            # d,e,f
            # g,h,i
            #

            # Get leads that are not in any group->limit 11

            accounts_plus_lead_usernames = []

            #Go to group link






```