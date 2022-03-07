from math import acos, sin, cos

def distanceBetweenCoordinates(lat1, lon1, lat2, lon2):
    d = 3963 * acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1))

    return d
