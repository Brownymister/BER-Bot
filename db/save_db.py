import os ,sys
p = os.path.abspath('.')
sys.path.insert(1, p)
from auth import (
    db_user,
    db_password,
    db,
    db_host
)
from src.calulate_distace import distace_in_km_by_coordinates
import mysql.connector
from scrape import Scrape
from datetime import datetime
import requests
import json
from bs4 import BeautifulSoup

"""
CREATE TABLE flights(id INT AUTO_INCREMENT PRIMARY KEY,
timestamp INT, icao24 varchar(20), callsighn varchar(10),
depatureAirport varchar(20), arrivalAirport varchar(20), 
distance varchar(255), status varchar(20), origin_country varchar(30));
"""


class Evaluation:

    def __init__(self) -> None:
        self.last_request_data = []
        pass

    def save_in_db(self) -> None:
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()
        scrape = Scrape()
        scrape_data = scrape.scrape_data()
        if scrape_data == False:
            return
        for i in scrape.all_flights:
            if len(self.last_request_data) != 0:
                if self.icao24_exsists(i['icao24']) == False:
                    self.commit_to_db(i, mycursor,mydb)
            else:
                self.commit_to_db(i, mycursor,mydb) 
        self.last_request_data = scrape.all_flights            
        
    def commit_to_db(self, i, mycursor,mydb) -> None:
        time_stamp = i['time_stamp']
        icao24 = i['icao24']
        callsighn = i['callsign']
        origin_country = i['origin_country']
        if i['on_ground'] == True:
            status = "landed"
        elif i['vertical_rate'] > 0:
            status = "depature"
        else:
            status = "arrival"
        sql = f'INSERT INTO flights (timestamp, icao24, callsighn,status,origin_country) VALUES ({time_stamp}, "{icao24}", "{callsighn}", "{status}","{origin_country}")'
        print(sql)
        mycursor.execute(sql)
        mydb.commit()

    def icao24_exsists(self,icao) -> bool:
        found = False
        for i in self.last_request_data:
            if i['icao24'] == icao:
                found = True
                break
        return found

    def evaluate(self) -> None:
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()
        mycursor = mydb.cursor()
        sql = "SELECT * FROM flights WHERE timestamp < "+str(int(datetime.now().timestamp())-(24*60*60))+" & arrivalAirport IS NULL;"
        print(sql)
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for i in myresult:
            begin_date = (i[1]- 24 * 60 * 60)
            end_date = str(int(datetime.now().timestamp()))
            url = f"https://opensky-network.org/api/flights/aircraft?icao24={i[2]}&begin={begin_date}&end={end_date}" 
            print(url)
            result = requests.get(url)
            result_json = json.loads(result.text)
            for a in result_json:
                if a['callsign'].replace(" ", "") == i[3] and a['firstSeen'] >  (i[1]- 60 * 60) and a['firstSeen'] < (i[1]+ 60 * 60):
                    if a['estDepartureAirport'] == "EDDB" or a['estArrivalAirport'] == "EDDB":
                        departure_airport = self.translate_icao(a['estDepartureAirport'])
                        arrival_airport = self.translate_icao(a['estArrivalAirport'])
                        print(departure_airport)
                        print(arrival_airport)
                        sql = f'UPDATE flights SET depatureAirport = "{departure_airport}", arrivalAirport = "{arrival_airport}" WHERE id = "{i[0]}"'
                        print(sql)
                        mycursor.execute(sql)
                        mydb.commit()

    def translate_icao(self, icao) -> str:
        url = "https://www.flughafendetails.de/fluginfo/flughafencodes-europaeischer-flughaefen/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        if icao == None:
            return "unknown"
        result = icao
        allInfection = soup.find('tbody')
        lines = allInfection.find_all('tr')
        for line in lines:
            if icao in line.text:
                elements = line.find_all('td')
                result = elements[2].text +" - "+ elements[0].text
                break
        return result

    def calculate_distance(self, airport_code):
        """52.369850, 13.500286 - BER coordinates"""

        distace_in_km_by_coordinates(52.369850, 13.500286)

    def get_most_dearture_airports(self) -> None:
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()
        mycursor = mydb.cursor()
        sql = "SELECT arrivalAirport FROM flights;"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        results = {}

        for i in myresult:
            i = str(i).replace("('", "").replace("',)", "")
            if i != "BER - Berlin Brandenburg Airport":
                if i not in results:
                    results.update({str(i):1})
                else:
                    results[i] += 1
        results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        print(results)



evaluate = Evaluation()
""" print(evaluate.translate_icao("EDDB")) """
""" evaluate.get_most_dearture_airports() """
evaluate.evaluate()