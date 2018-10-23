#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()
with open('requirements.txt', 'r') as f:
    requirements = f.read().split()

setup(name='python_grpc_tracing',
      version='0.1.1',
      description='Python gRPC jaeger tracing Interceptors',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Liu Chongliang',
      author_email='kjlcl@163.com',
      url="https://github.com/kjlcl/python-grpc-tracing",
      install_requires=requirements,
      license='MIT',
      packages=find_packages(exclude=["tests"]),
      )
