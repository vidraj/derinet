#!/usr/bin/env python3

import sys
from collections import namedtuple, defaultdict


Lexeme = namedtuple("Lexeme", ["dbase", "id", "lemma", "techlemma", "pos", "parent_id", "is_unmotivated", "is_compound"])



def format_lexeme(lex):
    return "{} {}".format(lex.techlemma, lex.pos + ("C" if lex.is_compound else "") + ("U" if lex.is_unmotivated else ""))

class DeriNetParser:
    def __init__(self, name, derinet_file_handle):
        self.name = name
        self.filehandle = derinet_file_handle

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.filehandle.close()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def parse_line(self, line):
        """Parse a single line from the TSV 1.6 (or prior) representation of DeriNet. Return the contents as a Lexeme."""
        id, lemma, techlemma, pos, parent_id = line.split('\t')
        id = int(id)
        parent_id = None if parent_id == "" else int(parent_id)
        is_unmotivated = False
        is_compound = False

        if len(pos) > 1:
            # There is a comment in the POS.
            #assert len(pos) == 2, "Unknown POS comment style in '{}'".format(line)
            assert len(pos) == 2 or pos[2] == "C", "Unknown POS comment style in '{}'".format(line)

            # Extract the comment and the true POS from the POS.
            pos_comment = pos[1]
            pos = pos[0]

            if pos_comment == "C":
                is_compound = True
            elif pos_comment == "U":
                is_unmotivated = True
            else:
                assert False, "Unknown POS comment '{}' in '{}'".format(pos_comment, line)

        return Lexeme(self.name, id, lemma, techlemma, pos, parent_id, is_unmotivated, is_compound)

    def next(self):
        line = self.filehandle.readline()
        if line:
            line = line.rstrip('\n')
            lexeme = self.parse_line(line)
            return lexeme
        else:
            raise StopIteration()



def load_db(filename):
    if filename.endswith(".gz"):
        filehandle = gzip.open(filename, "rt", encoding='utf-8', newline='\n')
    else:
        filehandle = open(filename, "rt", encoding='utf-8', newline='\n')
    parser = DeriNetParser(filename, filehandle)

    id_to_lexeme = {}
    lemma_to_lexeme = defaultdict(set)

    for lexeme in parser:
        assert lexeme.id not in id_to_lexeme, "Lexeme with ID {} defined twice.".format(lexeme.id)

        id_to_lexeme[lexeme.id] = lexeme

        # Add the lexeme to the set that will be returned.
        # First, check it is not already in there.
        if lexeme in lemma_to_lexeme[lexeme.lemma]:
            print("Lexeme '{}' defined twice!".format(format_lexeme(lexeme)))
        lemma_to_lexeme[lexeme.lemma].add(lexeme)

    return id_to_lexeme, lemma_to_lexeme


def cmp_lemma_pos(lex_a, lex_b):
    """Compare the lemmma and POS of two lexemes, return a bool indicating whether they are equal."""
    return lex_a.lemma == lex_b.lemma and lex_a.pos == lex_b.pos

def mask_fields(ntup, *fields):
    """Sets the fields of the named tuple ntup enumerated in args to None, returns the modified tuple."""
    kwargs = {field: None for field in fields}
    return ntup._replace(**kwargs)

def cmp_fields(ntup_a, ntup_b, *fields):
    """Compare lexemes ntup_a and ntup_b on the fields listed in fields. Return True if they are equal, False if they differ."""
    return all([getattr(ntup_a, field) == getattr(ntup_b, field) for field in fields])


def process_and_link(processed, list_a, list_b, *fields):
    """Link together and mark as processed lexemes from list_a and list_b which have equal contents of fields listed in fields. Return the list of links."""
    linked_lexemes = []

    for lexeme_old in list_a:
        if lexeme_old in processed:
            continue

        for lexeme_new in list_b:
            if lexeme_new in processed:
                continue
            elif cmp_fields(lexeme_old, lexeme_new, *fields):
                linked_lexemes.append((lexeme_old, lexeme_new))
                processed.add(lexeme_old)
                processed.add(lexeme_new)
                break

    return linked_lexemes



