from __future__ import with_statement
import os
import re
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import (Flask, request, g, redirect, url_for,
                   render_template, flash, send_from_directory)
import jinja2
from neorg.config import DefaultConfig
from neorg.wiki import gene_html


def regex_from_temp_path(path):
    """
    Generate regex expression from URL for matching template page

    >>> regex_from_temp_path('/non/temp/url/')
    '^/non/temp/url/$'
    >>> regex_from_temp_path('/just/one/_temp_/')
    '^/just/one/([^/]*)/$'
    >>> regex_from_temp_path('/try/two/_temp_/_temp_/')
    '^/try/two/([^/]*)/([^/]*)/$'

    """
    return '^%s$' % path.replace('_temp_', '([^/]*)')


def match_temp_path(path, temp_path_list):
    """
    Returs matched template path and the matched object

    >>> (temp_path, match) = match_temp_path(
    ...    '/my/url', ['/some/url', '/my/_temp_', '/_temp_'])
    ...
    >>> temp_path
    '/my/_temp_'
    >>> match.groups()
    ('url',)
    >>> (temp_path, match) = match_temp_path(
    ...    '/my/url', ['/some/url', '/my/_temp_', '/_temp_/_temp_'])
    ...
    >>> temp_path
    '/my/_temp_'
    >>> match.groups()
    ('url',)

    """
    for temp_path in sorted(temp_path_list, reverse=True):
        match = re.match(regex_from_temp_path(temp_path), path)
        if match:
            return (temp_path, match)
    return (None, None)


def find_temp_path(path):
    """
    Find the template path matches the given path
    """
    temp_path_list = g.db.execute(
        "select page_path from pages").fetchall()
    return match_temp_path(path, [row[0] for row in temp_path_list])


def temp_parent_path(temp_path):
    """
    The path of the parent page of the leftmost ``_temp_`` page

    >>> temp_parent_path('/parent/_temp_/')
    '/parent/'
    >>> temp_parent_path('/parent/_temp_/complicated/_temp_')
    '/parent/'

    """
    i = temp_path.find('/_temp_')
    if i >= 0:
        return temp_path[:i] + '/'
    else:
        raise ValueError("cannot find '_temp_' in '%s'" % temp_path)


def relpath_from_temp(page_path, temp_path):
    """
    Relative path from the parent of the leftmost ``_temp_`` page

    >>> relpath_from_temp('/parent/generated', '/parent/_temp_')
    '/generated'

    """
    parent_path = temp_parent_path(temp_path)
    parent_len = len(parent_path)
    if page_path[:parent_len] != parent_path:
        raise ValueError(
            "temp_path '%s' is not the correct template path of "
            "page_path '%s'." % (temp_path, page_path))
    return page_path[parent_len - 1:]


def remove_leading_slash(path):
    return path if len(path) == 0 or path[0] != '/' else path[1:]


def filter_descendants(path, path_list):
    """
    Find descendants of `path` in `path_list` and returns relative paths

    >>> path_list = ['a', 'a/b', 'a/b/c']
    >>> filter_descendants('', path_list)
    ['a', 'a/b', 'a/b/c']
    >>> filter_descendants('a', path_list)
    ['', 'b', 'b/c']
    >>> filter_descendants('a/b', path_list)
    ['', 'c']

    """
    lenpath = len(path)
    return [
        remove_leading_slash(p[lenpath:])
        for p in path_list if p.startswith(path)]


def find_descendants(path):
    """
    Find the pages which has `path` as its heading path.
    """
    path_list = [
        row[0] for row in
        g.db.execute("select page_path from pages").fetchall()]
    return filter_descendants(path, path_list)


ROOT_TITLE = 'Organize your experiments and find out more!'

app = Flask('neorg')
app.config.from_object(DefaultConfig)


def connect_db():
    """Returns a new connection to the database."""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    from neorg import __version__
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.execute(
            'insert into system_info (version) values (?)',
            [__version__])
        db.commit()


def system_info():
    """
    Get current system info stored in `system_info` table

    .. warning::

       Do NOT use this in app.
       New function using `g.db` should be implemented to use
       system_info table in app.

    """
    with closing(connect_db()) as db:
        sysinfo_current = db.execute(
            'select * from system_info').fetchone()
    if sysinfo_current:
        return dict(zip(
            ['version', 'updated'],
            sysinfo_current))


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()


@app.after_request
def after_request(response):
    """Closes the database again at the end of the request."""
    g.db.close()
    return response


def get_page_text(page_path):
    row = g.db.execute(
        'select page_text from pages where page_path = ?',
        [page_path]).fetchone()
    if row:
        return row[0]
    else:
        return None


def get_page_text_and_html(page_path):
    page_text = get_page_text(page_path)
    if page_text:
        page_html = gene_html(page_text, page_path)
    else:
        page_html = ''
    return (page_text, page_html)


@app.route('/_delete', defaults={'page_path': ''}, methods=['POST'])
@app.route('/<path:page_path>/_delete', methods=['POST'])
def delete(page_path):
    if request.form.get('yes') == 'Yes':
        g.db.execute(
            'delete from pages where page_path = ?',
            [page_path])
        g.db.execute(
            'insert into page_history (page_path, page_text, page_exists) '
            'values (?, ?, 0)',
            [page_path, ''])
        g.db.commit()
        flash('Page "%s" was deleted.' % page_path)
        return redirect(url_for('page', page_path=''))
    elif request.form.get('no') == 'No':
        flash('Cancel delete.')
        return redirect(url_for('page', page_path=page_path))


