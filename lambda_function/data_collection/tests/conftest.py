import pytest


@pytest.fixture(scope="session")
def sample_feed():
    return {
        "general": {
            "version": 3,
            "reload": 1,
            "update": "20230410110128",
            "update_timestamp": "2023-04-10T11:01:28.9810709Z",
            "connected_clients": 1210,
            "unique_users": 1160
        },
        "pilots": [
            {
                "cid": 12345678,
                "name": "John Doe KSEA",
                "callsign": "N123AB",
                "server": "USA-WEST2",
                "pilot_rating": 0,
                "latitude": 0.50284,
                "longitude": 153.92173,
                "altitude": 38904,
                "groundspeed": 487,
                "transponder": "2037",
                "heading": 148,
                "qnh_i_hg": 29.82,
                "qnh_mb": 1010,
                "flight_plan": {
                    "flight_rules": "I",
                    "aircraft": "B77L/H-SDFGHIJ2J4J5M1RWXYZ/CB1V1D1",
                    "aircraft_faa": "H/B77L/L",
                    "aircraft_short": "B77L",
                    "departure": "EDDF",
                    "arrival": "NZAA",
                    "alternate": "NZWP",
                    "cruise_tas": "462",
                    "altitude": "23000",
                    "deptime": "1750",
                    "enroute_time": "2130",
                    "fuel_time": "2331",
                    "remarks": "PBN/A1B1C1D1L1O1S2",
                    "revision_id": 7,
                    "assigned_transponder": "2037"
                },
                "logon_time": "2023-04-09T17:37:43Z",
                "last_updated": "2023-04-10T11:01:21.3302482Z"
            }
        ],
        "controllers": [
            {
                "cid": 98765432,
                "name": "Jane Doe",
                "callsign": "ABC_TWR",
                "frequency": "123.456",
                "facility": 4,
                "rating": 4,
                "server": "USA-EAST-1",
                "visual_range": 40,
                "text_atis": None,
                "last_updated": "2023-04-10T11:01:16.6919006Z",
                "logon_time": "2023-04-09T19:35:43.3132211Z"
            },
            {
                "cid": 13131313,
                "name": "John Doe",
                "callsign": "DEF_APP",
                "frequency": "121.500",
                "facility": 5,
                "rating": 6,
                "server": "USA-EAST-1",
                "visual_range": 150,
                "text_atis": None,
                "last_updated": "2023-04-10T11:01:16.6919006Z",
                "logon_time": "2023-04-09T19:35:43.3132211Z"
            }
        ],
        "atis": [
            {
                "cid": 55555555,
                "name": "James Doe",
                "callsign": "ABC_ATIS",
                "frequency": "118.000",
                "facility": 4,
                "rating": 8,
                "server": "USA-WEST",
                "visual_range": 0,
                "atis_code": "X",
                "text_atis": [
                    "ATIS YMML X 101055",
                    "[APCH] EXPECT GLS OR ILS APCH",
                    "[RWY] 16 FOR ARRS RWY 27 FOR DEPS",
                    "+[WIND] 250/8",
                    "[VIS] GT 10KM",
                    "+[CLD] FEW019, SCT035, BKN047",
                    "+[TMP] 11",
                    "[QNH] 1014"
                ],
                "last_updated": "2023-04-10T11:01:27.6027514Z",
                "logon_time": "2023-04-10T06:10:09.8316506Z"
            }
        ],
        "prefiles": [
            {
                "cid": 3333333,
                "name": "Jenny Doe",
                "callsign": "DEF123",
                "flight_plan": {
                    "flight_rules": "I",
                    "aircraft": "B748/H-SDE3FGHIM1M2RWXY/LB1",
                    "aircraft_faa": "H/B748/L",
                    "aircraft_short": "B748",
                    "departure": "KJFK",
                    "arrival": "WSSS",
                    "alternate": "WSAP",
                    "cruise_tas": "499",
                    "altitude": "41000",
                    "deptime": "0845",
                    "enroute_time": "1758",
                    "fuel_time": "1728",
                    "remarks": "RMK/TCAS SIMBRIEF /V/",
                    "route": "HAPIE DCT YAHOO",
                    "revision_id": 1,
                    "assigned_transponder": "1570"
                },
                "last_updated": "2023-04-10T08:12:59.9038933Z"
            }
        ],
        "facilities": [
            {
                "id": 0,
                "short": "OBS",
                "long": "Observer"
            },
            {
                "id": 1,
                "short": "FSS",
                "long": "Flight Service Station"
            },
            {
                "id": 2,
                "short": "DEL",
                "long": "Clearance Delivery"
            },
            {
                "id": 3,
                "short": "GND",
                "long": "Ground"
            },
            {
                "id": 4,
                "short": "TWR",
                "long": "Tower"
            },
            {
                "id": 5,
                "short": "APP",
                "long": "Approach/Departure"
            },
            {
                "id": 6,
                "short": "CTR",
                "long": "Enroute"
            }
        ],
        "ratings": [
            {
                "id": -1,
                "short": "INAC",
                "long": "Inactive"
            },
            {
                "id": 0,
                "short": "SUS",
                "long": "Suspended"
            },
            {
                "id": 1,
                "short": "OBS",
                "long": "Observer"
            },
            {
                "id": 2,
                "short": "S1",
                "long": "Tower Trainee"
            },
            {
                "id": 3,
                "short": "S2",
                "long": "Tower Controller"
            },
            {
                "id": 4,
                "short": "S3",
                "long": "Senior Student"
            },
            {
                "id": 5,
                "short": "C1",
                "long": "Enroute Controller"
            },
            {
                "id": 6,
                "short": "C2",
                "long": "Controller 2 (not in use)"
            },
            {
                "id": 7,
                "short": "C3",
                "long": "Senior Controller"
            },
            {
                "id": 8,
                "short": "I1",
                "long": "Instructor"
            },
            {
                "id": 9,
                "short": "I2",
                "long": "Instructor 2 (not in use)"
            },
            {
                "id": 10,
                "short": "I3",
                "long": "Senior Instructor"
            },
            {
                "id": 11,
                "short": "SUP",
                "long": "Supervisor"
            },
            {
                "id": 12,
                "short": "ADM",
                "long": "Administrator"
            }
        ],
        "pilot_ratings": [
            {
                "id": 0,
                "short_name": "NEW",
                "long_name": "Basic Member"
            },
            {
                "id": 1,
                "short_name": "PPL",
                "long_name": "Private Pilot License"
            },
            {
                "id": 3,
                "short_name": "IR",
                "long_name": "Instrument Rating"
            },
            {
                "id": 7,
                "short_name": "CMEL",
                "long_name": "Commercial Multi-Engine License"
            },
            {
                "id": 15,
                "short_name": "ATPL",
                "long_name": "Airline Transport Pilot License"
            }
        ]
    }
