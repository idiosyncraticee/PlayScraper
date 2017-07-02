import sqlite3
import json
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import pandas as pd

class PlayData:

    def __init__(self, database):
        #self.header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
        #self.data = None
        #self._tries = tries
        self.database = database
        self._initialize_database()

        pass

    def _get_credentials():
        creds = {}
        creds['gmail_password'] = str()

        # If the file credentials.py exists, then grab values from it.
        # Values: "twitter_consumer_key," "twitter_consumer_secret," "alchemy_apikey"
        # Otherwise, the values are entered by the user
        try:
            import credentials
            creds['gmail_password'] = credentials.gmail_password
        except:
            print "No credentials.py found"

        return creds

    def _getUrl(self):
        raise NotImplementedError

    def getTitle(self, appid):
        sql = "SELECT value FROM app_data WHERE appid=? AND key='title'"
        self.cursor.execute(sql, [(appid)])
        (title,) = self.cursor.fetchone()  # or use fetchone()
        if title == None:
            raise Exception("there isn't a title with id %s" % appid)
        return title

    def getAllTitles(self):
        sql = "SELECT appid,value FROM app_data WHERE key='title'"
        self.cursor.execute(sql,[])
        return json.dumps(self.cursor.fetchall())

    def getAllFullDescriptions(self):
        sql = "SELECT appid,value FROM app_data WHERE key='full_description'"
        self.cursor.execute(sql,[])
        return json.dumps(self.cursor.fetchall())

    def getRankLatest(self, appid, category, collection):
        sql = "SELECT date,rank FROM rank_data WHERE appid=? AND category=? AND collection=? ORDER BY date DESC"
        self.cursor.execute(sql, (appid, category, collection))
        try:
            (date,rank) = self.cursor.fetchone()  # or use fetchone()
        except:
            raise Exception("there is no data for %s with category %s and collection %s" % (appid,category,collection))
        if rank == None:
            raise Exception("there isn't a rank with id %s" % appid)
        return (date,rank)

    def getRank(self, appid, category, collection):
        sql = "SELECT date,rank FROM rank_data WHERE appid=? AND category=? AND collection=? ORDER BY date ASC"
        self.cursor.execute(sql, (appid, category, collection))
        return json.dumps(self.cursor.fetchall())

    def getApps(self, query):
        sql = "SELECT app_data.appid,app_data.value FROM app_data WHERE key='title' and value like ? ORDER BY value ASC"
        #print query
        #print sql
        self.cursor.execute(sql, ['%'+query+'%'])
        fields = map(lambda x:x[0], self.cursor.description)
        result = [dict(zip(fields,row)) for row in self.cursor.fetchall()]

        return json.dumps(result)

    def getAppDetails(self, appid, category, collection):
        sql = "SELECT value,key FROM app_data WHERE appid=?"
        #print query
        #print sql
        self.cursor.execute(sql, [appid])
        result = {}
        result['appid']=appid
        for row in self.cursor.fetchall():
            result[row[1]]=row[0]

        sql = "SELECT date,rank FROM rank_data WHERE appid=? AND category=? AND collection=? ORDER BY date ASC"
        self.cursor.execute(sql, (appid, category, collection))
        result['ranking']={}
        for row in self.cursor.fetchall():
            result['ranking'][row[0]]=row[1]

        return json.dumps(result)

    def getAllRanks(self, category, collection):
        sql = "SELECT appid,date,rank FROM rank_data WHERE category=? AND collection=? ORDER BY date ASC"
        self.cursor.execute(sql, (category, collection))
        return json.dumps(self.cursor.fetchall())

    def getAllRankingData(self, category, collection):
        sql = "SELECT appid,date,rank FROM rank_data WHERE category=? AND collection=? ORDER BY date ASC"
        self.cursor.execute(sql, (category, collection))

        all_ranking_data = pd.DataFrame(self.cursor.fetchall())
        all_ranking_data = all_ranking_data.rename(columns = {1:'Date'})
        all_ranking_data['Date'] = all_ranking_data['Date'].apply(pd.to_datetime)
        #all_ranking_data = all_ranking_data.set_index('Date')
        all_ranking_data = all_ranking_data.rename(columns = {0:'AppId'})
        all_ranking_data = all_ranking_data.rename(columns = {2:'Rank'})
        all_ranking_data=all_ranking_data.pivot(index='Date', columns='AppId', values='Rank')

        return all_ranking_data

    def getAllReviewsVerbose(self, category, collection):

        #sql = "SELECT DISTINCT reviews_data.appid,reviews_data.date,reviews_data.reviewer_ratings FROM reviews_data,rank_data WHERE rank_data.appid=reviews_data.appid AND rank_data.category='FINANCE' AND rank_data.collection='topselling_free' ORDER BY reviews_data.date ASC"
        sql = "SELECT DISTINCT reviews_data.appid,reviews_data.date,reviews_data.reviewer_ratings FROM reviews_data,rank_data WHERE rank_data.appid=reviews_data.appid AND rank_data.category=? AND rank_data.collection=? ORDER BY reviews_data.date ASC"

        self.cursor.execute(sql, (category, collection))
        return json.dumps(self.cursor.fetchall())


    def getAllReviews(self, category, collection):

        #sql = "SELECT DISTINCT reviews_data.appid,reviews_data.date,reviews_data.reviewer_ratings FROM reviews_data,rank_data WHERE rank_data.appid=reviews_data.appid AND rank_data.category='FINANCE' AND rank_data.collection='topselling_free' ORDER BY reviews_data.date ASC"
        sql = "SELECT DISTINCT reviews_data.appid,reviews_data.date,reviews_data.reviewer_ratings FROM reviews_data,rank_data WHERE rank_data.appid=reviews_data.appid AND rank_data.category=? AND rank_data.collection=? ORDER BY reviews_data.date ASC"

        self.cursor.execute(sql, (category, collection))
        return json.dumps(self.cursor.fetchall())

    def getAllReviewsData(self, category, collection, limit, cutoff):

        #sql = "SELECT DISTINCT reviews_data.appid,reviews_data.date,reviews_data.reviewer_ratings FROM reviews_data,rank_data WHERE rank_data.appid=reviews_data.appid AND rank_data.category='FINANCE' AND rank_data.collection='topselling_free' ORDER BY reviews_data.date ASC"
        sql = "SELECT DISTINCT reviews_data.appid,reviews_data.date,reviews_data.reviewer_ratings FROM reviews_data,rank_data WHERE rank_data.appid=reviews_data.appid AND rank_data.category=? AND rank_data.collection=? AND reviews_data.reviewer_ratings>=? ORDER BY reviews_data.date ASC LIMIT ? "

        self.cursor.execute(sql, (category, collection, cutoff, limit))

        all_reviews_data = pd.DataFrame(self.cursor.fetchall())
        all_reviews_data = all_reviews_data.rename(columns = {1:'Date'})
        all_reviews_data['Date'] = all_reviews_data['Date'].apply(pd.to_datetime)

        all_reviews_data = all_reviews_data.rename(columns = {0:'AppId'})
        #all_reviews_data = all_reviews_data.set_index('AppId')
        all_reviews_data = all_reviews_data.rename(columns = {2:'Reviews'})


        all_reviews_data['Reviews'] = all_reviews_data['Reviews'].str.replace(',', '')
        all_reviews_data['Reviews'].fillna(0,inplace=True)
        all_reviews_data['Reviews'] =  all_reviews_data['Reviews'].replace('',0)
        #print all_reviews_data.head()
        #all_reviews_data=all_reviews_data.pivot(index='Date', columns='AppId', values='Reviews')
        all_reviews_data.sort_values(by='Reviews', ascending=False).drop_duplicates(subset='AppId')

        return all_reviews_data

    def getAppReviews(self, apps, category, collection):

        comma = "','"
        apps_csv = comma.join(apps)
        apps_csv = "'"+apps_csv+"'"
        #print apps_csv

        sql = "SELECT reviews_data.appid,reviews_data.date,reviews_data.reviewer_ratings FROM reviews_data,rank_data WHERE rank_data.appid IN ( com.oxbowsoft.debtplanner,com.levelmoney.mobile ) AND rank_data.appid=reviews_data.appid AND rank_data.category='FINANCE' AND rank_data.collection='topselling_free' ORDER BY reviews_data.date ASC"
        #sql = "SELECT reviews_data.appid,reviews_data.date,reviews_data.reviewer_ratings FROM reviews_data,rank_data \
        #    WHERE rank_data.appid IN ( ? ) AND rank_data.appid=reviews_data.appid AND rank_data.category=? AND rank_data.collection=? \
        #    ORDER BY reviews_data.date ASC"

        self.cursor.execute(sql, (apps_csv, category, collection))

        return json.dumps(self.cursor.fetchall())

    def getDailyInfo(self, appid, category, collection):
        sql = "select rank.date,rank.rank,rev.reviewer_ratings,rev.current_rating \
        from rank_data as rank,reviews_data as rev \
        where rank.appid=? and rank.appid=rev.appid and rank.date=rev.date AND rank.category=? AND rank.collection=? ORDER BY rank.date ASC"
        self.cursor.execute(sql, (appid, category, collection))
        return json.dumps(self.cursor.fetchall())

    def sendEmail(self, appid):
        COMMASPACE = ', '

        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = 'ASO Date for '+appid
        # me == the sender's email address
        # family = the list of all recipients' email addresses
        #msg['From'] = "oxbowsoft@gmail.com"
        msg['From'] = "chris.schuermyer@gmail.com"
        to = ['chris.schuermyer@gmail.com']
        msg['To'] = COMMASPACE.join(to)
        msg.preamble = 'ASO Date for '+appid

        # Assume we know that the image files are all in PNG format
        file = appid+'.png'

        # Open the files in binary mode.  Let the MIMEImage class automatically
        # guess the specific image type.
        print file
        fp = open(file, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            #server.set_debuglevel(1)
            server.ehlo()
            server.starttls()
            credentials = self._get_credentials()
            gmail_pwd=credentials['gmail_password']
            server.login(msg['From'], gmail_pwd)
            server.sendmail(msg['From'], to, msg.as_string())
            server.close()
            print 'successfully sent the mail'
        except:
            print "failed to send mail"


    def _initialize_database(self):
        conn = sqlite3.connect(self.database) # or use :memory: to put it in RAM

        self.cursor = conn.cursor()