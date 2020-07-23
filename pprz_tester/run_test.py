import argparse
import logging
import os
import random
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path("../pprzlink/lib/v1.0/python").resolve()))
import flight_plan_generator
import flight_recorder
import aircraft_manager

# Set up logging
logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())


# Parse arguments


def wp_name(name):
    return {
        '1': 3,
        '2': 4,
        'S1': 6,
        'S2': 7,
    }[name]


parser = argparse.ArgumentParser()
parser.add_argument('--agent-name', nargs=1, default="MJafarIvyAgent")
parser.add_argument('--log', nargs=1, default="logs")
parser.add_argument('--prep-mode', nargs='*', choices=['circle', 'climb'])
parser.add_argument('--fuzz-wps', nargs='*', default=[wp_name(_) for _ in ('1', '2', 'S1', 'S2')],
                    choices=['1', '2', 'S1', 'S2'], type=wp_name)
parser.add_argument('--wp-fuzz-bounds-lat', nargs=2, type=float, default=[43.4598, 43.4675])
parser.add_argument('--wp-fuzz-bounds-lon', nargs=2, type=float, default=[1.2654, 1.2813])
parser.add_argument('--wp-fuzz-bounds-alt', nargs=2, type=int, default=[250, 300])
parser.add_argument('-p', '--paparazzi-home', nargs=1)
parser.add_argument('-w', '--wp-location', nargs=4, action='append')
parser.add_argument('-b', '--build', action='store_true', default=False)
parser.add_argument('--gcs', action='store_true', default=False)
parser.add_argument('--no-sim', action='store_true', default=False)
parser.add_argument('airframe', choices=['Bixler', 'Microjet'])
args = parser.parse_args()

# Apply arguments

## Waypoints
wp_locs = dict()
flight_plan_generator.VALID_RANGE_LON = args.wp_fuzz_bounds_lon
flight_plan_generator.VALID_RANGE_LAT = args.wp_fuzz_bounds_lat
for name in args.fuzz_wps:
    wp_locs[name] = flight_plan_generator.WaypointLocation(
        lat=flight_plan_generator.get_rand_lat(),
        long=flight_plan_generator.get_rand_lon(),
        alt=random.uniform(*args.wp_fuzz_bounds_alt),
    )

for name, *loc in (args.wp_location or []):
    name = wp_name(name)
    loc = flight_plan_generator.WaypointLocation(*[float(i) for i in loc])
    wp_locs[name] = loc

## Start
paparazzi_home = os.getenv('PAPARAZZI_HOME') or args.paparazzi_home or '../paparazzi'
paparazzi_home = Path(paparazzi_home).resolve()
if not paparazzi_home.exists():
    raise ValueError("Paparzzi installation not found. Please set PAPARAZZI_HOME environment "
                     "variable or provide the path with --paparazzi-home (or -p) argument")
paparazzi_home = str(paparazzi_home)


def build():
    command = ['make', '-C', paparazzi_home, '-f', 'Makefile.ac', 'AIRCRAFT=' + args.airframe, 'nps.compile']
    build = subprocess.check_call(command, env={
        'PAPARAZZI_HOME': paparazzi_home,
        'PAPARAZZI_SRC': paparazzi_home
    })
    return build


def run_gcs():
    command = [str((Path(paparazzi_home) / Path('sw/ground_segment/cockpit/gcs')).resolve()),
               '-layout', 'large_left_col.xml']
    _env = dict(os.environ)
    _env.update({
        'PAPARAZZI_HOME': paparazzi_home,
        'PAPARAZZI_SRC': paparazzi_home,
    })
    _gcs = subprocess.Popen(command, env=_env)
    return _gcs.pid


def run_server():
    command = [str((Path(paparazzi_home) / Path('sw/ground_segment/tmtc/server')).resolve()), "-no_md5_check"]
    _server = subprocess.Popen(command, env={
        'PAPARAZZI_HOME': paparazzi_home,
        'PAPARAZZI_SRC': paparazzi_home,
    })
    return _server.pid


def run_datalink():
    command = [str((Path(paparazzi_home) / Path('sw/ground_segment/tmtc/link')).resolve()),
               '-udp', '-udp_broadcast']
    _dl = subprocess.Popen(command, env={
        'PAPARAZZI_HOME': paparazzi_home,
        'PAPARAZZI_SRC': paparazzi_home,
    })
    return _dl.pid


def run_sim():
    command = [str((Path(paparazzi_home) / Path('sw/simulator/pprzsim-launch')).resolve()),
               '-a', args.airframe, '-t', 'nps']
    _sim = subprocess.Popen(command, env={
        'PAPARAZZI_HOME': paparazzi_home,
        'PAPARAZZI_SRC': paparazzi_home,
    })
    return _sim.pid


# Run the program and the tester

if args.build:
    build()

gcs, dl, server, sim = None, None, None, None
if args.gcs:
    gcs = run_gcs()

dl = run_datalink()
server = run_server()
if not args.no_sim:
    sim = run_sim()


def stop_procedure(*_):
    global aircraft_manager

    if gcs:
        logger.info('Closing GCS')
        os.kill(gcs, signal.SIGTERM)
    if dl:
        logger.info('Closing DataLink')
        os.kill(dl, signal.SIGTERM)
    if server:
        logger.info('Closing Server')
        os.kill(server, signal.SIGTERM)
    if sim:
        logger.info('Closing Simulator')
        os.kill(sim, signal.SIGTERM)

    if aircraft_manager:
        aircraft_manager.suicide()
        del aircraft_manager


flight_recorder.start_time = datetime.now().strftime("%m%d-%H%M%S")
flight_recorder.log_dir = Path.cwd() / Path(args.log)
aircraft_manager = aircraft_manager.AircraftManager(agent_name=args.agent_name, start_ivy=False)
aircraft_manager.waypoints = wp_locs
aircraft_manager.prep_mode = list(set(args.prep_mode or {'climb'}))
aircraft_manager.start()

signal.signal(signal.SIGINT, stop_procedure)
