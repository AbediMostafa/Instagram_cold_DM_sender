import sys
import os

sys.path.append(r"C:\Users\admin\AppData\Roaming\Python\Python312\site-packages")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from script.models.AccountHelper import *
from script.extra.base.BasePlaywright import BasePlaywright
from script.extra.actions.login.LoginContext import LoginContext
from script.extra.actions.connect_to_uploadPost.UploadPostConnectContext import UploadPostConnectContext
import traceback

# Ensure correct usage
if len(sys.argv) < 2:
    print("Usage: python upload_post_connect.py <account_id>")
    sys.exit(1)

account_id = sys.argv[1]

# Fetch the account
account = Account.get_by_id(account_id)
if not account:
    print(f"Account {account_id} not found")
    sys.exit(1)

print(f"[UploadPost] Starting for account {account.username} (ID: {account.id})")

browser_ig = None

try:
    browser_ig = BasePlaywright(account)
    browser_ig.init()

    # Login first
    LoginContext(browser_ig).fire()

    # Run the Upload-Post connect/disconnect flow
    UploadPostConnectContext(browser_ig).fire()

except Exception as e:
    print(f"[UploadPost] Error: {str(e)}")
    print(traceback.format_exc())

finally:
    if browser_ig:
        browser_ig.cleanup()
