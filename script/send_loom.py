import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.Command import Command
from script.extra.instagram.InstagramMobile import InstagramMobile
from script.extra.hooks.CheckNewMessageHooks import CheckNewMessageHooks
from script.extra.helper import get_post_path

if len(sys.argv) > 1:
    command_id = sys.argv[1]
    command = Command.get_by_id(command_id)

    message = command.get_commandable()
    thread_id = message.thread.thread_id

    loom = message.get_messageable()
    loom_abs_path = get_post_path(loom.path)

    ig_mobile = InstagramMobile(command.account)
    ig_mobile.set_proxy().log_in()

    command.update_cmd('state', 'processing')
    ig_mobile.direct_send_video(loom_abs_path, thread_id)
    command.update_cmd('state', 'success')
    loom.update_state('sent')
    message.update_state('seen')
