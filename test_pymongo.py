""" An example of how to connect to MongoDB """
import os, sys, string, time, re, datetime
import requests, json, urllib, urllib2, base64
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def main():
    """ Connect to MongoDB """
    try:
        client = MongoClient('localhost', 27017)
        print "Connected successfully"

        # GRAB THE ALCHEMY CREDENTIALS
        credentials = get_credentials()

        tweet = {}
        tweet["text"] = "Use the Givelify mobile giving app to conveniently give and track church giving and non profit donations from your smartphone. Enjoy easy access to accurate donation records for tax time. Your church or favorite charity doesn't even need to be registered to receive your donations. Simply search, donate and let Givelify handle the rest. Donate during fundraising events, worship services, while vacationing, at work, conventions or anywhere else. Donations can be completed in as few as three taps on your mobile phone and access to donation records is as easy as two taps. Now available to for non profits and churches."

        sentiment_target = ''

        #GET DATA FROM ALCHEMY
        result_queue = []
        get_text_sentiment(credentials['apikey'], tweet, sentiment_target, result_queue)

        # Store data in MongoDB
        store(result_queue)

        db = client['test-database']
        collection = db['test-collection']
        post = {"author": "Mike",
         "text": "My first blog post!",
         "tags": ["mongodb", "python", "pymongo"],
         "date": datetime.datetime.utcnow()}

        posts = db.posts
        post_id = posts.insert_one(post).inserted_id
        print post_id

        print posts.find_one()


    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)

def store(results):
    # Instantiate your MongoDB client
    mongo_client = pymongo.MongoClient('localhost', 27017)
    print "Connected successfully"
    # Retrieve (or create, if it doesn't exist) the twitter_db database from Mongo
    db = mongo_client.alchemy_db

    db_results = db.results

    for result in results:
        db_id = db_results.insert(result)

    db_count = db_results.count()

    print "Results stored in MongoDB! Number of documents in alchemy_db: %d" % db_count

    return

def get_credentials():
    creds = {}
    creds['apikey']      = str()

    # If the file credentials.py exists, then grab values from it.
    # Values: "twitter_consumer_key," "twitter_consumer_secret," "alchemy_apikey"
    # Otherwise, the values are entered by the user
    try:
        import credentials
        creds['apikey']          = credentials.alchemy_apikey
    except:
        print "No credentials.py found"
        creds['apikey']          = raw_input("Enter your AlchemyAPI key: ")

    print "Using the following credentials:"
    print "\tAlchemyAPI key:", creds['apikey']

    # Test the validity of the AlchemyAPI key
    test_url = "http://access.alchemyapi.com/calls/info/GetAPIKeyInfo"
    test_parameters = {"apikey" : creds['apikey'], "outputMode" : "json"}
    test_results = requests.get(url=test_url, params=test_parameters)
    test_response = test_results.json()

    if 'OK' != test_response['status']:
        print "Oops! Invalid AlchemyAPI key (%s)" % creds['apikey']
        print "HTTP Status:", test_results.status_code, test_results.reason
        sys.exit()

    return creds

def get_text_sentiment(apikey, tweet, target, output):

    # Base AlchemyAPI URL for targeted sentiment call
    alchemy_url = "http://access.alchemyapi.com/calls/text/TextGetTextSentiment"

    # Parameter list, containing the data to be enriched
    parameters = {
        "apikey" : apikey,
        "text"   : tweet['text'],
        "outputMode" : "json",
        "showSourceText" : 1
        }

    try:

        results = requests.get(url=alchemy_url, params=urllib.urlencode(parameters))
        response = results.json()

    except Exception as e:
        print "Error while calling TextGetTargetedSentiment on Tweet (ID %s)" % tweet['id']
        print "Error:", e
        return

    print response

    try:
        if 'OK' != response['status'] or 'docSentiment' not in response:
            print "Problem finding 'docSentiment' in HTTP response from AlchemyAPI"
            print response
            print "HTTP Status:", results.status_code, results.reason
            print "--"
            return

        tweet['sentiment'] = response['docSentiment']['type']
        tweet['score'] = 0.
        if tweet['sentiment'] in ('positive', 'negative'):
            tweet['score'] = float(response['docSentiment']['score'])
        print tweet
        output.append(tweet)

    except Exception as e:
        print e
        print "D'oh! There was an error enriching Tweet (ID %s)" % tweet['id']
        print "Error:", e
        print "Request:", results.url
        print "Response:", response

    return

if __name__ == "__main__":
    main()