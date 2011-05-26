import os
from glob import glob
from docutils import nodes, utils
from mock import Mock

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
    data = [
        (trim("""
         .. dictdiff:: file_*.pickle
         """),
         {'data/file_1.pickle': {'a': 1, 'b': 0},
          'data/file_2.pickle': {'a': 2, 'b': 0},
          'data/file_3.pickle': {'a': 3, 'b': 0},
          },
         {'a': {'data/file_1.pickle': 1,
                'data/file_2.pickle': 2,
                'data/file_3.pickle': 3,
                }},
         ),
        ]

    def check(self, page_text, file_tree, dictdiff):
        page_path = 'it does not depend on the page_path'
        web = MockWeb()
        DictTable = MockDictTable.new_mock(file_tree)
        glob_list = Mock(return_value=sorted(file_tree))
        setup_wiki(web=web, DictTable=DictTable, glob_list=glob_list)
        page_html = gene_html(page_text, page_path)

        for key in dictdiff:
            assert key in page_html


class TestConvTexts(CheckData):

    # texts/*.txt should be converted w/o system error
    textdir = os.path.join(os.path.dirname(__file__), 'texts')
    data = [
        (os.path.relpath(abspath, textdir),) for abspath in
        glob(os.path.join(textdir, '*.txt'))]

    def check(self, path):
        gene_html(file(os.path.join(self.textdir, path)).read())
