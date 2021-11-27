from setuptools import setup
from setuptools.command.install import install
from sys import prefix

from masterArtistMerger import masterArtistMerger
from masterArtistNameDB import masterArtistNameDB

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        mam = masterArtistMerger(install=True)
        mandb = masterArtistNameDB("main", install=True)
        mandb = masterArtistNameDB("multi", install=True)
        

setup(
  name = 'musicnames',
  py_modules = ['masterArtistNameDB', 'masterArtistNameCorrection', 'masterArtistMerger', 'findMergerData'],
  version = '0.0.1',
  cmdclass={'install': PostInstallCommand},    
  data_files = [],
  description = 'A Python Wrapper for Musicnames Data',
  long_description = open('README.md').read(),
  author = 'Thomas Gadfort',
  author_email = 'tgadfort@gmail.com',
  license = "MIT",
  url = 'https://github.com/tgadf/musicnames',
  keywords = ['Musicnames', 'music'],
  classifiers = [
    'Development Status :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
  install_requires=['jupyter_contrib_nbextensions'],
  dependency_links=['git+ssh://git@github.com/tgadf/utils.git#egg=utils-0.0.1', 'git+ssh://git@github.com/tgadf/multiartist.git#egg=multiartist-0.0.1', 'git+ssh://git@github.com/tgadf/musicdb.git#egg=musicdb-0.0.1']
)