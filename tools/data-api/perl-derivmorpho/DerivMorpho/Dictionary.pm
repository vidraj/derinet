package Treex::Tool::DerivMorpho::Dictionary;

use utf8;

use Moose;
use MooseX::SemiAffordanceAccessor;
use Treex::Tool::DerivMorpho::Lexeme;
use Treex::Tool::Lexicon::CS qw(truncate_lemma);

use Treex::Core::Log;

use Scalar::Util qw(weaken);

use PerlIO::via::gzip;
use Storable;


has '_lexemes' => (
    is      => 'rw',
    isa     => 'ArrayRef',
    default => sub {[]},
    documentation => 'all lexemes loaded in the dictionary',
);

has '_lemma2lexemes' => (
    is      => 'rw',
    isa     => 'HashRef',
    default => sub {{}},
    documentation => 'an index that maps lemmas to lexeme instances',
);

has '_mlemma2lexeme' => (
    is      => 'rw',
    isa     => 'HashRef',
    default => sub {{}},
    documentation => 'an index that maps lemmas to lexeme instances',
);

has '_next_id' => (
    is      => 'rw', # Could be RO, but when we load a database from file, we have to reapply the exact same numbers.
    isa     => 'Num',
    default => 0,
    traits  => ['Counter'],
    handles => {
        _inc_id => 'inc',
        _set_id => 'set'
    },
    documentation => 'a number that will be used as an ID for the next lexeme created'
);

sub get_lexemes {
    my $self = shift @_;
    return @{$self->_lexemes};
}

sub create_lexeme {
    my ($self, $lexeme_param_map) = @_;

    my $new_lexeme = Treex::Tool::DerivMorpho::Lexeme->new($lexeme_param_map);
    $new_lexeme->_set_dictionary($self);
    weaken($new_lexeme->{_dictionary}); # to avoid memory leaks due to ref. cycles

    if ($lexeme_param_map->{_id}) { # We're thawing a lexeme that has already been assigned an ID
        if ($self->_next_id == $lexeme_param_map->{_id}) {
            # It came in-order. All is OK.
            $self->_inc_id;
        } elsif ($self->_next_id > $lexeme_param_map->{_id}) {
            # It has a lower lexeme number. This means it may overwrite an already existing lexeme.
            log_warn('Lexeme ID loaded out of order: ' . $lexeme_param_map->{_id} . ': ' . $lexeme_param_map->mlemma);
        } else {
            # It has a higher lexeme number. This means it will create a gap in the lexeme array, but that doesn't really matter.
            $self->_set_id($lexeme_param_map->{_id} + 1);
        }
    } else { # We're assigning a new ID.
        $new_lexeme->_set_id($self->_next_id);
        $self->_inc_id;
    }

    $self->_lexemes->[$new_lexeme->{_id}] = $new_lexeme;
    if ( $self->_lemma2lexemes->{$new_lexeme->lemma} ) {
        push @{$self->_lemma2lexemes->{$new_lexeme->lemma}}, $new_lexeme;
    }
    else {
        $self->_lemma2lexemes->{$new_lexeme->lemma} = [ $new_lexeme ];
    }
    return $new_lexeme;
}

sub get_lexemes_by_lemma {
    my ( $self, $lemma ) = @_;
    if (!$lemma) {
        log_warn("Attempted search for an empty/undefined lemma.");
        return [];
    }
    return @{$self->_lemma2lexemes->{$lemma} || []};
}

sub save {
    my ( $self, $filename ) = @_;

    if ( $filename =~ /\.slex$/ ) { # derivational lexicon in perl storable format
        open( my $F, ">:via(gzip)", $filename ) or log_fatal "Couldn't open $filename for writing: $!";
        print $F Storable::nfreeze($self) or log_fatal "Couldn't freeze $filename: $!";
        close $F;
        return;
    }

    elsif ( $filename =~ /\.tsv$/ ) {
#         $self->_set_lexemes( [ sort {$a->lemma cmp $b->lemma} $self->get_lexemes ] );

        open my $F, '>:utf8', $filename or die $!;

        foreach my $lexeme ($self->get_lexemes) {
            my $source_lexeme_number = $lexeme->source_lexeme ? $lexeme->source_lexeme->{_id} : '';

            if ($lexeme->lemma ne Treex::Tool::Lexicon::CS::truncate_lemma($lexeme->mlemma, 1)) {
                log_warn('Non-matching lemma ' . $lexeme->lemma . ' and techlemma ' . $lexeme->mlemma);
            }

            print $F join("\t",($lexeme->{_id},
                                $lexeme->lemma,
                                $lexeme->mlemma || '',
#                                 $lexeme->tag || ($lexeme->pos . '??????????????') || '',
                                $lexeme->pos || '',
                                $source_lexeme_number,
                                ($lexeme->deriv_type || '' ),
                                ($lexeme->lexeme_creator || '' ),
                                $lexeme->get_derivation_history,
                            )) . "\n";
        }

        close $F;
    }

    else {
        log_fatal("Unrecognized file ending: $filename\n");
    }

}

