#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from setuptools import find_packages, setup


def get_file(*paths):
    path = os.path.join(*paths)
    try:
        with open(path, "rb") as f:
            return f.read().decode("utf8")
    except IOError:
        pass


def get_version():
    return "1.2.1"


def get_description():
    return "An async and updated version of the googletrans package."


def get_readme():
    return get_file(os.path.dirname(__file__), "README.md")


def get_requirements():
    return ["httpx>=0.23.0,<1.0.0"]


def install():
    setup(
        name="aiogtrans",
        version=get_version(),
        description=get_description(),
        long_description=get_readme(),
        long_description_content_type="text/markdown",
        license="MIT",
        author="Ben Z",
        author_email="bleg3ndary@gmail.com",
        url="https://github.com/Leg3ndary/aiogtrans",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Education",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Education",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
        ],
        packages=find_packages(exclude=["docs", "tests"]),
        keywords="google translate translator async",
        install_requires=get_requirements(),
        python_requires=">=3.9",
    )


if __name__ == "__main__":
    install()
