#!/usr/bin/python
# PlayScraper

import argparse
from bs4 import BeautifulSoup
import requests
import re
import sqlite3
import pymongo
import time
import datetime

#THIS IS TO GET IT TO WORK ON THE CRONJOB
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

# szCategories = ['BOOKS_AND_REFERENCE','BUSINESS',
#                 'EDUCATION','ENTERTAINMENT',
#                 'FINANCE','HEALTH_AND_FITNESS',
#                 'LIBRARIES_AND_DEMO','LIFESTYLE',
#                 'APP_WALLPAPER','MEDIA_AND_VIDEO',
#                 'MEDICAL','MUSIC_AND_AUDIO',
#                 'NEWS_AND_MAGAZINES','PERSONALIZATION',
#                 'PHOTOGRAPHY','PRODUCTIVITY',
#                 'SHOPPING','SOCIAL',
#                 'SPORTS','TOOLS',
#                 'TRANSPORTATION','TRAVEL_AND_LOCAL',
#                 'WEATHER','APP_WIDGETS',
#                 'GAME_ACTION','GAME_ADVENTURE',
#                 'GAME_ARCADE','GAME_BOARD',
#                 'GAME_CARD','GAME_CASINO',
#                 'GAME_CASUAL','GAME_EDUCATIONAL',
#                 'GAME_MUSIC',
#                 'GAME_PUZZLE','GAME_RACING',
#                 'GAME_ROLE_PLAYING','GAME_SIMULATION',
#                 'GAME_SPORTS','GAME_STRATEGY',
#                 'GAME_TRIVIA','GAME_WORD',
#                 'FAMILY_BRAINGAMES','FAMILY_CREATE',
#                 'FAMILY_EDUCATION','FAMILY_MUSICVIDEO',
#                 'FAMILY_PRETEND']

szCategories = ['FINANCE']

szCollection = ['topselling_free',
                'topselling_paid']

#                'topselling_new_free',
#                'topselling_new_paid',
#                'topgrossing',
#                'movers_shakers']

Countries = ['us']

