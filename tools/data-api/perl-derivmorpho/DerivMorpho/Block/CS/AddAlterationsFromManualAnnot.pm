package Treex::Tool::DerivMorpho::Block::CS::AddAlterationsFromManualAnnot;

use utf8;
use Moose;

extends 'Treex::Tool::DerivMorpho::Block';

use Treex::Core::Log;
# use Treex::Tool::Lexicon::CS;

has file => (
	is            => 'ro',
	isa           => 'Str',
	documentation => q(name of the file containing rules),
);

sub parse_second_line {
	my $second_line = shift;
	chomp $second_line;
	
	if ($second_line =~ /^    ([^# ]+)#([ADNV])$/) {
		return ($1, $2);
	} else {
		log_fatal("Error when parsing line '$second_line' as a second line.");
	}
}

# Eat second and third level lines
sub eat_nth_level_lines {
	my $handle = shift;
	
	my $line = $handle->getline();
	while ($line =~ /^    ([^# ]+#[ACDNV]|    [^# ]+ \+ rule .+ => .+ from .+)$/) {
		$line = $handle->getline();
		last if (!$line);
		chomp $line;
	}
}

sub add_lexeme {
	my ($self, $dict, $lemma, $pos) = @_;
	
	log_info("Adding new lexeme: $lemma-$pos.");
	
	return $dict->create_lexeme({
		lemma  => $lemma,
		mlemma => $lemma,
		pos => $pos,
		lexeme_creator => $self->signature,
	});
}

sub process_dictionary {
	my ($self, $dict) = @_;

	my $R;
	if ($self->{'file'}) {
		open $R, '<:utf8', $self->file
			or log_fatal('Cannot open file ' . $self->file . ": $!");
	}
	
	#### File structure documentation: see e-mail from Zdeněk :-)
	# Each record is structured into three levels; records are separated by vertical space.
	# 1st level: Hypothesized child + annotation
	# 2nd level: Parent
	# 3rd level: explanation for the derivation
	# 
	# > - dobře je nově navržený antecedent
	# > + lemma#pos navrhuju nový antecedent (použito i v případě, že vybírám jeden z
	# > více nabídnutých antecedentů)
	# > + NONE slovo má být bez předka (buď proto, že je to primární české slovo, nebo
	# > je třeba odvozené přímo z něčeho německého, nebo je to pravděpodobně
	# > neexistující slovo - třeba stolený / bubník / zubřský)
	# > + REVERSE to, co je navženo jako nový antecedent, má být dítětem řešeného
	# > lemmatu
	# > + OK správně je původní antecedent v DeriNet
	# 
	# TODO what to do when there are more 2nd level parents and the first level contains "-"?
	
	while (<$R>) {
		chomp;
		my $first_line = $_;
		
		while ($first_line =~ /^$/) {
			$first_line = $R->getline();
			chomp $first_line;
		}
		
		my ($parent_lemma, $parent_pos, $child_lemma, $child_pos);
		
		# Read and parse information about the two lexemes that are to be linked.
		if ($first_line =~ /^-\s+([^# ]+)#([ADNV])   \(antecedent in .*\)$/) {
			($child_lemma, $child_pos) = ($1, $2);
			($parent_lemma, $parent_pos) = parse_second_line($R->getline());
			
		} elsif ($first_line =~ /^\+\s+NONE\s+([^# ]+)#([ADNV])   \(antecedent in .*\)$/) {
			# No derivation
			($child_lemma, $child_pos) = ($1, $2);
# 			parse_second_line($R->getline()); # Verify that the file is structured properly, discarding the output.
			
			my @child_lexemes = grep { $_->pos eq $child_pos } $dict->get_lexemes_by_lemma($child_lemma);
			
			if (!@child_lexemes) {
				log_warn("Lexeme for lemma $child_lemma was not found, but we have to delete its source link!");
			}
			
			# Only select those that are actually derived
			@child_lexemes = grep { $_->source_lexeme } @child_lexemes;
			
			if (@child_lexemes) {
				log_info("Deleting links for lexeme(s) $child_lemma-$child_pos.");
				for my $child_lexeme (@child_lexemes) {
					$child_lexeme->set_source_lexeme(undef);
				}
			}
			
			eat_nth_level_lines($R);
			
			next;
			
		} elsif ($first_line =~ /^\+\s+REVERSE\s+([^# ]+)#([ADNV])   \(antecedent in .*\)$/) {
			($parent_lemma, $parent_pos) = ($1, $2);
			($child_lemma, $child_pos) = parse_second_line($R->getline());
			
		} elsif ($first_line =~ /^\+\s+OK\s+([^# ]+)#([ADNV])   \(antecedent in .*: ([^# ]+)#([ADNV])\)$/) {
			($child_lemma, $child_pos, $parent_lemma, $parent_pos) = ($1, $2, $3, $4);
# 			parse_second_line($R->getline()); # Verify that the file is structured properly, discarding the output.
			# TODO print a warning when the antecedent doesn't match
			
		} elsif ($first_line =~ /^[+!]\s+([^# ]+)#([ADNV])\s+([^# ]+)#([ADNV])   \(antecedent in .*\)$/) {
			($parent_lemma, $parent_pos, $child_lemma, $child_pos) = ($1, $2, $3, $4);
# 			parse_second_line($R->getline()); # Verify that the file is structured properly, discarding the output.
			
		} else {
			# TODO error
			log_fatal("Fucked up when processing line '$first_line'");
		}
		
		# Eat the rest of the second and third lines
		eat_nth_level_lines($R);
		
		
		# Information about both the parent and the child is filled in now.
		
		
		# Get proper lexemes
		my ($parent_lexeme, $child_lexeme) = $dict->find_lexeme_pair($parent_lemma, $parent_pos, $child_lemma, $child_pos);
		
		
		if (!defined $parent_lexeme) {
			$parent_lexeme = add_lexeme($self, $dict, $parent_lemma, $parent_pos);
		}
		
		if (!defined $child_lexeme) {
# 			$child_lexeme = add_lexeme($self, $dict, $child_lemma, $child_pos);
			log_warn("Child $child_lemma not found, skipping.");
			next;
		}
		
		
		if ($child_lexeme->source_lexeme and ($child_lexeme->source_lexeme eq $parent_lexeme)) {
			log_info("The derivation $parent_lemma -> $child_lemma is already correct.");
		} elsif ($child_lexeme->source_lexeme) {
			log_info("The lexeme $child_lemma is already derived, but from " . $child_lexeme->source_lexeme->lemma . " and not from $parent_lemma.");
			$dict->add_derivation({
				source_lexeme => $parent_lexeme,
				derived_lexeme => $child_lexeme,
				deriv_type => $parent_pos . '2' . $child_pos,
				derivation_creator => $self->signature,
			});
		} else {
			log_info("Adding derivation $parent_lemma -> $child_lemma.");
			$dict->add_derivation({
				source_lexeme => $parent_lexeme,
				derived_lexeme => $child_lexeme,
				deriv_type => $parent_pos . '2' . $child_pos,
				derivation_creator => $self->signature,
			});
		}
	}
	
	
	close $R
		or log_fatal('Error closing file ' . $self->file . ": $!");
	
	return $dict;
}

1;
