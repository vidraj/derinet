#!/usr/bin/env perl

## Usage:
# cat derinet092-shuffled-1000-annotated.tsv |./manual-annotation-prec-recall.pl derinet092.tsv >prec-recall.txt 2>&1

use strict;
use warnings;

use utf8;
use feature 'unicode_strings';

binmode STDIN,  'utf8';
binmode STDOUT, 'utf8';
binmode STDERR, 'utf8';


my $verbose_flag = 0;
my $db_file_name;

my $words_total = 0;
my $derivations_total = 0;
my $derivations_correct = 0;
my $lemmas_total = 0;
my $lemmas_correct = 0;

my (%derivation_creators_total, %derivation_creators_correct, %lemma_creators_total, %lemma_creators_correct);

my @database;
my %database_convertor;

sub deriv_is_correct {
	my ($creator) = @_;
	
	$derivations_total++;
	$derivations_correct++;
	
	if ($creator) {
		$derivation_creators_total{$creator}++;
		$derivation_creators_correct{$creator}++;
	}
}

sub deriv_is_incorrect {
	my ($creator) = @_;
	
	$derivations_total++;
	
	if ($creator) {
		$derivation_creators_total{$creator}++;
	}
}

sub deriv_is_missing {
	# no-op
}

sub lemma_is_correct {
	my ($creator) = @_;
	$words_total++;
	
	$lemmas_total++;
	$lemmas_correct++;
	
	$lemma_creators_total{$creator}++;
	$lemma_creators_correct{$creator}++;
}

sub lemma_is_incorrect {
	my ($creator) = @_;
	$words_total++;
	
	$lemmas_total++;
	
	$lemma_creators_total{$creator}++;
}

sub precision {
	return $derivations_correct / $derivations_total;
}

sub recall {
	return $derivations_correct / $words_total;
}

sub precision_by_creator {
	return join "\n", map { $_ . ":\t" . ($derivation_creators_correct{$_} / $derivation_creators_total{$_}) } keys %derivation_creators_total;
}

sub read_database {
	open(my $db, '<:encoding(UTF-8)', $db_file_name)
		|| die "Can't open DB file: $!\n";
		
	while (<$db>) {
		chomp;
		my ($id, $lemma, $techlemma, $pos, $parent_id, $deriv_type, $lexeme_creator, $deriv_creator) = $_ =~ /^(\d+)\t([^\t]+)\t([^\t]+)\t([ADNV])\t(\d+)?\t([^\t]+)?\t([^\t]+)?\t([^\t]+)?$/;
		#my ($id, $lemma) = $_ =~ /^(\d+)\t([^\t]+)/;
		
		next unless $id;
		
		if ($deriv_creator) {
			# Select the last part from the comma-separated list of creators, but don't include the square-brackets.
			($deriv_creator) = $deriv_creator =~ /.*(CS::[^[]+)/;
		}
		
		$database[$id] = {
			'lemma' => $lemma,
			'techlemma' => $techlemma,
			'pos' => $pos,
			'parent-id' => $parent_id,
			'derivation-type' => $deriv_type,
			'lexeme-creator' => $lexeme_creator,
			'derivation-creator' => $deriv_creator
		};
		
		if ($database_convertor{"$lemma#$pos#$techlemma"}) {
			die "Triplet $lemma#$pos#$techlemma specified twice!\n";
		} else {
			$database_convertor{"$lemma#$pos#$techlemma"} = $id;
		}
	}
	
	close($db);
}

sub get_lemma_for_id {
	my ($id) = @_;
	return $database[$id]->{'lemma'};
}

sub print_verbose {
	print @_ if $verbose_flag;
}

sub warn_verbose {
	print STDERR @_ if $verbose_flag;
}


for my $argument (@ARGV) {
	if ($argument eq '-v') {
		$verbose_flag = 1;
	} elsif (!$db_file_name) {
		$db_file_name = $argument;
	} else {
		die "Unknown argument '$argument' or more than one source file specified!\n";
	}
	
}

read_database();

while (<STDIN>) {
	chomp;
	my ($id, $lemma, $techlemma, $pos, $manual_deriv) = $_ =~ /^(\d+)\t([^\t]+)\t([^\t]+)\t([ADNV])\t([^\t]+)/;
	
	if (!$id) {
		die "Error reading input line:\n$_\n";
	}
	
	if (!$manual_deriv) {
		die "Manual derivation not filled in on line:\n$_\n";
	} elsif ($manual_deriv eq '?') {
		warn_verbose("Untagged lexeme $lemma\n");
		next;
	}
	
	
	$id = $database_convertor{"$lemma#$pos#$techlemma"};
	
	if (!$id) {
		if ($manual_deriv eq '!') {
			lemma_is_correct('deleted');
		} else {
			lemma_is_incorrect('deleted');
			warn_verbose("Incorrectly deleted $lemma\n");
		}
		next;
	}
	
	my ($parent_id, $deriv_type, $lexeme_creator, $deriv_creator) = map { $database[$id]->{$_} } qw(parent-id derivation-type lexeme-creator derivation-creator);
	
	if ($manual_deriv eq '!') {
		lemma_is_incorrect($lexeme_creator);
		warn_verbose("Bad lemma $lemma made by $lexeme_creator.\n");
		next;
	} else {
		lemma_is_correct($lexeme_creator);
	}
	
	if (!$parent_id) {
		if ($manual_deriv eq '-') {
			deriv_is_correct($deriv_creator);
		} else {
			warn_verbose("Missing derivation for '$lemma'; should be '$manual_deriv'\n");
			deriv_is_missing();
		}
	} elsif (get_lemma_for_id($parent_id) eq $manual_deriv) {
		deriv_is_correct($deriv_creator);
	} else {
		warn_verbose("Bad derivation for '$lemma':\tshould be '$manual_deriv',\tis '"
		           . get_lemma_for_id($parent_id) . "'. Made by $deriv_creator\n");
		deriv_is_incorrect($deriv_creator);
	}
}

print_verbose("Statistics for $db_file_name:\n");
print('Precision:  ' . precision() . "\nRecall:    " . recall() . "\n");

print_verbose("\nPrecision breakdown by creator:\n" . precision_by_creator() . "\n");
