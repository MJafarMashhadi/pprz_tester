import logging

from lxml import etree

import pprzlink as pl
from ivy_subscribe import IvySubscribeOnce

logger = logging.getLogger('pprz_tester')


class RequestUIDFactory:
    _generator = None

    @classmethod
    def _unique_id_generator(cls):
        import os
        pid = os.getpid()

        sequence_number = 0
        while True:
            sequence_number = sequence_number + 1
            yield f'{pid}_{sequence_number}'

    @classmethod
    def generate_uid(cls):
        if cls._generator is None:
            cls._generator = cls._unique_id_generator()
        return next(cls._generator)


class Aircraft(object):
    def __init__(self,
                 ivy_link: pl.ivy.IvyMessagesInterface,
                 ivy_agent_name: str,
                 ac_id: int,
                 auto_request_config: bool = True
                 ):
        self._ivy = ivy_link
        self._ivy_agent_name = ivy_agent_name
        self.id = ac_id
        self.flight_plan_uri = None
        self.mode = None

        if auto_request_config:
            self.request_config()

    def request_config(self):
        new_id = RequestUIDFactory.generate_uid()

        @IvySubscribeOnce(ivy_link=self._ivy, message_types=[r"^((\S*\s*)?%s ground CONFIG( .*|$))" % new_id])
        def aircraft_config_callback(ac_id, msg):
            assert int(ac_id) == self.id

            logger.info(f"Got new aircraft config {ac_id}: {msg}")
            flight_plan_uri = msg['flight_plan']

            fp_tree = etree.parse(flight_plan_uri)
            for block in fp_tree.xpath("//block"):
                print(f'block {block.attrib["name"]} ({block.attrib["no"]})')

        # Manually sending request message since it is not yet implemented in pprz_link.
        config_request_message = pl.message.PprzMessage("ground", "CONFIG_REQ")
        config_request_message.set_value_by_name('ac_id', self.id)
        data_request_message = ' '.join((
            self._ivy_agent_name, new_id, config_request_message.name, config_request_message.payload_to_ivy_string()
        ))
        self._ivy.send(data_request_message)
        logger.info("Requested new aircraft config")

    def jump_to_block(self, block_id):
        m = pl.message.PprzMessage("ground", "JUMP_TO_BLOCK")
        m.set_value_by_name('ac_id', self.id)
        m.set_value_by_name('block_id', block_id)

        return  self._ivy.send(m, ac_id=self.id)

    def update_mode(self, msg):
        new_mode = int(msg['ap_mode'])
        if new_mode == self.mode:
            # No news
            return False
        self.mode = new_mode
        if self.mode == 2:  # AUTO1 or AUTO2
            print("Mode = AUTO2, ready")

        return True

