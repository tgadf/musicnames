from distutils.core import setup
import setuptools
import pkg_resources
import os
import sys
from shutil import copyfile
from setuptools.command.install import install

        
class InstallWrapper(install):

  def run(self):
    # Run this first so the install stops in case 
    # these fail otherwise the Python package is
    # successfully installed
    self._copy_web_server_files()
    # Run the standard PyPi copy
    install.run(self)

  def _copy_web_server_files(self):
    ext = "yaml"
    # Check to see we are running as a non-prv
    targetFile = os.path.join(sys.prefix, 'musicnames', 'mainDBRenames.{0}'.format(ext))
    localFile  = "mainDBRenames.{0}".format(ext)
    print("===> Copying [{0}] to [{1}] to avoid overwritting the subsequent reverse copy".format(targetFile, localFile))
    copyfile(src=targetFile, dst=localFile)
    
setup(
  name = 'musicnames',
  py_modules = ['masterArtistNameDB'],
  version = '0.0.1',
  data_files = [(os.path.join(sys.prefix, 'musicnames'), ['mainDBRenames.yaml'])],
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
  install_requires=['utils==0.0.1', 'multiartist==0.0.1', 'musicdb==0.0.1', 'matchAlbums==0.0.1', 'jupyter_contrib_nbextensions'],
  dependency_links=['git+ssh://git@github.com/tgadf/utils.git#egg=utils-0.0.1', 'git+ssh://git@github.com/tgadf/multiartist.git#egg=multiartist-0.0.1', 'git+ssh://git@github.com/tgadf/musicdb.git#egg=musicdb-0.0.1']
)
 
