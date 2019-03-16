# Semantic Labelling of relations in DeriNet
This folder contains a list of semantically labelled relations from DeriNet.
The list is a result of initial experiments in field of semantic labelling using machine learning methods.

In this initial experiment, five semantic labels were predicted (DIMINUTIVE, FEMALE, POSSESSIVE, ASPECT, ITERATIVE).

## File format
The list of semantically labeled relations is saved to file `final-semantic-labels.tsv` in simple tab separated **.tsv** format.

The order of columns is as follow:
1. derivational parent (base word) with its part-of-speech tag separated by a dash,
2. derivationa child (derivative) with its part-of-speech tag separated by a dash,
3. predicted semantic label of the relation,
4. probability of predicted semantic label.

## Numbers of labelled relations for each semantic label
| Semantic label  | Count |
| ------------- | ------------- |
| DIMINUTIVE  | 6,042 |
| FEMALE  | 28,510 |
| POSSESSIVE | 88,620 |
| ASPECT | 15,459 |
| ITERATIVE | 11,890 |
| **total:** | **150,521** |
