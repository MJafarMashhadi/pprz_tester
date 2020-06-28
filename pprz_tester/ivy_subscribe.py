import sys
import logging
sys.path.append("../pprzlink/lib/v1.0/python")

from ivy.std_api import *
import pprzlink.ivy
import pprzlink.message as message


logger = logging.Logger(__name__, level=logging.DEBUG)

class IvySubscribe:
    def __init__(self,  ivy_link, message_types, allow_direct_calls=True):
        self.ivy_link = ivy_link
        self.message_types = message_types
        self.allow_direct_calls = allow_direct_calls

    def __call__(self, f):
        for message_class, message_name in self.message_types:
            msg_type_obj = message.PprzMessage(
                class_name=message_class, 
                msg=message_name
            )
            self.ivy_link.subscribe(f, msg_type_obj)
            logger.info(f"subscribed to {message_class}.{message_name}")
        
        if self.allow_direct_calls:
            return f
        else:
            def dummy(*__, **_): 
                raise RuntimeError("Direct calls to this method are not allowed")

            return dummy
