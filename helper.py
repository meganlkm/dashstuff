""" dashdoc generator helper classes and functions """

import os
import subprocess

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


class Wget(object):

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
                    self.exists(os.path.join(thing, 'index.html'))):
                self.move(
                    os.path.join(thing, 'index.html'),
                    self.get_new_file_name(thing))
            self.rm(thing)
