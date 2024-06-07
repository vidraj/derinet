#!/usr/bin/env python3

import sys
try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(iterable, *args, **kwargs):
        return iterable

def parse_file(f):
    """
    Parse each line and divide multi-word expressions into multiple
    single-word expressions.
    """
    for line in f:
        line = line.rstrip()
        lemma, sublemma, tag, count = line.split("\t")
        count = int(count)

        # We can't simply detect the '|' symbol in the lemma or
        #  sublemma, because it's not just a separator, but also
        #  legitimate punctuation.
        # Instead, detect the length by calculating the number of tags
        #  present. Each tag has 15 positions, each additional tag
        #  carries the '|' separator with it. The +1 is the result of
        #  subtracting 15 (for the starting tag), dividing the rest by
        #  16 (for the remaining tags) and adding 1 (for the starting
        #  tag again – so -15+(1*16) = +1.
        tag_count, remainder = divmod(len(tag) + 1, 16)
        assert remainder == 0

        if tag_count > 1:
            # It's a MWE.
            lemmas = lemma.split("|")
            sublemmas = sublemma.split("|")
            tags = tag.split("|")
            assert len(lemmas) == len(sublemmas) == len(tags) == tag_count, "The fields don't have equal lengths: {} {} {}".format(lemma, sublemma, tag)

            for l, s, t in zip(lemmas, sublemmas, tags):
                yield l, s, t, count
        else:
            # It's a single-word expression.
            yield lemma, sublemma, tag, count

def merge_tags(tag1, tag2):
    """
    Replace differing parts of tags with `?`s.
    """
    assert len(tag1) == len(tag2)
    t = []
    for c1, c2 in zip(tag1, tag2):
        if c1 == c2:
            t.append(c1)
        else:
            t.append("?")
    return "".join(t)

def add_tag(tags, new_tag, count):
    """
    Add new_tag into the tags structure with the given count.
    """
    pos = new_tag[0]

    if pos in tags:
        old_tag, old_count = tags[pos]
        tags[pos] = merge_tags(old_tag, new_tag), old_count + count
    else:
        tags[pos] = new_tag, count

    return tags

def main():
    l_sl = {}

    for lemma, sublemma, tag, count in tqdm(parse_file(sys.stdin), desc="Reading input", miniters=100000, unit="lines"):
        l = lemma, sublemma
        if l in l_sl:
            l_sl[l] = add_tag(l_sl[l], tag, count)
        else:
            l_sl[l] = {tag[0]: (tag, count)}

    for (lemma, sublemma), tags in tqdm(sorted(l_sl.items()), desc="Printing output", miniters=200000, unit="sublemmas"):
        for tag, count in sorted(tags.values()):
            print(lemma, sublemma, tag, count, sep="\t", end="\n")

if __name__ == "__main__":
    main()