def process_link(link, date, app_data, Category, Collection, Country, rank, params, cursor):

    print "link = "+link
    print "rank ("+str(Collection)+")= "+str(rank)


    cursor.execute("""INSERT OR IGNORE INTO 'apps' VALUES (?)""", (link,))


    cursor.execute("""INSERT OR IGNORE INTO 'rank_data' VALUES (?,?,?,?,?)""", (link, date, Category, Collection, rank))
    path = 'https://play.google.com/store/apps/details?id=' + link + '\n'
    '''
    The following is used for getting more information about each application
    '''
    details_url = 'https://play.google.com/store/apps/details?id=' + link

    hdetails = requests.post(details_url, params=params)
    #hLink = urllib2.urlopen(tmp)
    print('Getting the %s' % details_url)
    # get the response
    resp_detail = hdetails.text

    #FOR DEBUGGING, PRINT THE SOURCE OUT
    #print resp_detail

    #resp_detail = BeautifulSoup (resp_detail.decode('utf-8', 'ignore'))

    _title = re.search('class="document-title" itemprop="name"> <div>(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
    #print('Title : %s' % _title.group(1).encode('utf-8'))
    if _title:
        print('Title : %s' % _title.group(1).encode('ascii','ignore'))
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'title', _title.group(1).encode('ascii','ignore')))

    _author = re.search('<span itemprop="name">(.+?)</span>', resp_detail, re.DOTALL|re.UNICODE)
    if _author:
        print('Author : %s' % _author.group(1))
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'author', _author.group(1)))

    _author_url = re.search('<a class="document-subtitle primary" href="(.+?)"', resp_detail, re.DOTALL|re.UNICODE)
    if _author_url:
        print('Author URL : resp_detail://play.google.com%s' % _author_url.group(1))
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'author_url', _author_url.group(1)))

    _dateUpdated = re.search('<div class="content" itemprop="datePublished">(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
    if _dateUpdated:
        print('Date Updated : %s' % _dateUpdated.group(1))
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'date_updated', _dateUpdated.group(1)))

    _filesize = re.search('<div class="content" itemprop="fileSize">(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
    if _filesize:
        print('FileSize : %s' % _filesize.group(1))
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'file_size', _filesize.group(1)))

    numInstalls = re.search('<div class="content" itemprop="numDownloads">(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
    #OCCASIONALLY THE NUMBER OF INSTALLS MAY NOT BE LISTED
    if numInstalls:
        print('Number of Installs : %s' % numInstalls.group(1))
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'number_installs', numInstalls.group(1)))


    current_rating = re.search('<div class="current-rating" jsname=".+?" style="width: (.+?)%;"></div>', resp_detail, re.DOTALL|re.UNICODE)
    if current_rating:
        print('Current Rating : %s' % current_rating.group(1))
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'current_rating', current_rating.group(1)))

    reviewer_ratings = re.search('<span class="reviewers-small" aria-label=" (.+?) ratings "></span>', resp_detail, re.DOTALL|re.UNICODE)
    if reviewer_ratings:
        print('Total Ratings : %s' % reviewer_ratings.group(1))
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'reviewer_ratings', reviewer_ratings.group(1)))


    _full_description = re.search('<div class="show-more-content text-body" itemprop="description"(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
    if _full_description:
        _full_description = BeautifulSoup(_full_description.group(1), 'html.parser')
        print('full_description : %s' % _full_description.get_text())
        cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'full_description', _full_description.get_text()))

    #DAILY REVIEW AND DOWNLOAD DATA
    print('today\'s date : %s' % date)
    if (current_rating is not None) & (reviewer_ratings is not None):
        cursor.execute("""INSERT OR IGNORE INTO 'reviews_data' VALUES (?,?,?,?)""", (link, date, reviewer_ratings.group(1), current_rating.group(1)))
    elif current_rating is not None:
        cursor.execute("""INSERT OR IGNORE INTO 'reviews_data' VALUES (?,?,?,?)""", (link, date, '', current_rating.group(1)))
    elif reviewer_ratings is not None:
        cursor.execute("""INSERT OR IGNORE INTO 'reviews_data' VALUES (?,?,?,?)""", (link, date, reviewer_ratings.group(1), ''))
    else:
        cursor.execute("""INSERT OR IGNORE INTO 'reviews_data' VALUES (?,?,?,?)""", (link, date, '', ''))


def CurlReq(database, Category, Collection, Country, index, apps_per_query, cursor):
    # our parameters
    params = {'start':index,
              'num':apps_per_query,
              'numChildren':'0',
              'ipf':'1',
              'xhr':'1'}

    date = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')

    # establish connection with the webpage
    url = 'https://play.google.com/store/apps/category/' + Category + '/collection/' + Collection + '?authuser=0' + '&gl=' + Country

    # url encode the parameters

    #url_params = urllib.urlencode(params)

    try:
        # send out the POST request
        h = requests.post(url, params=params)
        #h = urllib2.urlopen(url, url_params)
        # get the response
        #resp = h.read()
        resp = h.text


        # Search for class="preview-overlay-container" data-docid=
        _download_links = re.findall('class="preview-overlay-container" data-docid="(.+?)"', resp, re.DOTALL|re.UNICODE)

        print _download_links

        counter=0

        for link in _download_links:

            counter+=1
            print "index="+str(index)
            rank = index+counter

            #PROCESS THIS INDIVIDUAL APP
            app_data = {}
            app_data['identifier']=link
            app_data['category']=Category
            app_data['collection']=Collection
            if 'rank' not in app_data:
                app_data['rank']={}
            app_data['rank'][date]=rank

            process_link(link, date, app_data, Category, Collection, Country, rank, params, cursor)


    except requests.exceptions.HTTPError:
        print "THERE WAS AN HTTP ERROR"

    except KeyboardInterrupt:
        print "HIT THE QUIT!"
        return

