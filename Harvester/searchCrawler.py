"""
Team 47
Guoning Qi 1022700
Longxuan Xu 963988
Hongju Xia 957832
Yihan Chen 1060155
Yuxuan Chen 1035457
"""


import json
import tweepy
import couchdb
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import re
import reverse_geocoder as rg

# global variables:
# boundary file - dictionary
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

boundaryJS = json.load(open('melb.json'))
# all suburb names - list
sub_list = [ele['properties']["SA2_NAME16"] for ele in boundaryJS["features"]]
consumer_key = "Mb5Miij5BhBiP5e3JHYeYFzaz"
consumer_secret = "Trw4ULKr5qtpz8uom2sLqv79Xp2liFNLHF77dvaHp2qr8xtEW6"

access_token = "1254087553587634178-S1jeOf4NZPzkhXhelgFJUmba0MpLX9"
access_token_secret = "Wy6w9sKwU1SffFRjAoFUABaPd8jgpmAVE0dE9uKu7umlj"
# initialize apis
key_secret_pairs = []
key_secret_pairs.append(('Mb5Miij5BhBiP5e3JHYeYFzaz', 'Trw4ULKr5qtpz8uom2sLqv79Xp2liFNLHF77dvaHp2qr8xtEW6'))
api_s = []
for key_secret_pair in key_secret_pairs:
    auth = tweepy.OAuthHandler(key_secret_pair[0], key_secret_pair[1])
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    api_s.append(api)
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


def analysis(tweets):
    sentiment = SentimentIntensityAnalyzer()
    text = tweets['text']
    text = removehttp(text)
    score = sentiment.polarity_scores(text)
    return score


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


def processtweets(tweet_list):
    count = 0
    print(len(tweet_list))
    food_list = get_food()
    smoke_list = get_smoke()
    for tweet in tweet_list[1:]:
        tweetJS = tweet._json
        score = analysis(tweetJS)
        text = removehttp(tweetJS['text'])
        if tweetJS['geo']:
            lat, long = tweetJS["geo"]["coordinates"][0], tweetJS["geo"]["coordinates"][1]
            suburb = cor2suburb([long, lat])
            for food in food_list:
                if food in text:
                    store_data = {'id': tweetJS['id'], 'suburb': suburb, 'score': score, 'text': text, 'doc': tweetJS}
                    db.save(store_data)
                    break
            for smoke in smoke_list:
                if smoke in text:
                    store_data1 = {'id': tweetJS['id'], 'suburb': suburb, 'score': score, 'text': text, 'doc': tweetJS}
                    db1.save(store_data1)
                    break

tweet_list =api_s[-1].search(geocode="-37.999250,144.997395,57km", count=100)
maxID = tweet_list[0].id
while len(tweet_list)>1:
    for api in api_s:
        tweet_list = api.search(max_id=maxID, geocode="-37.999250,144.997395,57km", count=100);
        try:
            processtweets(tweet_list)
        except:
            pass
        maxID  = tweet_list[-1].id
