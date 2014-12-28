""" dash docset generator """

import os

from dashdocgenerator.helper import AwesomeDict
from dashdocgenerator.filestuff import Fs, Wget
from dashdocgenerator.dbstuff import Sqlite
from dashdocgenerator.DRFdash import DRFDash, FixHtml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

docsetname = 'DjangoRestFramework'

dirs = AwesomeDict({
    'main': os.path.join(BASE_DIR, docsetname + '.docset'),
    'contents': '%(main)s/Contents',
    'resources': '%(contents)s/Resources',
    'documents': '%(resources)s/Documents'
})

drf = DRFDash()
doc_dirs = drf.get_doc_dirs()

wget_cmd = '/usr/local/bin/wget'
wget_opts = ['--mirror', '-p', '-k']
wget_url = 'http://127.0.0.1:8000/'
wget_runfrom = BASE_DIR

fs = Fs()

dbfile = fs.joinpath(dirs['resources'], 'docSet.dsidx')


def write_plist():
    """ write plist file """
    drf.write_plist_file(dirs['contents'] + '/Info.plist')


def setup_dash_package():
    """ setup dashdoc package """
    fs.mkdir(dirs['documents'])
    write_plist()


def get_docs():
    """ get the docs and clean em up """
    w = Wget()
    w.get_docs_from_url(wget_cmd, wget_opts, wget_url, wget_runfrom)
    fs.move(os.path.join(BASE_DIR, '127.0.0.1:8000'), dirs['documents'])

    for p in doc_dirs:
        pat = os.path.join(dirs['documents'], p + '/*')
        stuffs = fs.get_dir_files(pat)
        w.clean_structure(stuffs)


def setup_db():
    """ setup the dashdoc db """
    db = Sqlite(dbfile)
    db.dashdoc_init()
    db.done()


def insert_pages(pages=[]):
    """ insert pages """
    db = Sqlite(dbfile)
    for page in pages:
        db.insert(page['name'], page['type'], page['path'])
    db.done()


def fix_html(glob):
    """ fix html in files """
    for file in glob:
        print file
        pages = FixHtml(file).common_fixes().get_pages()
        # pages = f.get_pages()
        print pages
        insert_pages(pages)


def fix_index():
    """ fix html in files """
    file = fs.joinpath(dirs['documents'], 'index.html')
    FixHtml(file).index_fixes()

setup_dash_package()
get_docs()
setup_db()
fix_index()

for p in doc_dirs:
    pat = os.path.join(dirs['documents'], p + '/*')
    stuffs = fs.get_dir_files(pat)
    fix_html(stuffs)

# testfile = fs.joinpath(dirs['documents'], 'tutorial', '1-serialization.html')
# tmp = FixHtml(testfile)
# print tmp.get_toc_anchor()
