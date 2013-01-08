#!/usr/bin/python2

from distutils.core import setup

setup(name='blivet', version='0.1',
      description='Python module for working with system storage',
      author='David Lehman', author_email='dlehman@redhat.com',
      url='http://fedoraproject.org/wiki/blivet',
      packages=['blivet', 'blivet.devicelibs', 'blivet.formats'])
