import os
from hashlib import md5
from whoosh import index


def get_schema():
    """
    Get whoosh's schema object

    Defined fields
    --------------
    page_path : ID(stored=True, unique=True)
        This is as same as the `page_path` column in the `pages` table.
    page_text : TEXT
        This is as same as the `page_text` column in the `pages` table.
    hash : STORED
        This is the md5 hash of `page_text`.
        This is used for the comparison of the indexed `page_text`
        and possibly newer one.  If the hash is different, new
        `page_text` will be indexed.

    """
    from whoosh.fields import Schema, TEXT, ID, STORED

    return Schema(page_path=ID(stored=True, unique=True),
                  page_text=TEXT,
                  hash=STORED)


def get_index(indexdir):
    """
    Get Whoosh index object. Create the index if it does not exist.
    """
    if not os.path.isdir(indexdir):
        os.mkdir(indexdir)
    if not index.exists_in(indexdir):
        ix = index.create_in(indexdir, get_schema())
    else:
        ix = index.open_dir(indexdir)
    return ix


def _update_doc(writer, searcher, page_path, page_text):
    """
    Helper function for `update` and `update_all`.
    """
    old_document = searcher.document(page_path=page_path)
    if old_document:
        old_hash = old_document['hash']
    else:
        old_hash = None

    new_hash = md5(page_text.encode('utf-8')).hexdigest()
    if old_hash != new_hash:
        writer.update_document(
            page_path=unicode(page_path),
            page_text=page_text,
            hash=new_hash)
        return True
    else:
        return False


def update(ix, page_path, page_text):
    """
    Update or create new index.
    """
    with ix.writer() as writer:
        with writer.searcher() as searcher:
            return _update_doc(writer, searcher, page_path, page_text)


def update_all(ix, doc_list):
    """
    Update or create new index from the list of document.

    The argument `doc_list` must be a list of dictionary with keys
    'page_path' and 'page_text'.

    Note that this function does NOT check if there are any indexed
    document missing in the main DB (it should be deleted in the
    search index), because there is no possibility for that to happen.

    """
    num_updated = 0
    with ix.writer() as writer:
        with writer.searcher() as searcher:
            for doc in doc_list:
                if _update_doc(writer, searcher, **doc):
                    num_updated += 1
    return num_updated


def delete(ix, page_path):
    """
    Delete the given `page_path` from the search index.
    """
    with ix.writer() as writer:
        writer.delete_by_term('page_path', page_path)


def search(ix, querystr, get_page_text):
    """
    Search thought the index by given query string.

    `get_page_text` is `neorg.web.get_page_text` or its equivalent,
    i.e., it returns `page_text` given `page_path`.

    """

    from cgi import escape
    from whoosh.qparser import QueryParser

    querystr = unicode(querystr)
    with ix.searcher() as searcher:
        query = QueryParser("page_text", ix.schema).parse(querystr)
        results = searcher.search(query)

        for hit in results:
            page_path = hit['page_path']
            page_text = escape(get_page_text(page_path), True)
            yield (page_path, hit.highlights("page_text", page_text))
