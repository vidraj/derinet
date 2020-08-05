all:
	 cat batch1-1000-ZZ-SD.tsv | cut -f1,6 | perl -ne 'binmode(STDIN,":utf8");binmode(STDOUT,":utf8");@f=split("\t");print reverse(split("",$$f[0]))."\t".$$f[0]."\tBATCH-1\t\t".$$f[1]' > batch1-same-format.tsv

	cat batch2-1100-ZZ.tsv | cut -f1,2,5,6 | perl -ne 'binmode(STDIN,":utf8");binmode(STDOUT,":utf8");@f=split("\t");print reverse(split("",$$f[0]))."\t".$$f[0]."\tBATCH-2\t$$f[1]\t".$$f[2]."\t".$$f[3]' > batch2-same-format.tsv

	cat batch1-same-format.tsv batch2-same-format.tsv | sort | cut -f2- > union-2100-segmented.tsv
