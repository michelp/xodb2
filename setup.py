#!/usr/bin/env python
"""
====
xodb
====

Development Version
-------------------

The hg `xodb tip`_ can be installed via ``easy_install xodb==dev``.

.. _xodb tip: http://bitbucket.org/pelletier_michel/xodb/get/tip.zip#egg=xodb-dev

"""
from setuptools import setup, find_packages

setup(
  name="xodb2",
  version="1.0.0",
  packages=find_packages(exclude=['tests.*', 'tests', '.virt']),

  tests_require=['nose', 'translitcodec'],
  test_suite='nose.collector',

  author='Michel Pelletier',
  author_email='pelletier.michel@yahoo.com',
  description='experimental xapian object database',
  long_description=__doc__,
  license='MIT License',
  url='https://github.com/michelp/xodb',
      install_requires=[
        'nilsimsa',
        ],
  classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        ],
)
