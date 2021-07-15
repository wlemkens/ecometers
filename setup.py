# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ecometers',
    version='0.1.0',
    description='Python package for reading the Eco Meter S tank level sensor',
    long_description=readme,
    author='Wim Lemkens',
    author_email='wim.lemkens@gmail.com',
    url='https://github.com/wlemkens/ecometers',
    license=license,
    packages=find_packages()
)