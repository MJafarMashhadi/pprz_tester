import logging
from pathlib import Path

import pandas as pd

import pprzlink as pl
from observer import Observer

logger = logging.getLogger('pprz_tester')
start_time = ''
log_dir = Path.cwd() / 'logs'


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
        if self.ac.id == 14:  # Microjet
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
        log_file_addr = (log_dir / log_file_name).resolve()
        log_file_addr = str(log_file_addr)

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
