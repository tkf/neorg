import os
from glob import glob
from itertools import product
from docutils import nodes, utils
from cgi import escape
from mock import Mock
from nose.tools import eq_, assert_raises

from neorg.wiki import setup_wiki, gene_html
from neorg.tests.utils import (MockWeb, MockDictTable, CheckData, trim,
                               CaptureStdIO)


def doctree_from_dict(data):
    if 'document' == data['node']:
        node = utils.new_document('<string>')
    else:
        node = getattr(nodes, data['node'])(rawsource='',
                                            **data.get('kwds', {}))
    for child in data.get('children', []):
        node += doctree_from_dict(child)
    return node


def dirtext(directive, contents, *args, **kwds):
    """
    Generate directive text from data

    >>> print dirtext('image', '', 'fig.png', width='100px')
    .. image:: fig.png
       :width: 100px
    >>> print dirtext('csv-table', ['0,1,2', '3,4,5'],
    ...               'Numbers', keepspace=None)
    .. csv-table:: Numbers
       :keepspace:
    <BLANKLINE>
       0,1,2
       3,4,5

    """

    lines = ['.. {0}:: {1}'.format(directive, ' '.join(args))]

    for (key, val) in kwds.iteritems():
        key = key.replace('_', '-')
        if val is None:
            lines.append('   :{0}:'.format(key))
        else:
            lines.append('   :{0}: {1}'.format(key, val))
    if contents:
        lines.append('')
        if isinstance(contents, basestring):
            contents = contents.splitlines()
        lines += map('   {0}'.format, contents)
    return '\n'.join(lines)


class TestListPages(CheckData):
    data = [
        (['./', './Sub', './Sub/SubPage', './Sub/Sub/SubPage'],
         ),
        (['./', './Sub/SubPage', './Sub/Sub/SubPage'],
         ),
        ]

    def check(self, list_descendants):
        page_path = 'it does not depend on the page_path'
        page_text = ".. list-pages::"
        web = MockWeb(list_descendants=list_descendants)
        DictTable = object()  # DictTable should not be used
        setup_wiki(web=web, DictTable=DictTable)
        page_html = gene_html(page_text, page_path)

        assert 'List of Pages' in page_html
        html_format = 'href="%(link)s">%(link)s</a>'
        for sub_link in list_descendants:
            html_str = html_format % {'link': sub_link}
            assert html_str in page_html


class TestPagePathInlineMarkup(CheckData):
    data_symbols = ',!?;:(){}[]<>@#$%^&-+|\\~\'\"='

    data = [
        (trim("""
         This should become an /link/to/the/other/page/.
         But this should not: not/the/link/to/the/other/page/.
         """),
         ['/link/to/the/other/page/'],
         ['not/the/link/to/the/other/page/'],
         ),
        (trim("""
         /texts/in/the/literal/block/::

             /will/not/be/a/link/
         """),
         ['/texts/in/the/literal/block/'],
         ['/will/not/be/a/link/'],
         ),
        (trim("""
         */texts/in/the/inline/emphasis/literal/*
         **/texts/in/the/inline/strong/emphasis/literal/**
         """),
         ['/texts/in/the/inline/emphasis/literal/',
          '/texts/in/the/inline/strong/emphasis/literal/'],
         [],
         ),
        (trim("""
         ``/texts/in/the/inline/literal/``
         """),
         [],
         ['/texts/in/the/inline/literal/'],
         ),
        (trim("""
         `/texts/in/the/hyper/link/ <link>`_`
         """),
         [],
         ['/texts/in/the/hyper/link/'],
         ),
        (trim("""
         /texsts_with_a_-hyphen-after-the-under_score/
         """),  # known issue
         [],
         ['/texsts_with_a_-hyphen-after-the-under_score/'],
         ),
        (trim("""
         /texsts_with_a\_-hyphen-after-the-under_score/
         """),  # this (^-- this slash!) is a workaround
         ['/texsts_with_a_-hyphen-after-the-under_score/'],
         [],
         ),
        ] + [
        ('%s/starts/with/' % s, ['/starts/with/'], [])
        for s in '/' + data_symbols
        ] + [
        ('/ends/with/%s' % s, ['/ends/with/'], [])
        for s in '.' + data_symbols
        ]

    def check(self, page_text, links, not_links):
        page_path = 'it does not depend on the page_path'
        web = object()  # web shuold not be used
        DictTable = object()  # DictTable should not be used
        setup_wiki(web=web, DictTable=DictTable)
        page_html = gene_html(page_text, page_path,
                              settings_overrides={
                                  # ignore docutils system errors
                                  'report_level': 4,
                                  })

        def html_link(link):
            return 'href="%(link)s">%(link)s</a>' % {'link': link}

        for l in links:
            assert html_link(l) in page_html, \
                   "link '%s' should be in `page_html`" % l
        for l in not_links:
            assert html_link(l) not in page_html, \
                   "link '%s' should NOT be in `page_html`" % l


