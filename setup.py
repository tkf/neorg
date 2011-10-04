from setuptools import setup
from distutils.command.build import build
from distutils.cmd import Command
from distutils import log
import os
import shutil
try:
    # check if BuildDoc is available
    from sphinx.setup_command import BuildDoc
    BUILD_SPHINX_AVAILABLE = True
except ImportError:
    BUILD_SPHINX_AVAILABLE = False
import neorg
from neorg.verutils import current_version

current_version()  # make sure current version is a valid version

data_list = ['schema.sql', 'templates/*.html'] + [
    os.path.join('%s' % d, '*.%s' % e)
    for e in ['css', 'html', 'ico', 'inv', 'js', 'png', 'txt']
    for d in ['static', 'static/help',
              'static/help/_source', 'static/help/_static',]]


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


class my_build(build):

    def has_help_doc(self):
        help_source = os.path.join('doc', 'source')
        if os.path.exists(help_source):
            return True
        else:
            log.info("'%s' does not exist. do not run update_help."
                     % help_source)
            return False

    sub_commands = [  # run update_help before any other sub_commands
        ('update_help', has_help_doc),
        ] + build.sub_commands


class update_help(Command):
    description = 'Copy document to neorg/static/help'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sphinx_build_dir = os.path.join("doc", "build")
        sphinx_source_static_dir = os.path.join("doc", "source", "_static")

        # build directory is needed to be created before running build_sphinx
        mkdir(sphinx_build_dir)
        # suppress sphinx warning
        mkdir(sphinx_source_static_dir)
        # run build_sphinx before copying
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        sphinx_html_dir = os.path.join(sphinx_build_dir, 'html')
        static_help = os.path.join('neorg', 'static', 'help')
        if os.path.exists(sphinx_html_dir):
            if os.path.exists(static_help):
                shutil.rmtree(static_help)
            log.info("copying '%s' to '%s'" % (sphinx_html_dir, static_help))
            shutil.copytree(sphinx_html_dir, static_help)
        else:
            log.warn("'%s' does not exists. '%s' is not updated"
                     % (sphinx_html_dir, static_help))

    def has_sphinx(self):
        if BUILD_SPHINX_AVAILABLE:
            return True
        else:
            log.warn("sphinx is not available. do not run build_sphinx.")
            return False

    sub_commands = [
        # Do not run build_sphinx if is not available
        ('build_sphinx', has_sphinx),
        ]


class update_js(Command):
    description = 'Download and extract javascripts to neorg/static/js'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def _saveurl(url, filepath):
        from urllib2 import urlopen
        if os.path.exists(filepath):
            log.info("file '%s' already exists" % filepath)
        else:
            log.info("downloading '%s' -> '%s'" % (url, filepath))
            file(filepath, 'wb').write(urlopen(url).read())

    @classmethod
    def _saveurl_and_extract_zip(cls, url, zippath, dirpath):
        from zipfile import ZipFile
        cls._saveurl(url, zippath)
        zf = ZipFile(zippath)
        zf.extractall(dirpath)

    def run(self):
        from distutils.dir_util import mkpath, copy_tree
        from distutils.file_util import copy_file
        tmpdir = os.path.join('build', 'jstmp')
        jsdir = os.path.join('neorg', 'static', 'jslib')
        colorboxdir = os.path.join(jsdir, 'colorbox')
        jqtmppath = os.path.join(tmpdir, 'jquery-1.6.4.min.js')
        cbjstmppath = os.path.join(
            tmpdir, 'colorbox', 'colorbox', 'jquery.colorbox-min.js')
        cbcsstmppath = os.path.join(
            tmpdir, 'colorbox', 'example5', 'colorbox.css')
        cbimgtmppath = os.path.join(
            tmpdir, 'colorbox', 'example5', 'images')
        cbimglibpath = os.path.join(colorboxdir, 'images')

        if os.path.exists(jsdir):
            shutil.rmtree(jsdir)
            log.info("clear directory '%s'" % jsdir)
        mkpath(colorboxdir)  # which is under jsdir

        mkpath(tmpdir)
        if os.path.exists(os.path.join(tmpdir, 'colorbox')):
            shutil.rmtree(os.path.join(tmpdir, 'colorbox'))

        self._saveurl(
             'http://code.jquery.com/jquery-1.6.4.min.js', jqtmppath)
        copy_file(jqtmppath, jsdir)

        self._saveurl_and_extract_zip(
            'http://colorpowered.com/colorbox/latest',
            os.path.join(tmpdir, 'colorbox.zip'),
            tmpdir)
        copy_file(cbjstmppath, jsdir)
        copy_file(cbcsstmppath, colorboxdir)
        copy_tree(cbimgtmppath, cbimglibpath)


cmdclass = {
    'build': my_build,
    'update_help': update_help,
    'update_js': update_js,
    }
if BUILD_SPHINX_AVAILABLE:
    cmdclass.update(build_sphinx=BuildDoc)

setup(
    name='neorg',
    version=neorg.__version__,
    packages=['neorg', 'neorg.tests'],
    package_data={
        'neorg': data_list,
        'neorg.tests': ['texts/*.txt'],
        },
    description='NEOrg - Numerical Experiment Organizer',
    long_description=neorg.__doc__,
    author=neorg.__author__,
    author_email='aka.tkf@gmail.com',
    url='https://bitbucket.org/tkf/neorg',
    keywords='numerical simulation, research',
    license=neorg.__license__,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        ],
    entry_points = {
        'console_scripts': ['neorg = neorg.commands:main']},
    command_options={
        'build_sphinx': {  # specify the help document
            'source_dir': ('setup.py', 'doc/source/'),
            'build_dir': ('setup.py', 'doc/build/'),
            },
        },
    cmdclass=cmdclass,
    install_requires=[
        'docutils',
        'Flask',
        'argparse',
        'Whoosh',
    ],
    )
