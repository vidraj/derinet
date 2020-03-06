Roots of different trees, which look simmilar, and so we may want to merge their subtrees into a single tree.



We look at roots of trees. If the triplet loss model tells us, that roots of 2 different trees are very similar, it may mean, that their subtrees should be merged into a single tree.
So far, we did not compare all 200k trees with one another, although it seems like it should be computable as well with a few patches.
We've splitted trees into two cathegories - the big ones (5 or more nodes), and the small ones (4 or less nodes).

In the first type of experiment 
close_neighbors_from_different_trees-threshold_*.txt
We compared every node of a big tree with every node of the other big trees. If the distance was smaller than threshold, we wrote the pair of roots down.

In the second type of experiment
close_neighbors-roots_of_small_trees_which_might_be_part_of_the_big_ones-threshold_*.txt
We did the exact same thing, but we were looking for the closest neighbor of every small trees'root among the roots of the big trees. This shows us, that we may want to connect a small tree to one of the big trees.


The third type of experiment
edges_with_words_too_far_appart-threshold_*.txt

was somehow dual to the previous experiments:
we looked at the edges in the big trees, and if the distance between the connected vertices was too large (larger than threshold), we wrote that down, because it indicates that the edge may be wrong.



WARNING:
Please note, that every pair of similar roots is recorded twice