class TestTableData(CheckData):
    data_file_tree_1 = {
        'ex/data_1/file.pickle': {'a': 1, 'b': 0},
        'ex/data_2/file.pickle': {'a': 2, 'b': 0},
        'ex/data_3/file.pickle': {'a': 3, 'b': 0},
        }

    data = [
        ({'args': ['ex/data*/file.pickle'],
          'data': 'a b',},
         data_file_tree_1,
         []),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'base': 'ex',
          'widths': '1 2 2',
          'path-order': 'sort_r'},
         data_file_tree_1,
         []),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'base': 'ex',
          'widths': '1 2 2 2',  # four columns, because of `trans`
          'trans': None,
          'path-order': 'sort_r'},
         data_file_tree_1,
         []),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'base': 'ex',
          'widths': '1 2 2 2',  # four columns, because of 'link'
          'link': '%(relpath)s',
          'path-order': 'sort_r'},
         data_file_tree_1,
         ['data_1', 'data_2', 'data_3']),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'base': 'ex',
          'widths': '1 2',  # not enough number of widths
          'path-order': 'sort_r'},
         data_file_tree_1,
         [],
         ['WARNING/2',
          'Not enough widths arguments for table-data: "1 2"']),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'base': 'ex',
          'widths': '1 2 3 4',  # too many number of widths
          'path-order': 'sort_r'},
         data_file_tree_1,
         [],
         ['WARNING/2',
          'Too many widths arguments for table-data: "1 2 3 4"']),
        ]

    @staticmethod
    def genedir(args, **dirdata):
        return dirtext('table-data', '', *args, **dirdata)

    def check(self, dirdata, file_tree, links, errors=[]):
        page_text = self.genedir(**dirdata)

        page_path = 'it does not depend on the page_path'
        web = MockWeb()
        DictTable = MockDictTable.new_mock(file_tree)
        glob_list = Mock(return_value=sorted(file_tree))
        setup_wiki(web=web, DictTable=DictTable, glob_list=glob_list)
        with CaptureStdIO() as stdio:
            page_html = gene_html(page_text, page_path, _debug=True)
        stderr = stdio.read_stderr()

        for key in dirdata['data'].split():
            td_tag = '<td>{0}</td>'.format(key)
            assert td_tag in page_html

        for link in links:
            assert '{0}</a>'.format(link) in page_html

        for error in errors:
            assert escape(error, True) in page_html
            assert error in stderr
        if not errors:
            assert not stderr