sub load {
    my ( $self, $filename, $argref ) = @_;

    my $filetype;
    if ($argref and $argref->{filetype}) {
        $filetype = $argref->{filetype};
    } else {
        $filetype = $filename;
    }

    if ( $filetype =~ /\.slex$/ ) {

        open my $FILEHANDLE, "<:via(gzip)", $filename or log_fatal("Couldn't open $filename for reading: $!");
        my $serialized;
        # reading it this way is silly, but both slurping the file or
        #  using Storable::retrieve_fd lead to errors when used with via(gzip)
        while (<$FILEHANDLE>) {
            $serialized .= $_;
        }
        my $retrieved_dictionary = Storable::thaw($serialized) or log_fatal "Couldn't thaw $filename: $!";

        # moving the content from the retrieved dictionary into the already existing instance
        # (risky)
        foreach my $key (keys %$retrieved_dictionary) {
            $self->{$key} = $retrieved_dictionary->{$key}
        }
        return $self;
    }

    elsif ( $filetype =~ /\.tsv$/ ) {

        $self->_set_lexemes([]);
        $self->_set_lemma2lexemes({});
        $self->_set_mlemma2lexeme({});

        my %derived_number_to_source_number;

        open my $F,'<:utf8',$filename or die $!;
        my $linenumber;
        while (<$F>) {
            chomp;
            $linenumber++;
            last if $argref and $argref->{limit} and $argref->{limit} < $linenumber;
            my ($number, $lemma, $mlemma, $pos, $source_lexeme_number, $deriv_type, $lexeme_creator, $derivation_creator) = split /\t/;
            my $new_lexeme = $self->create_lexeme({_id => $number,
                                                   lemma => $lemma,
                                                   mlemma => $mlemma,
                                                   pos => $pos,
                                               });
            if (defined($source_lexeme_number) and $source_lexeme_number ne '' and $source_lexeme_number =~ /^[0-9]+$/) {
                if ($deriv_type) {
                    $new_lexeme->set_deriv_type($deriv_type);
                }
                if ($derivation_creator) {
                    $new_lexeme->set_derivation_creator($derivation_creator);
                }
                if ($lexeme_creator) {
                    $new_lexeme->set_lexeme_creator($lexeme_creator);
                }
                $derived_number_to_source_number{$number} = $source_lexeme_number + 0;
            }
        }

        foreach my $derived_number (keys %derived_number_to_source_number) {
            my $derived_lexeme =  $self->_lexemes->[$derived_number];
            my $source_lexeme = $self->_lexemes->[$derived_number_to_source_number{$derived_number}];
            if ($source_lexeme) {
                $derived_lexeme->set_source_lexeme($source_lexeme);
            }
            else {
                log_warn("Non-existent numerical reference to source lexeme: $derived_number_to_source_number{$derived_number}");
            }
        }

        return $self;
    }

    else {
        log_fatal("Unrecognized file ending: $filetype\n");
    }


}

sub add_derivation {
    my ( $self, $arg_ref ) = @_;
    my ( $source_lexeme, $derived_lexeme, $deriv_type, $derivation_creator ) =
        map { $arg_ref->{$_} } qw(source_lexeme derived_lexeme deriv_type derivation_creator);

    log_fatal("Undefined source lexeme") if not defined $source_lexeme;
    log_fatal("Undefined derived lexeme") if not defined $derived_lexeme;

    log_fatal('Source and derived lexemes (' . $source_lexeme->mlemma . ') must not be identical') if $source_lexeme eq $derived_lexeme;

    my @derivation_path = ($derived_lexeme, $source_lexeme);
    my $lexeme = $source_lexeme->source_lexeme;
    while ($lexeme) {
        push @derivation_path, $lexeme;
        if ($lexeme eq $derived_lexeme) {
            log_info("The new derivation would lead to a loop: "
                 . join (" -> ", reverse map {$_->lemma} @derivation_path)."   No derivation added.");
            return;
        }
        $lexeme = $lexeme->source_lexeme;
    }

    $derived_lexeme->set_source_lexeme($source_lexeme);
    $derived_lexeme->set_deriv_type($deriv_type);
    $derived_lexeme->set_derivation_creator($derivation_creator) if $derivation_creator;

    return $source_lexeme;
}

