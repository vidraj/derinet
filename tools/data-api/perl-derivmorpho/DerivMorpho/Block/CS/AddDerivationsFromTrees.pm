package Treex::Tool::DerivMorpho::Block::CS::AddDerivationsFromTrees;

use utf8;
use Moose;

extends 'Treex::Tool::DerivMorpho::Block';

use Treex::Core::Log;
use Treex::Tool::Lexicon::CS;

has file => (
	is            => 'ro',
	isa           => 'Str',
	documentation => q(name of the file containing the trees),
);

has ignore_missing => (
	is            => 'ro',
	isa           => 'Bool',
	documentation => q(in case a lexeme cannot be found, derive its children from its parent),
);

has pos => (
	is            => 'ro',
	isa           => 'Str',
	documentation => q(the part-of-speech of the lemmas in file),
);

sub get_lexeme_by_lemma {
	my ($self, $dict, $lemma) = @_;
	
	my $short_lemma = Treex::Tool::Lexicon::CS::truncate_lemma($lemma, 1); # Strip (optional) homonym numbers.
	my @lexemes = grep { $_->pos eq $self->pos } $dict->get_lexemes_by_lemma($short_lemma);
	
	if (@lexemes > 1) {
		# Multiple variants found.
		# But the $lemma may contain homonym numbers that distinguish variants.
		if ($short_lemma ne $lemma) {
			# There is special information at the end of $lemma. Filter only those lexemes that match this information.
			my @filtered_lexemes = grep { Treex::Tool::Lexicon::CS::truncate_lemma($_->mlemma, 0) eq $lemma } @lexemes;
			if (@filtered_lexemes > 0) {
				# … and there are some lexemes that do match.
				@lexemes = @filtered_lexemes;
			} # If there are no matching lexemes, just ignore the homonym numbers entirely and connect to a randomly-chosen one.
		}
	}
	
	if (@lexemes == 0) {
		log_warn("Lexeme '$lemma' not found.");
		return undef;
	} elsif (@lexemes > 1) {
		# If there are still multiple lexemes to choose from, issue a warning.
		log_warn("Lexeme '$lemma' has multiple variants: " . join(', ', map {$_->mlemma} @lexemes));
	}
	
	return $lexemes[0];
}

sub parse_children {
	my ($self, $dict, $parent, $tokens_ref) = @_;
	
	log_fatal("Broken structure: expected a list of children but didn't find a paren.") if (pop(@$tokens_ref) ne '(');
	
	my $child_lemma = pop @$tokens_ref;
	while ($child_lemma ne ')') {
		my $child = get_lexeme_by_lemma($self, $dict, $child_lemma);
		if (not defined $child) {
			# If the following token is '(', we have to eat everything until the next matching ')'
			if ($tokens_ref->[-1] eq '(') {
				log_warn('That missing lexeme has children!');
				if ($self->ignore_missing) {
					# Hang these below the current parent, instead of the missing parent.
					parse_children($self, $dict, $parent, $tokens_ref);
				} else {
					# Don't add the children, just eat their tokens.
					parse_children($self, $dict, undef, $tokens_ref);
				}
			}
			
			$child_lemma = pop @$tokens_ref;
			next;
		}
		
		if ($parent) {
			log_info('Adding derivation ' . $parent->lemma . " -> $child_lemma.");
			$dict->add_derivation({
				source_lexeme => $parent,
				derived_lexeme => $child,
				deriv_type => $parent->pos . '2' . $child->pos,
				derivation_creator => $self->signature,
			});
		}
		
		# If children follow, add them too.
		if ($tokens_ref->[-1] eq '(') {
			parse_children($self, $dict, $child, $tokens_ref);
		}
		
		$child_lemma = pop @$tokens_ref;
	}
}

sub process_dictionary {
	my ($self, $dict) = @_;

	my $R;
	if ($self->{'file'}) {
		open $R, '<:utf8', $self->file
			or log_fatal('Cannot open file ' . $self->file . ": $!");
	}
	
	#### File structure documentation: Self-explanatory bracketed derivation trees; each tree on a single line.
	# Example:
	#  bojovat ( vybojovat ( vybojovávat ) probojovat ( probojovávat ) )
	#
	# means bojovat ─┬─> vybojovat ──> vybojovávat
	#                └─> probojovat ──> probojovávat
	
	
	while (<$R>) {
		chomp;
		my $line = $_;
		
		# Tokenize on whitespace and convert the resulting array into a stack.
		my @tokens = reverse split /\s+/, $line;
		
		if (@tokens < 2) {
			log_warn("Line '$line' is too short.");
		}
		
		my $first_lexeme = get_lexeme_by_lemma($self, $dict, pop @tokens);
		next unless defined $first_lexeme;
		
		parse_children($self, $dict, $first_lexeme, \@tokens);
	}
	
	
	close $R
		or log_fatal('Error closing file ' . $self->file . ": $!");
	
	return $dict;
}

1;
