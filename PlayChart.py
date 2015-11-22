#!/usr/bin/env python
import PlayData
import argparse
import cgi
import os


def main():

    #IF THIS IS BEING CALLED FROM A WEB BROWSER
    if 'GATEWAY_INTERFACE' in os.environ:
        arguments = cgi.FieldStorage()
        if arguments.getvalue('appid') == None:
            return
        appid = arguments.getvalue('appid')
    else:
        #IF THIS IS BEING CALLED FROM THE COMMAND LINE
        parser = argparse.ArgumentParser(description='Display Playstore Data')
        parser.add_argument('-a','--app',help='-a <app identifier>', required=True)
        args = parser.parse_args()
        appid = args.app




    database = "playstore.db"


    displayer = PlayData.PlayData(database)
    title = displayer.getTitle(appid)
    (date,rank) = displayer.getRankLatest(appid, 'FINANCE', 'topselling_free')
    #print "The app %s is ranked %s on %s" % (title, rank, date)
    ranking_json = displayer.getRank(appid, 'FINANCE', 'topselling_free')

    #RETURN THE JSON RESULT
    print "Content-type: application/json\n"
    print ""
    print ranking_json


if __name__ == "__main__":
    main()