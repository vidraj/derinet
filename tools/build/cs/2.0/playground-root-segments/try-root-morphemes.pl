#!/usr/bin/perl

use strict;
use warnings;

use utf8;
binmode(STDOUT, ":utf8");
binmode(STDERR, ":utf8");
binmode(STDIN, ":utf8");

my @root_allomorphs;


sub penalty_for_spurious_occurrence {
    my ($segmented) = @_;
    return ($segmented =~ /\(t\)$|^(sub)?\(d\)o|^po\(d\)|^(pře|vy)\(d\)|^p\(řed\)|^(v)?o\(d\)|\([nt]\)[íěý]$|^(pro|pod)\(n\)a|^\(po\)|^\(n\)a|\(kův\)$|\(nos\)t(ní)?$|\(š\)í$|pseu\(d\)o|\(ší\)$|^\(vod\)v|\(s\)t$|\([tn]\)ost|^\(zn\)e|\(d\)lo$|^\(jist\)o/);
}
   

sub root_len {
    my ($segmented) = @_;

    if ($segmented =~ /\((.+)\)/) {
	return (length($1) - 0.5 * penalty_for_spurious_occurrence($segmented));
    }
    
    else {
	return 0;
    }
}


while (<>) {
    chomp;

    s/","/\t/g;
    s/,"/\t/g;
    s/",/\t/g;
    s/,,/\t\t/g;
    s/,$/\t/g;
    s/^"//;
    s/"$//;
    

    if (/^\s*$/ or /^Automatic/ ) {  } # empty lines ignored too

    
    elsif (/Manual roots for (\S+):/) {
	print "QQQQ $1\n";
	my $root_lemma = $1;
	my @columns = split /\t/;
	@root_allomorphs = grep {/\S/} split / /, $columns[1];
#	print "XXXXXXXXXXXXXXXx ".(join " ",@root_allomorphs)."\n";
    }

    elsif (/\t[\$\!]/) { } # lines to be ignored
    
    elsif (/^(\S+)\t(\S+)\t([A-Z])/) {
	my $short_lemma = $1;
	my $long_lemma = $2;
	my $pos = $3;

	my $err = 0;
	
	my @solutions;
	foreach my $root (@root_allomorphs) {
	    my @solutions_for_this_root;
	    while ($short_lemma =~ /$root/gi) {
		my $from = $-[0];
		my $to = $+[0];
		my $segmented_lemma = substr($short_lemma,0,$from) . "(" . substr($short_lemma,$from,$to-$from) . ")" . substr($short_lemma,$to,100);
		push @solutions_for_this_root, $segmented_lemma;

	    }


	    push @solutions, @solutions_for_this_root;
	    
	}

	@solutions = sort { root_len($b) <=> root_len($a) } @solutions; 
	
	if ($err) { # already reported
	}
	
	elsif (@solutions == 0) {
	    print STDERR "Error: No root allomorph found\t out of '".(join " ",@root_allomorphs)."' in '$short_lemma'\n";
	}
	
	elsif (@solutions > 1 and root_len($solutions[0]) == root_len($solutions[1])) {
	    print STDERR "Error: Ambiguous segmentation 2: more matching allomorphs of the same length\t in '$short_lemma' out of ".(join " ",grep {root_len($_) == root_len($solutions[0])} @solutions)."\n";
	}
	
	else {
	    chomp;
	    print $_."\t".$solutions[0]."\n";
	}

    }

    else {
	print STDERR "Error: unrecognized line: $_ \n";
    }
    
    
}
