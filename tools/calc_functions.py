from math import acos, sin, cos


def distanceBetweenCoordinates(lat1, lon1, lat2, lon2, debug, verbose):
    if debug is True:
        lat1 = 58.964432
        lat2 = 59.913868
        lon1 = 5.726250
        lon2 = 10.752245

    PI = 3.141592
    lat1 = lat1 * (PI / 180)
    lat2 = lat2 * (PI / 180)
    lon1 = lon1 * (PI / 180)
    lon2 = lon2 * (PI / 180)

    if debug or verbose is True:
        print(debug, lat1, lon1, lat2, lon2)
        print("Debug: 3963 * acos(sin({lat1}) * sin({lat2}) + cos({lat1}) * cos({lat2}) * cos({lon2} - {lon1})".format(
            lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2))

    d = (3963 * (acos((sin(lat1) * sin(lat2)) + (cos(lat1) * cos(lat2) * cos(lon2 - lon1)))))

    # Convert statute miles to nautical miles
    d = d * 0.87

    if debug is True:
        print("Control (Should be 164):", round(d))

    return d

    # D = 3963 * acos( sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 – lon1) );
