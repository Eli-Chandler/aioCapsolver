import codecs
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2'
DESCRIPTION = 'Async API wrapper for capsolver.com'
LONG_DESCRIPTION = 'An asynchronous API wrapper for capsolver.com, built to be reliable and versatile.'

# Setting up
setup(
    name="aiocapsolver",
    version=VERSION,
    author="Eli Chandler",
    author_email="eli.chandler@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['aiofiles', 'aiohttp', 'aiosignal', 'async-timeout', 'attrs', 'build', 'charset-normalizer', 'colorama', 'filelock', 'frozenlist', 'idna', 'multidict', 'packaging',
                      'platformdirs', 'pyproject-hooks', 'tomli', 'uritools', 'urlextract', 'urllib3', 'yarl'],
    keywords=['python', 'captcha', 'solver', 'capsolver', 'api', 'wrapper'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
