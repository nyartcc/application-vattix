from math import acos, sin, cos, radians, atan2, sqrt
from main import debug, verbose


def distance_between_coordinates(src, dst):
    if debug and verbose is True:
        lat1 = radians(58.964432)
        lat2 = radians(59.913868)
        lon1 = radians(5.726250)
        lon2 = radians(10.752245)
    else:
        lat1 = radians(src['lat'])
        lon1 = radians(src['lon'])
        lat2 = radians(dst['lat'])
        lon2 = radians(dst['lon'])

    if debug and verbose is True:
        print(debug, lat1, lon1, lat2, lon2)
        print("Debug: 3963 * acos(sin({lat1}) * sin({lat2}) + cos({lat1}) * cos({lat2}) * cos({lon2} - {lon1})".format(
            lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2))

    d = (3963 * (acos((sin(lat1) * sin(lat2)) + (cos(lat1) * cos(lat2) * cos(lon2 - lon1)))))

    # Convert statute miles to nautical miles
    d = d * 0.87

    if debug and verbose is True:
        print("Control (Should be 164):", round(d))

    return d


def cal_radian(coordinate):
    PI = 3.141592
    x = coordinate * (PI / 180)
    return x


def distance_points(src, dst):
    lat1 = radians(src['lat'])
    lon1 = radians(src['lon'])
    lat2 = radians(dst['lat'])
    lon2 = radians(dst['lon'])
    print("🐛 Debug - src['lat']", lat1, lon1, lat2, lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(dlon / 2)) ** 2

    R = 6373.0

    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance / 1.852
