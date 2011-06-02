"""
Convert page text using docutils

Usage
=====

1. Register directives defined here to the docutils internal using
   `setup_wiki` function.
   See `neorg.commands.serve` for the real usage.
2. Call `gene_html` with rst text.
   See functions in `neorg.web` for the real usage.

Internal
========

The class attribute `self._web` is used for accessing `neorg.web` from
`nerog.wiki`.  This is stored in the `self` for the unit testing.
Any mock object can be "injected" from the `setup_wiki` function.
The class attribute `self._DictTable` is used for the same reason.
Note that `self._dirc_name` is used to store the directive name to its
class for ease of the registration.

Definition and the usage of the `Writer` and the `Reader` (and
`Transform` classes in th Reader class) are pretty straightforward.
These are written in the docstring of `publish_programmatically` in
`docutils.core` which is referenced from `publish_parts` (the function
used here).

To pass the information from `neorg.web` to `neorg.wiki`, the
`settings_overrides` argument of the `publish_parts` is used.
This is usually command line options to the docutils tools.
Any object can be passed to `settings_overrides`.  This settings can
be accessed by `self.document.settings` from the `Transform` classes.

"""

import re
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives.images import Image
from docutils.readers import standalone
from docutils.transforms import Transform
from docutils.writers import html4css1
from docutils import nodes, writers

from os import path
from glob import glob


# disable docutils security hazards:
# http://docutils.sourceforge.net/docs/howto/security.html
SAFE_DOCUTILS = dict(file_insertion_enabled=False, raw_enabled=False)

# it seems that docuitls needs upper limit for
# `Directive.optional_arguments` attribute.
# OPTIONAL_ARGUMENTS_INF is virtually infinite number for NEOrg.
# nobody wants to put args more than this (I hope)
OPTIONAL_ARGUMENTS_INF = 10000


class SafeMagic(object):
    """
    Safe way to do ``spell % {'magic_word': value}``

    >>> sm = SafeMagic({'a': 1, 'b': 2})
    >>> sm('%(a)s plus %(b)s')
    '1 plus 2'
    >>> sm('%(non_magic_word)s')
    '%(non_magic_word)s'
    >>> sm.fails
    [KeyError('non_magic_word',)]

    """

    def __init__(self, magic_words):
        self._magic_words = magic_words
        self.fails = []

    def __call__(self, spell):
        try:
            return spell % self._magic_words
        except KeyError, err:
            self.fails.append(err)
            return spell


def convert_page_path_to_nodes(text, node_list=[]):
    split = _RE_PAGE_PATH.split(text, maxsplit=1)
    if len(split) == 7:
        pre = ''.join(split[:2])
        page_path = split[2]
        rest = ''.join(split[-2:])
        new_node_list = (
            node_list + [nodes.Text(pre)] + list(gene_link(page_path)))
        return convert_page_path_to_nodes(rest, new_node_list)
    elif len(split) == 1:
        return node_list + [nodes.Text(text)]

_RE_PAGE_PATH = re.compile(
    r'(?P<head>^|\s)'
    r'(?P<page_path>(\.{0,2}/)+([a-zA-Z0-9][a-zA-Z0-9_\-\.\+]*/)*)'
    r'(?P<tail>$|[\s\.!\?:;,])')


def condition_page_path(nd):
    return not isinstance(nd.parent, (nodes.FixedTextElement,
                                      nodes.reference,
                                      nodes.footnote_reference,
                                      nodes.citation_reference,
                                      nodes.substitution_reference,
                                      nodes.title_reference))


class AdHocInlineMarkup(Transform):
    """
    Adds simple in-line markup to ReST

    `cond_conv_list` attribute is a list of pair of the condition and
    the convert function. The condition function determines whether
    the conversion is needed for the given Text node. The convert
    function converts the given text to the list of nodes.

    """
    default_priority = 0

    cond_conv_list = [
        (condition_page_path, convert_page_path_to_nodes),
        ]

    def apply(self):

        for (cond, conv) in self.cond_conv_list:
            _cond = lambda nd: isinstance(nd, nodes.Text) and cond(nd)
            for node in self.document.traverse(_cond):
                new_node_list = conv(node.astext())
                node.parent.replace(node, new_node_list)


class list_pages(nodes.Admonition, nodes.Element):
    pass


class dictdiff(nodes.General, nodes.Element):
    pass


