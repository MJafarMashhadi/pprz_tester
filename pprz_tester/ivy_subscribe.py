import logging
import sys
from typing import List, Tuple

sys.path.append("../pprzlink/lib/v1.0/python")
import pprzlink.message as message
from pprzlink.ivy import IvyMessagesInterface

logger = logging.getLogger('pprz_tester')


class IvySubscribe:
    def __init__(self,
                 ivy_link: IvyMessagesInterface,
                 message_types: List[Tuple[str]],
                 allow_direct_calls: bool = True
                 ):
        self.ivy_link = ivy_link
        self.message_types = message_types
        self.allow_direct_calls = allow_direct_calls
        self.bound = False

    def __call__(self, f):
        for message_class, message_name in self.message_types:
            msg_type_obj = message.PprzMessage(
                class_name=message_class,
                msg=message_name
            )
            self.ivy_link.subscribe(f, msg_type_obj)
            logger.info(f"Function {f.__module__}.{f.__name__} is listening to {message_class}.{message_name}")
            self.bound = True

        def dummy(*__, **_):
            # Moved the if inside the function so it can be restored later if unsubbed
            if self.allow_direct_calls or not self.bound:
                return f(*__, **_)
            else:
                raise RuntimeError(f"Calls to {f.__module__}.{f.__name__} are not allowed")

        return dummy

    # TODO: a pythonic way to unsub