def initialize_mongo_database(database):
    pass

def initialize_sqlite_database(database):
    conn = sqlite3.connect(database) # or use :memory: to put it in RAM
    cursor = conn.cursor()

    version = 1.0
    date_and_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    #CREATE A TABLE FOR TABLE METADATA
    cursor.execute("""CREATE TABLE IF NOT EXISTS db_info(key, value)""")
    cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS db_info_key_index ON db_info(key)""")
    cursor.executemany("""INSERT OR IGNORE INTO 'db_info' VALUES (?, ?)""", [('version',version)])

    cursor.executemany("""INSERT OR IGNORE INTO 'db_info' VALUES (?, ?)""", [('created',date_and_time)])

    #cursor.execute("""CREATE TABLE IF NOT EXISTS
    #    users(username, phash, vcode, login_count, last_login, last_save_token DEFAULT 'begin', publiccode, first_access)
    #    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS
        apps(appid)
        """)
    cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS apps_appid_index ON apps(appid)""")

    # INFO ABOUT THE INDIVIDUAL APP
    cursor.execute("""CREATE TABLE IF NOT EXISTS app_data(appid, key, value)""")
    cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS app_data_appid_key_index ON app_data(appid, key)""")

    # INFO ABOUT THE DAILY RANKING OF EACH INDIVIDUAL APP
    cursor.execute("""CREATE TABLE IF NOT EXISTS rank_data(appid, date, category, collection, rank)""")
    cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS rank_data_appid_date_index ON rank_data(appid, date)""")
    cursor.execute("""CREATE INDEX IF NOT EXISTS rank_data_appid_category_index ON rank_data(appid, category)""")
    cursor.execute("""CREATE INDEX IF NOT EXISTS rank_data_appid_collection_index ON rank_data(appid, collection)""")

    # INFO ABOUT THE DAILY DOWNLOADS OF EACH INDIVIDUAL APP
    cursor.execute("""CREATE TABLE IF NOT EXISTS reviews_data(appid, date, reviewer_ratings, current_rating)""")
    cursor.execute("""CREATE UNIQUE INDEX IF NOT EXISTS reviews_data_appid_date_index ON reviews_data(appid, date)""")

    conn.commit()

    return conn

def main():
    parser = argparse.ArgumentParser(description='Scrape the Google PlayStore')
    parser.add_argument('-d','--database',help='-d <sqlite database>', required=True)
    parser.add_argument('-t','--type_database',help='-t <type of database>', required=True)
    parser.add_argument('-g','--apps_to_get',help='-g <get this many of the apps>', required=True)
    args = parser.parse_args()

    # ONLY GET 1 APP AT A TIME IF ITS LESS THAN 50
    apps_to_get = int(args.apps_to_get)
    if int(args.apps_to_get) < 50:
        apps_per_query = 1
    else:
        apps_per_query = 50


    #INITIALIZE THE DATABASE AND CREATE A CONNECTION
    if args.type_database == "sqlite":
        conn = initialize_sqlite_database(args.database)
    elif args.type_database == "mongo":
        conn = initialize_mongo_database(args.database)
    else:
        print('Unknown database '+str(args.type_database))
        return

    while True:

        try:

            for category in szCategories:
                for collection in szCollection:
                    print("Hit up the collection %s" % collection)
                    for Country in Countries:
                        print args.apps_to_get
                        print apps_per_query
                        for index in xrange(0,apps_to_get,apps_per_query):
                        #for index in xrange(0,10,1):
                            CurlReq(args.database, category, collection, Country, index, apps_per_query, conn.cursor())
                        conn.commit()
            return

        except KeyboardInterrupt:
            print('\nPausing...  (Hit ENTER to continue, type quit to exit.)')
            try:
                response = raw_input()
                if response == 'quit':
                    break
                print('Resuming...')
            except KeyboardInterrupt:
                print('Resuming...')
                continue

if __name__ == "__main__":
    main()
