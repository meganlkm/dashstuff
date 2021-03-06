""" dashdoc generator helper classes and functions """

import os
import shutil
import subprocess
from glob import glob
from bs4 import BeautifulSoup
from .helper import is_sequence

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Fs(object):

    """ filesystem helper """

    def get_new_file_name(self, filepath, ext='.html'):
        """ generate new filename based on the path """
        return self.joinpath(
            os.path.dirname(filepath),
            os.path.basename(filepath) + ext)

    def isdir(self, src):
        """ alias for os.path.isdir """
        return os.path.isdir(src)

    def exists(self, src):
        """ alias for os.path.exists """
        return os.path.exists(src)

    def joinpath(self, *args):
        """ os join shortcut """
        return os.path.join(*args)

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

    def get_dir_files(self, pattern):
        """ get files from directory """
        return glob(pattern)

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


class Wget(Fs):

    """ wget helper """

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
                    self.exists(self.joinpath(thing, 'index.html'))):
                self.move(
                    self.joinpath(thing, 'index.html'),
                    self.get_new_file_name(thing))
            self.rm(thing)


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
