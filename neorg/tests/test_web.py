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


def setup_app():
    web.app.config.from_object(DefaultConfig)
    (db_fd, web.app.config['DATABASE']) = tempfile.mkstemp(prefix=TMP_PREFIX)
    web.app.config['DATADIRPATH'] = tempfile.mkdtemp(prefix=TMP_PREFIX)
    web.app.config['SECRET_KEY'] = 'key for testing'
    app = web.app.test_client()
    web.init_db()

    from neorg.wiki import register_neorg_directives, gene_html
    register_neorg_directives(web.app.config['DATADIRPATH'], '/_data')
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

    def test_empty_db(self):
        response = self.app.get('/')
        assert response.location == "http://localhost/_edit"

        response = self.app.get('/', follow_redirects=True)
        assert '<form action="/_save"' in response.data

    def check_save(self, page_path, page_text, page_html=None):
        if page_html is None:
            page_html = self.gene_html(page_text)
        save_path = ("/_save" if page_path == "" else
                     "/".join([page_path, "_save"]))
        response = self.app.post(save_path, data={
            'save': 'Save',
            'page_text': page_text,
            }, follow_redirects=True)
        assert page_html in response.data

    @raises(AssertionError)
    def fail_check_save(self, *args, **kwds):
        return self.check_save(*args, **kwds)
    # fail_check_save = raises(AssertionError)(check_save)  # does not work!

    def test_save(self):
        for (page_path, page_text) in [("", "This is my first post"),
                                       ("", "This is my second post"),
                                       ("SubPage", "This is my subpage")]:
            yield (self.check_save, page_path, page_text)

        for (page_path, page_text) in [("", "This is my first post"),
                                       ("", "This is my second post"),
                                       ("SubPage", "This is my subpage")]:
            page_html = "But this is not!"
            yield (self.fail_check_save, page_path, page_text, page_html)
