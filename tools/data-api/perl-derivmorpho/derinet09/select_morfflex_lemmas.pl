#!/usr/bin/env perl

## Usage:
# xz -dkvvc morfflex-cz.2013-11-12.utf8.lemmaID_suff-tag-form.tab.csv.xz |./select_morfflex_lemmas.pl [--ignore-list LIST] > lemmas_from_morfflex.tsv

use strict;
use warnings;

use feature 'unicode_strings';
use utf8;
binmode STDIN,  ':utf8';
binmode STDOUT, ':utf8';
binmode STDERR, ':utf8';

my %techlemmas;
my %ignore_words;

# If there is a list of lemmas to ignore, load it.
if (@ARGV == 2 and $ARGV[0] eq '--ignore-list') {
	open(my $f, '<:encoding(UTF-8)', $ARGV[1])
		or die("Couldn't open file " . $ARGV[1] . ": $!\n");
	
	while (<$f>) {
		chomp;
		my $line = $_;
		if ($line =~ /^[^\t]*\t.$/) {
			$ignore_words{$line} = ();
		}
	}
	
	close $f
		or die("Couldn't close file " . $ARGV[1] . ": $!\n");
}

while (<STDIN>) {
	chomp;
	my $line = $_;
	
	# Try to extract the form. It might not be present, because extra_lemmas (non-morfflex manually added ones) don't have forms filled in.
	my ($lemma, $tag, $form) = $line =~ /^([^\t]*)\t([ACDNPRV][^\t]*)\t([^\t]*)$/;
	
	if (not $form) {
		# If there is no form, extract at least the rest.
		($lemma, $tag) = $_ =~ /^([^\t]*)\t([ACDNPRV][^\t]*)/;
	}
	
	next unless $tag; # Skip non-ADNV lemmas
	
	
	my $shortlemma = $lemma;
	$shortlemma =~ s/[_`].+//;
	$shortlemma =~ s/-\d+$//;
	if ($shortlemma =~ /\d/ or $lemma =~ /_:B/) {
		# Skip unwanted lemmas, i.e. lemmas containing numerals and abbreviations
		next;
	}
	
	my $lemma_matches_form = 0;
	if ($form) {
		$lemma_matches_form = $shortlemma eq $form;
	}
	
	my $pos = substr($tag, 0, 1);
	# my $gender = substr($tag, 2, 1);
	
	# Skip lemmas that are in the ignore-list
	next if exists $ignore_words{"$shortlemma\t$pos"};
	
	# If we've seen this lemma+POS combination before, merge its tags.
	my $lemma_data = $techlemmas{$lemma}->{$pos};
	
	if ($lemma_data) {
		my $variant_tag = $lemma_data->{'tag'};
		$lemma_data->{'count'}++;
		$lemma_data->{'has_equal_form'} ||= $lemma_matches_form;
		
		# Merge the two tags.
		my $merged_tag = '';
		
		for (my $i = 0; $i <= 14; $i++) {
			if (substr($tag, $i, 1) eq substr($variant_tag, $i, 1)) {
				$merged_tag .= substr($tag, $i, 1);
			} else {
				$merged_tag .= '?';
			}
		}
		
		$techlemmas{$lemma}->{$pos}->{'tag'} = $merged_tag;
# 		print STDERR "Updated variant for lemma $lemma: $merged_tag\n";
	} else {
# 		print STDERR "Storing new variant for lemma $lemma\n";
		my $new_lemma_data = {
			'tag' => $tag,
			'count' => 1,
			'has_equal_form' => $lemma_matches_form,
		};
		
		if (exists $techlemmas{$lemma}) {
			$techlemmas{$lemma}->{$pos} = $new_lemma_data;
		} else {
			$techlemmas{$lemma} = {
				$pos => $new_lemma_data,
			};
		}
	}
}

for my $lemma (keys %techlemmas) {
	for my $pos (keys %{$techlemmas{$lemma}}) {
		my $tag = $techlemmas{$lemma}->{$pos}->{'tag'};
		my $count = $techlemmas{$lemma}->{$pos}->{'count'};
		my $lemma_matches_form = $techlemmas{$lemma}->{$pos}->{'has_equal_form'} ? 1 : 0;
		
		print "$lemma\t$tag\t$count\t$lemma_matches_form\n";
	}
}
