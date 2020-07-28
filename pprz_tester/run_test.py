import argparse
import logging
import os
import signal
import subprocess
from pathlib import Path

import cli_helper
import aircraft_manager
import flight_recorder

# Set up logging
logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())


# Parse arguments

parser = argparse.ArgumentParser()
parser.add_argument('--agent-name', nargs=1, default="MJafarIvyAgent",
                    help="The unique name to use when communicating on Ivy bus")

log_group = parser.add_argument_group('Logging')
log_group.add_argument('-l', '--log', nargs=1, default="logs",
                    help="Log file directory")
log_group.add_argument('--log-format', nargs=1, default=["csv"], choices=list(flight_recorder.RecordFlight.LOGGING_FORMATS.keys()),
                    help="The format to store and compress logs in")

cli_helper.add_paparazzi_home_arg(parser)

wps_group = parser.add_argument_group('waypoint locations')
cli_helper.add_waypoint_fuzzing_args(wps_group)
cli_helper.add_waypoint_fixing_args(wps_group)

run_conf = parser.add_argument_group('run configurations')
run_conf.add_argument('-b', '--build', action='store_true', default=False,
                    help="Build the aircraft before launching the simulation")
run_conf.add_argument('--gcs', action='store_true', default=False,
                    help="Open GCS window")
run_conf.add_argument('--no-sim', action='store_true', default=False,
                    help="Does not launch the simulator")
run_conf.add_argument('--prep-mode', nargs='*', choices=['circle', 'climb'],
                    help="The required conditions before starting the flight scenario")

cli_helper.add_airframe_arg(parser)
parser.add_argument('plan',
                    help="Plan name to run. Format: <plan_name>[<arg1>=<val1>,<arg2>=<val2>,...]. Arguments are "
                         "optional. If provided, they will be passed to get_items as keyword arguments. They need "
                         "to be enclosed in square brackets.")
args = parser.parse_args()


## Start
wp_locs = cli_helper.parse_waypoints(args)
paparazzi_home = cli_helper.get_paparazzi_home(args)


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


aircraft_manager = aircraft_manager.AircraftManager(
    agent_name=args.agent_name,
    start_ivy=True,
    waypoints=wp_locs,
    prep_mode=list(set(args.prep_mode or {'climb'})),
    plan=args.plan,
    log_file_format=args.log_format[0],
    log_dir=Path.cwd() / Path(args.log),
)

signal.signal(signal.SIGINT, stop_procedure)