class ProcessListPages(Transform):
    _web = None  # needs override
    default_priority = 0

    def apply(self):
        nodes_list_pages = list(self.document.traverse(list_pages))
        if nodes_list_pages:
            page_path = self.document.settings.neorg_page_path
            page_list = self._web.list_descendants(page_path)
            for node in nodes_list_pages:
                title = 'List of Pages'
                admonition = nodes.admonition()
                admonition += nodes.title(title, title)
                admonition += gene_link_list(page_list)
                node.replace_self(admonition)


class ProcessDictDiff(Transform):
    _web = None  # needs override
    _DictTable = None  # needs override
    _glob_list = None  # needs override
    default_priority = 0

    def apply(self):
        for node in self.document.traverse(dictdiff):
            self._replace_node(node)

    def _replace_node(self, node):
        arguments = node.get('arguments')
        path_order = node.get('path-order', 'sorted')
        if path_order == 'sort_r':
            glob_list_sorted = lambda x: sorted(x, reverse=True)
        else:
            glob_list_sorted = sorted
        datadir = self._web.app.config['DATADIRPATH']
        base_syspath = path.join(datadir, node.get('base', ''))
        data_syspath_list = self._glob_list(
            [path.join(base_syspath,
                       directives.uri(arg)) for arg in arguments],
            glob_list_sorted)
        link = node.get('link', [])

        data_table = self._DictTable.from_path_list(data_syspath_list)
        if node.hasattr('sort'):
            data_table.sort_names_by_values(node.get('sort'))

        diff_data =  data_table.diff(include=node.get('include'),
                                     exclude=node.get('exclude'))

        keylist = sorted(diff_data)
        table_header = [''] + keylist
        if link:
            table_header.append('link(s)')
        table_data = [table_header]
        for data_syspath in data_table.names:
            data_relpath = path.relpath(data_syspath, datadir)
            parent_syspath = path.dirname(data_syspath)
            parent_relpath = path.dirname(data_relpath)

            link_magic = SafeMagic({
                'path': parent_relpath,
                'relpath': path.relpath(parent_syspath, base_syspath),
                })
            from_base = path.relpath(data_syspath, base_syspath)
            table_row = (
                [from_base] +
                [diff_data[keystr].get(data_syspath, '')
                 for keystr in keylist]
                )
            if link:
                table_row.append(gene_links_in_paragraph(
                    map(link_magic, link)))
                ## link_magic.fails  # need to do something w/ fails
            table_data.append(table_row)

        if node.hasattr('trans'):
            table_data = zip(*table_data)

        table_node = gene_table(
            table_data,
            title=title_from_path(
                arguments,
                node.get('base'),
                'Diff of data found in: %s',
                ))
        node.replace_self(table_node)


NEORG_TRANSFORMS = [
    AdHocInlineMarkup, ProcessListPages, ProcessDictDiff,
    ]


class Reader(standalone.Reader):

    def get_transforms(self):
        return standalone.Reader.get_transforms(self) + NEORG_TRANSFORMS


class Writer(html4css1.Writer):

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = HTMLTranslator


class HTMLTranslator(html4css1.HTMLTranslator):

    def visit_table(self, node):
        classes = ' '.join(['docutils', self.settings.table_style]
                           + ['neorg-table']).strip()
        self.body.append(
            # in html4css1.HTMLTranslator, ``border="1"`` is hard-corded!
            self.starttag(node, 'table', CLASS=classes))


def with_children(cls, children, *cls_args, **cls_kwds):
    """
    Generate new `cls` node instance and add `children` to it
    """
    node_instance = cls(*cls_args, **cls_kwds)
    node_instance += children
    return node_instance


def gene_paragraph(rawtext, classes=[]):
    paragraph = nodes.paragraph()
    paragraph += nodes.Text(rawtext)
    paragraph['classes'] += classes
    return paragraph


def gene_entry(node_or_any):
    """
    Generate entry node from `node` or `[node, ...]` or anything.
    """
    entry = nodes.entry()
    if isinstance(node_or_any, nodes.Node):
        entry += node_or_any
    elif (isinstance(node_or_any, (list, tuple)) and
          all(isinstance(n, nodes.Node) for n in node_or_any)):
        entry += node_or_any
    else:
        entry += gene_paragraph(str(node_or_any))
    return entry


