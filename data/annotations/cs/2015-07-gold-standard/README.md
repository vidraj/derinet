# Gold standard data

## Description

This data was created in 2015 by Jonáš Vidra (`devel` and `eval1`) and Kristýna Merthová (`eval2`) to evaluate progress by measuring precision and recall. There is a private fourth dataset annotated by Pavla Wernerová. The data for `devel` was sampled from an unreleased pre-version of DeriNet 1.0, so it contains lemmas from MorfFlex, but the lemma set doesn't exactly correspond to any version. Data for `eval1` and `eval2` is from DeriNet 1.0. Annotation was done by manually specifying the subjectively best parent for each lemma without consulting DeriNet or any other resource.

See [Extending the Lexical Network DeriNet (Vidra, 2015)](https://is.cuni.cz/webapps/zzp/detail/165563/) for details.

To measure precision and recall using this data, use the `derimor` module called `MeasurePrecisionRecall` like this:
```shell-session
$ derimor Load file=derinet.tsv MeasurePrecisionRecall file=annot-devel.tsv >stats.txt 2>error.log
```

## Data format

The data is in tab-separated values table.

1. The first column contains the lemma that is being annotated.
2. The second column contains its part-of-speech tag.
3. The third column contains the annotations. The format is as follows:
   * A dash marks a lemma without a parent (an ultimate tree root).
   * Some lemmas can be marked as unannotated by a question mark – these are considered to be correct, but the parent was not determinable by the annotators.
   * An exclamation mark is used to annotate bad lemmas.
   * A parent is referenced by its lemma.
   * Multiple parents are delimited by commas (regexp /,\s*/). If one of them is the preferred parent, it is the first one. There doesn't have to be a preferred parent.
   * Compounds are annotated by separating the multiple parents by spaces.