class TestTableDataAndImage(CheckData):
    data_file_tree_1 = {
        'ex/data_1/file.pickle': {'a': 1, 'b': 0},
        'ex/data_2/file.pickle': {'a': 2, 'b': 0},
        'ex/data_3/file.pickle': {'a': 3, 'b': 0},
        }

    data = [
        ({'args': ['ex/data*/file.pickle'],
          'data': 'a b',},
         data_file_tree_1,
         []),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'image': 'fig.png',
          'base': 'ex',
          'path-order': 'sort_r'},
         data_file_tree_1,
         []),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'image': 'fig.png',
          'base': 'ex',
          'link': '%(relpath)s',
          'path-order': 'sort_r'},
         data_file_tree_1,
         ['data_1', 'data_2', 'data_3']),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'image': 'fig.png fig2.png',
          'base': 'ex',
          'widths': '1 2',  # not enough number of widths
          'path-order': 'sort_r'},
         data_file_tree_1,
         [],
         ['WARNING/2',
          'Not enough widths arguments for table-data: "1 2"']),
        ({'args': ['data*/file.pickle'],
          'data': 'a b',
          'image': 'fig.png fig2.png',
          'base': 'ex',
          'widths': '1 2 3 4',  # too many number of widths
          'path-order': 'sort_r'},
         data_file_tree_1,
         [],
         ['WARNING/2',
          'Too many widths arguments for table-data: "1 2 3 4"']),
        ]

    @staticmethod
    def genedir(args=[], **dirdata):
        return dirtext('table-data-and-image', '', *args, **dirdata)

    def check(self, dirdata, file_tree, links, errors=[]):
        page_text = self.genedir(**dirdata)

        page_path = 'it does not depend on the page_path'
        web = MockWeb()
        DictTable = MockDictTable.new_mock(file_tree)
        glob_list = Mock(return_value=sorted(file_tree))
        setup_wiki(web=web, DictTable=DictTable, glob_list=glob_list)
        with CaptureStdIO() as stdio:
            page_html = gene_html(page_text, page_path, _debug=True)
        stderr = stdio.read_stderr()

        for key in dirdata['data'].split():
            td_tag = '<td>{0}</td>'.format(key)
            num_td = page_html.count(td_tag)
            num_data = len(filter(lambda d: key in d,
                                  file_tree.itervalues()))
            eq_(num_td, num_data,
                "there must be #{0} of '{2}'. #{1} exists".format(
                    num_data, num_td, td_tag))

        for link in links:
            assert '{0}</a>'.format(link) in page_html

        for error in errors:
            assert escape(error, True) in page_html
            assert error in stderr
        if not errors:
            assert not stderr


class TestFindImages(CheckData):

    data = [
        ({'args': ['ex/*/fig.png']},
         map('ex/data_{0}/fig.png'.format, range(3))),
        ({'args': ['*/fig.png'], 'base': 'ex'},
         map('ex/data_{0}/fig.png'.format, range(3))),
        ]

    @staticmethod
    def genedir(args=[], **dirdata):
        return dirtext('find-images', '', *args, **dirdata)

    def check(self, dirdata, files):
        page_text = self.genedir(**dirdata)

        page_path = 'it does not depend on the page_path'
        web = MockWeb()
        DictTable = None  # it will not be called
        glob_list = Mock(return_value=sorted(files))
        setup_wiki(web=web, DictTable=DictTable, glob_list=glob_list)
        page_html = gene_html(page_text, page_path, _debug=True)

        datadir = web.app.config['DATADIRPATH']
        base_syspath = os.path.join(datadir, dirdata.get('base', ''))
        glob_list.assert_called_with(
            map(lambda arg: os.path.join(base_syspath, arg),
                dirdata['args']))
        eq_(page_html.count('<img'), len(files))


class TestListPages(CheckData):
    data = [
        ('',  # root page
         ['sub/page', 'sub/sub/page']),
        ('some/page',
         ['sub/page', 'sub/sub/page']),
        ]

    def check(self, page_path, list_descendants):
        page_text = '.. list-pages::'
        web = MockWeb(list_descendants=list_descendants)
        DictTable = None  # it will not be called
        glob_list = None  # it will not be called
        setup_wiki(web=web, DictTable=DictTable, glob_list=glob_list)
        page_html = gene_html(page_text, page_path, _debug=True)

        web.list_descendants.assert_called_with(page_path)
        for subpage in list_descendants:
            assert subpage in page_html


