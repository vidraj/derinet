from derinet.modules.block import Block
from derinet.utils import CycleCreationError

import sys
import re


def homoindex_from_long_lemma(long_lemma):
    if "-" in long_lemma:
        m = re.search("^[^`_-]+-(\d+)", long_lemma)
        return m.group(1)

        #homoindex = long_lemma
        #homoindex = re.sub(r"[`_].+","",homoindex)
        #homoindex = re.sub(r".+-","",homoindex)
        #return homoindex
    else:
        return ""

def long_to_short(long_lemma):
    return re.sub(r"[\-_`].+",'',long_lemma)

def choose_lexeme(derinet, long_lemma, pos):

#    print("Searching for lexeme\t"+long_lemma)

    short_lemma = long_to_short(long_lemma)
    candidates = derinet.search_lexemes(short_lemma,pos=pos)

    if len(candidates) == 0:
        print("XXX: nenalezen zadny lexem\t"+long_lemma)
        return None

    elif len(candidates) == 1:
#        print("XXX: nalezen prave jeden lexem\t"+long_lemma)
        return candidates[0]

    else:
        given_homoindex = homoindex_from_long_lemma(long_lemma)
        for candidate in candidates:
            candidate_long_lemma = candidate.morph
            candidate_homoindex = homoindex_from_long_lemma(candidate_long_lemma)
            if candidate_homoindex == given_homoindex:
                #print("XXX: nalezeno vic kandidatu, vybran jeden\t"+long_lemma+" -> "+candidate_long_lemma)
                return candidate

        print("XXX: nalezeno vic kandidatu, ale zadny nesedi cislickem\t%s\t[%s]" % (long_lemma, ", ".join([c.morph for c in candidates])))
        return None


class AddFromTsvLemmaList(Block):
    """Add derivations found in files formatted like DeriNet-1.X

    The annotation file processed by this block has the following TSV structure:
    target-ID  target-lemma    target-techlemma    target-POS  source-ID   source-techlemma

    The IDs are ignored and the source-POS is assumed to be V."""

    def process(self, derinet):

        with open(self.args["file"]) as f:
            for line in f:
                target_id, target_short_lemma, target_long_lemma, pos, \
                    source_id, source_long_lemma = line.rstrip("\n").split("\t")

                best_source_lexeme = choose_lexeme(derinet, source_long_lemma, "V")
                best_target_lexeme = choose_lexeme(derinet, target_long_lemma, pos)

                if best_source_lexeme and best_target_lexeme:
                    print("adding edge "+best_source_lexeme.morph+" -> "+best_target_lexeme.morph )
                    source_id = derinet.get_id(best_source_lexeme.lemma, pos=best_source_lexeme.pos, morph=best_source_lexeme.morph)
                    target_id = derinet.get_id(best_target_lexeme.lemma, pos=best_target_lexeme.pos, morph=best_target_lexeme.morph)
                    print ("IDs: "+str(source_id)+" -> "+str(target_id))

                    #print("orig_parent_id: "+best_target_lexeme[4])

                    old_source_lexeme = derinet.get_parent(target_id)

                    if old_source_lexeme:
                        print("Old source lemma: "+old_source_lexeme.morph)
                        print("New source lemma: "+best_source_lexeme.morph)
                        if old_source_lexeme.morph == best_source_lexeme.morph:
                            print("Warning: same parent as before:\t"+best_source_lexeme.morph+" -> "+best_target_lexeme.morph)
                        else:
                            print("Warning: parent lemma changed:\t NEWPARENT: "+best_source_lexeme.morph+" -> "+best_target_lexeme.morph+ "  OLD: "+old_source_lexeme.morph)

                    try:
                        derinet.add_derivation(target_id, source_id, force=True)
                    except CycleCreationError:
                            print("Warning: cycle would be created by setting:\t NEWPARENT: "+best_source_lexeme.morph+" -> "+best_target_lexeme.morph)

        return derinet
