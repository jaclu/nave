#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup for the nave-public Django Application."""
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from nave.common import version
version = version.__version__

if sys.argv[-1] == 'publish':
    try:
        import wheel
        print('Wheel version: ', wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run `pip install wheel`')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print('Tagging the version on git:')
    os.system('git tag -a %s -m "version %s"' % (version, version))
    os.system('git push --tags')
    sys.exit()

readme = open('README.md').read()
# history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='nave-public',
    version=version,
    description="""Nave LoD platform""",
    long_description=readme,  # + '\n\n' + history,
    author='Sjoerd Siebinga',
    author_email='sjoerd@delving.eu',
    url='https://github.com/delving/nave',
    packages=[
        'nave',
    ],
    include_package_data=True,
    install_requires=[],
    license='BSD 3-Clause License',
    zip_safe=False,
    keywords='nave-public',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        'Framework :: flask :: 0.12',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
