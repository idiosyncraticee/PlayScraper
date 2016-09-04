#!/Users/chris/anaconda/bin/python

import PlayData
import argparse
import cgi
import cgitb
import os
import json
import sys
import simplejson as json

def main():

    print "Content-type: application/json"
    print "Access-Control-Allow-Origin: *\n"

    collection = 'topselling_free'
    category = 'FINANCE'


    #IF THIS IS BEING CALLED FROM A WEB BROWSER
    if 'GATEWAY_INTERFACE' in os.environ:
        arguments = cgi.FieldStorage()
        if arguments.getvalue('appid') == None:
            pass
        else:
            appid = arguments.getvalue('appid')


        if arguments.getvalue('state') == None:
            pass
        else:
            state = arguments.getvalue('state')

        if arguments.getvalue('query') == None:
            pass
        else:
            query = arguments.getvalue('query')
    else:
        #IF THIS IS BEING CALLED FROM THE COMMAND LINE
        parser = argparse.ArgumentParser(description='Display Playstore Data')
        parser.add_argument('-a','--app',help='-a <app identifier>', required=True)
        parser.add_argument('-s','--state',help='-s <state>', required=False)
        parser.add_argument('-q','--query',help='-q <query>', required=False)
        args = parser.parse_args()
        appid = args.app
        state = args.state
        query = args.query

    database = "playstore.db"
    displayer = PlayData.PlayData(database)

    if state == "AllApps" and query is not None:
        apps = {}
        apps_data = json.loads(displayer.getApps(query))
        apps['results'] = apps_data
        apps_json = json.dumps(apps)
        print(apps_json)
        return
    elif state == "AppDetails" and appid is not None:
        apps = {}
        apps_data = json.loads(displayer.getAppDetails(appid, category, collection))
        apps['results'] = apps_data
        apps_json = json.dumps(apps)
        print(apps_json)
        return





    title = displayer.getTitle(appid)
    (date,rank) = displayer.getRankLatest(appid, 'FINANCE', 'topselling_free')
    #print "The app %s with title %s is ranked %s on %s" % (appid, title, rank, date)
    ranking_json = displayer.getRank(appid, 'FINANCE', 'topselling_free')

    #RETURN THE JSON RESULT
    print(ranking_json)

if __name__ == "__main__":
    main()