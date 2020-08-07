import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / Path("pprzlink/lib/v1.0/python").resolve()))
from flight_plan import waypoint

# Set up logging
logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())


def add_waypoint_fuzzing_args(parser):
    parser.add_argument('--fuzz-wps', nargs='*',
                        help="Waypoints to fuzz locations of. Use * to fuzz all")
    parser.add_argument('--wp-fuzz-bounds-lat', nargs=2, type=float, default=[43.4598, 43.4675],
                        help="Minimum and maximum latitude to fuzz waypoint locations in",
                        metavar=('south', 'north'))
    parser.add_argument('--wp-fuzz-bounds-lon', nargs=2, type=float, default=[1.2654, 1.2813],
                        help="Minimum and maximum longitude to fuzz waypoint locations in",
                        metavar=('west', 'east'))
    parser.add_argument('--wp-fuzz-bounds-alt', nargs=2, type=int, default=[250, 300],
                        help="The boundaries inside which waypoint altitudes are fuzzed",
                        metavar=('floor', 'ceiling'))


def add_waypoint_fixing_args(parser):
    parser.add_argument('-w', '--wp-location', nargs=4, action='append',
                        help="Fix one or more waypoints locations (overrides fuzzing)",
                        metavar=('name', 'latitude', 'longitude', 'altitude'))


def add_paparazzi_home_arg(parser):
    parser.add_argument('-p', '--paparazzi-home', type=Path,
                        help="Directory in which Paparazzi source code is cloned in")


def add_airframe_arg(parser):
    parser.add_argument('airframe', choices=['Bixler', 'Microjet'],
                        help="The aircraft to simulate")


def parse_waypoints(args):
    wp_locs = dict()
    waypoint.VALID_RANGE_LON = args.wp_fuzz_bounds_lon
    waypoint.VALID_RANGE_LAT = args.wp_fuzz_bounds_lat
    waypoint.VALID_RANGE_ALT = args.wp_fuzz_bounds_alt

    for name in (args.fuzz_wps or []):
        wp_locs[name] = None

    for name, *loc in (args.wp_location or []):
        loc = waypoint.WaypointLocation(*[float(i) for i in loc])
        wp_locs[name] = loc

    return wp_locs


def get_paparazzi_home(args):
    paparazzi_home = args.paparazzi_home or os.getenv('PAPARAZZI_HOME') or '../paparazzi'
    if not isinstance(paparazzi_home, Path):
        paparazzi_home = Path(paparazzi_home)
    paparazzi_home = paparazzi_home.resolve()
    if not (paparazzi_home.exists() and paparazzi_home.is_dir()):
        raise ValueError("Paparazzi installation not found. Please set PAPARAZZI_HOME environment "
                         "variable or provide the path with --paparazzi-home (or -p) argument")

    return paparazzi_home
