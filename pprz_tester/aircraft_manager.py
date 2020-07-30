import functools
import importlib
import logging
import time
from typing import Dict

import aircraft
from flight_plan import items
from flight_plan.generation_helper import takeoff_and_launch, wait_for_mode_2, move_waypoints, \
    prepare_new_waypoint_locations, FlightPlanPerformingObserver
import pprzlink as pl
from flight_recorder import RecordFlight
from pprzlink_enhancements import IvySubscribe

logger = logging.getLogger('pprz_tester')


class AircraftManager:
    def __init__(self, agent_name="MJafarIvyAgent", start_ivy=False, *,
                 plan=None, plan_args=list(), waypoints=dict(), prep_mode=['climb'],
                 log_dir=None, log_file_format=None):
        from datetime import datetime

        self.aircraft_list: Dict[int, aircraft.Aircraft] = dict()
        self.ivy = pl.ivy.IvyMessagesInterface(agent_name=agent_name, start_ivy=False)
        # Had to patch it this way instead of my sweet sweet decorator
        self.new_aircraft_callback = IvySubscribe(ivy_link=self.ivy, message_types=[("ground", "NEW_AIRCRAFT")]) \
            (self.new_aircraft_callback)

        self.waypoints = waypoints
        self.prep_mode = prep_mode
        self.plan = plan
        self.plan_args = dict()
        for arg_str in (plan_args or []):
            if '=' in arg_str:
                key, value = arg_str.split('=')
            else:
                key, value = arg_str, True

            self.plan_args[key] = value
        self.start_time = datetime.now().strftime("%m%d-%H%M%S")
        self.log_dir = log_dir
        self.log_file_format = log_file_format

        if start_ivy:
            self.start()

    def start(self):
        self.ivy.start()
        time.sleep(0.1)  # TOFF
        self.request_aircraft_list()

    def add_aircraft_if_new(self, ac_id, kwargs):
        if ac_id not in self.aircraft_list:
            new_ac = self.create_aircraft(ac_id, kwargs)
            self.aircraft_list[ac_id] = new_ac

    def load_plan(self, ac):
        if not self.plan:
            logger.warning('No plan specified')
            return []

        module_name = self.plan

        plan_module = importlib.import_module(f'generated_plans.{module_name}')
        plan_instance = plan_module.Plan(ac=ac)
        return plan_instance.get_items(**self.plan_args)

    def _plan_generator(self, new_ac):
        yield from wait_for_mode_2

        if self.waypoints:
            yield from move_waypoints(prepare_new_waypoint_locations(new_ac.flight_plan_waypoints, self.waypoints))
            # 3: WaypointLocation(lat=43.4659053, long=1.2700005, alt=300),
            # 4: WaypointLocation(lat=43.4654170, long=1.2799074, alt=300),

        yield from takeoff_and_launch

        yield items.WaitForState(state_name_or_id='Standby')

        prep_list = []
        if 'circle' in self.prep_mode:
            prep_list.append(items.WaitForCircles(n_circles=1))
        if 'climb' in self.prep_mode:
            prep_list.append(items.WaitClimb(tolerance=5))
        yield items.WaitAll(*prep_list)

        yield from self.load_plan(new_ac)

    def _get_log_file_name(self, ac):
        arg_str = ('[' +
                   ",".join(f'{k}={v}' for k, v in self.plan_args.items()) +
                   ']') if self.plan_args else ''
        return f'{ac.name}_{self.start_time}_{self.plan}{arg_str}'

    def create_aircraft(self, ac_id, kwargs):
        new_ac = aircraft.Aircraft(
            ivy_link=self.ivy,
            ac_id=ac_id,
            **kwargs
        )

        flight_plan_runner = FlightPlanPerformingObserver(new_ac, self._plan_generator(new_ac))
        new_ac.observe('navigation__cur_block', flight_plan_runner)
        new_ac.observe('navigation__circle_count', flight_plan_runner)
        new_ac.observe('pprz_mode__ap_mode', flight_plan_runner)
        new_ac.observe('flight_param', flight_plan_runner)
        new_ac.observe('flight_param', RecordFlight(
            ac=new_ac,
            log_dir=self.log_dir,
            log_file_name=functools.partial(self._get_log_file_name, ac=new_ac),
            log_file_format=self.log_file_format,
        ))

        return new_ac

    def new_aircraft_callback(self, ac_id, msg):
        logger.info(f"New aircraft message {ac_id}: {msg}")
        ac_id = int(ac_id)
        kwargs = dict(auto_request_config=True)
        self.add_aircraft_if_new(ac_id, kwargs)

    def request_aircraft_list(self):
        def aircraft_list_callback(ac_id, msg):
            for ac_id in map(int, msg['ac_list']):
                kwargs = dict(auto_request_config=True)
                self.add_aircraft_if_new(ac_id, kwargs)

        self.ivy.send_request(
            class_name="ground",
            request_name="AIRCRAFTS",
            callback=aircraft_list_callback,
        )

    def suicide(self):
        # GH-12 Flight records need to be saved before calling __del__
        flight_recorders = []
        for ac in self.aircraft_list.values():
            for pname, obs in ac._observers.items():
                if isinstance(obs, RecordFlight):
                    obs.save_history()
                    flight_recorders.append((ac, pname, obs))

        for ac, pname, obs in flight_recorders:
            ac.look_away(pname, obs)

        self.new_aircraft_callback.__ivy_subs__.unsubscribe()
        self.aircraft_list.clear()
        self.ivy.stop()

    def __del__(self):
        self.suicide()
