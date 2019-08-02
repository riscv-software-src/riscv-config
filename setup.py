import os
import codecs
import pip
from setuptools import setup, find_packages

import rifle

# Base directory of package
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


#Long Description
with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(name="rifle",
      version=rifle.__version__,
      description="RISC-V Featrue Legalizer by Incoresemi Ltd.",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python :: 3.7",
          "License :: OSI Approved :: BSD License",
          "Development Status :: 4 - Beta"
      ],
      url='https://gitlab.com/incoresemi/rifle',
      author='InCore Semiconductors Pvt. Ltd.',
      author_email='neelgala@incoresemi.com',
      license='BSD-3-Clause',
      packages=find_packages(),
      install_package_data=True,
      package_dir={'rifle': 'rifle/'},
      package_data={'rifle': ['schemas/*']},
      install_requires=['Cerberus>=1.3.1', 'ruamel.yaml>=0.16.0'],
      python_requires=">=3.7.0",
      entry_points={
          "console_scripts": ["rifle=rifle.main:main"],
      })
