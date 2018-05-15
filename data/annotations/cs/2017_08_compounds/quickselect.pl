#/usr/bin/env perl

use strict;
use warnings;

my ($file1, $file2) = @ARGV;

open (IN1, "<", $file1) or die "Unable to open file 1.\n";
open (IN2, "<", $file2) or die "Unable to open file 2.\n";

my $line2 = <IN2>;
chomp $line2;
$line2 = "\t".$line2."\t";

my $line = <IN1>;
chomp $line;
   
while ($line) {
    
    if ($line =~ $line2) {
	while ($line =~ $line2) {
	    my ($id, $lemma, $techlemma, $pos, $parent) = split("\t", $line);
	    $pos = $pos."C";
	    $line = $id."\t".$lemma."\t".$techlemma."\t".$pos."\t".$parent;
	    print $line."\n";
	    $line = <IN1>;
	    if ($line) {
		chomp $line;
	    }
	}
	$line2 = <IN2>;
	if ($line2) {
	    chomp $line2;
	    $line2 = "\t".$line2."\t";
	}
	else {
	    $line2 = "bh;oj;ef oI;JOJDDDIJ;"
	}
    }
    else {
	print $line."\n";
	$line = <IN1>;
	if ($line) {
	    chomp $line;
	}    
    }
}
