# Paparazzi Tester
:airplane: Remote controlling paparazzi-powered UAVs to collect flight data.

This consists of a test generator and a test runner. The test scenarios are stored as 
python modules in `pprz_tester/generated_plans`.

## Installation
```git clone --recursive https://github.com/MJafarMashhadi/pprz_tester```
Set `PAPARAZZI_HOME` environment variable to the directory you cloned 
[Paparazzi](https://github.com/paparazzi/paparazzi/) in.

## Test Runner Usage
Your gateway to the tester is [`run_test.py`](pprz_tester/run_test.py) file.

It will run the simulator (unless run with `--no-sim`), data link, and server processes then starts communicating with them through ivy link
protocol. 

### AircraftManager
It starts with `AircraftManager` class listening to new aircraft messages and then requesting the current active 
aircraft list from the server. For each new aircraft it creates an `Aircraft` instance and stores it a dictionary.

### Aircraft
`Aircraft` class downloads the aircraft settings and flight plan XML and stores the relevant parts in its instance 
variables. It also listens for a number of ivy messages to receive aircraft status updates. 

#### params
Upon receiving messages they are decoded and stored in `params` property of the aircraft. 
Parameters store both the messages and their fields. To access a message use its name in lowercase (e.g. 
`ac.params.engine_status`); to access the properties, use `<message_name>__<attribute_name>` (e.g. 
`ac.params.engine_status__rpm`). 

#### commands
`commands` property provides a number of methods to issue new commands to the aircraft. 

    ac.commands.takeoff()
    ac.commands.launch()
    ac.commands.jump_to_block('Survey 1-2')

#### Listen for parameter changes and Ivy messages
By subclassing `Observer`, you can create observer objects that get notified when some parameters change.
To register an observer object to listen for changes in a particular parameter use `oobserve` method in `Aircraft`.

For example:
    
    class AltitudeChanged(Observer):
        def notify(self, property_name, old_value, new_value):
            if old_value is not None and abs(old_value - new_value) < 0.5:
                # Not large enough, just ignore.
                return
            logger.info(f'Aircraft {self.ac.id} changed altitude to {new_value}m')
    
    ac = aircraft_list[14]
    ac.observe('flight_param__alt', AltitudeChanged(ac))
 
The first parameter to observe is the parameter name (or message name), the same as what is used with `ac.params`.
In case of observing a single parameter (just like the above example) it is guaranteed that `notify` is invoked only when 
`new_value != old_value`. Merely receiving an update (which doesn't change the observed parameter) won't trigger it.
`property_name` parameter will be the same as what was passed when registering it.
In case of registering an observer for a whole message the observer will be notified every time that message is 
received. In that case `old_value` will be `None`. For an example check out `RecordFlight` class which subscribes to 
`FLIGHT_PARAM` message.

### Flight Plan
Flight plan is an ordered list of `PlanItem`s. Whenever there is an update in aircraft's status an event is sent
to the flight plan manager. The manager checks the event against the next item in queue, if they match the action will
be performed and removed from the queue (upon successful completion), otherwise the message is ignored. Matching and 
performing are defined by overriding `match` and `act` methods, or alternatively passing callables to the constructor
via `matcher` and `actor` parameters.

An example of passing parameters:

    PlanItem(actor=lambda ac, *_: ac.commands.takeoff())

and a simple example of subclassing `PlanItem` can be seen in `WaitForCircles` class. 

The flight plan always starts with a certain sequence of items. First, it waits for autopilot mode `AUTO 2` to activate, 
it happens after the AP is boot up and ready. Immediately after, it sends a take off command and waits for the take off
mode to activate. As soon as take off mode is activated a launch command is sent that kick starts the flight.
based on `--prep-mode` parameter it waits for certain conditions to be met before moving on to the next stages.

`--prep-mode` with no parameters indicates skipping this step. You can either wait for the climb to finish or wait for
a complete circle around the stand-by waypoint. You can also do both, `--prep-mode circle climb`.

### Fixing and Fuzzing parameters
#### Waypoints
Waypoint locations can be fuzzed during the test generation or the running. Fuzzing in runtime overrides any 
fuzzing/fixing that happened during test generation. In both cases fixing takes priority over fuzzing. So to summarize, 
a waypoint will be located at the place:
1. Fixed in runtime (`run_test.py -w <name or id> <lat> <long> <altitude>`) 
2. Fuzzed in runtime (`run_test.py --fuzz-wps <name or id>`)
3. Fixed in generation (`gen_test.py -w <name or id> <lat> <long> <altitude>`) 
4. Fuzzed in generation (`gen_test.py --fuzz-wps <name or id>`)
5. Specified in flight plan

Note that the commandline options for fuzzing and fixing waypoint locations are the same in both running and generating
modes. `--wp-location` can replace `-w` as its long form as well.

To specify the boundaries in which waypoint locations are randomized in, use `--wp-fuzz-bounds-lat`, 
`--wp-fuzz-bounds-lon`, and `--wp-fuzz-bounds-alt` options to provide min and max ranges (a cube). 

Example:

    python pprz_tester/gen_test.py -w S1 43.4659053 1.27 300 --fuzz-wps S2 --wp-fuzz-bounds-alt 200 220 -l 2 Microjet pprz_tester/generated_plans/l2.py

It fixes waypoint S1, randomizes S2's location and altitude while providing bounds for S2's altitude (200-220 meters)
and using the default east-west and north-south boundaries for its location.

#### In flight actions 
During flight, you can perform various actions to control and monitor the aircraft:

1. **Change Target Altitude**
   ```python
   ac.commands.change_target_altitude(new_altitude)
   ```
   This command allows you to change the target altitude of the aircraft during flight.

2. **Jump to Block**
   ```python
   ac.commands.jump_to_block(block_name_or_id)
   ```
   You can jump to any block in the flight plan either by name or ID. This is useful for testing specific flight segments.
   Common block names include:
   - `'Figure 8 around wp 1'`: Performs a figure-8 pattern around waypoint 1
   - `'Oval 1-2'`: Flies an oval pattern between waypoints 1 and 2
   - `'MOB'`: Man Over Board pattern
   - `'Survey S1-S2'`: Survey pattern between survey points S1 and S2
   - `'Path 1,2,S1,S2,STDBY'`: Follows a specific path through multiple waypoints

3. **Flight Recording**
   The system automatically records flight data including:
   - Flight parameters (airspeed, pitch, roll, heading, altitude)
   - Control surfaces (elevator, aileron, rudder, throttle, flaps)
   - Autopilot states (gaz, lateral, horizontal control modes)
   - Navigation data

   The data is saved in either CSV or HDF5 format (specified by `--log-format`).

4. **Flight Plan Items**
   You can create custom flight plan items by subclassing `PlanItem` or using existing ones:
   - `WaitForState`: Waits for a specific flight state
   - `WaitForSpeed`: Waits for a specific airspeed (with tolerance)
   - `WaitForCircles`: Waits for a number of circles to be completed
   - `WaitClimb`: Waits for altitude to stabilize
   - `WaitForSeconds`: Waits for a specified duration
   - `WaitAny`: Waits for any of the specified conditions
   - `WaitAll`: Waits for all specified conditions

   Example of creating a custom flight plan:
   ```python
   plan = [
       items.JumpToBlock('Survey S1-S2'),
       items.WaitForState('Survey S1-S2'),
       items.WaitForSeconds(60),
       items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
       items.WaitForState('Path 1,2,S1,S2,STDBY'),
       items.WaitForSeconds(30)
   ]
   ```

#### Other parameters
1. **Aircraft Selection**
   The system supports two aircraft types:
   - `Bixler`: A trainer aircraft
   - `Microjet`: A jet-powered aircraft

   Select the aircraft using the `airframe` argument:
   ```bash
   python pprz_tester/run_test.py Bixler ...
   ```

2. **Logging Configuration**
   - `--log`: Directory to store log files (default: "logs")
   - `--log-format`: Format to store logs in (choices: "csv", "hd5")
   - Log files are automatically named using the pattern: `{aircraft_name}_{timestamp}_{plan_name}[args]`
   - Log files contain detailed flight data including:
     - Speed (converted to feet/second)
     - Pitch and roll (scaled to ±35 degrees)
     - Yaw (scaled to ±30 degrees)
     - Control surface positions
     - Throttle percentage
     - Autopilot states

3. **Run Configuration**
   - `--build`: Build the aircraft before launching simulation
   - `--gcs`: Open GCS (Ground Control Station) window
   - `--no-sim`: Skip launching the simulator
   - `--prep-mode`: Specify required conditions before starting flight scenario
     - `circle`: Wait for a complete circle around standby waypoint
     - `climb`: Wait for climb to finish
     - Can use both: `--prep-mode circle climb`
   - `--agent-name`: Unique name for Ivy bus communication (default: "MJafarIvyAgent")

4. **Flight Plan Generation**
   - Plans can be generated with different lengths (1-5)
   - Each plan can have multiple permutations
   - Plans can include waypoint modifications
   - Plans can be customized for specific aircraft types
   - Example plan structure:
     ```python
     class CustomPlan(PlanBase):
         def get_items(self, **kwargs):
             return [
                 items.JumpToBlock('Figure 8 around wp 1'),
                 items.WaitForState('Figure 8 around wp 1'),
                 items.WaitForSeconds(60),
                 items.StopTest()
             ]
     ```

5. **Ivy Communication**
   - The system uses Ivy protocol for communication between components
   - Messages are automatically decoded and stored in aircraft parameters
   - Supports real-time monitoring of aircraft state
   - Enables remote control and command execution
   - Handles automatic reconnection and error recovery

## Test Generator Usage
Test generator's entry point is `