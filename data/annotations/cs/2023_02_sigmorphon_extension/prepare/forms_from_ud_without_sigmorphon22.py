#!/usr/bin/env python3

import sys
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

MAX_UD_SENTENCES = 4000  # formy z prvniho tisice vet uz byly v sigmorphonu 22, pridavame z dalsich 4000

already_segmented = {}

for filename in [f"input_data/sigmorphon2022/data/ces.word.{section}.tsv" for section in ['train','dev','test']]:
    
    logging.info(f"Loading {filename} ...")
    
    fd = open(filename)

    for line in fd:
        (orig,segmented) = (line.rstrip()+"\t").split("\t")[:2]
        already_segmented[orig] = 1
        #print(f"Adding segmented form {segmented}")

unsegmented = {}
processed_sentences = 0

logging.info("Number of words with known segmentation: " + str(len(already_segmented)))

ud_filename = "input_data/ud/cs_pdt-ud-train.conllu"
logging.info(f"Loading {ud_filename}")
ud = open(ud_filename)
for line in ud:

    line = line.rstrip()

    if line == "":
        processed_sentences += 1
        if processed_sentences == MAX_UD_SENTENCES:
            break

    elif line[0]=="#":
        pass

        
    else:
        (id, form, lemma, PoS, xpos) = line.split("\t")[:5]

        form = form.lower()
        
        if (not form in already_segmented) and (not form in unsegmented) and (not PoS in ["PUNCT","NUM"]) and len(form)>1:
            unsegmented[form] = 1


for form in unsegmented:
    print(form)