class TestDictDiff(CheckData):
    data_page_text_1 = trim(
        """
        .. dictdiff:: data*/file.pickle
        """)
    data_page_text_2 = trim(
        """
        .. dictdiff:: data*/file.pickle
           :link: %(path)s
        """)
    data_page_text_3 = trim(
        """
        .. dictdiff:: data*/file.pickle
           :link: %(non_magic_word)s
        """)
    data_file_tree = {
        'data_1/file.pickle': {'a': 1, 'b': 0},
        'data_2/file.pickle': {'a': 2, 'b': 0},
        'data_3/file.pickle': {'a': 3, 'b': 0},
        }
    data_dictdiff = {
        'a': {'data_1/file.pickle': 1,
              'data_2/file.pickle': 2,
              'data_3/file.pickle': 3,
              },
        }
    data_links_2 = ['data_1', 'data_2', 'data_3']

    data = [
        (data_page_text_1, data_file_tree, data_dictdiff, []),
        (data_page_text_2, data_file_tree, data_dictdiff, data_links_2),
        (data_page_text_3, data_file_tree, data_dictdiff, None),
        ]

    def check(self, page_text, file_tree, dictdiff, links):
        page_path = 'it does not depend on the page_path'
        web = MockWeb()
        DictTable = MockDictTable.new_mock(file_tree)
        glob_list = Mock(return_value=sorted(file_tree))
        setup_wiki(web=web, DictTable=DictTable, glob_list=glob_list)
        page_html = gene_html(page_text, page_path)

        for key in dictdiff:
            assert key in page_html

        if links:
            for link in links:
                assert '%s</a>' % link in page_html
        elif links == []:
            assert 'link(s)' not in page_html



class TestGridImages(CheckData):

    data_file_tree_1 = dict(
        ('a_%d_b_%d_c_%d/file.pickle' % (a, b, c), dict(a=a, b=b, c=c))
        for (a, b, c) in product([0, 1, 2], [3, 4, 5], [6, 7, 8]))

    data_file_tree_2 = dict(
        (key, val) for (key, val) in data_file_tree_1.iteritems()
        if key not in ['a_%d_b_%d_c_%d/file.pickle' % abc
                       for abc in [(0, 3, 6), (0, 3, 7)]])

    data_page_text_1 = trim(
        """
        .. grid-images:: */file.pickle
           :param: a b c
           :image: dummy-image.png
        """)

    data = [
        (data_page_text_1,
         data_file_tree_1,
         {'<td>': ((3 ** 3) * 2  # number of images + c=%d besides it
                   + 3 * 3  # number of sub-tables (num_a x num_b)
                   + 3 * 2  # number of a=%d and b=%d
                   + 1  # top-left empty cell
                   ),
          },
         ),
        (data_page_text_1,
         data_file_tree_2,
         {'<td>': ((3 ** 3) * 2  # number of images + c=%d besides it
                   + 3 * 3  # number of sub-tables (num_a x num_b)
                   + 3 * 2  # number of a=%d and b=%d
                   + 1  # top-left empty cell
                   ),
          },
         ),
        (data_page_text_1,
         {},  # no match
         {'<td>': 1},
         ),
        ]

    def check(self, page_text, file_tree, stats):
        page_path = 'it does not depend on the page_path'
        web = MockWeb()
        DictTable = MockDictTable.new_mock(file_tree)
        glob_list = Mock(return_value=sorted(file_tree))
        setup_wiki(web=web, DictTable=DictTable, glob_list=glob_list)
        page_html = gene_html(page_text, page_path)

        for (key, val) in stats.iteritems():
            eq_(page_html.count(key), val,
                "page_html must contains %d of '%s'" % (val, key))



class TestConvTexts(CheckData):

    # texts/*.txt should be converted w/o system error
    textdir = os.path.join(os.path.dirname(__file__), 'texts')
    data = [
        (os.path.relpath(abspath, textdir),) for abspath in
        glob(os.path.join(textdir, '*.txt'))]

    def check(self, path):
        gene_html(file(os.path.join(self.textdir, path)).read(),
                  settings_overrides={
                      # ignore docutils system errors
                      'report_level': 4,
                      })


class CheckException(Exception):
    pass


def test_gene_html_no_fail():
    exception_message = (
        '`gene_html` should not fail whatever happen during the '
        'html generation, provided DEBUG=False')
    page_text = trim("""
    .. dictdiff:: *

    dictdiff is for raising Exception via DictTable
    """)
    page_path = 'it does not depend on the page_path'
    web = MockWeb()
    DictTable = Mock()
    DictTable.from_path_list = Mock(
        side_effect=CheckException(exception_message))
    glob_list = Mock(return_value=[])
    setup_wiki(web=web, DictTable=DictTable, glob_list=glob_list)

    # error must be suppressed when _debug=False
    page_html = gene_html(page_text, page_path, _debug=False)
    assert exception_message in page_html   # TB will be returned

    # error must NOT be suppressed when _debug=True
    assert_raises(CheckException, gene_html,
                  page_text, page_path, _debug=True)
