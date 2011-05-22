from setuptools import setup
from distutils.command.build import build
from distutils.cmd import Command
import os
import shutil
import neorg

data_list = ['schema.sql', 'templates/*.html'] + [
    os.path.join('%s' % d, '*.%s' % e)
    for e in ['css', 'html', 'ico', 'inv', 'js', 'png', 'txt']
    for d in ['static', 'static/help',
              'static/help/_source', 'static/help/_static',]]


class my_build(build):
    sub_commands = [  # run update_help before any other sub_commands
        ('update_help', lambda _: True),
        ] + build.sub_commands


class update_help(Command):
    description = 'Copy document to neorg/static/help'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # run build_sphinx before copying
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        sphinx_build_dir = 'doc/build/html'
        static_help = 'neorg/static/help'
        if os.path.exists(static_help):
            shutil.rmtree(static_help)
        print "copying '%s' to '%s'" % (sphinx_build_dir, static_help)
        shutil.copytree(sphinx_build_dir, static_help)

    sub_commands = [
        ('build_sphinx', lambda _: True),
        ]


# build directory is needed to be created before running build_sphinx
if not os.path.exists("doc/build"):
    os.mkdir("doc/build")


setup(
    name='neorg',
    version=neorg.__version__,
    packages=['neorg'],
    package_data={
        'neorg': data_list},
    description='NEOrg - Numerical Simulation Organizer',
    long_description=neorg.__doc__,
    author=neorg.__author__,
    author_email='aka.tkf@gmail.com',
    url='https://bitbucket.org/tkf/neorg',
    keywords='numerical simulation, research',
    license=neorg.__license__,
    classifiers=[
        "Development Status :: 1 - Planning",
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
    cmdclass={
        'build': my_build,
        'update_help': update_help,
        },
    )
