"""
Convert page text using docutils
"""

from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives.images import Image
from docutils.readers import standalone
from docutils.transforms import Transform
from docutils.writers import html4css1
from docutils import nodes, writers

from os import path
from glob import glob

from neorg.data import load_any, get_nested_fnmatch


# disable docutils security hazards:
# http://docutils.sourceforge.net/docs/howto/security.html
SAFE_DOCUTILS = dict(file_insertion_enabled=False, raw_enabled=False)


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



def gene_paragraph(rawtext):
    paragraph = nodes.paragraph()
    paragraph += nodes.Text(rawtext)
    return paragraph


def gene_entry(node_or_any):
    entry = nodes.entry()
    if isinstance(node_or_any, nodes.Node):
        entry += node_or_any
    else:
        entry += gene_paragraph(str(node_or_any))
    return entry


def gene_table(list2d, title=None, colwidths=None):
    """
    Generate table node from 2D list
    """
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


class TableDataAndImage(Directive):
    """
    Search data and show matched data and corresponding image(s)

    ::

        .. table-data-and-image:: my/experiment/2011-02-*/data.json
           :data: x y result sub.result
           :image: x_y_plot.png x_result_plot.png

    widths : integer [, integer...]
        A comma- or space-separated list of relative column widths.
        Note that the first column is data sub-table and the second and
        the after are the images specified in `:image:`.

    image-{OPTION} : integer:{VAL} [, integer:{VAL} ...]
        `integer` is the index of the image.
        `{VAL}` specifies the value of the `{OPTION}` of the
        image directive.

    """

    _dirc_name = 'table-data-and-image'
    _datadir = None  # needs override
    _dataurlroot = None  # needs override

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'data': lambda x: x.split(),
                   'image': lambda x: x.split(),
                   'widths': directives.positive_int_list}
    option_spec.update(_adapt_option_spec_from_image())
    has_content = False


    def run(self):
        datapath = path.join(self._datadir,
                             directives.uri(self.arguments[0]))

        data_keys = self.options.get('data', [])
        image_names = self.options.get('image', [])
        image_options = get_suboptions(self.options, 'image-')
        colwidths = self.options.get('widths')

        rowdata = []
        for fullpath in glob(datapath):
            relpath = path.relpath(fullpath, self._datadir)
            parenturl = path.join(self._dataurlroot,
                                  path.dirname(relpath))
            data = load_any(fullpath)
            keyval = []
            for dictpath in data_keys:
                keyval += get_nested_fnmatch(data, dictpath)
            subtable = gene_table(keyval, relpath)
            images = [
                nodes.image(uri=path.join(parenturl, name),
                            **image_options.get(i, {}))
                for (i, name) in enumerate(image_names)]
            rowdata.append([subtable] + images)
        return [gene_table(rowdata, colwidths=colwidths)]


def register_neorg_directives(datadir, dataurlroot):
    for cls in [TableDataAndImage]:
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
