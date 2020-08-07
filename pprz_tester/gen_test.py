import argparse
import itertools
import logging
import random
from pathlib import Path
from typing import Union, Iterable

from lxml import etree

import cli_helper

# Set up logging
from flight_plan.generation_helper import prepare_new_waypoint_locations

logger = logging.getLogger('pprz_tester')

parser = argparse.ArgumentParser()
cli_helper.add_paparazzi_home_arg(parser)

wps_group = parser.add_argument_group('waypoint locations')
cli_helper.add_waypoint_fuzzing_args(wps_group)
cli_helper.add_waypoint_fixing_args(wps_group)

fp_group = parser.add_argument_group('flight plan options')
fp_group.add_argument('-i', '--include', nargs='+',
                      help="Flight plan blocks to include in the generated plans")
fp_group.add_argument('-x', '--exclude', nargs='+',
                      help="Flight plan blocks to exclude from the generated plans")
fp_group.add_argument('-l', '--length', default='*',
                      help="How many blocks to include in the generated flight plan. Enter '*' to generate all possible"
                           " lengths from 1 to the number of available blocks.")

cli_helper.add_airframe_arg(parser)
parser.add_argument('output', help="Output file name or the directory to output the generated plans")

args = parser.parse_args()

## Start
paparazzi_home = cli_helper.get_paparazzi_home(args)

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

new_wp_locs = prepare_new_waypoint_locations(flight_plan_waypoints, cli_helper.parse_waypoints(args))


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
        yield list(include) + [block_pool[i] for i in combination]


# Plan template
plan_template = """
from flight_plan import items
from flight_plan import generation_helper
from flight_plan.waypoint import WaypointLocation
from . import PlanBase


class {ClassName}(PlanBase):
    def get_items(self, **kwargs):
        plan = list()
{params}
        new_wp_locs = {new_wps}
        if new_wp_locs:
            plan += generation_helper.move_waypoints(new_wp_locs)
{get_items}
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
test_length = args.length
if args.length == '*':
    blocks_gen = itertools.chain(
        *(gen_blocks(flight_plan_blocks, test_length, args.include, args.exclude)
          for test_length in range(1, len(flight_plan_blocks) + 1))
    )
else:
    test_length = int(args.length)
    blocks_gen = gen_blocks(flight_plan_blocks, test_length, args.include, args.exclude)

for i, blocks in enumerate(blocks_gen):
    block_jumps = []
    for block in blocks:
        block_jumps.append(f"items.JumpToBlock('{flight_plan_blocks[block]}')")
        block_jumps.append(f"items.WaitForState('{flight_plan_blocks[block]}')")
        block_jumps.append(f"items.WaitForSeconds({int(random.uniform(60, 90))})")

    if block_jumps:
        scenarios.append(f"lambda: [  # {i}\n" +
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
        ], n=2, join=True),
        new_wps='{\n' + indent(
            [f'    {key}: {value},' for key, value in new_wp_locs.items()] + ['}'],
            n=2, join=True
        ),
    )
)
