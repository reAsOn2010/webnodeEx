# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
from webnodeex import __version__

setup(
    name='webnodeex',
    version=__version__,
    description='webnode Ex',
    long_description=open('README.rst').read(),
    url='https://github.com/reAsOn2010/webnodeEx',
    author='reAsOn2010',
    author_email='the.reason.sake@gmail.com',
    license='MIT License',
    keywords='webnode',
    packages=find_packages(exclude=['docs', 'tests*']),
    zip_safe=False,
    install_requires=[
        'tornado',
    ]
)
