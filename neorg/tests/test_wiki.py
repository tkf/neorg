import os
from glob import glob
from docutils import nodes, utils
from mock import Mock

from neorg.wiki import setup_wiki, gene_html, convert_page_path
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


class TestConvertPagePath(CheckData):

    data = [
        (trim("""
              /this/is/page/path/0/
              ./this/is/page/path/1/
              ../this/is/page/path/2/
              this/is/NOT/page/path/3/
              /this/is/NOT/page/path/4
              """),
         ['/this/is/page/path/0/',
          './this/is/page/path/1/',
          '../this/is/page/path/2/',
          ],
         ['this/is/NOT/page/path/3/',
          '/this/is/NOT/page/path/4',
          ],
         ),
        # to make sure converting-twice method works
        ("\n".join("/this/is/page/path/%d/" % i for i in range(12)),
         ['/this/is/page/path/%d/' % i for i in range(12)],
         [],
         ),
        # ... and with odd number, too.
        ("\n".join("/this/is/page/path/%d/" % i for i in range(13)),
         ['/this/is/page/path/%d/' % i for i in range(13)],
         [],
         ),
        # repeating heading './' and '../'
        (trim("""
              ../../parent/parent/
              ../../../parent/parent/parent/
              ././me/me/
              ./././me/me/she/
              ../brother/../sister/../../uncle/../../../grandpa/
              """),
         ['../../parent/parent/',
          '../../../parent/parent/parent/',
          '././me/me/',
          './././me/me/she/',
          ],
         ['../brother/../sister/../../uncle/../../../grandpa/',
          # ... is not supported
          ],
         ),
        # comma, period, semicolon, exclamation mark and question mark
        (trim("""
              By the way, the link ./like-this/, can be
              followed by the comma, period and semicolon,
              which is very ../nice/; link can be at the
              end of the /sentence/.
              Be careful! ./this/.will/be/a/weird/link.
              /nice/? /very/nice/!
              """),
         ['./like-this/',
          '../nice/',
          '/sentence/',
          './this/',
          '/nice/',
          '/very/nice/',
          ],
         [],
         ),
        # known problems
        (trim("""
              `This /should/not/be/a/link/ <but/it/will/be>`_
              *This /is/also/not/ good*.
              `You can \./escape/ <like/this>`_
              and `like \/this/ </which/should/be/enough>`_.

              ::

                  but this is /very/big/problem/!!!

              """),
         ['/should/not/be/a/link/',
          '/is/also/not/',
          '/very/big/problem/',
          ],
         ['./escape/',
          '/this/'],
         ),
        ]
    data_allowed = [
        '/good/path/',
        '/this_is_not_bad/',
        '/this.is.not.bad/',
        ]
    data_not_allowed = [
        '/_this_is_bad/',
        '/-this_is_bad/',
        '/.this_is_bad/',
        '.../thisisbad/',
        ]

    def check(self, page_text, link_list, not_link_list):
        converted = convert_page_path(page_text)

        def rstlink(l):
            return '`%(link)s <%(link)s>`_' % {'link': l}

        for link in link_list:
            assert rstlink(link) in converted, \
                   "%s is not converted" % link

        for not_link in not_link_list:
            assert rstlink(not_link) not in converted, \
                   "%s is converted" % link

    def __init__(self):
        self.data = self.data + [
            self.allowed(l) for l in self.data_allowed
            ] + [
            self.not_allowed(l) for l in self.data_not_allowed
            ]

    @classmethod
    def allowed(cls, link):
        page_text = cls.with_dummy_text(link)
        return (page_text, [link], [])

    @classmethod
    def not_allowed(cls, link):
        page_text = cls.with_dummy_text(link)
        return (page_text, [], [link])

    @staticmethod
    def with_dummy_text(link):
        page_text = trim(
            """
            some dummy string
            %s
            other dummy string
            """ % link)
        return page_text


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
