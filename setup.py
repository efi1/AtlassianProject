"""Minimal setup file for pythonMProject."""

from setuptools import find_packages, setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='pythonMProject',
    version='0.1.0',
    description='pythonMProject',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        "cfg.cfg_global": ["*.json"],
        "cfg.cfg_tests": ["*.json"]
    },

    # metadata
    author='Efi Ovadia',
    author_email='efovadia@gmail.com',
    license='proprietary',
    install_requires=[required, 'pytest']
)
