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


class TestAddPageLinks(CheckData):
    data = [
        (trim("""
         This should become an `link_to_the_other_page`_.
         But this should not: `title_in_this_page`_.

         title_in_this_page
         ==================
         """),
         ['link_to_the_other_page'],
         ['title_in_this_page'],
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

        def html_not_link(link):
            return 'href="#%(id)s">%(link)s</a>' % {
                'link': link,
                'id': nodes.make_id(link),
                }

        for l in links:
            assert html_link(l) in page_html
            assert html_not_link(l) not in page_html
        for l in not_links:
            assert html_link(l) not in page_html
            assert html_not_link(l) in page_html


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