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

Historically, not only the APIs, but also the format of the database
changed, with DeriNet 2.0 being the first one in the new format, and a
conversion to a different set of part-of-speech tags
([Universal POS tags](https://universaldependencies.org/u/pos/index.html)
instead of the old set of A, D, N and V) being performed in 2.0.5.


## The DerivMorpho API (Deprecated)

The older Perl DerivMorpho API is used to build DeriNet 0.9 through 1.3
and resides in [tools/data-api/perl-derivmorpho/](tools/data-api/perl-derivmorpho/). Its modular system
was inspired by [Treex](https://ufal.mff.cuni.cz/treex). The main
runner, [tools/data-api/perl-derivmorpho/derimor](tools/data-api/perl-derivmorpho/derimor), is invoked with a
list of arguments (“the scenario”) describing the modules, their
arguments and data files to use, it invokes the modules one after the
other and passes the constructed network to each one.

All code, modules, annotation files and intermediate build files used
by DerivMorpho are stored under the API dir.

Documentation is available in [Vidra, 2015](http://hdl.handle.net/20.500.11956/81939).


## The Intermediate Python APIs (Deprecated)

There were two intermediate Python API versions, which are still used
both for building the network itself and by various experiments checked
into the repository. These APIs don't use a modular system with
scenarios, but open-coded scripts tailored for each version. These are
used to build DeriNet versions 1.3 (partially built using DerivMorpho)
through 1.7.

Starting with version 1.3, the repository structure was redone. Newer
annotations are supposed to be stored in [data/annotations/cs/](data/annotations/cs/),
modules in the API dir under [tools/data-api/derinet2/derinet/modules/](tools/data-api/derinet2/derinet/modules/)
and build artifacts in [tools/build/cs/](tools/build/cs/), where the
main Makefile is. Note that this division is not always respected and
some data is still found in the build dirs as well.

No documentation of the APIs is provided.


## The DeriNet API (Current)

The newer Python DeriNet API is located in [tools/data-api/derinet2/](tools/data-api/derinet2/)
and it is used to build versions starting with 2.0. It can load data in
the old file format, but defaults to using the new one.

The API keeps the modular approach of the Perl DerivMorpho, but threads
the modules in a slightly different way, especially wrt. parameter
parsing. See [tools/data-api/derinet2/README.md](tools/data-api/derinet2/README.md) for some info.

A thorough hands-on walkthrough for the new API can be found in the
following Google Colab documents:
1. [Introduction to the API and its methods](https://colab.research.google.com/drive/1so-LDMNDghtZw68eG5VT2WdJoD-0Se9f?usp=sharing)
2. [Writing new modules](https://colab.research.google.com/drive/1ZU6zc8q4MSthENcAefQb7-rMl_YMwIXE?usp=sharing)
3. [A simple example of using the API for searching the data](https://colab.research.google.com/drive/1lQdYJb_70A2eiVfaFEdPzOoHS8ZvgeF4?usp=sharing)


## Major Steps in the Build System

The build process starts in [tools/data-api/perl-derivmorpho/derinet09](tools/data-api/perl-derivmorpho/derinet09),
where the MorfFlex lexicon is filtered and loaded into the API. This
early stage of the pipeline contains several important steps that are
frequently used to fix issues with later versions: Any changes to the
lexeme set should be applied here (this is not consistent, but it's
a good rule to follow) to ensure that later steps see all lexemes and do
not use lexemes which will get deleted.

It is possible to delete erroneous lexemes from MorfFlex by listing them
in [derinet09/lemmas-to-ignore.tsv](tools/data-api/perl-derivmorpho/derinet09/lemmas-to-ignore.tsv),
and extra lexemes missing from there can be added to [derinet09/extra_words.txt](tools/data-api/perl-derivmorpho/derinet09/extra_words.txt).
Phantom lexemes (a feature since v2.0) are also added at this stage.
Another important file of interest that is applied at the very beginning
of the pipeline is [derinet09/one_off_derivations.tsv](tools/data-api/perl-derivmorpho/derinet09/one_off_derivations.tsv),
which contains miscellaneous fixups and relations that should be added
early. Since later steps should generally not disconnect existing
relations (this rule is also not consistently followed, but should be –
erroneous relations should be fixed by amending their source annotation
files, not by fixing up later), adding the correct relation early should
block adding an incorrect one later, which is especially useful with
homonyms.

The handoff between the Perl and Python APIs happens in two steps.
First, the produced database conforming to the (old) TSV file format
is used as the basis for finalizing the build of 1.3 using Python.
Second, the information not present in this database (tag masks/lemids)
needed in 2.0 are pulled from an extended debugging file
`tools/data-api/perl-derivmorpho/derinet-1-3b.tsv` (not in the repo,
buildable only), which mostly uses the old file format, but contains
the extra information.

Corpus counts are only added in 2.0.5, so any modules requiring them
for statistical processing must run later in the build pipeline. This
version also changes the naming of the POS tags from `{A,D,N,V}` to
`{ADJ,ADV,NOUN,VERB}`.
