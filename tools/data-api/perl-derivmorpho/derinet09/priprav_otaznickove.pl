#!/usr/bin/env perl


binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";

use strict;
use warnings;


my $first_lexeme_descr;
my $is_first = 1;


sub extract_lexeme_from_line {
    my $line = shift;
    if (/^(\S+#.)/) {
	return $1;
    }
}

while (<>) {

    if (/^\s*$/) {
	$is_first = 1
    }

    elsif ($is_first) {
	$first_lexeme_descr = extract_lexeme_from_line($_);
	$is_first = 0;
    }

    elsif (s/^\s*([,.])\s*//) {
	my $direction = $1;
	my $second_lexeme_descr = extract_lexeme_from_line($_);
	
	my $output_line;
	if ($direction eq ",") {
	    $output_line = "$first_lexeme_descr\t$second_lexeme_descr\n";
	}
	else {
	    $output_line = "$second_lexeme_descr\t$first_lexeme_descr\n";
	}

	$output_line =~ s/#/\t/g;

	print $output_line;
    }
}
