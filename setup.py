# coding=utf-8
from setuptools import setup

setup(
    name='corefgraph',
    version='1.2.3',
    author='Josu Bermudez, Rodrigo Agerri',
    author_email="josu.bermudez@deusto.es, rodrigo.agerri@ehu.es",
    license='Apache License Version 2.0',
    packages=['corefgraph',
              'corefgraph.graph',
              'corefgraph.output',
              'corefgraph.process',
              'corefgraph.properties',
              'corefgraph.resources',
              'corefgraph.resources.files',
              'corefgraph.resources.languages',
              'corefgraph.resources.languages.en',
              'corefgraph.resources.languages.en.animate',
              'corefgraph.resources.languages.en.demonym',
              'corefgraph.resources.languages.en.gender',
              'corefgraph.resources.languages.en.number',
              'corefgraph.resources.languages.es',
              'corefgraph.resources.languages.es.animate',
              'corefgraph.resources.languages.es.demonym',
              'corefgraph.resources.languages.es.gender',
              'corefgraph.resources.languages.es.number',
              'corefgraph.resources.tagsets',
              'corefgraph.resources.tagsets.conll',
              'corefgraph.resources.tagsets.semeval_es',
              'corefgraph.resources.tagsets.standford',
              'corefgraph.resources.tagsets.penntreebank',
              'corefgraph.multisieve',
              'corefgraph.multisieve.features',
              'corefgraph.multisieve.sieves',
              'corefgraph.multisieve.catchers',
              'corefgraph.multisieve.filters',
              'corefgraph.multisieve.purges',
              ],
    package_data={
        "corefgraph.properties": ["logging.yaml"],
        "corefgraph.resources.languages.en.animate": ["*.txt"],
        "corefgraph.resources.languages.en.demonym": ["*.txt"],
        "corefgraph.resources.languages.en.gender": ["*.txt"],
        "corefgraph.resources.languages.en.number": ["*.txt"],
        "corefgraph.resources.languages.es.animate": ["*.txt"],
        "corefgraph.resources.languages.es.demonym": ["*.txt"],
        "corefgraph.resources.languages.es.gender": ["*.txt"],
        "corefgraph.resources.languages.es.number": ["*.txt"],
    },

    url='https://bitbucket.org/josu/corefgraph/',
    download_url='https://bitbucket.org/Josu/corefgraph//get/default.tar.gz',

    description='Module to resolve intra-document coreference.',
    long_description=open('LONG.rst').read(),
    install_requires=[
        'lxml',
        'networkx',
        'pynaf',
        'pycorpus',
        'PyYAML',
        'configargparse'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: Spanish", 
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"],
    entry_points={
        'console_scripts': [
            'corefgraph=corefgraph.process.file:main',
            'corefgraph_corpus=corefgraph.process.corpus:main']
    }
)
