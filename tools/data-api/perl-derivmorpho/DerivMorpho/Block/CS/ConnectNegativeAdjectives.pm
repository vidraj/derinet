package Treex::Tool::DerivMorpho::Block::CS::ConnectNegativeAdjectives;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

use utf8;

use Treex::Core::Log;
use Treex::Tool::Lexicon::CS;
use Treex::Tool::Lexicon::Generation::CS;

my $analyzer = Treex::Tool::Lexicon::Generation::CS->new();


sub process_lexeme {
	my ($self, $lexeme, $dict) = @_;
	
	my $lemma = $lexeme->lemma;
	return if $lexeme->source_lexeme or $lemma !~ /^ne/ or $lexeme->pos ne 'A';
	
	my @analyses = grep { $_->{tag} =~ /^AAMS1.....N/ } $analyzer->analyze_form($lemma);
	my @analyzed_lemmas = map { $_->{lemma} } @analyses;
	
	if (@analyzed_lemmas == 1) {
		if ('ne' . Treex::Tool::Lexicon::CS::truncate_lemma($analyzed_lemmas[0], 1) eq $lemma) {
			log_info('Adding derivation ' . $analyzed_lemmas[0] . " --> $lemma");
			
			my @parent_lexemes = $dict->get_lexemes_by_lemma(Treex::Tool::Lexicon::CS::truncate_lemma($analyzed_lemmas[0], 1));
			
			my @filtered_parent_lexemes = grep { $_->mlemma eq $analyzed_lemmas[0] } @parent_lexemes;
			
			if (@filtered_parent_lexemes) { # We prefer strongly matching lexemes, but if there are none, unfiltered ones will do as well.
				@parent_lexemes = @filtered_parent_lexemes;
			}
			
			if (!@parent_lexemes) {
				log_info("\tNo lexeme found for lemma " . $analyzed_lemmas[0] . '!');
			} else {
				if (@parent_lexemes > 1) {
					log_info("\tMultiple lexemes found for lemma " . $analyzed_lemmas[0] . ': ' . join(', ', map { $_->mlemma } @parent_lexemes));
				}
				
				log_info("\tAdded successfully.");
				$dict->add_derivation({
					source_lexeme => $parent_lexemes[0],
					derived_lexeme => $lexeme,
					deriv_type => 'A2A',
					derivation_creator => $self->signature,
				});
			}
		} else {
			log_info('The lemmas don\'t match: ' . $analyzed_lemmas[0] . " and $lemma.");
		}
	} elsif (@analyzed_lemmas > 1) {
		log_info('Got multiple analyses for lemma ' . $lexeme->mlemma . ": '" . join("', '", map { $_->{lemma} . ' ' . $_->{tag} } @analyses) . "'.");
	} else {
		log_info("No analysis for lemma $lemma.");
	}
}

1;
