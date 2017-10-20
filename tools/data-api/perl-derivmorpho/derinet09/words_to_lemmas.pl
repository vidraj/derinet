#!/usr/bin/env perl

## A script that guesses POS tags and techlemmas for input words.
## Usage:
# cat extra_words.txt |./words_to_lemmas.pl

use strict;
use warnings;

use utf8;
use feature 'unicode_strings';

binmode STDIN,  'utf8';
binmode STDOUT, 'utf8';
binmode STDERR, 'utf8';

use Treex::Tool::Lexicon::CS;
use Treex::Tool::Lexicon::Generation::CS;


sub starts_with {
	my ($hay, $needle) = @_;
	return substr($hay, 0, length($needle)) eq $needle;
}


my $analyzer = Treex::Tool::Lexicon::Generation::CS->new();
my $tag_length = 15;

while (<>) {
	chomp;
	next if (/^\s*$/ or /^\s*#/);
	my ($short_lemma, $orig_tag) = split /\t/, $_;
	
	# The correct way of handling this is to generate all possible forms, then analyze each of them, then plug the results into the standard MorfFlex pipeline.
	#  … but we can't generate forms from unknown lemmas.
	my @lexemes = grep { Treex::Tool::Lexicon::CS::truncate_lemma($_->{lemma}, 1) eq $short_lemma
	                     and starts_with($_->{tag}, $orig_tag) } $analyzer->analyze_form($short_lemma, 1);
	
	if (!@lexemes) {
		print STDERR "No lexemes found for word $short_lemma\n";
		
		my $pad = '?' x ($tag_length - length($orig_tag));
		
		print "$short_lemma\t$orig_tag$pad\n";
		next;
	}
	
	for my $lexeme (@lexemes) {
		my $long_lemma = $lexeme->{lemma};
		my $pos = substr($lexeme->{tag}, 0, 1);
		
		#print "$long_lemma\t$pos\t" . $lexeme->{tag} . "\n";
		print "$long_lemma\t" . $lexeme->{tag} . "\n";
# 		print "$long_lemma\t$pos\n";
	}
}
