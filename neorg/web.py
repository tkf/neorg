from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import (Flask, request, g, redirect, url_for,
                   render_template, flash, send_from_directory)

from neorg.config import DefaultConfig
from neorg.wiki import gene_html

ROOT_TITLE = 'Organize your experiments and find out more!'

app = Flask('neorg')
app.config.from_object(DefaultConfig)


def connect_db():
    """Returns a new connection to the database."""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()


@app.after_request
def after_request(response):
    """Closes the database again at the end of the request."""
    g.db.close()
    return response


@app.route('/_save', defaults={'page_path': ''}, methods=['POST'])
@app.route('/<path:page_path>/_save', methods=['POST'])
def save(page_path):
    if request.form.get('save') == 'Save':
        page_text_old = g.db.execute(
            'select page_text from pages where page_path = ?',
            [page_path]).fetchone()
        if page_text_old and page_text_old[0] == request.form['page_text']:
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
        page_html = gene_html(page_text)
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


@app.route('/_edit', defaults={'page_path': ''})
@app.route('/<path:page_path>/_edit')
def edit(page_path):
    page_text = g.db.execute(
        'select page_text from pages where page_path = ?',
        [page_path]).fetchone()
    return render_template("edit.html",
                           title='Edit - ' + (page_path or ROOT_TITLE),
                           page_path=page_path,
                           page_html=gene_html(page_text[0]) if page_text else '',
                           page_text=page_text[0] if page_text else '')


@app.route('/', defaults={'page_path': ''})
@app.route('/<path:page_path>/')
def page(page_path):
    page_text = g.db.execute(
        'select page_text from pages where page_path = ?',
        [page_path]).fetchone()
    if page_text:
        page_html = gene_html(page_text[0])
        return render_template("page.html",
                               title=page_path or ROOT_TITLE,
                               page_path=page_path,
                               page_html=page_html)
    else:
        return redirect(url_for('edit', page_path=page_path))


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
    page_html = gene_html(page_text[0])
    return render_template("page.html",
                           title=page_path or ROOT_TITLE,
                           page_path=page_path,
                           page_html=page_html)


@app.route('/_data/<path:filepath>')
def data_file(filepath):
    return send_from_directory(app.config['DATADIRPATH'], filepath)


@app.route('/favicon.ico/')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))
