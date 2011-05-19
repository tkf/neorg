"""
Convert page text using docutils
"""

from docutils.readers import standalone
from docutils.transforms import Transform
from docutils import nodes

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


def gene_html(text):
    from docutils.core import publish_parts
    return publish_parts(
        text,
        writer_name='html',
        reader=Reader(),
        settings_overrides=SAFE_DOCUTILS)['html_body']
