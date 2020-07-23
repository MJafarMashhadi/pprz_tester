import inspect
import logging
from typing import List, Tuple, Optional, Union

from pprzlink.ivy import IvyMessagesInterface
from pprzlink_enhancements.message import MessageBuilder

logger = logging.getLogger('pprz_tester')


class IvySubscribe:
    def __init__(self,
                 ivy_link: IvyMessagesInterface,
                 message_types: Optional[List[Union[Tuple[str, str], str]]] = None
                 ):
        """
        Decorator to assign a method for listening to incoming ivy messages.

        :param: ivy_link
        :param: message_types
        """
        self.ivy_link = ivy_link
        self.message_types = message_types
        self.subscription_ids = []
        self.function_name = ''

    def _subscribe_to_all(self, f):
        subscription_id = self.ivy_link.subscribe(f)
        logger.info(f"Function {self.function_name} is listening to all messages")
        self.subscription_ids.append(subscription_id)

    def __call__(self, f):
        self.function_name = f'{f.__module__}.{f.__name__}'
        callback = self.wrap_callback(f)
        direct_call = self.wrap_direct_call(f)

        if self.message_types is None:
            self._subscribe_to_all(callback)
        else:
            self._subscribe(callback)

        if inspect.ismethod(f):
            setattr(direct_call.__func__, '__ivy_subs__', self)
        else:
            setattr(direct_call, '__ivy_subs__', self)

        return direct_call

    def _subscribe(self, f):
        for subscription_pattern in self.message_types:
            if isinstance(subscription_pattern, tuple):
                message_class, message_name = subscription_pattern
                msg_type_obj = MessageBuilder()\
                    .class_name(message_class)\
                    .message_name(message_name)\
                    .build()
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
            if subscription_id not in self.subscription_ids:
                logger.warning(f'Function {self.function_name} had no subscription {subscription_id}')
                continue
            try:
                self.ivy_link.unsubscribe(subscription_id)
                self.subscription_ids.remove(subscription_id)
            except:
                logger.warning(f'Ignored error during unsubscribing {self.function_name} from #{subscription_id}')

    def wrap_callback(self, f):
        return f

    def wrap_direct_call(self, f):
        return f


class DisallowDirectCallsMixin:
    def wrap_direct_call(self: IvySubscribe, f):
        f = super(DisallowDirectCallsMixin, self).wrap_direct_call(f)

        def _wrapped(*args, **kwargs):
            # Moved the if inside the function so it can be restored later if unsubbed
            if len(self.subscription_ids) > 0:
                return f(*args, **kwargs)
            else:
                raise RuntimeError(
                    f"Direct calls to {self.function_name} while it is listening to messages are not allowed")

        return _wrapped


class OneTimeSubsMixin:
    def wrap_callback(self: IvySubscribe, f):
        f = super(OneTimeSubsMixin, self).wrap_callback(f)

        def _call_and_unsub(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
            except Exception as e:
                raise e
            else:
                return result
            finally:
                self.unsubscribe(self.subscription_ids)

        return _call_and_unsub


class IvySubscribeOnce(OneTimeSubsMixin, IvySubscribe):
    """
    All subscriptions expire as soon as one matching message is processed
    """
    pass


class IvyNoDirectCallsSubscribe(DisallowDirectCallsMixin, IvySubscribe):
    """
    While the wrapped function is listening to some messages it cannot be called by anyone other than the ivy interface.

    """
    pass