def gene_table(list2d, title=None, colwidths=None, classes=[],
               _baseclass='neorg-gene-table'):
    """
    Generate table node from 2D list
    """
    allclasses = [_baseclass] + classes
    if not list2d:
        table = nodes.table()
        table['classes'] += allclasses
        return table
    nrow = len(list2d)
    ncol = len(list2d[0])
    if colwidths is None:
        colwidths = [1] * ncol

    table = nodes.table()
    tgroup = nodes.tgroup(cols=ncol)
    tbody = nodes.tbody()
    colspecs = [nodes.colspec(colwidth=cw) for cw in colwidths]
    rows = [nodes.row() for dummy in range(nrow)]

    if title:
        table += nodes.title(title, title)
    table += tgroup
    tgroup += colspecs
    tgroup += tbody
    tbody += rows

    for (row, list1d) in zip(rows, list2d):
        row += [gene_entry(elem) for elem in list1d]

    table['classes'] += allclasses
    return table


def gene_link(uri):
    """
    Generate link (a reference and a target)

    >>> (reference, target) = gene_link('my/link')
    >>> print reference.pformat()
    <reference name="my/link" refuri="my/link">
        my/link
    <BLANKLINE>
    >>> print target.pformat()
    <target ids="my-link" names="my/link" refuri="my/link">
    <BLANKLINE>

    """
    reference = nodes.reference(uri, text=uri, name=uri, refuri=uri)
    target = nodes.target(
        ids=[nodes.make_id(reference['name'])],
        names=[nodes.fully_normalize_name(reference['name'])],
        refuri=reference['name'],
        )
    return (reference, target)


def gene_link_list(uri_list, bullet="*"):
    """
    Generate bullet list of uri from the list of uri

    >>> print gene_link_list(['a', 'b']).pformat()
    <bullet_list bullet="*">
        <list_item>
            <paragraph>
                <reference name="a" refuri="a">
                    a
                <target ids="a" names="a" refuri="a">
        <list_item>
            <paragraph>
                <reference name="b" refuri="b">
                    b
                <target ids="b" names="b" refuri="b">
    <BLANKLINE>

    """
    bullet_list = nodes.bullet_list(bullet=bullet)
    bullet_list += [
        nodes.list_item(
            '', with_children(nodes.paragraph, gene_link(l)))
        for l in uri_list]
    return bullet_list


def gene_links_in_paragraph(uri_list, sep=" | "):
    """
    Generate list of uri in a paragraph from the list of uri

    >>> print gene_links_in_paragraph(['a', 'b']).pformat()
    <paragraph>
        <reference name="a" refuri="a">
            a
        <target ids="a" names="a" refuri="a">
         | 
        <reference name="b" refuri="b">
            b
        <target ids="b" names="b" refuri="b">
    <BLANKLINE>

    """
    paragraph = nodes.paragraph()
    last = len(uri_list) - 1
    for (i, l) in enumerate(uri_list):
        paragraph += gene_link(l)
        if i != last:
            paragraph += nodes.Text(sep)
    return paragraph


def parse_text_list(argument, delimiter=','):
    """
    Converts a space- or comma-separated list of values into a list
    """
    if delimiter in argument:
        entries = argument.split(delimiter)
    else:
        entries = argument.split()
    return [v.strip() for v in entries]


def _adapt_option_spec_from_image():
    """
    Adapt option_spec from image directive
    """
    def wrap(key, oldparse):
        def parse(arg):
            valdict = {}
            for kv in arg.split(','):
                (k, v) = [s.strip() for s in kv.split(':', 1)]
                valdict[int(k)] = oldparse(v)
            return valdict
        return parse

    for (key, oldparse) in Image.option_spec.iteritems():
        yield ('image-%s' % key, wrap(key, oldparse))


def transpose_dict(dict_of_dict):
    """
    Transpose dictionary-of-dictionary

    >>> dod = {'a': {0: 'a0', 2: 'a2'}, 'b': {0: 'b0', 1: 'b1'}}
    >>> tr = transpose_dict(dod)
    >>> sorted(tr[0])
    ['a', 'b']
    >>> sorted(tr[1])
    ['b']
    >>> tr[2]['a']
    'a2'

    """
    subkeyset = set()
    for (key, subdict) in dict_of_dict.iteritems():
        subkeyset.update(subdict)
    transposed = {}
    for subkey in subkeyset:
        transposed[subkey] = dict(
            (key, dict_of_dict[key][subkey]) for key in dict_of_dict
            if subkey in dict_of_dict[key]
            )
    return transposed


