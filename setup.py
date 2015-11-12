from setuptools import setup, find_packages
from pkg_resources import parse_version
from warnings import warn

with open('pdf_parser/VERSION') as f:
    version = parse_version(f.read().strip())

with open('README.md', encoding='utf8') as f:
    long_description = f.read()

url = 'https://github.com/ajmarks/pdf_parser/'
requires = ['Pillow>=2.7', 'numpy>=1.0', 'bidict>=0.9']
classifiers = ['Development Status :: 3 - Alpha',
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

setup(name='pdf_parser',
      packages=['pdf_parser'],#find_packages(exclude=['tests']),
      version=version,
      author='Andrew Marks',
      author_email='ajmarks@gmail.com',
      url=url,
      download_url=url+'/tarball/'+version,
      keywords=['pdf', 'acrobat'],
      install_requires=requires,
      description='PDF document parser in Python 3',
      classifiers=classifiers
      )