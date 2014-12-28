""" dashdoc generator helper classes and functions """

import os
import re
from urllib import quote
from jinja2 import Template
from .filestuff import Fs, Soupy


class DRFDash(object):

    """ DRF stuff """

    # base = 'DjangoRestFramework.docset/Contents/Resources/Documents'

    def get_doc_dirs(self):
        """ DRF doc dirs """
        return ['tutorial', 'api-guide', 'topics', ]

    def get_plist_content(self):
        """ generate dash docset plist content """
        tmpl_file = 'templates/info.plist.j2'
        template = Template(Fs().get_file_contents(tmpl_file))
        return template.render(
            doc={
                "id": "drf",
                "name": "DjangoRestFramework",
                "index": "index.html"})

    def write_plist_file(self, dest):
        """ write the plist file """
        data = self.get_plist_content()
        Fs().rewrite_file(dest, data)

    def get_dash_anchor(self):
        """ dash toc anchor """
        return "<a name='//apple_ref/cpp/%s/%s' class='dashAnchor' />"


class FixHtml(Soupy, DRFDash):

    """ docset html fixes """

    def __init__(self, filename):
        """ init """
        super(FixHtml, self).__init__(filename)
        self.p_href = re.compile('http://127.0.0.1:8000/')
        self.pagename = quote(self.soup.title.string, '')
        self.pages = []
        # self.fix_link_tags()
        # self.fix_title()
        # self.fix_script_tags()
        # self.fix_hrefs()
        # self.remove_divs()
        # self.fix_main_div()
        # self.save()

    def get_toc_anchor(self):
        """ get this documents anchor """
        a = self.get_dash_anchor()
        return a % ('Guide', self.pagename)

    def common_fixes(self):
        """ most files require these """
        self.fix_link_tags()
        self.fix_title()
        self.fix_script_tags()
        self.fix_hrefs()
        self.remove_divs()
        self.fix_main_div()
        self.save()
        return self

    def index_fixes(self):
        """ fixes for the index page """
        self.fix_link_tags_index()
        self.fix_script_tags()
        self.remove_divs()
        self.fix_main_div()

        p = re.compile('/[\w\.-]+.1')
        tags = self.find_tags(href=p)
        for tag in tags:
            basename = '/' + self.get_base_name(tag['href'])
            tag['href'] = p.sub(basename + '.html', tag['href'])

        tags = self.find_tags('a', href='index.html')
        for tag in tags:
            if self.p_href.match(tag.string):
                tag['href'] = 'http://127.0.0.1:8000/'

        self.save()
        return self

    def fix_link_tags_index(self):
        """ remove icon tag and fix stylesheet urls """
        self.delete(self.find_tags('link', rel="icon"))
        tags = self.find_tags('link', rel="stylesheet")
        for tag in tags:
            tag['href'] = self.p_href.sub('', tag['href'])

    def fix_link_tags(self):
        """ remove icon tag and fix stylesheet urls """
        self.delete(self.find_tags('link', rel="icon"))
        tags = self.find_tags('link', rel="stylesheet")
        for tag in tags:
            tag['href'] = self.p_href.sub('../', tag['href'])

    def fix_script_tags(self):
        """ remove icon tag and fix stylesheet urls """
        tags = self.find_tags('script')
        for tag in tags:
            if 'src' in tag.attrs:
                tag['src'] = self.p_href.sub('../', tag['src'])
            else:
                tag.extract()

    def remove_divs(self):
        """ remove divs """
        divs = self.find_tags(
            'div', class_="navbar navbar-inverse navbar-fixed-top")
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

    def fix_hrefs(self):
        """ fix urls """
        p = re.compile('^../[\w\.-]+.1')
        tags = self.find_tags(href=p)
        for tag in tags:
            basename = self.get_base_name(tag['href'])
            if self.ignored(tag['href'], basename) or tag.string is None:
                continue
            good = self.find_path(basename + '.html')
            if len(tag['href']):
                tag['href'] = p.sub(good, tag['href'])
                self.add_page(tag)

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

    def add_page(self, page):
        """ add page """
        type = self.get_page_type(page)
        self.pages.append({
            # "name": basename if tag.string is None else tag.string,
            "name": self.get_page_name(page, type),
            "type": type,
            "path": page['href']
        })

    def get_pages(self):
        """ get pages """
        return self.pages

    def get_page_type(self, page):
        """ get the type of page """
        if re.search('^\.', page.string):
            return 'Function'
        if re.search('[\w\.-]+\.html$', page['href']):
            return 'Guide'
        return 'Section'

    def get_page_name(self, page, type):
        """ get the page name """
        name = page.string
        if type == 'Section':
            name += ' - ' + self.soup.title.string
        return name

    def ignored(self, str, basename=None):
        """ don't do anything with these """
        ignore = [
            '\#searchModal',
            '\#',
        ]
        if basename is not None:
            ignore.insert(0, '\#' + basename)
        search = '|'.join(ignore)
        return re.search('(' + search + ')$', str)


    # def fix_id_href(self):
    #     """ fix urls """
    #     p = re.compile('^../[\w\.-]+.1#[\w\.-]+$')
    #     ps = re.compile('../[\w\.-]+.1')
    #     tags = self.find_tags(href=p)
    #     for tag in tags:
    #         basename = self.get_base_name(tag['href'])
    #         print basename
    #         good = self.find_path(basename + '.html')
    #         print good
    #         tag['href'] = ps.sub(good, tag['href'])

    #         # skip it if there is no tag string
    #         if tag.string is None:
    #             continue
    #         self.add_page(tag)

    # def fix_hrefs(self):
    #     """ fix urls """
    #     p = re.compile('../[\w\.-]+.1$')
    #     tags = self.find_tags(href=p)
    #     for tag in tags:
    #         basename = self.get_base_name(tag['href'])
    #         tag['href'] = self.find_path(basename + '.html')

    #         # skip it if there is no tag string
    #         if tag.string is None:
    #             continue
    #         self.add_page(tag)
