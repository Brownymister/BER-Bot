import tweepy
from scrape import Scrape
import schedule
import time
from auth import (consumer_key, consumer_secret,
                  access_token, access_token_secret)
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


def tweet() -> None:
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    scrape = Scrape()
    scrape_data = scrape.scrape_data()
    if scrape_data == False:
        return

    msg = generate_tweet_qoute(scrape)
    print(msg)
    filename = getnerate_image(msg, scrape.get_allfligth_len())

    media_id = api.media_upload(filename).media_id
    api.update_status(status="@BERAirport_Bot at " +
                      get_date(), media_ids=[media_id])


def generate_tweet_qoute(scrape) -> str:
    msg = """------------@BERAirport_Bot at """+get_date()+"""------------
        total aircraft at BER: """+str(scrape.get_allfligth_len())+"""
        currantly arriving aircraft: 
        -----------------------------------------
            """
    if len(scrape.currantly_landing) == 0:
        msg += """---
        """
    else:
        for i in range(len(scrape.currantly_landing)):
            msg += str(i+1)+""". callsign: """ + str(scrape.currantly_landing[i]['callsign']) + """ 
            origin country: """+str(scrape.currantly_landing[i]['origin_country'])+""" 
            altitude: """+str(scrape.currantly_landing[i]['altitude'])+"m"
            msg += """  
            -----------------------------------------
            """
    msg += """
        currantly departing aircraft:
        -----------------------------------------
            """

    if len(scrape.currantly_take_off) == 0:
        msg += """---
        """
    else:
        for i in range(len(scrape.currantly_take_off)):
            msg += str(i+1)+""". callsign: """ + str(scrape.currantly_take_off[i]['callsign']) + """ 
            origin country: """+str(scrape.currantly_take_off[i]['origin_country'])+""" 
            altitude: """+str(scrape.currantly_take_off[i]['altitude'])+"m"
            msg += """  
            -----------------------------------------
            """
    msg += """
        allready landed (boarding):
        -----------------------------------------
            """

    if len(scrape.already_landed) == 0:
        msg += """---
        """
    else:
        for i in range(len(scrape.already_landed)):
            msg += str(i+1)+""". callsign: """ + str(scrape.already_landed[i]["callsign"]) + """ 
            origin country: """+str(scrape.already_landed[i]["origin_country"])+"""
            altitude: """+str(scrape.already_landed[i]['altitude']) + """
            -----------------------------------------
            """

    return msg


def getnerate_image(quote, all_fligth_len) -> str:
    x = 460
    y = 100 * (all_fligth_len+2)
    img = Image.new('RGB', (x, y), color="white")
    d1 = ImageDraw.Draw(img)
    font = ImageFont.truetype('/Library/Fonts/Arial.ttf', 15)
    d1.text((65, 10), quote, fill="black", font=font)
    file_name = "./img/BER_Log_"+get_date().replace(" ", "_").replace("/", "_")+".jpeg"
    img.save(file_name)
    return file_name


def get_date() -> str:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return str(dt_string)


if __name__ == "__main__":
    tweet()
    schedule.every().hour.do(tweet)

    while 1:
        schedule.run_pending()
        time.sleep(1)
