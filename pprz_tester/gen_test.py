import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Union, Iterable

from lxml import etree

sys.path.append(str(Path("../pprzlink/lib/v1.0/python").resolve()))
import flight_plan_generator

# Set up logging
logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())


parser = argparse.ArgumentParser()
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
parser.add_argument('-p', '--paparazzi-home', type=Path,
                    help="Directory in which Paparazzi source code is cloned in")
parser.add_argument('-w', '--wp-location', nargs=4, action='append',
                    help="Fix one or more waypoints locations (overrides fuzzing)",
                    metavar=('name', 'latitude', 'longitude', 'altitude'))
parser.add_argument('-i', '--include', nargs='+',
                    help="Flight plan blocks to include in the generated plans")
parser.add_argument('-x', '--exclude', nargs='+',
                    help="Flight plan blocks to exclude from the generated plans")
parser.add_argument('-l', '--length', default='*',
                    help="How many blocks to include in the generated flight plan. Enter '*' to generate all possible "
                         "lengths from 1 to the number of available blocks.")
parser.add_argument('output',
                    help="Directory to output the test plans.")
parser.add_argument('airframe', choices=['Bixler', 'Microjet'],
                    help="The aircraft to simulate")

args = parser.parse_args()

## Start
# Set paparazzi home
paparazzi_home = os.getenv('PAPARAZZI_HOME') or args.paparazzi_home or '../paparazzi'
if not isinstance(paparazzi_home, Path):
    paparazzi_home = Path(paparazzi_home)
paparazzi_home = paparazzi_home.resolve()
if not (paparazzi_home.exists() and paparazzi_home.is_dir()):
    raise ValueError("Paparazzi installation not found. Please set PAPARAZZI_HOME environment "
                     "variable or provide the path with --paparazzi-home (or -p) argument")
paparazzi_home = Path(paparazzi_home)

# Load flight plan
flight_plan_uri = paparazzi_home / 'var' / 'aircrafts' / args.airframe / 'flight_plan.xml'
flight_plan_blocks = dict()
flight_plan_blocks_idx = dict()
flight_plan_waypoints = dict()
fp_tree = etree.parse(f'file://{flight_plan_uri}')
for block in fp_tree.xpath("//block"):
    flight_plan_blocks[int(block.attrib['no'])] = block.attrib['name']
    flight_plan_blocks_idx[block.attrib['name']] = int(block.attrib['no'])
for idx, wp in enumerate(fp_tree.xpath("//waypoint"), start=1):
    flight_plan_waypoints[wp.attrib['name']] = idx

# Make waypoint movement commands
wp_locs = dict()
flight_plan_generator.VALID_RANGE_LON = args.wp_fuzz_bounds_lon
flight_plan_generator.VALID_RANGE_LAT = args.wp_fuzz_bounds_lat
flight_plan_generator.VALID_RANGE_ALT = args.wp_fuzz_bounds_alt
for name in (args.fuzz_wps or []):
    wp_locs[name] = None
for name, *loc in (args.wp_location or []):
    loc = flight_plan_generator.WaypointLocation(*[float(i) for i in loc])
    wp_locs[name] = loc

# Test lengths
test_length = args.length
if test_length == '*':
    raise NotImplementedError("Generating all different lengths is not supported yet.")
else:
    test_length = int(test_length)


def _map_name_to_index(name_or_index):
    try:
        index = int(name_or_index)
    except ValueError:
        index = flight_plan_blocks_idx.get(name_or_index, None)

    return index


def gen_blocks(blocks, l, include=None, exclude=None):
    include = frozenset(map(_map_name_to_index, include or []))
    exclude = frozenset(map(_map_name_to_index, exclude or []))
    to_remove = frozenset(include | exclude)
    block_pool = [*filter(lambda block_index: {block_index, blocks[block_index]}.isdisjoint(to_remove), blocks)]

    def _combinations(start_from, remaining_length):
        undecided_length = len(block_pool) - start_from
        if undecided_length <= 0 or remaining_length <= 0 or undecided_length < remaining_length:
            yield []
        elif undecided_length == remaining_length:
            yield [*range(start_from, len(block_pool))]
        else:
            for combi in _combinations(start_from + 1, remaining_length - 1):
                yield [start_from] + combi
            for combi in _combinations(start_from + 1, remaining_length):
                yield combi

    for combination in _combinations(0, l - len(include)):
        yield list(include) + combination


# Plan template
plan_template = """
import flight_plan
from . import PlanBase


class {ClassName}(PlanBase):
    def get_items(self, **kwargs):
        plan = list()
{params}
{get_items}
        plan.append(flight_plan.StopTest())
        return plan


Plan = {ClassName}
__all__ = ['Plan']
"""


def indent(lines, n=1, indentation=' ' * 4, join=False) -> Union[str, Iterable[str]]:
    def _inner_gen(_lines):
        computed_indent = indentation * n
        for l in _lines:
            if isinstance(l, str):
                yield computed_indent + l
            elif isinstance(l, Iterable):
                yield from _inner_gen(l)
            else:
                raise TypeError(f"Donno what to do with a {type(l)}")

    gen = _inner_gen(lines)
    if join:
        return '\n'.join(gen)
    return gen


scenarios = []
for i, blocks in enumerate(gen_blocks(flight_plan_blocks, test_length, args.include, args.exclude)):
    block_jumps = []
    for block in blocks:
        block_jumps.append(f"flight_plan.JumpToBlock('{flight_plan_blocks[block]}')")
        block_jumps.append(f"flight_plan.WaitForState('{flight_plan_blocks[block]}')")

    scenarios.append("lambda: [\n" +
                    ',\n'.join(indent(block_jumps, n=4)) + ", \n" +
                    (" " * 4 * 3) + "]")

outfile: Path = Path(args.output)
if outfile.exists() and outfile.is_dir():
    outfile = outfile / f'gen__l_{test_length}__{args.airframe}.py'


def make_params(*parameter_names):
    return [
        f"{parameter_name} = kwargs.pop('{parameter_name}')"
        for parameter_name in parameter_names
    ]


outfile.write_text(
    plan_template.format(
        ClassName='GeneratedCombinationsPlan',
        params=indent(make_params('i'), n=2, join=True),
        get_items=indent([
            'plan += [',
            map(lambda line: line + ',', indent(scenarios)),
            '][int(i)]()',
        ], n=2, join=True)
    )
)
