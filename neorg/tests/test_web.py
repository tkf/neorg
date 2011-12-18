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
import re
import tempfile
import shutil
import urllib
from nose.tools import raises, assert_raises

from neorg import web
from neorg.config import DefaultConfig, set_config
from neorg.tests.utils import trim, CaptureStdIO, ChangeNEOrgVersion

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
            path += b
        else:
            path += '/' + b
    return path


def setup_app():
    web.app.config.from_object(DefaultConfig)
    (db_fd, web.app.config['DATABASE']) = tempfile.mkstemp(prefix=TMP_PREFIX)
    dirpath = tempfile.mkdtemp(prefix=TMP_PREFIX)  # = NEORG_ROOT
    set_config(web.app.config, dirpath)
    os.mkdir(web.app.config['NEORG_DIR'])
    web.app.config['SECRET_KEY'] = 'key for testing'
    app = web.app.test_client()
    web.init_db()
    web.update_search_index()

    from neorg.wiki import setup_wiki, gene_html
    setup_wiki()

    def gene_html_with_encode(*args, **kwds):
        return gene_html(*args, **kwds).encode('utf-8')

    return (app, db_fd, gene_html_with_encode)


def teardown_app():
    os.remove(web.app.config['DATABASE'])
    shutil.rmtree(web.app.config['NEORG_ROOT'])


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

