import os
import tempfile
import shutil
from nose.tools import raises

from neorg import web
from neorg.config import DefaultConfig

TMP_PREFIX = 'neorg-tmp'


class TestNEOrgWeb(object):

    def setUp(self):
        """Before each test, set up a blank database"""
        web.app.config.from_object(DefaultConfig)
        self.db_fd, web.app.config['DATABASE'] = (
            tempfile.mkstemp(prefix=TMP_PREFIX))
        web.app.config['DATADIRPATH'] = tempfile.mkdtemp(prefix=TMP_PREFIX)
        web.app.config['SECRET_KEY'] = 'key for testing'
        self.app = web.app.test_client()
        web.init_db()

        from neorg.wiki import register_neorg_directives, gene_html
        register_neorg_directives(web.app.config['DATADIRPATH'], '/_data')
        self.gene_html = gene_html

    def tearDown(self):
        os.remove(web.app.config['DATABASE'])
        shutil.rmtree(web.app.config['DATADIRPATH'])

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
