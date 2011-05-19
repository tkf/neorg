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


@app.route('/_save', defaults={'pagepath': ''}, methods=['POST'])
@app.route('/<path:pagepath>/_save', methods=['POST'])
def save(pagepath):
    if request.form.get('save') == 'Save':
        g.db.execute(
            'insert or replace into pages (pagepath, pagetext) values (?, ?)',
            [pagepath, request.form['pagetext']])
        g.db.commit()
        flash('Saved!')
        return redirect(url_for("page", pagepath=pagepath))
    elif request.form.get('preview') == 'Preview':
        pagetext = request.form['pagetext']
        pagehtml = gene_html(pagetext)
        flash('Previewing... Not yet saved!')
        return render_template(
            "edit.html",
            title='Preview - ' + (pagepath or ROOT_TITLE),
            pagepath=pagepath,
            pagetext=pagetext,
            pagehtml=pagehtml)
    elif request.form.get('cancel') == 'Cancel':
        flash('Discarded changes!')
        return redirect(url_for("page", pagepath=pagepath))


@app.route('/_edit', defaults={'pagepath': ''})
@app.route('/<path:pagepath>/_edit')
def edit(pagepath):
    pagetext = g.db.execute('select pagetext from pages where pagepath = ?',
                            [pagepath]).fetchone()
    return render_template("edit.html",
                           title='Edit - ' + (pagepath or ROOT_TITLE),
                           pagepath=pagepath,
                           pagehtml=gene_html(pagetext[0]) if pagetext else '',
                           pagetext=pagetext[0] if pagetext else '')


@app.route('/', defaults={'pagepath': ''})
@app.route('/<path:pagepath>/')
def page(pagepath):
    pagetext = g.db.execute('select pagetext from pages where pagepath = ?',
                        [pagepath]).fetchone()
    if pagetext:
        pagehtml = gene_html(pagetext[0])
        return render_template("page.html",
                               title=pagepath or ROOT_TITLE,
                               pagepath=pagepath,
                               pagehtml=pagehtml)
    else:
        return redirect(url_for('edit', pagepath=pagepath))


@app.route('/_data/<path:filepath>')
def data_file(filepath):
    return send_from_directory(app.config['DATADIRPATH'], filepath)


@app.route('/favicon.ico/')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))
