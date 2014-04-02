from setuptools import setup, find_packages
from xymon import __version__ as package_version


with open('README.rst') as doc:
    long_description = doc.read()

setup(
    name = "Xymon",
    author = 'Rob McBroom',
    author_email = 'pypi [at] skurfer.com',
    url = 'https://github.com/skurfer/python-xymon',
    license = "Don't Be a Dick",
    packages = ['xymon'],
    version = package_version,
    description = 'Update and query statuses on a Xymon server',
    long_description = long_description,
    install_requires = [],
)
