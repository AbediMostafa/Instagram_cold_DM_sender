import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.Command import Command
from script.extra.instagram.InstagramMobile import InstagramMobile
from script.extra.hooks.CheckNewMessageHooks import CheckNewMessageHooks

if len(sys.argv) > 1:
    command_id = sys.argv[1]
    command = Command.get_by_id(command_id)

    ig_mobile = InstagramMobile(command.account)
    ig_mobile.set_proxy().log_in()

    command.update_cmd('state', 'processing')
    CheckNewMessageHooks(command.account, ig_mobile)
    command.update_cmd('state', 'success')