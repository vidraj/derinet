#!/usr/bin/env python3

import sys
import re
import glob

orig2segmented = {}
origin = {}


# ---------- 1. previously existing resources (slavickova's, ostrava's, and ours)

for old_annotation_filename in sorted(glob.glob('../prepare/for_annotation/inputs/*')):  # sorted in order to make our annotations come later
    fh = open(old_annotation_filename)

    for line in fh:
        segmented = line.rstrip().lower()
        orig = segmented.replace('-','')
        orig2segmented[orig] = segmented
        origin[orig] = re.sub(r'.+\/','',old_annotation_filename)


# ---------- 2. completion towards ud sample

fh = open('../hand-annotated/2022 leden segmentace retro.xlsx - 2022 leden segmentace retro.tsv')

for line in fh:
    columns = line.rstrip().split('\t')
    (orig, retro, segmented) = columns[:3]
    orig2segmented[orig] = segmented.replace(' ','-')
    origin[orig] = 'extension-for-ud'

# ---------- 3. resolved inconsistencies among resources
        
fh = open('../hand-annotated/inconsist.xlsx - inconsist.tsv')
for line in fh:
    columns = line.rstrip().split('\t')

    (orig, retro, segmentations_str, sources_str, correct_segmentation, correct_source) = columns[0:6]

    if not re.match(r'homo$',correct_source):

    
        winner = None

        if len(correct_segmentation) != 0:
            winner = correct_segmentation
            orig2segmented[orig] = correct_segmentation
            origin[orig] = 'inconsist-new'

        else:
    

            segmentations = segmentations_str.split('|')
            sources = sources_str.lower().split('|')


            for i in range(len(sources)):
                if correct_source == sources[i]:
                    winner = segmentations[i]
                    orig2segmented[orig] = segmentations[i]
                    origin[orig] = 'inconsist-'+correct_source+'-winner'

            if not winner:
                sys.stderr.write(f'No winner: {line}   orig={orig} retro={retro} segmentations_str={segmentations_str} sources_str={sources_str} correct={correct_source}\n')

            else:
                #sys.stderr.write(f'OK: {line}\n')
                pass
            

# -------------  4. revisions in all.tsv

fh = open('../hand-annotated/all.tsv')

for line in fh:
    columns = (line.rstrip()+'\t').split('\t')
    (orig, retro, segmented, comment) = columns[:4]
    segmented = segmented.replace(' ','-')
    if comment in ['opraveno','our'] and segmented != orig2segmented[orig]:
        orig2segmented[orig] = segmented
        origin[orig] = 'all-revision'


# ----------- 5. dvouznakove

fh = open ('../hand-annotated/dvouznakove HOTOVA ANOTACE.tsv')

for line in fh:
    columns = (line.lower().rstrip()+"\t").split('\t')
    if len(columns) == 4:
        (freq,form,morphemecount,comment) = columns[:4]

        if morphemecount == '2' and not '/' in comment:
            orig2segmented[form] = form[0] + '-' + form[1]
            origin[form] = 'dvouznakove'

# -------------
            
for orig in [word for word in sorted(orig2segmented) if len(word)>1]:
    print('\t'.join([orig.rstrip(),orig[::-1],orig2segmented[orig],origin[orig]]))
    
