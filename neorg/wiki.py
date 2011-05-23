"""
Convert page text using docutils

Usage
=====

1. Register directives defined here to the docutils internal using
   `register_neorg_directives` function.
   See `neorg.commands.serve` for the real usage.
2. Call `gene_html` with rst text.
   See functions in `neorg.web` for the real usage.

Internal
========

Registration of the `Directive` classes is tricky, because they
uses `self._datadir` (file path to the data directory) and
`self._dataurlroot` (url-equivalent of the `self._datadir`).
These two class attributes are set in the `register_neorg_directives`
function before the registration.  Note that `self._dirc_name` is
used to store the directive name to its class for ease of the
registration.

Definition and the usage of the `Writer` and the `Reader` (and
`Transform` classes in th Reader class) are pretty straightforward.
These are written in the docstring of `publish_programmatically` in
`docutils.core` which is referenced from `publish_parts` (the function
used here).

"""

from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives.images import Image
from docutils.readers import standalone
from docutils.transforms import Transform
from docutils.writers import html4css1
from docutils import nodes, writers

from os import path
from glob import glob

from neorg.data import DictTable


# disable docutils security hazards:
# http://docutils.sourceforge.net/docs/howto/security.html
SAFE_DOCUTILS = dict(file_insertion_enabled=False, raw_enabled=False)

# it seems that docuitls needs upper limit for
# `Directive.optional_arguments` attribute.
# OPTIONAL_ARGUMENTS_INF is virtually infinite number for NEOrg.
# nobody wants to put args more than this (I hope)
OPTIONAL_ARGUMENTS_INF = 10000


class AddPageLinks(Transform):
    """
    Adds all unknown referencing names as the links to the other pages
    """

    default_priority = 0

    def apply(self):
        for refname in (set(self.document.refnames) -
                        set(self.document.nameids)):
            reference = self.document.refnames[refname][0]
            self.document += nodes.target(
                ids=[nodes.make_id(reference['name'])],
                names=[nodes.fully_normalize_name(reference['name'])],
                refuri=reference['name'],
                )


class Reader(standalone.Reader):

    def get_transforms(self):
        return standalone.Reader.get_transforms(self) + [
            AddPageLinks,
            ]


class Writer(html4css1.Writer):

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = HTMLTranslator


class HTMLTranslator(html4css1.HTMLTranslator):

    def visit_table(self, node):
        classes = ' '.join(['docutils', self.settings.table_style]).strip()
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


def gene_paragraph(rawtext):
    paragraph = nodes.paragraph()
    paragraph += nodes.Text(rawtext)
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


def gene_table(list2d, title=None, colwidths=None):
    """
    Generate table node from 2D list
    """
    if not list2d:
        return nodes.table()
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
    _datadir = None  # needs override
    _dataurlroot = None  # needs override

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
        #     - *_relpath is relative path from `self._datadir`
        #     - *_absurl is url with leading slash
        path_order = self.options.get('path-order', 'sorted')
        if path_order == 'sort_r':
            glob_list_sorted = lambda x: sorted(x, reverse=True)
        else:
            glob_list_sorted = sorted

        base_syspath = path.join(self._datadir,
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

        data_table = DictTable.from_path_list(data_syspath_list,
                                              from_base_list)
        data_table = data_table.filter_by_fnmatch(data_keys)
        rowdata = data_table.as_list()
        if link is not None:
            rowdata[0].append('link(s)')

        for (data_syspath, row) in zip(data_syspath_list, rowdata[1:]):
            data_relpath = path.relpath(data_syspath, self._datadir)
            parent_syspath = path.dirname(data_syspath)
            parent_relpath = path.dirname(data_relpath)
            link_magic = {
                'path': parent_relpath,
                'relpath': path.relpath(parent_syspath, base_syspath),
                }
            if link is not None:
                row.append(gene_links_in_paragraph(
                    [l % link_magic for l in link]))
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
    _datadir = None  # needs override
    _dataurlroot = None  # needs override

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
        #     - *_relpath is relative path from `self._datadir`
        #     - *_absurl is url with leading slash
        path_order = self.options.get('path-order', 'sort')
        if path_order == 'sort_r':
            glob_list_sorted = lambda x: sorted(x, reverse=True)
        else:
            glob_list_sorted = sorted

        base_syspath = path.join(self._datadir,
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

        data_table = DictTable.from_path_list(data_syspath_list)
        if 'sort' in self.options:
            data_table.sort_names_by_values(self.options['sort'])

        rowdata = []
        for data_syspath in data_table.names:
            data_relpath = path.relpath(data_syspath, self._datadir)
            parent_syspath = path.dirname(data_syspath)
            parent_relpath = path.dirname(data_relpath)
            parent_absurl = path.join(self._dataurlroot, parent_relpath)
            link_magic = {
                'path': parent_relpath,
                'relpath': path.relpath(parent_syspath, base_syspath),
                }
            subtable = gene_table(
                data_table.get_nested_fnmatch(data_syspath, data_keys),
                title=path.relpath(data_syspath, base_syspath))
            col0 = [subtable]
            if link is not None:
                col0.append(
                    gene_link_list([l % link_magic for l in link]))
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


class FindImages(Directive):

    _dirc_name = 'find-images'
    _datadir = None  # needs override
    _dataurlroot = None  # needs override

    required_arguments = 1
    optional_arguments = OPTIONAL_ARGUMENTS_INF
    final_argument_whitespace = True
    option_spec = {'base': directives.path}
    has_content = False

    def run(self):
        # naming note:
        #     - *_syspath is system path
        #     - *_relpath is relative path from `self._datadir`
        #     - *_absurl is url with leading slash

        base_syspath = path.join(self._datadir,
                                 self.options.get('base', ''))
        image_syspath_list = glob_list([path.join(base_syspath,
                                                  directives.uri(arg))
                                        for arg in self.arguments])

        def gene_image(relpath):
            image_node = nodes.image(
                rawsource='',
                uri=path.join(self._dataurlroot, relpath))
            image_node['classes'].append('neorg-find-images-image')
            return image_node

        node_list = []
        for image_syspath in image_syspath_list:
            image_relpath = path.relpath(image_syspath, self._datadir)
            node_list += [gene_paragraph(image_relpath),
                          gene_image(image_relpath)]
        return node_list


def register_neorg_directives(datadir, dataurlroot):
    for cls in [TableData, TableDataAndImage, FindImages]:
        cls._datadir = datadir
        cls._dataurlroot = dataurlroot
        directives.register_directive(cls._dirc_name, cls)


def gene_html(text):
    from docutils.core import publish_parts
    return publish_parts(
        text,
        writer=Writer(),
        reader=Reader(),
        settings_overrides=SAFE_DOCUTILS)['html_body']
