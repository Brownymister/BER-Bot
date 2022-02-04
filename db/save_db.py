import os ,sys
p = os.path.abspath('.')
sys.path.insert(1, p)
from auth import (
    db_user,
    db_password,
    db,
    db_host
)
import mysql.connector
from scrape import Scrape
import time

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

    def commit_to_db(self, i, mycursor,mydb):
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
        sql = f'INSERT INTO flights (timestamp, icao24, callsighn,status,origin_country, model) VALUES ({time_stamp}, "{icao24}", "{callsighn}", "{status}","{origin_country}")'
        mycursor.execute(sql)
        mydb.commit()

    def icao24_exsists(self,icao) -> bool:
        found = False
        for i in self.last_request_data:
            if i['icao24'] == icao:
                found = True
                break
        return found

evaluation = Evaluation()
evaluation_data = evaluation.save_in_db()
time.sleep(20)
evaluation_data = evaluation.save_in_db()