def get_suboptions(options, prefix):
    prefixlen = len(prefix)
    suboptions = {}
    for (key, val) in options.iteritems():
        if key.startswith(prefix):
            suboptions[key[prefixlen:]] = val
    return transpose_dict(suboptions)


def glob_list(pathlist, sorted=sorted):
    globed = []
    for pathname in pathlist:
        globed += sorted(glob(pathname))
    return globed


def title_from_path(pathlist, base=None, format='%s'):
    """
    Format title string for searched path

    >>> title_from_path(['just_one'])
    'just_one'
    >>> title_from_path(['one', 'two'])
    '{one, two}'
    >>> title_from_path(['one', 'two'], base='with_base')
    'with_base/{one, two}'

    """
    base = '' if base is None else base
    if len(pathlist) < 2:
        pathstr = path.join(base, pathlist[0])
    else:
        pathstr = path.join(
            base,
            '{%s}' % ', '.join(
                [arg.strip(path.sep) for arg in pathlist]))
    return format % pathstr


def choice_from(*choices):
    def conv_func(argument):
        return directives.choice(argument, choices)
    return conv_func


class TableData(Directive):
    """
    Search data and show matched data and corresponding image(s)
    """

    _dirc_name = 'table-data'
    _web = None  # needs override
    _DictTable = None  # needs override

    required_arguments = 1
    optional_arguments = OPTIONAL_ARGUMENTS_INF
    final_argument_whitespace = True
    option_spec = {'data': parse_text_list,
                   'base': directives.path,
                   'link': parse_text_list,
                   'widths': directives.positive_int_list,
                   'path-order': choice_from('sort', 'sort_r'),
                   'trans': directives.flag}
    has_content = False


    def run(self):
        # naming note:
        #     - *_syspath is system path
        #     - *_relpath is relative path from `datadir`
        #     - *_absurl is url with leading slash
        datadir = self._web.app.config['DATADIRPATH']
        path_order = self.options.get('path-order', 'sorted')
        if path_order == 'sort_r':
            glob_list_sorted = lambda x: sorted(x, reverse=True)
        else:
            glob_list_sorted = sorted

        base_syspath = path.join(datadir,
                                 self.options.get('base', ''))
        data_syspath_list = glob_list([path.join(base_syspath,
                                                 directives.uri(arg))
                                       for arg in self.arguments],
                                      glob_list_sorted)
        from_base_list = [
            path.relpath(x, base_syspath) for x in data_syspath_list]

        data_keys = self.options.get('data', [])
        colwidths = self.options.get('widths')
        link = self.options.get('link')

        data_table = self._DictTable.from_path_list(data_syspath_list,
                                                    from_base_list)
        data_table = data_table.filter_by_fnmatch(data_keys)
        rowdata = data_table.as_list()
        if link is not None:
            rowdata[0].append('link(s)')

        for (data_syspath, row) in zip(data_syspath_list, rowdata[1:]):
            data_relpath = path.relpath(data_syspath, datadir)
            parent_syspath = path.dirname(data_syspath)
            parent_relpath = path.dirname(data_relpath)
            link_magic = SafeMagic({
                'path': parent_relpath,
                'relpath': path.relpath(parent_syspath, base_syspath),
                })
            if link is not None:
                row.append(gene_links_in_paragraph(
                    map(link_magic, link)))
                ## link_magic.fails  # need to do something w/ fails
        if 'trans' in self.options:
            rowdata = zip(*rowdata)
        return [gene_table(rowdata,
                           title=title_from_path(
                               self.arguments,
                               self.options.get('base'),
                               'Data found in: %s'),
                           colwidths=colwidths)]


