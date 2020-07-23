import logging
import time
from typing import Dict

import aircraft
import pprzlink as pl
from flight_plan import PlanItemWaitForState, PlanItemAll, PlanItemJumpToBlock, FlightPlanPerformingObserver, \
    PlanItemWaitClimb, PlanItemWaitForCircles
from flight_plan_generator import move_waypoints, takeoff_and_launch, wait_for_mode_2
from flight_recorder import RecordFlight
from pprzlink_enhancements import IvySubscribe

logger = logging.getLogger('pprz_tester')


class AircraftManager:
    def __init__(self, agent_name="MJafarIvyAgent", start_ivy=False):
        self.aircraft_list: Dict[int, aircraft.Aircraft] = dict()
        self.ivy = pl.ivy.IvyMessagesInterface(agent_name=agent_name, start_ivy=False)
        # Had to patch it this way instead of my sweet sweet decorator
        self.new_aircraft_callback = IvySubscribe(ivy_link=self.ivy, message_types=[("ground", "NEW_AIRCRAFT")])\
            (self.new_aircraft_callback)

        self.waypoints = {}
        self.prep_mode = ['climb']

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

    def create_aircraft(self, ac_id, kwargs):
        new_ac = aircraft.Aircraft(
            ivy_link=self.ivy,
            ac_id=ac_id,
            **kwargs
        )

        set_up = wait_for_mode_2 + takeoff_and_launch
        if self.waypoints:
            set_up.extend(move_waypoints(self.waypoints))
            # 3: WaypointLocation(lat=43.4659053, long=1.2700005, alt=300),
            # 4: WaypointLocation(lat=43.4654170, long=1.2799074, alt=300),

        prep_list = [PlanItemWaitForState(state_name_or_id='Standby')]
        if 'circle' in self.prep_mode:
            prep_list.append(PlanItemWaitForCircles(n_circles=1))
        if 'climb' in self.prep_mode:
            prep_list.append(PlanItemWaitClimb(tolerance=5))
        set_up.append(PlanItemAll(*prep_list))

        flight_plan_runner = FlightPlanPerformingObserver(new_ac, set_up + [
            PlanItemJumpToBlock(state_id_or_name='Oval 1-2'),
        ])
        new_ac.observe('navigation__cur_block', flight_plan_runner)
        new_ac.observe('navigation__circle_count', flight_plan_runner)
        new_ac.observe('pprz_mode__ap_mode', flight_plan_runner)
        new_ac.observe('flight_param', flight_plan_runner)
        new_ac.observe('flight_param', RecordFlight(new_ac))

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
        self.new_aircraft_callback.__ivy_subs__.unsubscribe()
        self.aircraft_list.clear()
        self.ivy.stop()

    def __del__(self):
        self.suicide()
