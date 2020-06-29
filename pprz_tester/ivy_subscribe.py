import logging
import sys
from typing import List, Tuple, Optional

sys.path.append("../pprzlink/lib/v1.0/python")
import pprzlink.message as message
from pprzlink.ivy import IvyMessagesInterface

logger = logging.getLogger('pprz_tester')


class IvySubscribe:
    def __init__(self,
                 ivy_link: IvyMessagesInterface,
                 message_types: Optional[List[Tuple[str]]]=None,
                 allow_direct_calls: bool = True
                 ):
        """
        Decorator to assign a method for listening to incoming ivy messages.

        :param: ivy_link
        :param: message_types
        :param: allow_direct_calls
        """
        self.ivy_link = ivy_link
        self.message_types = message_types
        self.allow_direct_calls = allow_direct_calls
        self.bound = False

    def _subscribe_to_all(self, f):
        self.ivy_link.subscribe(f)
        logger.info(f"Function {f.__module__}.{f.__name__} is listening to all messages")

    def __call__(self, f):
        if self.message_types is None:
            self._subscribe_to_all(f)
        else:
            self._subscribe(f)
        self.bound = True

        def dummy(*__, **_):
            # Moved the if inside the function so it can be restored later if unsubbed
            if self.allow_direct_calls or not self.bound:
                return f(*__, **_)
            else:
                raise RuntimeError(f"Calls to {f.__module__}.{f.__name__} are not allowed")

        return dummy

    def _subscribe(self, f):
        for message_class, message_name in self.message_types:
            msg_type_obj = message.PprzMessage(
                class_name=message_class,
                msg=message_name
            )
            self.ivy_link.subscribe(f, msg_type_obj)
            logger.info(f"Function {f.__module__}.{f.__name__} is listening to {message_class}.{message_name}")

    # TODO: a pythonic way to unsub
