import os
import sys
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
import csv

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
        scrape = Scrape()
        scrape_data = scrape.scrape_data()
        if scrape_data == False:
            return
        for i in scrape.all_flights:
            if len(self.last_request_data) != 0:
                if self.icao24_exsists(i['icao24']) == False:
                    self.commit_to_db(i)
            else:
                self.commit_to_db(i)
        self.last_request_data = scrape.all_flights

    def commit_to_db(self, i) -> None:
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()

        time_stamp = i['time_stamp']
        icao24 = i['icao24']
        callsighn = i['callsign']
        origin_country = i['origin_country']
        if i['on_ground'] == True:
            status = "landed"
        elif i['vertical_rate'] != None and i['vertical_rate'] > 0:
            status = "depature"
        else:
            status = "arrival"
        sql = f'INSERT INTO flights (timestamp, icao24, callsighn,status,origin_country) VALUES ({time_stamp}, "{icao24}", "{callsighn}", "{status}","{origin_country}")'
        print(sql)
        mycursor.execute(sql)
        mydb.commit()

    def icao24_exsists(self, icao) -> bool:
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
        sql = "SELECT * FROM flights WHERE timestamp < " + \
            str(int(datetime.now().timestamp())-(24*60*60)) + \
            " & arrivalAirport IS NULL;"
        print(sql)
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for i in myresult:
            begin_date = (i[1] - 24 * 60 * 60)
            end_date = str(int(datetime.now().timestamp()))
            url = f"https://opensky-network.org/api/flights/aircraft?icao24={i[2]}&begin={begin_date}&end={end_date}"
            print(url)
            result = requests.get(url)
            result_json = json.loads(result.text)
            for a in result_json:
                if  a['callsign'] != None:
                    if a['callsign'].replace(" ", "") == i[3] and a['firstSeen'] > (i[1] - 60 * 60) and a['firstSeen'] < (i[1] + 60 * 60):
                        if a['estDepartureAirport'] == "EDDB" or a['estArrivalAirport'] == "EDDB":
                            departure_airport = self.translate_icao(
                                a['estDepartureAirport'])
                            arrival_airport = self.translate_icao(
                                a['estArrivalAirport'])
                            print(departure_airport)
                            print(arrival_airport)
                            sql = f'UPDATE flights SET depatureAirport = "{departure_airport}", arrivalAirport = "{arrival_airport}" WHERE id = "{i[0]}"'
                            print(sql)
                            mycursor.execute(sql)
                            mydb.commit()

    def translate_icao(self, icao) -> str:
        url = "https://en.wikipedia.org/wiki/List_of_airports_by_ICAO_code:_E"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        if icao == None:
            return "unknown"
        result = icao
        lines = soup.find_all('li')
        for line in lines:
            if icao in line.text:
                code = line.text.split("(")
                if len(code) > 1:
                    code = code[1].split(")")
                    result = code[0] + code[1]
                else:
                    result = code[0]
                break
        return result

    def calculate_distance(self, airport_code,db_id) -> None:
        """52.369850, 13.500286 - BER coordinates"""
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()
        mycursor = mydb.cursor()

        lines = []

        with open('./airports.csv', 'r') as readFile:
            reader = csv.reader(readFile, quotechar='/')
            for row in reader:
                lines.append(row)
                for field in row:
                    if 'Date' in field:
                        lines.remove(row)

        with open('./airports.csv', 'w') as writeFile:
            writer = csv.writer(writeFile, quotechar='/')
            writer.writerows(lines)
        with open('./airports.csv', 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for line in reader:
                if airport_code in line[0]:
                    # line = list(set(line))
                    airport_coordinates = line[5].replace("POINT (", "")
                    airport_coordinates = airport_coordinates.replace(")", "")
                    airport_coordinates = airport_coordinates.split(" ")
                    distance = distace_in_km_by_coordinates(52.369850, 13.500286, airport_coordinates[1], airport_coordinates[0])
                    sql = f'UPDATE flights SET distance = {distance} WHERE id = "{db_id}"'
                    print(sql)
                    mycursor.execute(sql)
                    mydb.commit()
                    break

    def get_most_airports(self, airport) -> None:
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()
        mycursor = mydb.cursor()
        sql = f"SELECT {airport} FROM flights;"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        results = {}
        if myresult != None:
            for i in myresult:
                i = str(i).replace("('", "").replace("',)", "")
                if i != "BER - Berlin Brandenburg Airport" and i != '(None,)':
                    if i not in results:
                        results.update({str(i): 1})
                    else:
                        results[i] += 1
            results = sorted(results.items(), key=lambda x: x[1], reverse=True)
            print(airport)
            print(results)

    def get_total_distance(self) -> None:
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()
        mycursor = mydb.cursor()
        sql = f"SELECT distance FROM flights;"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        result = 0
        for i in myresult:
            i = list(i)
            if i[0] != None:
                result += float(i[0])
        print(str(result)+" km")

    def get_most_origin(self) -> None:
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()
        mycursor = mydb.cursor()
        sql = f"SELECT origin_country FROM flights;"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        results = {}
        if myresult != None:
            for i in myresult:
                i = str(i).replace("('", "").replace("',)", "")
                if i not in results:
                    results.update({str(i): 1})
                else:
                    results[i] += 1
            results = sorted(results.items(), key=lambda x: x[1], reverse=True)
            print(results)

    def update_distance_db(self) -> None:
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db
        )
        mycursor = mydb.cursor()
        mycursor = mydb.cursor()
        sql = f"SELECT * FROM flights WHERE distance IS NULL;"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for i in myresult:
            if i[4] != None and i[5] != None:
                code_a = i[4].split("-")
                code_a = code_a[0].replace(" ", "")
                code_d = i[5].split("-")
                code_d = code_d[0].replace(" ", "")
                if code_a != "BER":
                    result = self.calculate_distance(code_a, i[0])
                else:
                    result = self.calculate_distance(code_d, i[0])
                print(result)


evaluate = Evaluation()
evaluate.get_most_origin()
evaluate.get_total_distance()
evaluate.get_most_airports("depatureAirport")
evaluate.get_most_airports("arrivalAirport")
""" evaluate.update_distance_db() """