class TableDataAndImage(Directive):
    """
    Search data and show matched data and corresponding image(s)
    """

    _dirc_name = 'table-data-and-image'
    _web = None  # needs override
    _DictTable = None  # needs override

    required_arguments = 1
    optional_arguments = OPTIONAL_ARGUMENTS_INF
    final_argument_whitespace = True
    option_spec = {'data': parse_text_list,
                   'image': parse_text_list,
                   'base': directives.path,
                   'link': parse_text_list,
                   'path-order': choice_from('sort', 'sort_r'),
                   'sort': parse_text_list,
                   'widths': directives.positive_int_list}
    option_spec.update(_adapt_option_spec_from_image())
    has_content = False


    def run(self):
        # naming note:
        #     - *_syspath is system path
        #     - *_relpath is relative path from `datadir`
        #     - *_absurl is url with leading slash
        datadir = self._web.app.config['DATADIRPATH']
        datadirurl = self._web.app.config['DATADIRURL']
        path_order = self.options.get('path-order', 'sort')
        if path_order == 'sort_r':
            glob_list_sorted = lambda x: sorted(x, reverse=True)
        else:
            glob_list_sorted = sorted

        base_syspath = path.join(datadir,
                                 self.options.get('base', ''))
        data_syspath_list = glob_list([path.join(base_syspath,
                                                 directives.uri(arg))
                                       for arg in self.arguments],
                                      glob_list_sorted)

        data_keys = self.options.get('data', [])
        image_names = self.options.get('image', [])
        image_options = get_suboptions(self.options, 'image-')
        colwidths = self.options.get('widths')
        link = self.options.get('link')

        data_table = self._DictTable.from_path_list(data_syspath_list)
        if 'sort' in self.options:
            data_table.sort_names_by_values(self.options['sort'])

        rowdata = []
        for data_syspath in data_table.names:
            data_relpath = path.relpath(data_syspath, datadir)
            parent_syspath = path.dirname(data_syspath)
            parent_relpath = path.dirname(data_relpath)
            parent_absurl = path.join(datadirurl, parent_relpath)
            link_magic = SafeMagic({
                'path': parent_relpath,
                'relpath': path.relpath(parent_syspath, base_syspath),
                })
            subtable = gene_table(
                data_table.get_nested_fnmatch(data_syspath, data_keys),
                title=path.relpath(data_syspath, base_syspath))
            col0 = [subtable]
            if link is not None:
                col0.append(gene_link_list(
                    map(link_magic, link)))
                ## link_magic.fails  # need to do something w/ fails
            images = [
                nodes.image(uri=path.join(parent_absurl, name),
                            **image_options.get(i, {}))
                for (i, name) in enumerate(image_names)]
            rowdata.append([col0] + images)
        return [gene_table(rowdata,
                           title=title_from_path(
                               self.arguments,
                               self.options.get('base'),
                               'Data found in: %s'),
                           colwidths=colwidths)]


class DictDiff(Directive):
    _dirc_name = 'dictdiff'

    required_arguments = 1
    optional_arguments = OPTIONAL_ARGUMENTS_INF
    final_argument_whitespace = True
    option_spec = {'base': directives.path,
                   'link': parse_text_list,
                   'include': parse_text_list,
                   'exclude': parse_text_list,
                   'sort': parse_text_list,
                   'path-order': choice_from('sort', 'sort_r'),
                   'trans': directives.flag}
    has_content = False

    def run(self):
        return [dictdiff(rawsource=self.block_text,
                         arguments=self.arguments,
                         **self.options)]


class FindImages(Directive):

    _dirc_name = 'find-images'
    _web = None  # needs override
    _DictTable = None  # needs override

    required_arguments = 1
    optional_arguments = OPTIONAL_ARGUMENTS_INF
    final_argument_whitespace = True
    option_spec = {'base': directives.path}
    has_content = False

    def run(self):
        # naming note:
        #     - *_syspath is system path
        #     - *_relpath is relative path from `datadir`
        #     - *_absurl is url with leading slash
        datadir = self._web.app.config['DATADIRPATH']
        datadirurl = self._web.app.config['DATADIRURL']

        base_syspath = path.join(datadir,
                                 self.options.get('base', ''))
        image_syspath_list = glob_list([path.join(base_syspath,
                                                  directives.uri(arg))
                                        for arg in self.arguments])

        def gene_image(relpath):
            image_node = nodes.image(
                rawsource='',
                uri=path.join(datadirurl, relpath))
            image_node['classes'].append('neorg-find-images-image')
            return image_node

        node_list = []
        for image_syspath in image_syspath_list:
            image_relpath = path.relpath(image_syspath, datadir)
            node_list += [gene_paragraph(image_relpath),
                          gene_image(image_relpath)]
        return node_list