NEORG_FASTTEST = os.environ.get("NEORG_FASTTEST") or False
if NEORG_FASTTEST:
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

    def check_save(self, page_path, page_text, page_html=None):
        if page_html is None:
            page_html = self.gene_html(page_text)
        save_path = urljoin('/', page_path, "_save")
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
        delete_path = urljoin('/', page_path, "_delete")
        response = self.app.post(delete_path, data={
            'yes': 'Yes',
            })
        assert page_html not in response.data
        assert response.location == "http://localhost/"

    def check_delete_no(self, page_path, page_text):
        (save_response, page_html,
         ) = self.check_save(page_path, page_text)
        delete_path = urljoin('/', page_path, "_delete")
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

    def check_confirm_delete(self, page_path, page_text):
        (save_response, page_html,
         ) = self.check_save(page_path, page_text)
        confirm_delete_path = urljoin('/', page_path, "_confirm_delete")
        response = self.app.get(confirm_delete_path)
        assert page_html in response.data
        delete_path = urljoin('/', page_path, "_delete")
        assert '<form action="%s"' % delete_path in response.data
        assert ('<input type="submit" name="yes" value="Yes" />'
                in response.data)
        assert '<input type="submit" name="no" value="No" />' in response.data

    def test_confirm_delete(self):
        for (page_path, page_text) in self.gene_pages("TestConfirmDel"):
            yield (self.check_confirm_delete, page_path, page_text)

    def check_edit_new_page(self, page_path, page_text):
        (save_response, page_html,
         ) = self.check_save(page_path, page_text)
        edit_path = urljoin('/', page_path, "_edit")
        response = self.app.get(edit_path, follow_redirects=True)
        assert page_text in response.data
        return (response, page_html)

    def check_edit_existing_page(self, page_path, page_text):
        (response, page_html,
         ) = self.check_edit_new_page(page_path, page_text)
        assert page_html in response.data

    def test_edit_new_page(self):
        for (page_path, page_text) in self.gene_pages("TestEditNew"):
            if page_path == "":
                continue
            yield (self.check_edit_new_page, page_path, page_text)

    def test_edit_existing_page(self):
        for (page_path, page_text) in self.gene_pages("TestEditExisting"):
            yield (self.check_edit_existing_page, page_path, page_text)

    def check_preview(self, page_path, page_text, page_html=None):
        if page_html is None:
            page_html = self.gene_html(page_text)
        preview_path = urljoin('/', page_path, "_save")
        response = self.app.post(preview_path, data={
            'preview': 'Preview',
            'page_text': page_text,
            }, follow_redirects=True)
        assert page_html in response.data
        assert page_text in response.data
        assert '<form action="%s"' % preview_path in response.data

    def test_preview(self):
        for (page_path, page_text) in self.gene_pages("TestPreview"):
            yield (self.check_preview, page_path, page_text)

    def test_descendants(self):
        page_root = 'TestDescendantsRoot'
        list_relpath = []
        for (page_relpath, page_text) in self.gene_pages("TestDescendants"):
            list_relpath.append(page_relpath)
            page_path = urljoin(page_root, page_relpath)
            self.check_save(page_path, page_text)

        desc_path = urljoin('/', page_path, "_descendants")
        response = self.app.get(desc_path, follow_redirects=True)
        for page_relpath in list_relpath:
            assert page_relpath in response.data

    def check_history(self, page_path, page_text, num_update=5):
        page_text_history = []
        for dummy in range(num_update):
            page_text_history.append(page_text)
            self.check_save(page_path, page_text)
            page_text = '"%s" is older than this' % page_text
        hist_path = urljoin('/', page_path, "_history")
        response = self.app.get(hist_path)
        old_links = re.findall('<a href=".*_old/[0-9]*">', response.data)
        assert num_update == len(old_links)
        assert 1 == len(re.findall('\n *Newest\n', response.data))
        return (response, page_text_history)

    def test_history(self):
        page_root = 'TestHistRoot'
        for (page_relpath, page_text) in self.gene_pages("TestHist"):
            page_path = urljoin(page_root, page_relpath)
            yield (self.check_history, page_path, page_text)

    def check_old(self, page_path, page_text, num_update=5):
        (hist_response, page_text_history,
         ) = self.check_history(page_path, page_text, num_update)
        old_links = re.findall('<a href="(.*_old/[0-9]*)">',
                               hist_response.data)
        assert len(page_text_history) == len(old_links)
        for (link, old_text) in zip(old_links,
                                    reversed(page_text_history)):
            response = self.app.get(link)
            old_html = self.gene_html(old_text)
            assert old_html in response.data

    def test_old(self):
        page_root = 'TestOldRoot'
        for (page_relpath, page_text) in self.gene_pages("TestOld"):
            page_path = urljoin(page_root, page_relpath)
            yield (self.check_old, page_path, page_text)

    def test_help(self):
        response = self.app.get('/_help/index.html')
        assert response.location == "http://localhost/static/help/index.html"

        response = self.app.get('/_help/index.html',
                                follow_redirects=True)
        import neorg
        assert (  # depends on sphinx version?
            'NEOrg v%s documentation' % neorg.__version__ in response.data or
            'NEOrg %s documentation' % neorg.__version__ in response.data)

    def check_temp(self, base_path, page_text, num):
        assert num > 0
        temp_path = urljoin(base_path, *(['_temp_'] * num))
        temp_text = page_text + "\n" + trim("""
        path: {{ path }}
        relpath: {{ relpath }}
        """) + "\n" + "\n".join(
            "args[%(i)d]: {{ args[%(i)d] }}" % {'i': i}
            for i in range(num))

        self.check_save(temp_path, temp_text)

        args = ['arg%d' % i for i in range(num)]
        page_path = urljoin(base_path, *args)
        response = self.app.get(page_path + '/')
        for (i, a) in enumerate(args):
            assert "args[%d]: %s" % (i, a) in response.data
        assert "path: %s" % page_path in response.data
        assert "relpath: /%s" % '/'.join(args) in response.data

        # clean up is needed to avoid the template page to match
        # another page. this is required when NEORG_FASTTEST is
        # specified.
        if NEORG_FASTTEST:
            self.check_delete_yes(temp_path, '')

    def test_temp(self):
        page_root = 'TestTempRoot'
        num_max = 3
        for (page_relpath, page_text) in self.gene_pages("TestTemp"):
            page_path = urljoin(page_root, page_relpath)
            for num in range(1, num_max + 1):
                yield (self.check_temp, page_path, page_text, num)

    def test_no_fail_page(self):

        def gene_page_with_error(debug):
            page_text = "nonexistent_target_"
            page_html = self.gene_html(
                page_text,
                settings_overrides={
                  'halt_level': 2,  # raise Error
                  },
               _debug=debug)
            return page_html

        # error must NOT be suppressed when _debug=True
        from docutils.utils import SystemMessage
        with CaptureStdIO() as stdio:  # suppress stderr
            assert_raises(SystemMessage, gene_page_with_error,
                          debug=True)
        stderr = stdio.read_stderr()
        assert ('(ERROR/3) Unknown target name: "nonexistent_target".'
                in stderr)

        # error must be suppressed when _debug=False
        with CaptureStdIO() as stdio:  # suppress stderr
            page_html = gene_page_with_error(debug=False)
        stderr = stdio.read_stderr()
        assert ('(ERROR/3) Unknown target name: "nonexistent_target".'
                in stderr)
        assert '<h1>Failed to generate HTML</h1>' in page_html

    def get_search_response(self, query):
        quoted = urllib.quote_plus(query)
        return self.app.get('/_search?q={0}'.format(quoted))

    @staticmethod
    def assert_page_path_in_search_result(page_path, response):
        page_path_link = '<h2><a href="/{0}">'.format(page_path)
        assert page_path_link in response.data, \
               "page_path '{0}' should be in the response"

    def check_search_match(self, page_path, page_text, query):
        self.check_save(page_path, page_text)
        response = self.get_search_response(query)
        self.assert_page_path_in_search_result(page_path, response)

    @raises(AssertionError)
    def check_search_no_match(self, page_path, page_text, query):
        self.check_search_match(page_path, page_text, query)

    def test_search(self):
        num_test = 3
        for ((page_path, page_text), query) in zip(
            self.gene_pages('TestSearchMatch', num_test),
            map('match{0} query{0}'.format, range(num_test))
            ):
            page_text = ' '.join([page_text, query])
            yield (self.check_search_match,
                   page_path, page_text, query)

        for ((page_path, page_text), query) in zip(
            self.gene_pages('TestSearchNoMatch', num_test),
            map('match{0} query{0}'.format, range(num_test))
            ):
            yield (self.check_search_no_match,
                   page_path, page_text, query)

    def test_search_deleted(self):
        query = 'some_long_string_to_test_search_deleted.'
        page_path = 'TestSearchDeleted'
        page_text = trim("""
        This page will be deleted
        -------------------------

        {0}.
        """.format(query))
        self.check_search_match(page_path, page_text, query)
        self.check_delete_yes(page_path, page_text)  # delete
        response = self.get_search_response(query)
        assert_raises(AssertionError,
                      self.assert_page_path_in_search_result,
                      page_path, response)  # no match

    def test_jump_to_descendants(self):
        page_path = 'TestJumpToDesc/SubPage'
        self.check_save(page_path, 'subpage exists')

        # if sub-page(s) exists, show them
        response = self.app.get('TestJumpToDesc/')
        assert (response.location ==
                "http://localhost/TestJumpToDesc/_descendants")

        # if no sub-page exists, jump to the edit form
        response = self.app.get('TestJumpToDesc/NoSubPage/')
        assert (response.location ==
                "http://localhost/TestJumpToDesc/NoSubPage/_edit")


