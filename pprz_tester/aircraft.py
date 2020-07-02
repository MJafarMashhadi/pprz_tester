import logging

from lxml import etree

import pprzlink as pl
from ivy_request_messages import request_data

logger = logging.getLogger('pprz_tester')


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
        self.flight_plan_blocks = dict()

        if auto_request_config:
            self.request_config()

        self._ac = AircraftCommands(self)

    @property
    def commands(self):
        return self._ac

    def request_config(self):
        def aircraft_config_callback(ac_id, msg):
            assert int(ac_id) == self.id

            logger.info(f"Got new aircraft config {ac_id}: {msg}")
            flight_plan_uri = msg['flight_plan']

            logger.info(f"Loading flight plan {ac_id}: {flight_plan_uri}")
            fp_tree = etree.parse(flight_plan_uri)
            for block in fp_tree.xpath("//block"):
                self.flight_plan_blocks[block.attrib['name']] = int(block.attrib['no'])

        request_data(
            self._ivy,
            self._ivy_agent_name,
            "ground",
            "CONFIG",
            aircraft_config_callback,
            ac_id=self.id
        )

    def update_mode(self, msg):
        new_mode = int(msg['ap_mode'])
        if new_mode == self.mode:
            # No news
            return False
        self.mode = new_mode
        if self.mode == 2:  # AUTO1 or AUTO2
            print(f'{self.id} Mode = AUTO2, ready')

        return True


class AircraftCommands(object):
    def __init__(self, ac: Aircraft):
        self.ac = ac

    def __getattr__(self, item):
        if hasattr(self.ac, item):
            return getattr(self.ac, item)
        else:
            raise AttributeError('No such command \'%s\' available for this aircraft.' % item)

    def _send(self, message):
        return self._ivy.send(message, ac_id=self.id)

    def jump_to_block(self, block_id):
        m = pl.message.PprzMessage("ground", "JUMP_TO_BLOCK")
        m.set_value_by_name('ac_id', self.id)
        m.set_value_by_name('block_id', block_id)

        return self._send(m)

    def takeoff(self):
        # Must ensure takeoff mode is activated before launching
        assert 'Takeoff' in self.flight_plan_blocks, 'No takeoff block found, check if the plan is down linked'
        return self.jump_to_block(self.flight_plan_blocks['Takeoff'])
