# To Do

## Tooling
- [x] Establish Database
- [ ] Build importer for VATSPY Data project
- [ ] Parse VATSPY Airports and airspace boundaries
- 

## Flights
- [ ] If flights are within X degrees of desination airport and within Xft of field elevation, and speed 0, mark flight as completed.
- [ ] If flights are within X+Y degrees of destination airport maybe flag as completed in case of disconnect?
- [ ] If flights are over X+Y degrees away from destination, flag as incomplete pending state? If reconnect within 3 hours, flag as complete?
- [ ] Always count departures when X degrees away from departure field.
- [ ] Do not count pre-filed flightplans.



## Notes:
Formula for calculating the distance in NM between two coordinates:
D = 3963 * acos( sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon2 - lon1));
where lat1, lat2 are latitudes, lon1, lon2 are lonitudes.