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
 -- To be added --

#### In flight actions 
 -- To be added --

#### Other parameters
 -- To be added --
 
## Test Generator Usage
Test generator's entry point is `pprz_tester/gen_test.py`. It expects the aircraft to be built so the required files are
present in `$PAPARAZZI_HOME/var`. Some parameters such as waypoint fuzzing are shared with test runner. Note that the
parameters that are fuzzed at test generation level are fixed, they won't change every time you run the test; that's to 
improve reproducibility in case of encountering any bugs or anomalous behaviour.

Example: 

    python pprz_tester/gen_test.py --exclude 0 1 2 3 4 10 11 land final flare --length 2 Microjet pprz_tester/generated_plans/l2.py

States 0-4 and 10-14 are excluded from the test, the test length is 2 and it uses the flight plan stored at 
`$PAPARAZZI_HOME/var/aircrafts/Microjet/flight_plan.xml`. The generated test will be stored in `l2.py`.
State names can be used instead of state ids, the state name equivalent of above command is:

    python pprz_tester/gen_test.py -x "Wait GPS" "Geo init" "Holding point" Takeoff Standby "Land Right AF-TD" "Land Left AF-TD" land final flare -l 2 Microjet pprz_tester/generated_plans/l2.py


