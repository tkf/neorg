"""
Tests for neorg.web flask application

Fast test by class-level setup/teardown
---------------------------------------
The class TestNEOrgWeb supports both instance-level and class-level
setup/teardown. This can be selected by setting the NEORG_FASTTEST
environment variable. Nonzero length string means the class-level
setup/teardown.

"""

import os
import tempfile
import shutil
from nose.tools import raises

from neorg import web
from neorg.config import DefaultConfig

TMP_PREFIX = 'neorg-tmp'


def urljoin(a, *p):
   """
   Join two or more pathname components, inserting '/' as needed.

   If any component is an absolute path, all previous path components
   will be discarded. (Adapted from the `posixpath` module.)

   """
   path = a
   for b in p:
       if b.startswith('/'):
           path = b
       elif path == '' or path.endswith('/'):
           path +=  b
       else:
           path += '/' + b
   return path


def setup_app():
    web.app.config.from_object(DefaultConfig)
    (db_fd, web.app.config['DATABASE']) = tempfile.mkstemp(prefix=TMP_PREFIX)
    web.app.config['DATADIRPATH'] = tempfile.mkdtemp(prefix=TMP_PREFIX)
    web.app.config['SECRET_KEY'] = 'key for testing'
    app = web.app.test_client()
    web.init_db()

    from neorg.wiki import setup_wiki, gene_html
    setup_wiki()
    return (app, db_fd, gene_html)


def teardown_app():
    os.remove(web.app.config['DATABASE'])
    shutil.rmtree(web.app.config['DATADIRPATH'])


class TestNEOrgWebSlow(object):

    def setUp(self):
        """Before each test, set up a blank database"""
        (self.app, self.db_fd, self.gene_html) = setup_app()

    def tearDown(self):
        teardown_app()


class TestNEOrgWebFast(object):

    @classmethod
    def setUpClass(cls):
        """Set up a blank database for all test"""
        (cls.app, cls.db_fd, gene_html) = setup_app()
        cls.gene_html = staticmethod(gene_html)

    @classmethod
    def tearDownClass(cls):
        teardown_app()


if os.environ.get("NEORG_FASTTEST") or False:
    TestNEOrgWebBase = TestNEOrgWebFast
else:
    TestNEOrgWebBase = TestNEOrgWebSlow


class TestNEOrgWeb(TestNEOrgWebBase):
    num_test = 3  # Number of test for generated page

    @staticmethod
    def gene_page_paths(num, prefix="test"):
        yield ""
        page_path = prefix
        for i in range(1, num):
            yield page_path
            page_path += "/%s-%d" % (prefix, i)

    @staticmethod
    def gene_page_texts(num, prefix="test"):
        yield "this is root page for prefix=%s" % prefix
        for i in range(1, num):
            yield "this is %d-th page for prefix=%s" % (i, prefix)

    def gene_pages(self, prefix="test", num=None):
        num = self.num_test if num is None else num
        return zip(self.gene_page_paths(num, prefix),
                   self.gene_page_texts(num, prefix))

    def test_empty_db(self):
        response = self.app.get('/')
        assert response.location == "http://localhost/_edit"

        response = self.app.get('/', follow_redirects=True)
        assert '<form action="/_save"' in response.data

    def check_save(self, page_path, page_text, page_html=None):
        if page_html is None:
            page_html = self.gene_html(page_text)
        save_path = urljoin(page_path, "_save")
        response = self.app.post(save_path, data={
            'save': 'Save',
            'page_text': page_text,
            }, follow_redirects=True)
        assert page_html in response.data
        return (response, page_html)

    @raises(AssertionError)
    def fail_check_save(self, *args, **kwds):
        return self.check_save(*args, **kwds)
    # fail_check_save = raises(AssertionError)(check_save)  # does not work!

    def test_save(self):
        fake_html = "But this is not!"
        for (page_path, page_text) in self.gene_pages("TestSave"):
            yield (self.check_save, page_path, page_text)
            yield (self.fail_check_save, page_path, page_text, fake_html)

    def check_delete_yes(self, page_path, page_text):
        (save_response, page_html,
         ) = self.check_save(page_path, page_text)
        delete_path = urljoin(page_path, "_delete")
        response = self.app.post(delete_path, data={
            'yes': 'Yes',
            }, follow_redirects=True)
        assert page_html not in response.data
        assert '<form action="/_save"' in response.data

    def check_delete_no(self, page_path, page_text):
        (save_response, page_html,
         ) = self.check_save(page_path, page_text)
        delete_path = urljoin(page_path, "_delete")
        response = self.app.post(delete_path, data={
            'no': 'No',
            }, follow_redirects=True)
        assert page_html in response.data

    def test_delete_yes(self):
        for (page_path, page_text) in self.gene_pages("TestDelYes"):
            yield (self.check_delete_yes, page_path, page_text)

    def test_delete_no(self):
        for (page_path, page_text) in self.gene_pages("TestDelNo"):
            yield (self.check_delete_no, page_path, page_text)
