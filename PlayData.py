import sqlite3
import json

class PlayData:

    def __init__(self, database):
        #self.header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
        #self.data = None
        #self._tries = tries
        self.database = database
        self._initialize_database()

        pass

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


    def _initialize_database(self):
        conn = sqlite3.connect(self.database) # or use :memory: to put it in RAM

        self.cursor = conn.cursor()