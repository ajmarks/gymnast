"""
Let's make this into a nice package
"""

#Because Windows
import os
del os.link

from setuptools import setup, find_packages
from pkg_resources import parse_version

with open('gymnast/VERSION') as f:
    VERSION = parse_version(f.read().strip()).public

README = 'README.md'
try:
    from pypandoc import convert
    LONG_DESCRIPTION = convert(README, 'rst', 'md')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    with open(README, 'r') as f:
        LONG_DESCRIPTION = f.read()


NAME = 'gymnast'
URL = 'https://github.com/ajmarks/gymnast/'
REQUIRES = ['bidict>=0.9', 'six>=1.0']
KEYWORDS = ['pdf', 'acrobat']
LICENSE  = 'MIT License'
CLASSIFIERS = ['Development Status :: 3 - Alpha',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: MIT License',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3 :: Only',
               'Programming Language :: Python :: 3.3',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.5',
               'Topic :: Text Processing',
               'Topic :: Utilities']
PACKAGES = find_packages(exclude=['tests'])

setup(name=NAME,
      packages=PACKAGES,
      version=VERSION,
      author='Andrew Marks',
      author_email='ajmarks@gmail.com',
      license=LICENSE,
      url=URL,
      download_url=URL+'tarball/'+VERSION,
      keywords=KEYWORDS,
      install_requires=REQUIRES,
      description='Gymnast: PDF document parser in Python 3',
      classifiers=CLASSIFIERS,
      include_package_data=True,
      long_description=LONG_DESCRIPTION,
     )
