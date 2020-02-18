def load_data(file):
    f=open(file,"r", encoding="utf-8")
    data=f.readlines()
    f.close()
    data2=[]
    for line in data:
        parts=line.strip().split("\t")
        data2.append((parts[1],parts[2].lower().strip().replace(" ","|"))) #lemma and segmentated lemma
    return data2

train=load_data("manual_segmentation_1000\\train.txt")
devel=load_data("manual_segmentation_1000\\devel.txt")
test =load_data("manual_segmentation_1000\\test.txt")