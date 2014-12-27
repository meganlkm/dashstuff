""" dashdoc generator helper classes and functions """

import os
import re
from .filestuff import Soupy


class DRFDash(object):

    """ DRF stuff """

    def get_doc_dirs(self):
        """ DRF doc dirs """
        return ['tutorial', 'api-guide', 'topics', ]


class FixHtml(Soupy, DRFDash):

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
        dirs = self.get_doc_dirs()
        for d in dirs:
            filepath = os.path.join(os.path.join(base, d), filename)
            if self.exists(filepath):
                filepath = p.sub('', filepath)
                return filepath
        return None

    def get_pages(self):
        """ get pages """
        return self.pages
