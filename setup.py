"""
Let's make this into a nice package
"""

from setuptools import setup
from pkg_resources import parse_version

with open('pdf_parser/VERSION') as f:
    VERSION = parse_version(f.read().strip())

with open('README.rst', encoding='utf8') as f:
    LONG_DESCRIPTION = f.read()

NAME = 'pdf_parser'
URL = 'https://github.com/ajmarks/pdf_parser/'
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
PACKAGES = find_packages(where='pdf_parser')

setup(name=NAME,
      packages=PACKAGES,
      version=VERSION,
      author='Andrew Marks',
      author_email='ajmarks@gmail.com',
      license=LICENSE,
      url=URL,
      download_url=URL+'/tarball/'+VERSION,
      keywords=KEYWORDS,
      install_requires=REQUIRES,
      description='PDF document parser in Python 3',
      classifiers=CLASSIFIERS,
      include_package_data=True,
     )
