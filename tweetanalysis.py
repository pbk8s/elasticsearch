import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
from elasticsearch import Elasticsearch


from config import *

es = Elasticsearch([{'host' : 'clusterIP', 'port' : 9200}])


class TweetStreamListener(StreamListener):


    def on_data(self, data):


        dict_data = json.loads(data)


        tweet = TextBlob(dict_data["text"])

        print ("Gathering live tweets...")

        if tweet.sentiment.polarity < 0:
            sentiment = "negative"
        elif tweet.sentiment.polarity == 0:
            sentiment = "neutral"
        else:
            sentiment = "positive"

        es.index(index="sentiment",
                 doc_type="test-type",
                 body={"author": dict_data["user"]["screen_name"],
                       "date": dict_data["created_at"],
                       "message": dict_data["text"],
                       "polarity": tweet.sentiment.polarity,
                       "subjectivity": tweet.sentiment.subjectivity,
                       "sentiment": sentiment})
        return True

    def on_error(self, status):
        print (status)

if __name__ == '__main__':


    listener = TweetStreamListener()

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, listener)

    stream.filter(track=['graviton2'])
