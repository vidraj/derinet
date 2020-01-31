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
    return ($segmented =~ /\(t\)$|^(sub)?\(d\)o|^po\(d\)|^(pře|vy)\(d\)|^p\(řed\)|^(v)?o\(d\)|\([nt]\)[íěý]$|^(pro|pod)\(n\)a|^\(po\)|^\(n\)a|\(kův\)$|\(nos\)t(ní)?$|\(š\)í$|pseu\(d\)o|\(ší\)$|^\(vod\)v|\(s\)t$|\([tn]\)ost|^\(zn\)e|\(d\)lo$|^\(jist\)o|\(va\)$|^\(pro\)|^\(pr\)o|su\(per\)|\(v[aá]\)(t|ní|tí|ný|vající|jící|nost|cí)$|\(čk\)a$|\(vě\)$|\(nov\)[ýě]$|\(va\)$/);
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


my $ignore_composite = 0;
my $rootnode = 0;
my $firstcluster = 1;
my $print_buffer = "";
my $nonempty_cluster = 0;

LINE: while (<>) {
    chomp;

    s/","/\t/g;
    s/,"/\t/g;
    s/",/\t/g;
    s/,,/\t\t/g;
    s/,$/\t/g;
    s/^"//;
    s/"$//;
    

    if (/^\s*$/ or /Automatic roots/ ) {  } # empty lines ignored too

    elsif (/Manual roots for (\S+\#[AV]C):/ or /telef/) {
	$ignore_composite = 1;
    }
    
    elsif (/Manual roots for (\S+):/) {
	$ignore_composite = 0;
	my $root_lemma = $1;
	my @columns = split /\t/;
	my $allomorph_string = $columns[1];
	if (@columns>3) {
	    $allomorph_string = $columns[4];
	}
	
	@root_allomorphs = grep {/[[:alpha:]]/} split / /, $allomorph_string;
	$rootnode = 1;
	
	if (not $firstcluster and $nonempty_cluster) {
	    print "ENDOFCLUSTER\n";
	}
	$firstcluster = 0;
	    
	$print_buffer =  "STARTOFCLUSTER\t".(join " ",@root_allomorphs)."\n";
	$nonempty_cluster = 0;
    }

    elsif (/\%/) {
	next LINE;
    }

    elsif (/\t[\$\!]/) { 
	my ($shortlemma,$longlemma,$pos) = split /\t/;
	if ($shortlemma and $longlemma) {
	    print $print_buffer."STOPNODE\t$longlemma\n";
	    $print_buffer = "";
    	    $nonempty_cluster = 1;
	}
    }

    elsif ($ignore_composite) {
	next LINE;
    }
    
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
	    print $print_buffer;	    
	    if ($rootnode) {
		print "ROOTNODE\t$short_lemma\t$long_lemma\t$solutions[0]\n";
	    }

	    print "SEGMENTEDNODE\t$long_lemma\t$solutions[0]\n";
	    $print_buffer = "";
	    $nonempty_cluster = 1;
	}
	$rootnode = 0;

    }

    else {
	print STDERR "Error: unrecognized line: $_ \n";
    }

    
}

print "ENDOFCLUSTER\n";
