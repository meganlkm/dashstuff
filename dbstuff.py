""" dashdoc generator helper classes and functions """

import sqlite3

from .filestuff import Fs


class Sqlite(object):

    """ sql stuff for dashdoc generator """

    def __init__(self, dbfile):
        """ init """
        self.dbfile = dbfile
        self.table = 'searchIndex'
        self.fields = 'name, type, path'
        self.insert_sql = 'INSERT OR IGNORE INTO ' + self.table + '('
        self.insert_sql += self.fields + ') VALUES (?,?,?)'
        self.connect()

    def connect(self):
        """ connect to db """
        Fs().touch(self.dbfile)
        self.conn = sqlite3.connect(self.dbfile)
        self.cursor = self.conn.cursor()

    def dashdoc_init(self):
        """ initialize dashdoc db and table """
        self.drop_table()
        self.create_table()
        self.create_index()

    def get_fields_def(self):
        """ field definition """
        return 'id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT'

    def drop_table(self):
        """ drop dashdoc table """
        sql = 'DROP TABLE ' + self.table
        self._execute(sql)

    def create_table(self):
        """ create dashdoc table """
        sql = 'CREATE TABLE ' + self.table + '(' + self.get_fields_def() + ')'
        self._execute(sql)

    def create_index(self):
        """ create index for dashdoc table """
        sql = 'CREATE UNIQUE INDEX anchor ON '
        sql += self.table + ' (' + self.fields + ')'
        self._execute(sql)

    def insert(self, name=None, type=None, path=None):
        """ insert an anchor into the dashdoc db """
        self.cursor.execute(self.insert_sql, (name, type, path))

    def done(self):
        """ clean up """
        self.conn.commit()
        self.conn.close()

    def _execute(self, sql, params=None):
        """ execute sql statement """
        try:
            self.cursor.execute(sql)
        except:
            print "something went wrong..."
            pass
