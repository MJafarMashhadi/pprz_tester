import sys

from observer import Observer

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
logger.setLevel(logging.DEBUG)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())

agent_name = "MJafarIvyAgent"
start_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S.hd5")
log_file_name = os.path.join("logs/fit/", start_time)
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


class CircleCountChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        logger.info(f'Aircraft {self.ac.id} circle count changed to {new_value}')


class AltitudeChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        if old_value is not None and abs(old_value - new_value) < 0.5:
            # Not large enough, just ignore.
            return
        logger.info(f'Aircraft {self.ac.id} changed altitude to {new_value}m')


class RecordFlight(Observer):
    def __init__(self, ac):
        super(RecordFlight, self).__init__(ac)
        self.history = {name: list() for name in ['unix_time', 'roll', 'pitch', 'heading', 'lat', 'long', 'speed', 'course', 'alt',
                                                  'climb', 'agl', 'itow', 'airspeed']}
        self._df = None

    def notify(self, property_name, old_value, new_value: pl.message.PprzMessage):
        msg_dict = new_value.to_dict()
        msg_dict.pop('msgname')
        msg_dict.pop('msgclass')
        msg_dict.pop('ac_id')
        for k in self.history:  # They share keys, no need for checking if history.keys() is a subset of msg_dict
            self.history[k].append(msg_dict[k])
        self._df = None  # Not thread safe
        if len(self.history['unix_time']) % 10 == 0:
            # Periodic save
            self._save_history()

    def _save_history(self):
        self.history_df.to_hdf(log_file_name, self.ac.id)

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
    request_aircraft_list()


if __name__ == '__main__':
    main()
