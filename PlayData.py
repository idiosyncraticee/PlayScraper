import sqlite3
import json
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

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

    def getRankLatest(self, appid, category, collection):
        sql = "SELECT date,rank FROM rank_data WHERE appid=? AND category=? AND collection=? ORDER BY date DESC"
        self.cursor.execute(sql, (appid, category, collection))
        (date,rank) = self.cursor.fetchone()  # or use fetchone()
        if rank == None:
            raise Exception("there isn't a rank with id %s" % appid)
        return (date,rank)

    def getRank(self, appid, category, collection):
        sql = "SELECT date,rank FROM rank_data WHERE appid=? AND category=? AND collection=? ORDER BY date ASC"
        self.cursor.execute(sql, (appid, category, collection))
        return json.dumps(self.cursor.fetchall())

    def getAllRanks(self, category, collection):
        sql = "SELECT appid,date,rank FROM rank_data WHERE category=? AND collection=? ORDER BY date ASC"
        self.cursor.execute(sql, (category, collection))
        return json.dumps(self.cursor.fetchall())

    def sendEmail(self, appid):
        COMMASPACE = ', '

        # Create the container (outer) email message.
        msg = MIMEMultipart()
        msg['Subject'] = 'ASO Date for '+appid
        # me == the sender's email address
        # family = the list of all recipients' email addresses
        msg['From'] = "oxbowsoft@gmail.com"
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