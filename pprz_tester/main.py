import sys

from observer import Observer
from pprzlink_enhancements import MessageBuilder

sys.path.append("../pprzlink/lib/v1.0/python")
import logging
from typing import Dict
import datetime

import pandas as pd
import os

import pprzlink as pl

from pprz_tester.pprzlink_enhancements import IvySubscribe
from pprz_tester import aircraft

logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())

agent_name = "MJafarIvyAgent"
start_time = datetime.datetime.now().strftime("%m%d-%H%M%S")
ivy = pl.ivy.IvyMessagesInterface(
    agent_name=agent_name,
    start_ivy=True,
)

aircraft_list: Dict[int, aircraft.Aircraft] = dict()


class CurrentBlockChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        block_name = self.ac.find_block_name(new_value)
        logger.info(f'Aircraft {self.ac.id} in block {new_value}: {block_name}')
        if block_name == 'Takeoff':
            self.ac.commands.launch()


class APModeChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        logger.debug(f'{self.ac.id} changed mode to {new_value}')
        if self.ac.params.pprz_mode__ap_mode == 2:  # AUTO1 or AUTO2
            logger.info(f'Aircraft {self.ac.id} Mode = AUTO2, ready')
            self.ac.commands.takeoff()
            ivy.send(MessageBuilder('ground', 'MOVE_WAYPOINT').p('ac_id', self.ac.id).p('alt', 300)
                     .p('wp_id', 3).p('lat', 43.4659053).p('long', 1.2700005).build())
            ivy.send(MessageBuilder('ground', 'MOVE_WAYPOINT').p('ac_id', self.ac.id).p('alt', 300)
                     .p('wp_id', 4).p('lat', 43.4654170).p('long', 1.2799074).build())


class CircleCountChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        logger.info(f'Aircraft {self.ac.id} circle count changed to {new_value}')
        if self.ac.params.navigation__cur_block == self.ac.flight_plan_blocks['Standby'] and new_value >= 1:
            # End of circle
            self.ac.commands.jump_to_block('Oval 1-2')


class AltitudeChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        if old_value is not None and abs(old_value - new_value) < 0.5:
            # Not large enough, just ignore.
            return
        logger.info(f'Aircraft {self.ac.id} changed altitude to {new_value}m')


class RecordFlight(Observer):
    def __init__(self, ac):
        super(RecordFlight, self).__init__(ac)
        self.history = {name: list() for name in ['unix_time', 'roll', 'pitch', 'heading', 'agl', 'airspeed',
                                                  'throttle', 'aileron', 'elevator', 'rudder', 'flaps']}
        self.ready = False
        self._df = None

    def notify(self, property_name, old_value, new_value: pl.message.PprzMessage):
        if not self.ready and any(required is None for required in [
            self.ac.params.commands__values,
            self.ac.params.engine_status__throttle,
        ]):
            return
        self.ready = True
        msg_dict = new_value.to_dict()
        msg_dict.pop('msgname')
        msg_dict.pop('msgclass')
        msg_dict.pop('ac_id')
        for k in self.history.keys() & msg_dict.keys():
            self.history[k].append(msg_dict[k])
        self.history['throttle'].append(self.ac.params.engine_status__throttle)
        if self.ac.id == 14:   # Microjet
            _, roll, pitch, _ = self.ac.params.commands__values  # throttle, roll, pitch, shutter
            yaw = 0
        elif self.ac.id == 2:  # Bixler
            _, roll, pitch, yaw = self.ac.params.commands__values  # throttle, roll, pitch, yaw

        self.history['aileron'].append(roll)
        self.history['elevator'].append(pitch)
        self.history['rudder'].append(yaw)
        self.history['flaps'].append(0)

        # Invalidate DF cache
        self._df = None  # Not thread safe
        if len(self.history['unix_time']) % 10 == 0:
            # Periodic save
            self._save_history()

    def _save_history(self):
        log_file_name = f'{self.ac.name}_{start_time}'
        log_file_addr = os.path.join("..", "logs", log_file_name)

        logger.debug(f"Saving aircraft telemetry logs to {log_file_addr}")
        # self.history_df.to_hdf(log_file_addr + '.hd5', f'ac_{self.ac.id}')
        self.history_df.to_csv(log_file_addr + '.csv')

    @property
    def history_df(self):  # Not thread safe
        if self._df is None:
            df = pd.DataFrame(self.history)
            df['unix_time'] = pd.to_datetime(df['unix_time'], unit='s')
            df.set_index('unix_time', inplace=True)
            self._df = df
        return self._df

    def __del__(self):
        self._save_history()


def add_aircraft_if_new(ac_id, kwargs):
    if ac_id not in aircraft_list:
        new_ac = create_aircraft(ac_id, kwargs)
        aircraft_list[ac_id] = new_ac


def create_aircraft(ac_id, kwargs):
    new_ac = aircraft.Aircraft(
        ivy_link=ivy,
        ac_id=ac_id,
        **kwargs
    )
    new_ac.observe('navigation__cur_block', CurrentBlockChanged(new_ac))
    new_ac.observe('navigation__circle_count', CircleCountChanged(new_ac))
    new_ac.observe('pprz_mode__ap_mode', APModeChanged(new_ac))
    new_ac.observe('flight_param__alt', AltitudeChanged(new_ac))
    new_ac.observe('flight_param', RecordFlight(new_ac))
    return new_ac


@IvySubscribe(ivy_link=ivy, message_types=[("ground", "NEW_AIRCRAFT")])
def new_aircraft_callback(ac_id, msg):
    logger.info(f"New aircraft message {ac_id}: {msg}")
    ac_id = int(ac_id)
    kwargs = dict(auto_request_config=True)
    add_aircraft_if_new(ac_id, kwargs)


def request_aircraft_list():
    def aircraft_list_callback(ac_id, msg):
        for ac_id in map(int, msg['ac_list']):
            kwargs = dict(auto_request_config=True)
            add_aircraft_if_new(ac_id, kwargs)

    ivy.send_request(
        class_name="ground",
        request_name="AIRCRAFTS",
        callback=aircraft_list_callback,
    )


def main():
    import time
    time.sleep(0.1)  # TOFF
    request_aircraft_list()


if __name__ == '__main__':
    main()