sub _get_subtree_pos_signature {
    my ($self, $lexeme, $touched_rf) = @_;
    $touched_rf->{$lexeme} = 1;

    my $signature = $lexeme->pos;

    my @derived_lexemes = $lexeme->get_derived_lexemes;

    if (grep {$touched_rf->{$_}} @derived_lexemes and grep {not $touched_rf->{$_}} @derived_lexemes) {
        log_fatal("Something weird is going on here! I'm looking at lexeme: '" . $lexeme->mlemma . "'\n and children:\n"
                . join("\n", map { $_->mlemma . ($touched_rf->{$_} ? " (touched)" : " (not touched)") . "; parent='" . ($_->source_lexeme ? $_->source_lexeme->mlemma : '(nothing)') . "'" } @derived_lexemes)
                . "\nParent of this lexeme is '" . ($lexeme->source_lexeme ? $lexeme->source_lexeme->mlemma : "(nothing)") . "'\n");
    }

    if (@derived_lexemes and not grep {$touched_rf->{$_}} @derived_lexemes) { # prevent cycles
        my $child_signatures = join ',', sort map {$self->_get_subtree_pos_signature($_,$touched_rf)} @derived_lexemes;
        $signature .="->($child_signatures)"
    }
    return $signature;
}

sub _get_lexemes_for_lemma_pos {
    my ($self, $lemma, $pos) = @_;

    my @lexemes = $self->get_lexemes_by_lemma($lemma);

    if ($pos) {
        @lexemes = grep {$_->pos eq $pos} @lexemes;
    }

    if (!@lexemes) {
        log_info("No lexeme found for lemma=$lemma pos=$pos");
    }

    return @lexemes
}


sub select_best_parent_lexeme {
        my ($self, $lexeme, $parents_ref) = @_;
        
        if (!$parents_ref or !@$parents_ref) {
                return undef;
        } elsif (@$parents_ref == 1) {
                return $parents_ref->[0];
        }
        
        my $parent_w_correct_number;
        my $child_mlemma = $lexeme->mlemma;
        for my $parent (@$parents_ref) {
                if ($lexeme->source_lexeme and $lexeme->source_lexeme == $parent) {
                        return $parent;
                }
                
                my $child_number = $lexeme->get_homonym_number();
                my $parent_number = $parent->get_homonym_number();
                
                if ($child_number eq $parent_number) {
                        $parent_w_correct_number = $parent;
                }
        }
        
        if ($parent_w_correct_number) {
                log_info("Selecting a parent for $child_mlemma based on numbers.");
                return $parent_w_correct_number;
        }
        
        log_info("\tSelecting random candidate for $child_mlemma: " . $parents_ref->[0]->mlemma);
        return $parents_ref->[0];
}

sub find_lexeme_pair {
    my ($self, $source_lemma, $source_pos, $target_lemma, $target_pos) = @_;

    if (!$source_lemma or !$source_pos or !$target_lemma or !$target_pos) {
        log_warn('Undefined arguments supplied to find_lexeme_pair.');
        return (undef, undef);
    }

    my @source_candidates = $self->_get_lexemes_for_lemma_pos($source_lemma, $source_pos);
    my @target_candidates = $self->_get_lexemes_for_lemma_pos($target_lemma, $target_pos);

    # If one of them doesn't exist, we have no clues as to which candidate from the others to choose. Return the first one.
    if (!@source_candidates or !@target_candidates) {
        return (@source_candidates ? $source_candidates[0] : undef,
                @target_candidates ? $target_candidates[0] : undef);
    }

    if (@source_candidates == 1 and @target_candidates == 1) {
        # There is nothing to choose from.
        return ($source_candidates[0], $target_candidates[0]);
    }

    # Now there is more than one candidate in at least one of the arrays.

    # Try to find one that is already connected. If it is there, return it.
    for my $source_candidate (@source_candidates) {
        for my $target_candidate (@target_candidates) {
            if ($target_candidate->source_lexeme and $target_candidate->source_lexeme eq $source_candidate) {
                return ($source_candidate, $target_candidate);
            }
        }
    }

    # None of the candidates are connected.

    # Try to find a pair with matching homonym numbers.
    for my $source_candidate (@source_candidates) {
        for my $target_candidate (@target_candidates) {
            my $source_number = $source_candidate->get_homonym_number();
            my $target_number = $target_candidate->get_homonym_number();

            if ($source_number eq $target_number) {
                return ($source_candidate, $target_candidate);
            }
        }
    }

    # Last ditch effort – find a $target that doesn't have a source yet to at least connect something new.
    my @unconnected_targets = grep { !$_->source_lexeme } @target_candidates;

    # Nothing worked. Return any pair, e.g. the first ones.
    return ($source_candidates[0], (@unconnected_targets ? $unconnected_targets[0] : $target_candidates[0])); # TODO: kdyz se nenajde nic, mohl by se vytvorit
}

1;
