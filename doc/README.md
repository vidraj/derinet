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

Building the Czech DeriNet
--------------------------

Run `make` in the [tools/build/cs](../tools/build/cs) directory.

TODO Specify dependencies, requirements, environment setup.

Using the APIs and tools, writing new modules
---------------------------------------------

There are currently 3 different APIs in use when building DeriNet: The old Perl API `derimor`, the newer scriptable `derinet-python` API and the newest module-based `derinet2` API. For new applications, you should use the last one, `derinet2`.

### derimor

TODO

### derinet-python

TODO

### derinet2

TODO

Our advice for writing modules:

-   Make sure you return the modified database from the module.

-   Log all decisions using the `logging` module. Be more verbose than you think is necessary. Use the levels (`logger.info`, `.warning`, `.error`) appropriately.

-   Do not change the dictionary set by adding or removing lexemes. Our stance on this may change, but you should just log the required changes and merge them at the very beginning of the pipeline, because each such change is very serious. We strive to be as compatible with the MorfFlex CZ dictionary as possible, so these changes should be reported to MorfFlex CZ developers anyway.

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
