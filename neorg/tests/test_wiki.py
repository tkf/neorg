import os
from glob import glob
from itertools import product
from docutils import nodes, utils
from mock import Mock
from nose.tools import eq_

from neorg.wiki import setup_wiki, gene_html
from neorg.tests.utils import MockWeb, MockDictTable, CheckData, trim


def doctree_from_dict(data):
    if 'document' == data['node']:
        node = utils.new_document('<string>')
    else:
        node = getattr(nodes, data['node'])(rawsource='',
                                            **data.get('kwds', {}))
    for child in data.get('children', []):
        node += doctree_from_dict(child)
    return node


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
        ]

    def check(self, page_text, links, not_links):
        page_path = 'it does not depend on the page_path'
        web = object()  # web shuold not be used
        DictTable = object()  # DictTable should not be used
        setup_wiki(web=web, DictTable=DictTable)
        page_html = gene_html(page_text, page_path)

        def html_link(link):
            return 'href="%(link)s">%(link)s</a>' % {'link': link}

        for l in links:
            assert html_link(l) in page_html
        for l in not_links:
            assert html_link(l) not in page_html


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
