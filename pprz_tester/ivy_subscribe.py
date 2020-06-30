import logging
import sys
from typing import List, Tuple, Optional, Union

sys.path.append("../pprzlink/lib/v1.0/python")
import pprzlink.message as message
from pprzlink.ivy import IvyMessagesInterface

logger = logging.getLogger('pprz_tester')


class IvySubscribe:
    def __init__(self,
                 ivy_link: IvyMessagesInterface,
                 message_types: Optional[List[Union[Tuple[str], str]]] = None,
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
        self.subscription_ids = []
        self.function_name = ''

    def _subscribe_to_all(self, f):
        subscription_id = self.ivy_link.subscribe(f)
        logger.info(f"Function {self.function_name} is listening to all messages")
        self.subscription_ids.append(subscription_id)

    def __call__(self, f):
        self.function_name = f'{f.__module__}.{f.__name__}'
        callback = self._wrap_callback(f)
        direct_call = self._wrap_direct_call(f)

        if self.message_types is None:
            self._subscribe_to_all(callback)
        else:
            self._subscribe(callback)

        direct_call.__ivy_subs__ = self
        return direct_call

    def _subscribe(self, f):
        for subscription_pattern in self.message_types:
            if isinstance(subscription_pattern, tuple):
                message_class, message_name = subscription_pattern
                msg_type_obj = message.PprzMessage(
                    class_name=message_class,
                    msg=message_name
                )
                subscription_id = self.ivy_link.subscribe(f, regex_or_msg=msg_type_obj)
                logger.info(f"Function {self.function_name} is listening to {message_class}.{message_name}")
            elif isinstance(subscription_pattern, str):
                subscription_id = self.ivy_link.subscribe(f, regex_or_msg=subscription_pattern)
                logger.info(f"Function {self.function_name} is listening to messages matching {subscription_pattern}")
            else:
                raise ValueError(f'Invalid subscription pattern {subscription_pattern}')

            self.subscription_ids.append(subscription_id)

    def unsubscribe(self, ids=None):
        if ids is None:
            ids = self.subscription_ids

        if isinstance(ids, int):
            ids = [ids]

        for subscription_id in ids:
            try:
                self.ivy_link.unsubscribe(subscription_id)
            except:
                logger.warning(f'Ignored error during unsubscribing {self.function_name} from #{subscription_id}')

    def _wrap_callback(self, f):
        return f

    def _wrap_direct_call(self, f):
        def wrapped(*args, **kwargs):
            # Moved the if inside the function so it can be restored later if unsubbed
            if len(self.subscription_ids) > 0:
                return f(*args, **kwargs)
            else:
                raise RuntimeError(
                    f"Direct calls to {self.function_name} while it is listening to messages are not allowed")

        return wrapped
