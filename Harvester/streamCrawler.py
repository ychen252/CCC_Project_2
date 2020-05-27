"""
Team 47
Guoning Qi 1022700
Longxuan Xu 963988
Hongju Xia 957832
Yihan Chen 1060155
Yuxuan Chen 1035457
"""

from __future__ import absolute_import, print_function
import json
import re
import time

import tweepy
import TwitterAPI
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from tweepy.parsers import JSONParser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import reverse_geocoder as rg
import couchdb
from googletrans import Translator


consumer_key = "Mb5Miij5BhBiP5e3JHYeYFzaz"
consumer_secret = "Trw4ULKr5qtpz8uom2sLqv79Xp2liFNLHF77dvaHp2qr8xtEW6"

access_token = "1254087553587634178-S1jeOf4NZPzkhXhelgFJUmba0MpLX9"
access_token_secret = "Wy6w9sKwU1SffFRjAoFUABaPd8jgpmAVE0dE9uKu7umlj"

boundaryJS = json.load(open('melb.json'))
sub_list = [ele['properties']["SA2_NAME16"] for ele in boundaryJS["features"]]

translator=Translator()
couch = couchdb.Server("http://admin:123456@172.26.133.148:5984/")
#couch.resource.credentials = ('admin', '123456')
try:
    couch.create("food_test_twitters")
except couchdb.http.PreconditionFailed:
    pass
db = couch["food_test_twitters"]
try:
    couch.create("smoke_test_twitters")
except couchdb.http.PreconditionFailed:
    pass
db1 = couch["smoke_test_twitters"]
def analysis(tweets):
    sentiment = SentimentIntensityAnalyzer()
    text = tweets['text']
    text = removehttp(text)
    score = sentiment.polarity_scores(text)
    return score


def get_food():
    food_list = []
    with open("food.txt", encoding='utf-8') as f:
        for line in f.readlines():
            data = line.strip('\n').strip(' ')
            food_list.append(data)
    return food_list


def get_smoke():
    smoke_list = []
    with open("smoke.txt", encoding='utf-8') as f:
        for line in f.readlines():
            data = line.strip('\n').strip(' ')
            smoke_list.append(data)
    return smoke_list


def removehttp (text): #remove web address

    text = text

    pattern = re.compile('https://t.co/\w+')

    pat = pattern.findall(text)

    if len(pat) is 1:
        aa = pat[0]
        text = text.replace(aa, "")
    return text



def cor2suburb(coordinates):
    for ele in boundaryJS["features"]:
        if ele['geometry']['type'] == 'Polygon':
            if Polygon(ele["geometry"]["coordinates"][0]).contains(Point(coordinates)):
                return ele['properties']["SA2_NAME16"]
        elif ele['geometry']['type'] == 'MultiPolygon':
            for polygon in ele['geometry']['coordinates']:
                if Polygon(polygon[0]).contains(Point(coordinates)):
                    return ele['properties']["SA2_NAME16"]
    return None



class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        try:
            food_list = get_food()
            smoke_list = get_smoke()
            tweets = json.loads(data)
            #print(data)
            score = analysis(tweets)
            text = removehttp(tweets['text'])
            if tweets['geo']:
                lat, long = tweets["geo"]["coordinates"][0], tweets["geo"]["coordinates"][1]
                suburb = cor2suburb([long, lat])
                for food in food_list:
                    if food in text:
                        store_data = {'id': tweets['id'], 'suburb': suburb, 'score': score, 'text': text, 'doc': tweets}
                        db.save(store_data)
                        break
                for smoke in smoke_list:
                    if smoke in text:
                        store_data1 = {'id': tweets['id'], 'suburb': suburb, 'score': score, 'text': text, 'doc': tweets}
                        db1.save(store_data1)
                        break

            return True
        except BaseException as e:
            print(str(e))
            time.sleep(5)


    def on_error(self, status):
        print(status)





if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth_handler=auth, parser=JSONParser(), wait_on_rate_limit=True)
    auth.set_access_token(access_token, access_token_secret)

    stream = tweepy.Stream(auth, l)
    stream.filter(languages=['en'], locations=
    [145.12,-38.45,145.53,-37.38])

