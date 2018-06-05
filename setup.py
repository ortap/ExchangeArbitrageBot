#!/usr/bin/env python
from setuptools import setup

setup(name='theocean_python',
      version='0.0.1',
      description='',
      classifiers=[
        'Programming Language :: Python :: 3.6',
      ],
      url='https://gitlab.the0cean.net/shailesh/ExchangeArbitrageBot',
      author='Shailesh',
      author_email='shailesh@theocean.trade',
      license='MIT',
      packages=['exchangearbitragebot'],
      install_requires=[
          'web3',
          'requests',
          'urllib3'
      ],
      zip_safe=False)
