package Treex::Tool::DerivMorpho::Block::CS::ReconnectVerbalDerivatives;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

#### Description:
#    This package was created to rectify systematical errors in the derivational
# information contained in MorfFlex. It searches for known errors and reconnects
# the affected words.

use utf8;

use Treex::Core::Log;
use Treex::Tool::Lexicon::CS;

has file => (
	is            => 'ro',
	isa           => 'Str',
	documentation => q(file name to load),
);

has aggressive => (
	is            => 'ro',
	isa           => 'Bool',
	documentation => q(tries to connect words even when the stems don't match),
);

# Returns OK and a list of parents. OK means that the lexeme is already connected. TODO This should be refactored somehow.
sub get_parents_by_rule {
	my ($rule_name, $rule, $lexeme, $aggressive, $dict) = @_;
	
	my $rule_regex = $rule->{'regex'};
	if ($lexeme->lemma =~ $rule_regex and $lexeme->pos eq $rule->{'pos'}) {
		my $parent_suffix = $rule->{'parent'};
		my $orig_suffix = $rule->{'orig'};

		# Apply the rule to get lemma of the probable parent and original (current and incorrect) parent
		my $parent_lemma = $lexeme->lemma =~ s/$rule_regex/$parent_suffix/r;
		my $orig_lemma = $lexeme->lemma =~ s/$rule_regex/$orig_suffix/r;

		log_info("\tApplying rule '$rule_name' to get parent $parent_lemma");


		if ($lexeme->source_lexeme->lemma eq $parent_lemma) {
			# The connection is already right; nothing to do
			log_info("\tAlready connected.");
			return (1, undef);
		} elsif ($lexeme->source_lexeme->lemma eq $orig_lemma) { # Check that the current parent is the expected wrong one.
			# Find lexemes matching the parent lemma and the required POS
			my @parents = grep { $_->lemma eq $parent_lemma and $_->pos eq $rule->{'parentpos'} } $lexeme->source_lexeme->get_derived_lexemes(); #$dict->get_lexemes_by_lemma($parent_lemma);
			
			return (0, \@parents);
		} elsif ($aggressive) {
# 			if ($lexeme->source_lexeme->lemma =~ /\Q$parent_suffix\E$/) { # FIXME: Asi je to stejně blbost, tohle dělat. Pokud není připojený přesně, tak se ho prostě pokusíme přepojit a hotovo. Jinak tam mám false positives, něco se nepřepojí, i když by mělo.
# 				log_info("\tAlready connected approximate.");
# 				return (1, undef);
# 			} els
			if ($lexeme->source_lexeme->lemma =~ $rule_regex) {
				# The suffix of the parent is the same as mine → it is probably derived by prefixation.
				log_info("\tConnected to " . $lexeme->source_lexeme->lemma . ', which seems OK. Prefix maybe?');
				return (1, undef);
			} elsif ($lexeme->source_lexeme->lemma =~ /\Q$orig_suffix\E$/) {
				# First, search for an exactly matching sibling.
				my @parents = grep { $_->lemma eq $parent_lemma and $_->pos eq $rule->{'parentpos'} } $lexeme->source_lexeme->get_derived_lexemes();
				
				if (!@parents) {
					# There are no appropriate words inside the current cluster. Search for an exact match outside this cluster.
					@parents = grep { $_->pos eq $rule->{'parentpos'} } $dict->get_lexemes_by_lemma($parent_lemma);
				}
				
				if (!@parents) {
					# If all else fails, search for any sibling with the correct suffix. This is dangerous, but let's get aggressive. :-)
					@parents = grep { $_->lemma =~ /\Q$parent_suffix\E$/ and $_->pos eq $rule->{'parentpos'} } $lexeme->source_lexeme->get_derived_lexemes();
					
					if (@parents) { # It has succeeded. Better warn someone there might be something fishy going on.
						log_info('LINGUISTS BEWARE! Trying to attach ' . $lexeme->lemma . ' to ' . $parents[0]->lemma);
					}
				}
			
				return (0, \@parents);
			} else {
				#log_info( TODO );
			}
		} else {
			#log_info("\tRule '$rule_name' not applicable to '" . $lexeme->lemma . "', because parent '" . $lexeme->source_lexeme->lemma . "' doesn't match the expected wrong one $orig_lemma.");
		}
	} else {
		# Rule doesn't match
		return (0, undef);
	}
}

sub process_dictionary {
	my ($self, $dict) = @_;

	my $R;
	if ($self->{'file'}) {
		open $R, '<:utf8', $self->file
			or log_fatal('Cannot open file ' . $self->file . ": $!");
	} else {
		open $R, '<:utf8', $self->my_directory . 'manual.ReconnectVerbalDerivatives.rules.tsv'
			or log_fatal('Cannot open file ' . $self->my_directory . 'manual.ReconnectVerbalDerivatives.rules.tsv: ' . $!);
	}

	log_info('Loading rules');
	my @rules;
	my $any_rule_regex = qr/^$/;

	while (<$R>) {
		chomp;
		my $rule = $_;

		if ($rule =~ /^([ADNV])-(\w*)\t([ADNV])-(\w+)\t([ADNV])-(\w*)$/) {
			my $regex = qr/\Q$4\E$/;
			push @rules, {
				'rule'      => $rule,
				'regex'     => $regex,
				'pos'       => $3,
				'parent'    => $2,
				'parentpos' => $1,
				'orig'      => $6,
				'origpos'   => $5
			};
			$any_rule_regex = qr/$any_rule_regex|($regex$)/;
		}
	}

	# TODO finish and enable this
	#log_info('Loading negative instances');
	#open my $I, '<:utf8', $self->my_directory.'manual.ReconnectVerbalDerivatives.instances.tsv' or log_fatal($!);
	#while (<$I>) {
	#	next if /^[@#]/;
	#	if (/^wrong: (\w+) --> (\w+)\s+rule: (\w)-(\w*) --> (\w)-(\w*)$/) {
	#		my ($source_lemma, $target_lemma, $source_pos,$source_suffix,$target_pos,$target_suffix) = ($1,$2,$3,$4,$5,$6);
	#		# …
	#	}
	#}

	log_info('Processing lexemes');
	
	LEXEME:
	for my $lexeme ($dict->get_lexemes) {
		#log_info('Processing lexeme ' . $lexeme->lemma);
		
		if ($lexeme->lemma =~ $any_rule_regex and $lexeme->source_lexeme) {
			log_info('Found lexeme ' . $lexeme->mlemma . ' [' . $lexeme->source_lexeme->mlemma . ']');
		} else {
			next LEXEME;
		}
		
		RULE:
		for my $rule (@rules) {
			my $rule_name = $rule->{'rule'};
			#log_info("\tApplying rule $rule_name");
			my ($ok, $new_parents_ref) = get_parents_by_rule($rule_name, $rule, $lexeme, $self->aggressive, $dict);
			
			next LEXEME if $ok;
			
			if ($new_parents_ref) {
				if (!@$new_parents_ref) {
					# Everything was OK, we've tried to search for the new parent lexeme,
					#  but the array of results is empty → there is no such lexeme in the dictionary.
					my $rule_regex = $rule->{'regex'};
					my $parent_suffix = $rule->{'parent'};
					my $parent_lemma = $lexeme->lemma =~ s/$rule_regex/$parent_suffix/r;
					log_info("\tNo appropriate lexemes found for lemma $parent_lemma.");
					next RULE;
				}
				
				my $parent = $dict->select_best_parent_lexeme($lexeme, $new_parents_ref);
				
				log_fatal('ERROR: A parent for lemma ' . $lexeme->mlemma . " and rule '$rule_name' not found!") if (not $parent);

				log_info("\tAdding derivation " . $lexeme->mlemma . ' --> ' . $parent->mlemma);

				$dict->add_derivation({
					source_lexeme => $parent,
					derived_lexeme => $lexeme,
					deriv_type => $rule->{'parentpos'} . '2' . $rule->{'pos'},
					derivation_creator => $self->signature,
				});
				
				next LEXEME;
			}
		}
		
		log_info("\tNo rule satisfies " . $lexeme->mlemma);
	}

	return $dict;
}

1;
