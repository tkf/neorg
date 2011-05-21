from setuptools import setup
from os import path
import neorg

data_list = ['schema.sql', 'templates/*.html'] + [
    path.join('%s' % d, '*.%s' % e)
    for e in ['css', 'html', 'ico', 'inv', 'js', 'png', 'txt']
    for d in ['static', 'static/help',
              'static/help/_source', 'static/help/_static',]]

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
    )
