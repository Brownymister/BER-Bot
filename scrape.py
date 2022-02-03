import requests
import json
from auth import (
    user,
    password
)


class Scrape:

    def __init__(self) -> None:
        self.url = 'https://'+user+':'+password + \
            '@opensky-network.org/api/states/all?lamin=52.311624&lomin=13.426828&lamax=52.416285&lomax=13.636693'
        self.all_flights = []
        self.currantly_landing_or_take_off = []
        self.already_landed = []
        pass

    def scrape_data(self) -> None:
        result = requests.get(url=self.url)
        result_json = json.loads(result.text)
        self.set_allflight(result_json['states'])

    def set_allflight(self, result) -> None:
        for i in result:
            if len(i[1].replace(" ", "")) > 4 and i[1] != "":
                self.all_flights.append(
                    {"callsign": i[1].replace(" ", ""), "icao24": i[0], "origin_country": i[2], "altitude": i[13], "on_ground": i[8], "time_stamp": i[4]})
        self.filter_allfligths()

    def filter_allfligths(self) -> None:
        for i in self.all_flights:
            if i["on_ground"] == False and i["altitude"] < 500:
                self.currantly_landing_or_take_off.append(i)
            else:
                self.already_landed.append(i)

    def get_allfligth_len(self) -> int:
        return len(self.all_flights)


"""
    latitude   longitude
min 52.380853, 13.429389
max 52.416350, 13.636716
"""
