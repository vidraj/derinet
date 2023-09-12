# DeriNet

DeriNet is a network of Czech derivational relations. This repository contains tools that are needed to build it from the base set of lemmas, annotations used in the process, auxiliary scripts and the released versions.

The homepage of the project can be found at [https://ufal.mff.cuni.cz/derinet](https://ufal.mff.cuni.cz/derinet).

Released versions are stored in [data/releases/cs/](data/releases/cs/) and can be searched
online using [DeriSearch](https://quest.ms.mff.cuni.cz/derisearch2/v2/databases/).


# The Build System

The DeriNet network is built out of a combination of automatic and
manual annotations, starting from a lexicon taken mostly from
[the MorfFlex CZ project](https://ufal.mff.cuni.cz/morfflex). Each
new version builds on top of the old ones, and the directory
structure mostly reflects this, with one directory for the build
scripts for each new version.

To keep the ability to fix old mistakes at the source (in the
annotations themselves), the network can be rebuilt from scratch when
creating a new version, building fixed equivalents of old versions to
use as the basis for new ones. All versions are tied together by
recursive Makefiles, starting with the one at
[tools/build/cs/Makefile](tools/build/cs/Makefile).

As a result, there are multiple build systems in use, reflecting
historical development of the code, since the code to create old
versions is seldom updated to newer APIs and methods.


## The DerivMorpho API (Deprecated)

The older Perl DerivMorpho API is used to build DeriNet 0.9 through 1.3
and resides in [tools/data-api/perl-derivmorpho/](tools/data-api/perl-derivmorpho/). Its modular system
was inspired by [Treex](https://ufal.mff.cuni.cz/treex). The main
runner, [tools/data-api/perl-derivmorpho/derimor](tools/data-api/perl-derivmorpho/derimor), is invoked with a
list of arguments describing the modules, their arguments and data
files to use, it invokes the modules one after the other and passes the
constructed network to each one.

All code, modules, annotation files and intermediate build files used
by DerivMorpho are stored under the API dir.

There were two intermediate Python API versions, which are no longer
used for building the network itself, but may still be referenced by
various experiments checked into the repository.


## The DeriNet API (Current)

The newer Python DeriNet API is located in [tools/data-api/derinet2/](tools/data-api/derinet2/)
and it is used to build versions starting with 1.3 (which was partially
built in Perl and partially in Python). With that version, the
repository structure was redone. Newer annotations are stored in
[data/annotations/cs/](data/annotations/cs/), modules in the API dir under
[tools/data-api/derinet2/derinet/modules/](tools/data-api/derinet2/derinet/modules/) and build artifacts in
[tools/build/cs/](tools/build/cs/), where the main Makefile is.

The newer API keeps the modular approach of the old one, but threads
the modules in a slightly different way, especially wrt. parameter
parsing. See [tools/data-api/derinet2/README.md](tools/data-api/derinet2/README.md) for some info.

A thorough hands-on walkthrough for the new API can be found in the
following Google Colab documents:
1. [Introduction to the API and its methods](https://colab.research.google.com/drive/1so-LDMNDghtZw68eG5VT2WdJoD-0Se9f?usp=sharing)
2. [Writing new modules](https://colab.research.google.com/drive/1ZU6zc8q4MSthENcAefQb7-rMl_YMwIXE?usp=sharing)
3. [A simple example of using the API for searching the data](https://colab.research.google.com/drive/1lQdYJb_70A2eiVfaFEdPzOoHS8ZvgeF4?usp=sharing)
