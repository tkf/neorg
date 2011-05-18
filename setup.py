from setuptools import setup
import neorg

setup(
    name='neorg',
    version=neorg.__version__,
    packages=['neorg'],
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
