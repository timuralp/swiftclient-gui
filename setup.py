#!/usr/bin/python

from setuptools import setup

setup(name='swiftclient-gui',
      version='0.0.1',
      test_suite='nose.collector',
      url='https://github.com/timuralp/swiftclient-gui',
      packages=['swiftclient_gui'],
      entry_points={
          'gui_scripts': [
              'swiftclient-gui = swiftclient_gui.__main__:main'
          ],
      })
