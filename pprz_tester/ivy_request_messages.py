import logging
from typing import Callable, Any

import pprzlink as pl
from ivy_subscribe import IvySubscribeOnce
from pprzlink.ivy import IvyMessagesInterface
from util import RequestUIDFactory

logger = logging.getLogger('pprz_tester')


def request_data(
        ivy_link: IvyMessagesInterface,
        ivy_agent_name: str,
        message_class: str,
        request_name: str,
        callback: Callable[[int, pl.message.PprzMessage], Any],
        **request_extra_data
):
    new_id = RequestUIDFactory.generate_uid()

    @IvySubscribeOnce(ivy_link=ivy_link,
                      message_types=[r"^((\S*\s*)?%s %s %s( .*|$))" % (new_id, message_class, request_name)])
    def data_request_callback(ac_id, msg):
        logger.info(f"Received a response for %s.%s %s: %s" % (message_class, request_name, ac_id, msg))
        callback(int(ac_id), msg)

    # Manually sending request message since it is not yet implemented in pprz_link.
    request_message = pl.message.PprzMessage(message_class, "%s_REQ" % request_name)
    for k, v in request_extra_data.items():
        request_message.set_value_by_name(k, v)

    data_request_message = ' '.join((
        ivy_agent_name, new_id, request_message.name, request_message.payload_to_ivy_string()
    ))
    ivy_link.send(data_request_message)
    logger.info("Sent new request for %s.%s (uid=%s)" % (message_class, request_name, new_id))