if __name__ == '__main__':
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("old", metavar="OLD.tsv", help="a path to the first (old) file to compare.")
    parser.add_argument("new", metavar="NEW.tsv", help="a path to the second (new) file to compare.")
    args = parser.parse_args()


    old_db_id, old_db = load_db(args.old)
    new_db_id, new_db = load_db(args.new)

    linked_lexemes = []
    #processed = set()

    for lemma, old_lexemes in old_db.items():
        new_lexemes = new_db[lemma]

        processed = set()

        # Detect completely identical lexemes and mark them as done.
        unchanged = process_and_link(processed, old_lexemes, new_lexemes, "lemma", "techlemma", "pos", "is_unmotivated", "is_compound")
        linked_lexemes += unchanged

        # From the rest, link simple cases.

        # The simplest case is a change in motivatedness mark or compounding mark.
        mark_changed = process_and_link(processed, old_lexemes, new_lexemes, "lemma", "techlemma", "pos")
        linked_lexemes += mark_changed

        # The next simplest case is difference in techlemma.
        techlemma_changed = process_and_link(processed, old_lexemes, new_lexemes, "lemma", "pos", "is_unmotivated", "is_compound")
        techlemma_mark_changed = process_and_link(processed, old_lexemes, new_lexemes, "lemma", "pos")
        linked_lexemes += techlemma_changed + techlemma_mark_changed

        # The most difficult case is difference in POS.
        pos_changed = process_and_link(processed, old_lexemes, new_lexemes, "lemma", "techlemma", "is_unmotivated", "is_compound")
        pos_mark_changed = process_and_link(processed, old_lexemes, new_lexemes, "lemma", "techlemma")
        pos_techlemma_mark_changed = process_and_link(processed, old_lexemes, new_lexemes, "lemma")
        linked_lexemes += pos_changed + pos_mark_changed + pos_techlemma_mark_changed


        # Report the changes.
        for (o, n) in mark_changed:
            print("C/U mark changed in {} → {}".format(format_lexeme(o), format_lexeme(n)))
        for (o, n) in techlemma_changed:
            print("Techlemma changed in {} → {}".format(format_lexeme(o), format_lexeme(n)))
        for (o, n) in techlemma_mark_changed:
            print("Techlemma and C/U mark changed in {} → {}".format(format_lexeme(o), format_lexeme(n)))
        for (o, n) in pos_changed:
            print("POS changed in {} → {}".format(format_lexeme(o), format_lexeme(n)))
        for (o, n) in pos_mark_changed:
            print("POS and C/U mark changed in {} → {}".format(format_lexeme(o), format_lexeme(n)))
        for (o, n) in pos_techlemma_mark_changed:
            print("POS, techlemma and C/U mark changed in {} → {}".format(format_lexeme(o), format_lexeme(n)))

        # The rest of the lexemes are added or removed ones that cannot be linked to anything.
        # TODO distinguish deleting one variant of a lemma while leaving other from deleting all variants at once.
        # TODO also distinguish the same cases with insertions.
        for lexeme in old_lexemes:
            if lexeme not in processed:
                # TODO report if the deleted lexeme had a parent or children.
                print("Deleted {}".format(format_lexeme(lexeme)))
        for lexeme in new_lexemes:
            if lexeme not in processed:
                # TODO report if the new lexeme has a parent or children.
                print("New lexeme {}".format(format_lexeme(lexeme)))


    # Create lookup tables for transfer between databases in both directions.
    link_old_to_new = {o.id: n.id for (o, n) in linked_lexemes}
    link_new_to_old = {n.id: o.id for (o, n) in linked_lexemes}
    assert len(link_old_to_new) == len(link_old_to_new) == len(linked_lexemes), "Some internal lexeme representation is ambiguous, the linkage is not a bijection."

    # Find differences in derivations of linked lexemes.
    # TODO find differences among unlinked lexemes. This should probably be done above.
    for old_id, new_id in link_old_to_new.items():
        old_lexeme = old_db_id[old_id]
        new_lexeme = new_db_id[new_id]

        if new_lexeme.parent_id is None:
            if old_lexeme.parent_id is None:
                # Neither has a parent. Nothing to see here.
                pass
            else:
                # The old lexeme had a parent, the new one doesn't.
                # Report a link deletion.
                old_parent = old_db_id[old_lexeme.parent_id]
                print("Disconnected {} from {}".format(format_lexeme(new_lexeme), format_lexeme(old_parent)))
        else:
            if old_lexeme.parent_id is None:
                # The new lexeme has a parent, the old one doesn't.
                # Report a new link.
                new_parent = new_db_id[new_lexeme.parent_id]
                print("Newly connected {} to {}".format(format_lexeme(new_lexeme), format_lexeme(new_parent)))
            else:
                # Both lexemes have a parent. Verify it's the same one.
                old_parent = old_db_id[old_lexeme.parent_id]
                new_parent = new_db_id[new_lexeme.parent_id]

                if old_lexeme.parent_id in link_old_to_new and link_old_to_new[old_lexeme.parent_id] == new_lexeme.parent_id:
                    # The parent of the old lexeme has its counterpart in the new database
                    #  and the two match. This case is not interesting, do not report.
                    pass
                else:
                    # The old parent either has no counterpart in the new database,
                    #  but there is a new parent, or it has a counterpart but it is not
                    #  the one in the new database.
                    # Either way, the parents differ, report a reconnection.
                    print("Reconnected {} from {} to {}".format(format_lexeme(new_lexeme), format_lexeme(old_parent), format_lexeme(new_parent)))
