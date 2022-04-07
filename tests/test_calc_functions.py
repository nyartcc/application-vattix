from tools.calc_functions import distance_between_coordinates, get_bearing, distance_points


class TestCalculations:
    def test_add(self):
        assert 1 + 1 == 2

    def test_distance_between_coordinates(self):
        source = {'lat': 58.964432, 'lon': 5.726250}  # Stavanger
        destination = {'lat': 59.914095, 'lon': 10.757933}  # Oslo
        # print(distance_between_coordinates(source, destination))

        assert distance_between_coordinates(source, destination) == 164.16528202268145

    def test_get_bearing(self):
        source = {'lat': 58.964432, 'lon': 5.726250}  # Stavanger
        destination = {'lat': 59.914095, 'lon': 10.757933}  # Oslo
        assert get_bearing(source, destination) == 67.48055421251048

    def test_distance_points(self):
        source = {'lat': 58.964432, 'lon': 5.726250}  # Stavanger
        destination = {'lat': 59.914095, 'lon': 10.757933}  # Oslo

        assert distance_points(source, destination) == 163.79649900003935
