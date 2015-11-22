# PlayScraper

import argparse
#from bs4 import BeautifulSoup
import requests
import re
import sqlite3
import time
import datetime

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

szCollection = ['topselling_free']
#                'topselling_paid',
#                'topselling_new_free',
#                'topselling_new_paid',
#                'topgrossing',
#                'movers_shakers']

def CurlReq(database, Category, Collection, index, apps_per_query, cursor):
    # our parameters
    params = {'start':index,
              'num':apps_per_query,
              'numChildren':'0',
              'ipf':'1',
              'xhr':'1'}

    date = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')

    # establish connection with the webpage
    url = 'https://play.google.com/store/apps/category/' + Category + '/collection/' + Collection + '?authuser=0'

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
            print "link = "+link
            print "index="+str(index)
            print "apps_per_query="+str(apps_per_query)
            rank = index+counter
            print "rank = "+str(rank)
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
            _title = re.search('class="document-title" itemprop="name"> <div>(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
            print('Title : %s' % _title.group(1))
            cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'title', _title.group(1)))
            _author = re.search('<span itemprop="name">(.+?)</span>', resp_detail, re.DOTALL|re.UNICODE)
            print('Author : %s' % _author.group(1))
            cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'author', _author.group(1)))
            _author_url = re.search('<a class="document-subtitle primary" href="(.+?)"', resp_detail, re.DOTALL|re.UNICODE)
            print('Author URL : resp_detail://play.google.com%s' % _author_url.group(1))
            cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'author_url', _author_url.group(1)))
            _dateUpdated = re.search('<div class="content" itemprop="datePublished">(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
            print('Date Updated : %s' % _dateUpdated.group(1))
            cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'date_updated', _dateUpdated.group(1)))
            _filesize = re.search('<div class="content" itemprop="fileSize">(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
            if _filesize:
                print('FileSize : %s' % _filesize.group(1))
                cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'file_size', _filesize.group(1)))
            _numInstalls = re.search('<div class="content" itemprop="numDownloads">(.+?)</div>', resp_detail, re.DOTALL|re.UNICODE)
            print('Number of Installs : %s' % _numInstalls.group(1))
            cursor.execute("""INSERT OR IGNORE INTO 'app_data' VALUES (?,?,?)""", (link, 'number_installs', _numInstalls.group(1)))


    except requests.exceptions.HTTPError:
        print "THERE WAS AN HTTP ERROR"

    except KeyboardInterrupt:
        print "HIT THE QUIT!"
        return

def initialize_database(database):
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

    conn.commit()

    return conn

def main():
    parser = argparse.ArgumentParser(description='Scrape the Google PlayStore')
    parser.add_argument('-d','--database',help='-d <sqlite database>', required=True)
    args = parser.parse_args()
    apps_per_query = 5
    apps_to_get = 10


    #INITIALIZE THE DATABASE AND CREATE A CONNECTION
    conn = initialize_database(args.database)

    while True:

        try:

            for category in szCategories:
                for Collection in szCollection:
                    for index in xrange(0,apps_to_get,apps_per_query):
                    #for index in xrange(0,10,1):
                        CurlReq(args.database, category, Collection, index, apps_per_query, conn.cursor())
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
