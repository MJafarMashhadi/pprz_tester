import collections
import random

WaypointLocation = collections.namedtuple('WaypointLocation', 'lat long alt')

VALID_RANGE_LAT = [43.4598, 43.4675]
VALID_RANGE_LON = [1.2654, 1.2813]
VALID_RANGE_ALT = [250, 300]


def get_rand_lat():
    return round(random.uniform(*VALID_RANGE_LAT), 6)


def get_rand_lon():
    return round(random.uniform(*VALID_RANGE_LON), 6)


def get_rand_alt():
    return round(random.uniform(*VALID_RANGE_ALT))


def get_rand_waypoint():
    return WaypointLocation(lat=get_rand_lat(), long=get_rand_lon(), alt=get_rand_alt())
