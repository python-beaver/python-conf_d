#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conf_d import __version__

try:
    from setuptools import setup
    setup  # workaround for pyflakes issue #13
except ImportError:
    from distutils.core import setup

# Hack to prevent stupid TypeError: 'NoneType' object is not callable error on
# exit of python setup.py test # in multiprocessing/util.py _exit_function when
# running python setup.py test (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
    multiprocessing
except ImportError:
    pass


setup(
    name='conf_d',
    version=__version__,
    author='Jose Diaz-Gonzalez',
    author_email='conf_d@josediazgonzalez.com',
    packages=['conf_d'],
    url='http://github.com/josegonzalez/conf_d',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description='read configuration files, conf.d style',
    long_description=open('README.rst').read() + '\n\n' +
                open('CHANGES.rst').read(),
    tests_require=['nose'],
    test_suite='nose.collector',
    install_requires=[],
)
