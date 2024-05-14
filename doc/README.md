Documentation of the DeriNet build system and related tools
===========================================================

The DeriNet build system is designed to create the DeriNet database of Czech lexical derivations by adding derivational relations from hand-annotated files to a list of lexemes, saving the result to a file.

<!-- This documentation file describes the output file format,  -->
File formats
------------

The file formats differ between the older 0.x and 1.x versions, and the upcoming 2.x releases. Both of them are text/tab-separated-values files, but the new format is much more flexible, contains more information and requires more care while both parsing and producing it.

Both formats are distributed as optionally-gzipped plain text files in the UTF-8 character encoding, with no byte-order mark and with Unix newlines (ASCII LF). They are designed to be easily processible with standard Unix utilities and spreadsheet applications.

### Old 0.x and 1.x format

The old format is a simple TSV with five columns. Each line describes a single lexeme in the database. The columns are, in order:

1.  ID
    An unsigned integer that uniquely identifies the lexeme in the database.

    Be aware that it does not work as an identifier across versions and that the IDs need not be sorted, or indeed form a contiguous sequence.

2.  Lemma
    A string containing the textual representation of the base form of the lexeme.

3.  Techlemma
    An internal representation of the lexeme in the MorfFlex CZ dictionary. It is used mostly for interop and you should treat it as an implementation detail. That said, the technical suffixes do contain some useful information. This column should be left empty in languages which do not have comparable information to include.

4.  Part of speech tag
    A single letter denoting the part-of-speech (POS) of the lexeme. It can have the following four values:

    -   A: Adjective
    -   D: Adverb
    -   N: Noun
    -   V: Verb

    Other classes are not considered, as DeriNet is built on content words only. This limitation will be removed in the new format.

    Since version 1.4, the POS tag position is also used to annotate compound words, i.e. words with more than one formal predecessor. This is done by appending the letter “C” to the POS tag, resulting in a two-character tag. The lexemes which make up the compound are not specified – the only recorded information is a boolean value specifying the process responsible for creating the lexeme.

5.  Parent ID
    The numerical ID of the lexeme’s derivational parent, i.e. the lexeme that this one was derived from. Refers to the first column.

### New 2.x format

See the description in [big-bang-derinet-2.0.txt](./big-bang-derinet-2.0.txt).

TODO write a correct, up-to-date version in English.

The DeriNet 2.0 database is stored in a TSV file format inspired by CONLL-U. The main structure of the file is still tree-based, but it can contain secondary edges, which can form general directed acyclic graphs, including multiple derivational parent options and compounding.

The file format can also store additional information, including morphological segmentation, relation labels and free-form JSON annotation.

The database file is divided into blocks separated by empty lines (two newlines). These blocks correspond to connected components formed by the primary edges.

Each line in a block describes a single lexeme in the following format,
with items separated by tabulators:

| ID | LEMID | LEMMA | POS | FEATS | SEGMENTATION | PARENTID | RELTYPE | OTHERRELS | JSON |
| -- | ----- | ----- | --- | ----- | ------------ | -------- | ------- | --------- | ---- |
| 187300.1047 | vybrat#V????--??-??P?? | vybrat | VERB | ConjugClass=1&Loanword=False | End=2&Morph=vy&Start=0&Type=Prefix&#124;End=4&Morph=br&Start=2&Type=Root&#124;End=5&Morph=a&Start=4&Type=Suffix&#124;End=6&Morph=t&Start=5&Type=Suffix | 187300.1 | Type=Derivation |  | {"corpus_stats": {"absolute_count": 726762, "percentile": 99.95177823764378, "relative_frequency": 0.0002899462472670399, "sparsity": 3.537682507890981}, "techlemma": "vybrat"} |

1.  ID
    A dot-separated pair of integers. The former identifies the tree in the file, the latter identifies the lexeme in the tree.

2.  LEMID
    A mostly-unique reference to a lexeme that should be stable between
    versions. It is possible for homonyms to share an identical lemid
    under some (undesirable but also largely unavoidable) circumstances.
    The lemids are generated as tag masks by looking at all inflectional
    positional tags listed for inflectional forms of the lexeme in the
    MorfFlex lexicon, copying the positions where all forms share the
    same value and replacing the varying positions with question marks
    (`?`).

3.  LEMMA
    The lemma of the lexeme. In (non-Czech) datasets where lemmatization
    is not available or not desirable, this will be the word form, with
    the actual lemma optionally present in the FEATS.