class TestNEOrgWebWithEmptyDB(TestNEOrgWebSlow):

    def test_system_info(self):
        from neorg import __version__
        from neorg.web import system_info
        sysinfo = system_info()
        assert sysinfo['version'] == __version__
        assert sysinfo['updated'].startswith('20')
        assert sysinfo['updated'][:4].isdigit()

    def test_update_system_info_to_current(self):
        from neorg.web import update_system_info, system_info
        sysinfo_0 = system_info()
        update_system_info()
        sysinfo_1 = system_info()
        assert sysinfo_0 == sysinfo_1  # nothing changed

    def test_update_system_info_to_newer(self):
        import neorg
        from neorg.web import update_system_info
        newer_version = '1.0.0'
        assert newer_version > neorg.__version__  # make sure it is newer
        with ChangeNEOrgVersion(newer_version):
            # version has been changed
            assert_raises(AssertionError, self.test_system_info)
            # update success w/o an error
            update_system_info()
            # check if the version was updated
            self.test_system_info()
        # DB has been changed
        assert_raises(AssertionError, self.test_system_info)

    def test_update_system_info_to_older(self):
        import neorg
        from neorg.web import update_system_info
        older_version = '0.0.0'
        assert older_version < neorg.__version__  # make sure it is older
        with ChangeNEOrgVersion(older_version):
            # version has been changed
            assert_raises(AssertionError, self.test_system_info)
            # update fails wtih an RuntimeError
            assert_raises(RuntimeError, update_system_info)
        # DB has not been changed
        self.test_system_info()

    def test_empty_db(self):
        response = self.app.get('/')
        assert response.location == "http://localhost/_edit"

        response = self.app.get('/', follow_redirects=True)
        assert '<form action="/_save"' in response.data
