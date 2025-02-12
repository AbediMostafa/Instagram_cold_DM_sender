import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import subprocess
import sys
from script.models.Process import Process
from script.models.Account import Account
from script.models.Lead import Lead
from script.models.Command import Command
from script.models.Spintax import Spintax
from script.models.Category import Category
from script.models.Template import Template
from script.models.AccountHelper import get_next_account
from dotenv import load_dotenv
from script.extra.base.BasePlaywright import BasePlaywright
from script.extra.events.browser_events.BrowserLoginEvent import BrowserLoginEvent
from script.extra.events.browser_events.BrowserDmFollowUpEvent import BrowserDmFollowUpEvent
from script.extra.actions.send_dm.SendDmContext import SendDmContext
from script.extra.helper import tehran_now
from script.extra.actions.DmFollowUp import DmFollowUp
from script.extra.actions.lead_generate_through_api.LeadGenerateThroughApiContext import LeadGenerateThroughApiContext
from script.extra.helper import hours_ago

#
account = Account.get_by_id(1201)
browser_ig = BasePlaywright(account)
browser_ig.start_browser().go_to_instagram()
SendDmContext(browser_ig).fire()

# lead = Lead.get_by_id(707456)
# account = Account.get_by_id(2474)
#
# leads = DmFollowUp(account).leads_to_send_dm_follow_ups(100)
#
# for lead in leads:
#     print('------------------------------------')
#     print(lead.username)
#     print(lead.dm_text)
#     print('------------------------------------')


# lead.change_state(account, 'dm follow up', add_history=True, times=1, update_date=True)
#
# #
#
# print(tehran_now())
# print(((tehran_now() - lead.last_command_send_date).total_seconds()/3600)/24 )

# print(account.categories())
#
# def run_background_script():
#     # Define the path to the background script
#     background_script = "C:\\Users\\Administrator\\Desktop\\project\\script\\t.py"
#
#     # Run the background script in the background
#     process = subprocess.Popen(
#         [sys.executable, background_script],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE)
#
#     Process.create(pid=process.pid)
#
#
# if __name__ == "__main__":
#     run_background_script()
#     print("Background script started!")