4.  POS
    The part-of-speech tag from the [Universal POS Tag inventory](https://universaldependencies.org/u/pos/index.html).

5.  FEATS
    Morphological features of the lexeme.
    TODO Document the format.

6.  SEGMENTATION
    Morphological / morphematical segmentation of the lexeme. The main
    unit of the segmentation is the morph, which refers to a nonempty
    contiguous subsequence of characters of LEMMA. This representation
    was chosen for simplicity rather than linguistic adequacy.
    TODO Document the format, further specify the pitfalls.

7.  PARENTID
    The ID of the main parent from the main relation of the lexeme.
    The graph formed by lexemes as linked by PARENTIDs is a forest
    (i.e. acyclic).

8.  RELTYPE
    Additional description of the relation to which PARENTID belongs,
    including potentially any other parents.

9.  OTHERRELS
    Relations that did not fit into the main PARENTID / RELTYPE pair.

    Conceptually, all the relations have the same importance and are
    contained in a single list. This list is then split, with the first
    element stored in PARENTID and RELTYPE and the rest listed here.
    This is because it enables us to use simple algorithms designed for
    trees to process the data. E.g. if you start from the roots and
    follow the main relations only, you are guaranteed to process each
    lexeme exactly once.

    NOTE: The OTERRELS are not yet implemented in the derinet2 API. The
    DeriSearch2 search engine does support them, though.

10. JSON
    General data in the JSON format. It may contain e.g. annotation not fitting elsewhere, debugging labels, authorship information or comments.

Building the Czech DeriNet
--------------------------

tl;dr:
1. Make sure you have GNU Make and core Unix utilities installed (you probably do).
2. Install Perl 5 and the dependencies listed in [tools/data-api/perl-derivmorpho/README](../tools/data-api/perl-derivmorpho/README).
3. Install Python 3.6 or newer and Pandas.
4. Run `make` in the [tools/build/cs](../tools/build/cs) directory.

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
[tools/build/cs/Makefile](../tools/build/cs/Makefile).

As a result, there are multiple build systems in use, reflecting
historical development of the code, since the code to create old
versions is seldom updated to newer APIs and methods.

Historically, not only the APIs, but also the format of the database
changed, with DeriNet 2.0 being the first one in the new format, and a
conversion to a different set of part-of-speech tags
([Universal POS tags](https://universaldependencies.org/u/pos/index.html)
instead of the old set of A, D, N and V) being performed in 2.0.5.

The build process starts in [tools/data-api/perl-derivmorpho/derinet09](../tools/data-api/perl-derivmorpho/derinet09),
where the MorfFlex lexicon is filtered and loaded into the API. This
early stage of the pipeline contains several important steps that are
frequently used to fix issues with later versions: Any changes to the
lexeme set should be applied here (this is not consistent, but it's
a good rule to follow) to ensure that later steps see all lexemes and do
not use lexemes which will get deleted.

It is possible to delete erroneous lexemes from MorfFlex by listing them
in [derinet09/lemmas-to-ignore.tsv](../tools/data-api/perl-derivmorpho/derinet09/lemmas-to-ignore.tsv),
and extra lexemes missing from there can be added to [derinet09/extra_words.txt](../tools/data-api/perl-derivmorpho/derinet09/extra_words.txt).
Phantom lexemes (a feature since v2.0) are also added at this stage.
Another important file of interest that is applied at the very beginning
of the pipeline is [derinet09/one_off_derivations.tsv](../tools/data-api/perl-derivmorpho/derinet09/one_off_derivations.tsv),
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


Using the APIs and tools, writing new modules
---------------------------------------------

There are currently 3 different APIs in use when building DeriNet: The old Perl API `derimor`, the newer scriptable `derinet-python` API and the newest module-based `derinet2` API. For new applications, you should use the last one, `derinet2`.

### derimor

The older Perl DerivMorpho API is used to build DeriNet 0.9 through 1.3
and resides in [tools/data-api/perl-derivmorpho/](../tools/data-api/perl-derivmorpho/). Its modular system
was inspired by [Treex](https://ufal.mff.cuni.cz/treex). The main
runner, [tools/data-api/perl-derivmorpho/derimor](../tools/data-api/perl-derivmorpho/derimor), is invoked with a
list of arguments (“the scenario”) describing the modules, their
arguments and data files to use, it invokes the modules one after the
other and passes the constructed network to each one.

All code, modules, annotation files and intermediate build files used
by DerivMorpho are stored under the API dir.

Documentation is available in [Vidra, 2015](http://hdl.handle.net/20.500.11956/81939).


### derinet-python

There were two intermediate Python API versions, which are still used
both for building the network itself and by various experiments checked
into the repository. These APIs don't use a modular system with
scenarios, but open-coded scripts tailored for each version. These are
used to build DeriNet versions 1.3 (partially built using DerivMorpho)
through 1.7.

Starting with version 1.3, the repository structure was redone. Newer
annotations are supposed to be stored in [data/annotations/cs/](../data/annotations/cs/),
modules in the API dir under [tools/data-api/derinet2/derinet/modules/](../tools/data-api/derinet2/derinet/modules/)
and build artifacts in [tools/build/cs/](../tools/build/cs/), where the
main Makefile is. Note that this division is not always respected and
some data is still found in the build dirs as well.

No documentation of the APIs is provided.


### derinet2

The newer Python DeriNet API is located in [tools/data-api/derinet2/](../tools/data-api/derinet2/)
and it is used to build versions starting with 2.0. It can load data in
the old file format, but defaults to using the new one.

The API keeps the modular approach of the Perl DerivMorpho, but threads
the modules in a slightly different way, especially wrt. parameter
parsing. See [tools/data-api/derinet2/README.md](../tools/data-api/derinet2/README.md) for some info.

A thorough hands-on walkthrough for the new API can be found in the
following Google Colab documents:
1. [Introduction to the API and its methods](https://colab.research.google.com/drive/1so-LDMNDghtZw68eG5VT2WdJoD-0Se9f?usp=sharing)
2. [Writing new modules](https://colab.research.google.com/drive/1ZU6zc8q4MSthENcAefQb7-rMl_YMwIXE?usp=sharing)
3. [A simple example of using the API for searching the data](https://colab.research.google.com/drive/1lQdYJb_70A2eiVfaFEdPzOoHS8ZvgeF4?usp=sharing)


Our advice for writing modules:

-   Make sure you return the modified database from the module.

-   Log all decisions using the `logging` module. Be more verbose than you think is necessary. Use the levels (`logger.info`, `.warning`, `.error`) appropriately.

-   In Czech, do not change the dictionary set by adding or removing lexemes. Our stance on this may change, but you should just log the required changes and merge them at the very beginning of the pipeline, because each such change is very serious. We strive to be as compatible with the MorfFlex CZ dictionary as possible, so these changes should be reported to MorfFlex CZ developers anyway.

-   The output of each module must be deterministic. Therefore, whenever you choose from an unordered set of options, first order them according to some externally-defined criterion.


Creating annotation files
-------------------------

Generally, most derivational links and other information included in DeriNet are automatically generated and manually verified. We usually do this by

1.  preparing and running a custom script that reads the current DeriNet (usually only its lemma set) and outputs a list of candidate derivational pairs into a text file;
2.  manually confirming or rejecting the individual pairs in the text file, marking them as correct or incorrect;
3.  writing an API module that reads the annotated text file and adds the confirmed links to the database, and optionally deletes the rejected ones;
4.  writing a scenario that uses the module in conjunction with the annotation file and using that scenario to build a new version of the DeriNet database.

There are no strict guidelines for creating new annotation files. It is, of course, advisable to first look at the library of existing modules and reuse them if possible; but you can create your own format and modules that read and write it. You generally have to write the candidate extraction script anyway.

Some advice is:

-   The numerical IDs and techlemmas are not stable across versions. Do not rely on them as unique identifiers, they are not. Therefore, when selecting lexemes from the database, either use the plain lemma only or fall back to it when the techlemma is not found.

-   Take homonymy into account. A single lemma can be found in multiple lexemes, make sure you can distinguish them and cope with the inevitable collisions. Therefore, always include a part-of-speech tag in your annotation files; they can distinguish most cases of homonymy by themselves.

    More detailed treatment of homonymy may come in future versions. Due to the lack of usable permanent identifiers of lexemes, we do not treat homonymy beyond using the part-of-speech tag.

-   It is very useful if your annotation format distinguishes at least the following annotator decisions:

    1.  Accepted item, add to the database,
    2.  rejected item, do not add and optionally remove it,
    3.  unannotated item, do not process.

    Furthermore, the following may be useful in some situations:

    1.  Bad input (i.e. the words in the derivational pair are themselves wrong, so deciding on whether they are related is meaningless,
    2.  a free-form field that contains the correct decision – e.g. the correct derivational parent, if the automatically discovered candidate is not the right one.
    3.  a comment field detailing the reasons for the decision and/or a discussion about the issues.