def gene_table_from_grid_dict(grid_dict, param, conv, title=None, **kwds):
    list2d = []
    len_axes = len(grid_dict.axes)
    if len_axes > 1:
        axes0 = sorted(grid_dict.axes[0])
        axes1 = sorted(grid_dict.axes[1])
        list2d.append(
            [''] +
            [gene_paragraph('%s=%s' % (param[1], y),
                            classes=['neorg-grid-col'])
             for y in axes1])
        for x in axes0:
            list1d = [gene_paragraph('%s=%s' % (param[0], x),
                                     classes=['neorg-grid-row'])]
            for y in axes1:
                dct = grid_dict[x, y]
                if len_axes == 2:
                    elem = conv(dct)
                else:
                    elem = gene_table_from_grid_dict(
                        dct, param[2:], conv, **kwds)
                list1d.append(elem)
            list2d.append(list1d)
    else:
        axes0 = sorted(grid_dict.axes[0])
        list2d = [
            [gene_paragraph('%s=%s' % (param[0], x),
                            classes=['neorg-grid-row']),
             conv(grid_dict[x]),
             ] for x in axes0]
    if len(list2d) > 0 and len(list2d[0]) > 1:
        data_num = (len(list2d[0]) - 1)
        colwidths = [1] + [int(99.0 / data_num)] * data_num
    else:
        colwidths = None
    return gene_table(list2d, title=title, colwidths=colwidths, **kwds)


class GridImages(Directive):
    _dirc_name = 'grid-images'
    _web = None  # needs override
    _DictTable = None  # needs override
    _glob_list = None  # needs override

    required_arguments = 1
    optional_arguments = OPTIONAL_ARGUMENTS_INF
    final_argument_whitespace = True
    option_spec = {'param': parse_text_list,
                   'image': parse_text_list,
                   'base': directives.path}
    has_content = False

    def run(self):
        # naming note:
        #     - *_syspath is system path
        #     - *_relpath is relative path from `datadir`
        #     - *_absurl is url with leading slash
        if 'param' not in self.options:
            return []
        param = self.options['param']
        if 'image' not in self.options:
            return []
        image_names = self.options['image']
        datadir = self._web.app.config['DATADIRPATH']
        datadirurl = self._web.app.config['DATADIRURL']

        base_syspath = path.join(datadir,
                                 self.options.get('base', ''))
        data_syspath_list = self._glob_list(
            [path.join(base_syspath, directives.uri(arg))
             for arg in self.arguments])
        data_table = self._DictTable.from_path_list(data_syspath_list)
        grid_dict = data_table.grid_dict(param)

        def images_from_data_syspath(data_syspath):
            data_relpath = path.relpath(data_syspath, datadir)
            parent_relpath = path.dirname(data_relpath)
            parent_absurl = path.join(datadirurl, parent_relpath)

            return [
                nodes.image(uri=path.join(parent_absurl, name),
                            classes=['neorg-grid-images-image'])
                for (i, name) in enumerate(image_names)]

        def conv(name_list):
            lst = []
            for name in name_list:
                lst += images_from_data_syspath(name)
            return lst

        title = title_from_path(self.arguments,
                                self.options.get('base'),
                                'Comparing images of data found in: %s')

        return [gene_table_from_grid_dict(grid_dict,
                                          param,
                                          conv,
                                          title,
                                          classes=['neorg-grid-images'],
                                          )]

class ListPages(Directive):
    _dirc_name = 'list-pages'

    def run(self):
        return [list_pages('')]


NEORG_DIRECTIVES = [
    TableData, TableDataAndImage, FindImages, ListPages, DictDiff,
    GridImages,
    ]


def setup_wiki(web=None, DictTable=None, glob_list=None):
    if web is None:
        from neorg import web
    if DictTable is None:
        from neorg.data import DictTable
    if glob_list is None:
        from neorg.wiki import glob_list
    glob_list = staticmethod(glob_list)
    for cls in NEORG_TRANSFORMS:
        cls._web = web
        cls._DictTable = DictTable
        cls._glob_list = glob_list
    for cls in NEORG_DIRECTIVES:
        cls._web = web
        cls._DictTable = DictTable
        cls._glob_list = glob_list
        directives.register_directive(cls._dirc_name, cls)


def gene_html(text, page_path=None, settings_overrides={}):
    from docutils.core import publish_parts
    new_settings_overrides = SAFE_DOCUTILS.copy()
    new_settings_overrides.update(
        # these data can be accessed from `self.document.settings`
        # of the Transform classes
        neorg_page_path=page_path,
        **settings_overrides
        )
    return publish_parts(
        text,
        writer=Writer(),
        reader=Reader(),
        settings_overrides=new_settings_overrides)['html_body']
