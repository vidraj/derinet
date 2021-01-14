# Explanation of common features

## Basic ones

- lemma
    The lemma of the lexeme.
    - open-class feature
- pos
    The part-of-speech category of the lexeme.
    - ADJ
    - ADV
    - NOUN
    - VERB
- id
    A technical ID identifying the lexeme in the particular version of the database.
    - open-class feature
- lemid
    A technical ID which should be more stable between versions of the resource and could be used to identify one lexeme across versions.
    - open-class feature


## FEATS

Features in the FEATS section mostly correspond to their identically-named counterparts from the Universal Features set, developed as part of [the Universal Dependencies project](https://universaldependencies.org/), but some are DeriNet-specific.

- feats/Animacy
    <https://universaldependencies.org/cs/feat/Animacy>
    Animacy of masculine nouns.
    - Anim (masculine animate gender)
    - Inan (masculine inanimate gender)
- feats/Aspect
    <https://universaldependencies.org/cs/feat/Aspect>
    Verbal aspect.
    - Imp (imperfective)
    - Perf (perfective)
- feats/ConjugClass
    DeriNet-specific.
    Verbal conjugation class according to the present tense ending (prézentní slovesná třída). Five classes are identified by numbers and cases where the verb has multiple possible conjugation classes are marked by listing all variants in a hash-mark-delimited list.
    - 1
    - 2
    - 3
    - 4
    - 5
    - 1#2
    - etc.
- feats/Fictitious
    DeriNet-specific.
    A common root of related lexemes which do not have a common ancestor in the synchronous language. Non-fictitious lexemes are identified by an absence of this feature. Contrast with misc/corpus_stats/absolute_count, marking existing but unattested lexemes.
    - Yes
- feats/Foreign
    <https://universaldependencies.org/cs/feat/Foreign>
    A literal word from another language used inside a text; not a loanword. Non-foreign lexemes are identified by an absence of this feature. Contrast with Loanword.
    - Yes
- feats/Gender
    <https://universaldependencies.org/cs/feat/Gender>
    Nominal gender.
    - Fem (feminine gender)
    - Masc (masculine gender; see also feats/Animacy)
    - Neut (neuter gender)
- feats/Loanword
    DeriNet-specific.
    Lexemes of foreign origin, i.e. lexemes whose ancestors are from another language. Contrast with Foreign.
    - False (the lexeme is natural or naturalized enough in the language)
    - True (the lexeme is of recent foreign origin)
- feats/NameType
    <https://universaldependencies.org/cs/feat/NameType.html>
    Type of a named entity.
    - Com (company or organization name)
    - Geo (geographical name)
    - Giv (given name of a person)
    - Nat (nationality)
    - Oth (other type of name, e.g. an event, band)
    - Pro (name of a product)
    - Prs (name of a person not classifiable as Giv or Sur)
    - Sur (surname of a person)
- feats/Poss
    <https://universaldependencies.org/cs/feat/Poss>
    Possessivity of adjectives.
    - Yes
- feats/Style
    <https://universaldependencies.org/cs/feat/Style>
    Style of a non-neutral lexeme. Stylistically neutral lexemes are identified by an absence of this feature.
    - Arch (archaic)
    - Coll (colloquial)
    - Expr (expressive but not Vulg, e.g. diminutives)
    - Rare (less frequent spelling)
    - Slng (slang)
    - Vrnc (vernacular)
    - Vulg (vulgar)


## MISC

All features in the MISC section are DeriNet-specific.

Compared to FEATS, MISC contains data that:
1. Have no gold-standard annotation, such as the corpus stats, whose values depend on the exact chosen corpus.
2. Have temporary, development nature, such as the is_compound mark, which should go away as soon as all ancestors of compounds are identified.
3. Are technical, not linguistic, such as the techlemma, which serves as a link with the underlying dictionary.

- misc/corpus_stats/absolute_count
    An absolute count of the lexeme occurrences in the SYNv4 corpus.
    - open-class feature
- misc/corpus_stats/percentile
    Percentile position of this lexeme calculated from misc/corpus_stats/absolute_count, expressed in percent. Higher = more frequent.
    - open-class feature
- misc/corpus_stats/relative_frequency
    The absolute count normalized by corpus size. The result is within the \[0, 1\] range and the sum of all relative_frequencies across the corpus yields 1.
    - open-class feature
- misc/corpus_stats/sparsity
    For corpus-attested lexemes, the negative base-10 logarithm of the relative_frequency. For OOV lexemes, -log_10(1/corpus_size) (i.e. we perform add-1 smoothing, but only for OOV lexemes).
    - open-class feature
- misc/is_compound
    A binary mark of lexemes which are created by compounding, without identifying their parents.
    - true
    - false
- misc/segmentation
    A parentheses-delimited string expressing the segmentation of selected words.
    FIXME should we delete this from the database? Segmentation should be stored in the appropriate column only.
    - open-class feature
- misc/techlemma
    A string identifying the lexeme within the MorfFlex CZ dictionary, used for linking lexemes from DeriNet and MorfFlex.
    - open-class feature
- misc/unmotivated
    A binary mark of lexemes which are not created from another lexeme using word-formation rules, and therefore should have no ancestors.
    - true
    - false


## RELATIONS

Relations have features identifying the type of relation and the kind of difference between the motivating and motivated lexemes.

- SemanticLabel
    - Aspect
    - Diminutive
    - Female
    - Iterative
    - Possessive
- Type
    - Compounding
    - Conversion
    - Derivation
