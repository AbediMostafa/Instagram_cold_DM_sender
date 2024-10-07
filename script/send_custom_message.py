import sys
import os
from time import sleep
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script.models.Command import Command
from script.extra.instagram.api.InstagramMobile import InstagramMobile


if len(sys.argv) > 1:
    command_id = sys.argv[1]
    command = Command.get_by_id(command_id)

    ig_mobile = InstagramMobile(command.account)
    ig_mobile.log_in()

    command.update_cmd('state', 'processing')

    lead = command.lead

    if not lead.instagram_id:
        ig_mobile.user_id_from_username(lead)

    sleep(random.randint(2, 5))

    ig_message = ig_mobile.direct_send(
        [lead.instagram_id],
        command.get_commandable().text
    )

    command.update_cmd('state', 'success')
    db_message = command.get_commandable()
    db_message.message_id = ig_message.id
    db_message.state = 'seen'
    db_message.save()