@app.route('/_confirm_delete', defaults={'page_path': ''})
@app.route('/<path:page_path>/_confirm_delete')
def confirm_delete(page_path):
    (page_text, page_html) = get_page_text_and_html(page_path)
    return render_template("confirm_delete.html",
                           title='Delete this page - ' + (page_path or ROOT_TITLE),
                           page_path=page_path,
                           page_html=page_html)


@app.route('/_save', defaults={'page_path': ''}, methods=['POST'])
@app.route('/<path:page_path>/_save', methods=['POST'])
def save(page_path):
    if request.form.get('save') == 'Save':
        if get_page_text(page_path) == request.form['page_text']:
            flash('No change was found.')
            return redirect(url_for("page", page_path=page_path))
        g.db.execute(
            'insert or replace into pages (page_path, page_text) values (?, ?)',
            [page_path, request.form['page_text']])
        g.db.execute(
            'insert into page_history (page_path, page_text) values (?, ?)',
            [page_path, request.form['page_text']])
        g.db.commit()
        flash('Saved!')
        return redirect(url_for("page", page_path=page_path))
    elif request.form.get('preview') == 'Preview':
        page_text = request.form['page_text']
        page_html = gene_html(page_text, page_path)
        if get_page_text(page_path) == page_text:
            flash('Previewing... No change was found.')
        else:
            flash('Previewing... Not yet saved!')
        return render_template(
            "edit.html",
            title='Preview - ' + (page_path or ROOT_TITLE),
            page_path=page_path,
            page_text=page_text,
            page_html=page_html)
    elif request.form.get('cancel') == 'Cancel':
        flash('Discarded changes!')
        return redirect(url_for("page", page_path=page_path))
    elif request.form.get('delete') == 'Delete':
        return redirect(url_for("confirm_delete", page_path=page_path))


@app.route('/_edit', defaults={'page_path': ''})
@app.route('/<path:page_path>/_edit')
def edit(page_path):
    (page_text, page_html) = get_page_text_and_html(page_path)
    return render_template("edit.html",
                           title='Edit - ' + (page_path or ROOT_TITLE),
                           page_path=page_path,
                           page_html=page_html,
                           page_text=page_text if page_text else '')


@app.route('/', defaults={'page_path': ''})
@app.route('/<path:page_path>/')
def page(page_path):
    (page_text, page_html) = get_page_text_and_html(page_path)
    if page_text:
        return render_template("page.html",
                               title=page_path or ROOT_TITLE,
                               page_path=page_path,
                               page_html=page_html)
    else:
        generated = gene_from_template(page_path)
        if generated:
            return generated
        else:
            return redirect(url_for('edit', page_path=page_path))


def gene_from_template(page_path):
    (temp_path, match) = find_temp_path(page_path)
    if match:
        temp_text = get_page_text(temp_path)
        template = jinja2.Environment().from_string(temp_text)
        page_text = template.render({
            'path': page_path,
            'relpath': relpath_from_temp(page_path, temp_path),
            'args': match.groups(),
            })
        page_html = gene_html(page_text, page_path)
        return render_template("page.html",
                               title=page_path or ROOT_TITLE,
                               temp_path=temp_path,
                               page_path=page_path,
                               page_html=page_html)


def list_descendants(page_path):
    return map(u'./{0}'.format, sorted(find_descendants(page_path)))


@app.route('/_descendants', defaults={'page_path': ''})
@app.route('/<path:page_path>/_descendants')
def descendants(page_path):
    link_list = list_descendants(page_path)
    return render_template("descendants.html",
                           title='Descendants - ' + (page_path or ROOT_TITLE),
                           link_list=link_list,
                           page_path=page_path)


@app.route('/_history', defaults={'page_path': ''})
@app.route('/<path:page_path>/_history')
def history(page_path):
    page_history_list = g.db.execute(
        'select history_id, page_text, updated '
        'from page_history where page_path = ?',
        [page_path]).fetchall()
    page_history_keys = ('history_id', 'page_text', 'updated')
    page_history = [dict(zip(page_history_keys, row))
                    for row in reversed(page_history_list)]
    return render_template("history.html",
                           title='History - ' + (page_path or ROOT_TITLE),
                           page_path=page_path,
                           page_history=page_history)


@app.route('/_old/<int:history_id>', defaults={'page_path': ''})
@app.route('/<path:page_path>/_old/<int:history_id>')
def old(page_path, history_id):
    page_text = g.db.execute(
        'select page_text from page_history where history_id = ?',
        [history_id]).fetchone()
    page_html = gene_html(page_text[0], page_path)
    return render_template("page.html",
                           title=page_path or ROOT_TITLE,
                           page_path=page_path,
                           page_html=page_html)


@app.route('/_data/<path:filepath>')
def data_file(filepath):
    return send_from_directory(app.config['DATADIRPATH'], filepath)


@app.route('/favicon.ico')
@app.route('/favicon.ico/')
def favicon():
    favicon_path = os.path.join(app.config['NEORG_DIR'], 'favicon.ico')
    if os.path.exists(favicon_path):
        return send_from_directory(app.config['NEORG_DIR'],
                                   'favicon.ico')
    else:
        return redirect(url_for('static', filename='favicon.ico'))


@app.route('/_help/<path:filename>')
def help(filename):
    helpdirpath = app.config.get('HELPDIRPATH')
    if (isinstance(helpdirpath, basestring) and
        os.path.exists(helpdirpath)):
        return send_from_directory(helpdirpath, filename)
    else:
        return redirect(url_for('static',
                                filename=os.path.join('help', filename)))
