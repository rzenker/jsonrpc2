from setuptools import setup, find_packages
import os
here = os.path.dirname(__file__)
readme = open(os.path.join(here, "README")).read()
example = open(os.path.join(here, "rpc_example.txt")).read()
changelog = open(os.path.join(here, "ChangeLog")).read()
version="0.3.2"

tests_require = [
    "Nose",
    "WebTest",
    "simplejson",
]

setup(
    name="jsonrpc2",
    description="WSGI Framework for JSON RPC 2.0",
    long_description=readme + "\n" + example + "\n" + changelog,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
    author='Atsushi Odagiri',
    author_email='aodagx@gmail.com',
    keywords='wsgi request web http json rpc',
    license="MIT",
    url='http://hg.aodag.jp/jsonrpc2/',
    version=version,
    install_requires=[
    ],
    include_package_data=True,
    test_suite="nose.collector",
    tests_require=tests_require,
    extras_require={
        "PASTE":[
            "PasteScript",
        ],
        "test":tests_require,
    },
    packages=find_packages(exclude=['tests']),
    entry_points={
        "console_scripts":[
            "runjsonrpc2=jsonrpc2.cmd:main",
        ],
        "paste.app_factory":[
            "main=jsonrpc2.paste:make_app",
        ],
        "paste.paster_create_template":[
            "paster_jsonrpc2=jsonrpc2.paste.templates:JsonRpcTemplate",
        ],
    },
)

