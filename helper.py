""" dashdoc generator helper classes and functions """

import os
import shutil
import subprocess
import sqlite3
import re
from bs4 import BeautifulSoup, NavigableString, Tag

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def is_sequence(arg):
    """ check type is list or other iterable """
    return (
        not hasattr(arg, "strip")
        and hasattr(arg, "__getitem__")
        or hasattr(arg, "__iter__"))


class AwesomeDict(dict):

    """ self referencing dictionary """

    def __getitem__(self, item):
        """ get item """
        return dict.__getitem__(self, item) % self


class Fs(object):

    """ filesystem helper """

    def get_docs_from_url(
            self,
            cmd='wget',
            opts=[],
            url="localhost",
            runfrom=BASE_DIR):
        """
        get the docs
        wget --mirror -p -k http://127.0.0.1:8000/
        """
        cmdList = [cmd]
        cmdList.extend(opts)
        cmdList.append(url)
        retcode = subprocess.call(cmdList, cwd=runfrom)
        return retcode

    def clean_structure(self, fileglob):
        """ clean the wget .1 and name/index.html structure """
        for thing in fileglob:
            if (self.isdir(thing) and
                    self.exists(os.path.join(thing, 'index.html'))):
                self.move(
                    os.path.join(thing, 'index.html'),
                    self.get_new_file_name(thing))
            self.rm(thing)

    def get_new_file_name(self, filepath, ext='.html'):
        """ generate new filename based on the path """
        return os.path.join(
            os.path.dirname(filepath),
            os.path.basename(filepath) + ext)

    def isdir(self, src):
        """ alias for os.path.isdir """
        return os.path.isdir(src)

    def exists(self, src):
        """ alias for os.path.exists """
        return os.path.exists(src)

    def mkdir(self, filename):
        """ mkdir -p """
        try:
            os.makedirs(filename)
            return True
        except:
            return False

    def rm(self, src):
        """ remove file/dir """
        if os.path.isdir(src):
            return self.rmdir(src)
        return self.rmfile(src)

    def rmfile(self, src):
        """ remove file """
        return os.remove(src)

    def rmdir(self, src):
        """ remove directory """
        return shutil.rmtree(src)

    def move(self, src, dest):
        """ move a file """
        if self.isdir(src):
            return self.movedir(src, dest)
        return shutil.move(src, dest)

    def movedir(self, src, dest):
        """ rename directory """
        return os.rename(src, dest)

    def get_base_name(self, filename=None):
        """ get name of file without ext """
        if filename is None:
            filename = self.filename
        return os.path.splitext(os.path.basename(filename))[0]

    def dirname(self, filename):
        """ dirname """
        return os.path.dirname(filename)

    def touch(self, filename):
        """ touch a file """
        if self.exists(filename):
            return os.utime(filename, None)
        return open(filename, 'a').close()

    def rewrite_file(self, filename, content):
        """ rewrite a file """
        with open(filename, "wb") as file:
            file.write(content)

    def get_file_contents(self, filename):
        """ load html file """
        if self.exists(filename):
            with open(filename) as doc:
                return doc.read()


class Db(object):

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


class Soupy(Fs):

    """ beautiful soup stuff """

    def __init__(self, filename):
        """ init """
        self.filename = filename
        self.content = self.get_file_contents(self.filename)
        self.soup = BeautifulSoup(self.content)

    def get_content(self):
        """ get content """
        return self.content

    def save(self):
        """ rewrite html file """
        self.rewrite_file(self.filename, self.soup.renderContents())

    def find_tags(self, *args, **kwargs):
        """ find tags """
        return self.soup.find_all(*args, **kwargs)

    def delete(self, tags):
        """ delete tags """
        if is_sequence(tags):
            [s.extract() for s in tags]
        else:
            tags.extract()


class FixHtml(Soupy):

    """ docset html fixes """

    def __init__(self, filename):
        """ init """
        super(FixHtml, self).__init__(filename)
        self.p_href = re.compile('http://127.0.0.1:8000')
        self.pages = []
        # self.fix_link_tags()
        # self.fix_script_tags()
        # self.remove_divs()
        # self.fix_main_div()
        # self.fix_title()
        self.fix_hrefs()
        # self.fix_id_href()
        # self.save()

    def fix_link_tags(self):
        """ remove icon tag and fix stylesheet urls """
        self.delete(self.find_tags('link', rel="icon"))
        tags = self.find_tags('link', rel="stylesheet")
        for tag in tags:
            tag['href'] = self.p_href.sub('..', tag['href'])

    def fix_script_tags(self):
        """ remove icon tag and fix stylesheet urls """
        tags = self.find_tags('script')
        for tag in tags:
            if 'src' in tag.attrs:
                tag['src'] = self.p_href.sub('..', tag['src'])
            else:
                tag.extract()

    def remove_divs(self):
        """ remove divs """
        divs = self.find_tags('div', class_="navbar navbar-inverse navbar-fixed-top")
        divs += self.find_tags('div', class_="span3")
        divs += self.find_tags('div', id="searchModal")
        self.delete(divs)

    def fix_main_div(self):
        """ edit text """
        tag = self.find_tags('div', class_="span9").pop()
        tag['class'] = ['span12']

    def fix_title(self):
        """ fix title """
        p = re.compile('- Django REST framework')
        title = self.soup.title
        new_title = p.sub('', title.string)
        title.string.replace_with(new_title)

    def fix_id_href(self):
        """ fix urls """
        fixed = self.get_base_name(
            self.dirname(
                self.filename)) + '/' + self.get_base_name() + '.html#'
        bad = '../' + self.get_base_name() + '.1#'
        p = re.compile(bad)
        tags = self.find_tags(href=p)
        for tag in tags:
            tag['href'] = p.sub(fixed, tag['href'])
            self.pages.append({
                "name": tag.string,
                "type": "Guide",
                "path": tag['href']
            })

    def fix_hrefs(self):
        """ fix urls """
        p = re.compile('../' + self.get_base_name() + '.1$')
        tags = self.find_tags(href=p)
        for tag in tags:
            fixed = self.find_path(self.get_base_name(tag['href']) + '.html')
            tag['href'] = p.sub(fixed, tag['href'])
            self.pages.append({
                "name": tag.string,
                "type": "Guide",
                "path": tag['href']
            })

    def find_path(self, filename):
        """ find the correct path of the file """
        base = 'DjangoRestFramework.docset/Contents/Resources/Documents'
        p = re.compile(base + '/')
        dirs = ['tutorial', 'api-guide', 'topics', ]
        for d in dirs:
            filepath = os.path.join(os.path.join(base, d), filename)
            if self.exists(filepath):
                filepath = p.sub('', filepath)
                return filepath
        return None

    def get_pages(self):
        """ get pages """
        return self.pages
