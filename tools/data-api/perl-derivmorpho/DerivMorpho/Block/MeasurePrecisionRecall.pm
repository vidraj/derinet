package Treex::Tool::DerivMorpho::Block::MeasurePrecisionRecall;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

use strict;
use warnings;

use feature 'unicode_strings';
use utf8;
binmode STDIN,  ':utf8';
binmode STDOUT, ':utf8';
binmode STDERR, ':utf8';

use Treex::Core::Log;

has file => (
	is            => 'ro',
	isa           => 'Str',
	documentation => 'name of file with annotated lemmas to load'
);

has ignore_composition => (
	is            => 'ro',
	isa           => 'Bool',
	documentation => 'enable to treat lemmas created by composition as cluster roots'
);

has verbose => (
	is            => 'ro',
	isa           => 'Bool',
        documentation => 'enable extra output'
);

my $words_total = 0;
my $derivations_possible = 0;
my $derivations_total = 0;
my $derivations_correct = 0;
my $lemmas_total = 0;
my $lemmas_correct = 0;

my (%derivation_creators_total, %derivation_creators_correct, %lemma_creators_total, %lemma_creators_correct);

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

	$creator = 'undefined' if !$creator;
	
	$lemma_creators_total{$creator}++;
	$lemma_creators_correct{$creator}++;
}

sub lemma_is_incorrect {
	my ($creator) = @_;
	$words_total++;
	
	$lemmas_total++;
	
	$creator = 'undefined' if !$creator;
	
	$lemma_creators_total{$creator}++;
}

sub precision {
	log_info("Correct: $derivations_correct");
	log_info("Total:   $derivations_total");
	return $derivations_correct / $derivations_total;
}

sub recall {
	return $derivations_correct / $derivations_possible;
}

sub precision_by_creator {
	return join "\n", map { $_ . ":\t" . (($derivation_creators_correct{$_} ? $derivation_creators_correct{$_} : 0) / $derivation_creators_total{$_}) . "\t(" . ($derivation_creators_correct{$_} ? $derivation_creators_correct{$_} : 0) . ' out of ' . $derivation_creators_total{$_} . ')' } keys %derivation_creators_total;
}

sub lemma_precision_by_creator {
	return join "\n", map { $_ . ":\t" . (($lemma_creators_correct{$_} ? $lemma_creators_correct{$_} : 0) / $lemma_creators_total{$_}) . "\t(" . ($lemma_creators_correct{$_} ? $lemma_creators_correct{$_} : 0) . ' out of ' . $lemma_creators_total{$_} . ')' } keys %lemma_creators_total;
}

sub is_in_list {
	my ($lemma, $list) = @_;
	my @lemmas = split /,\s*/, $list;
	log_fatal("Annotated parents seem to be empty: '$list'") unless @lemmas;
	return grep { $lemma eq $_ } @lemmas;
}

sub is_composition {
	my ($deriv_info) = @_;
	return $deriv_info =~ /[^,[:space:]]\s+/;
}

sub remove_compositional_information {
	my ($deriv_info) = @_;
	my @parts = split /,\s*/, $deriv_info;
	return join(',', map { is_composition($_) ? '-' : $_ } @parts);
}


sub process_dictionary {
	my ($self, $dict) = @_;

	open my $F, '<:utf8', $self->file
		or log_fatal("You have to pass a valid filename as an argument named 'file'.\nError: $!");
	
	LINE:
	while (<$F>) {
		chomp;
		next if (/^#/ or /^\s*$/);
		my ($lemma, $pos, $manual_deriv) = split /\t/;
		next if not $lemma;
		
		if (!$manual_deriv) {
			log_info("Manual derivation not filled in on line: '$_'");
			next LINE;
		} elsif ($manual_deriv eq '?') {
			log_info("Untagged lexeme $lemma");
			next LINE;
		} elsif ($self->ignore_composition and is_composition($manual_deriv)) {
			log_info("Ignoring some parents of lexeme created by composition: $lemma") if $self->verbose;
			$manual_deriv = remove_compositional_information($manual_deriv); # TODO solve properly the case of "foo, bar, comp osition, baz"
		}

		my @lexemes = grep { $_->pos eq $pos } $dict->get_lexemes_by_lemma($lemma);
		
		if (!@lexemes) {
			if ($manual_deriv eq '!') {
				lemma_is_correct('deleted');
			} else {
				lemma_is_incorrect('deleted');
				log_info("Incorrectly deleted $lemma");
			}
			next LINE;
		}
		
		LEXEME:
		for my $lexeme (@lexemes) {
			my $parent_lemma;
			if ($lexeme->source_lexeme) {
				$parent_lemma = $lexeme->source_lexeme->lemma;
			}
			
			my $lexeme_creator = $lexeme->lexeme_creator || 'unknown';
			my $deriv_creator = $lexeme->get_derivation_creator() || 'unknown';
			
			if ($manual_deriv eq '!') {
				lemma_is_incorrect($lexeme_creator);
				log_info('Bad lemma ' . $lexeme->mlemma . " made by $lexeme_creator.");
				next LEXEME; # We want all bad lexemes to count, not just one.
			} else {
				lemma_is_correct($lexeme_creator);
			}

			$derivations_possible++;
			
			if (!$parent_lemma) {
				if ($manual_deriv eq '-') {
					deriv_is_correct('no parent');
				} else {
					log_info("Missing derivation for '$lemma'; should be '$manual_deriv'.") if $self->verbose;
		                        deriv_is_missing();
				}
			} elsif (is_in_list($parent_lemma, $manual_deriv)) {
				deriv_is_correct($deriv_creator);
			} else {
	                        log_info("Bad derivation for '$lemma':\tshould be '$manual_deriv',\tis '$parent_lemma'. Made by $deriv_creator.");
				deriv_is_incorrect($deriv_creator);
			}
		}
	}
	
	close $F;

	print 'Precision:  ' . precision() . "\nRecall:    " . recall()
	    . "\n\nPrecision breakdown by creator:\n" . precision_by_creator()
	    . "\n\nLemma precision breakdown:\n" . lemma_precision_by_creator() . "\n";

	return $dict;
}

1;
