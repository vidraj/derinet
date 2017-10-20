package Treex::Tool::DerivMorpho::Block::PrintStats;
use utf8;
use Moose;

extends 'Treex::Tool::DerivMorpho::Block';

use Treex::Core::Log;

has singletons_file => (
    is => 'ro',
    isa => 'Str',
    documentation => q(filename for saving a list of all singleton clusters in the database)
);

sub process_dictionary {
    my ($self,$dict) = @_;

    my %pos_cnt;
    my %pos2pos_cnt;
    my $relations_cnt = 0;
    my %derived_lexemes_cnt;
    my %lemmas;
    my %deriv_creators_cnt;

    foreach my $lexeme ($dict->get_lexemes) {
        $pos_cnt{$lexeme->pos}++;
        if ($lexeme->source_lexeme) {
            $relations_cnt++;
            $pos2pos_cnt{$lexeme->source_lexeme->pos."2".$lexeme->pos}++
        }

        $derived_lexemes_cnt{scalar($lexeme->get_derived_lexemes)}++;

        $lemmas{$lexeme->lemma}++;

        my $deriv_creator = $lexeme->source_lexeme ? ($lexeme->get_derivation_creator() || 'unknown') : 'no parent';
        $deriv_creators_cnt{$deriv_creator}++;
    }

    print "LEXEMES\n";
    print "  Number of lexemes: ".scalar(@{$dict->_lexemes})."\n";
    print "  Number of lexemes by part of speech:\n";
    foreach my $pos (sort {$pos_cnt{$b}<=>$pos_cnt{$a}} keys %pos_cnt) {
        print "    $pos $pos_cnt{$pos}\n";
    }
    print "  Number of lemmas: " . scalar(keys %lemmas) . "\n";

    print "\nDERIVATIVE RELATIONS BETWEEN LEXEMES\n";
    print "  Total number of derivative relations: $relations_cnt\n";
    print "  Types of derivative relations (POS-to-POS):\n";
    foreach my $pos2pos (sort {$pos2pos_cnt{$b}<=>$pos2pos_cnt{$a}} keys %pos2pos_cnt) {
        print "    $pos2pos $pos2pos_cnt{$pos2pos}\n";
    }

    print "  Number of lexemes immediately derived from a lexeme:\n";
    foreach my $derived (sort {$derived_lexemes_cnt{$b}<=>$derived_lexemes_cnt{$a}} keys %derived_lexemes_cnt) {
        print "    $derived $derived_lexemes_cnt{$derived}\n";
    }

    print "\nModules by productivity:\n"
        . join("\n", map { "$_: " . $deriv_creators_cnt{$_} } sort { $deriv_creators_cnt{$b} <=> $deriv_creators_cnt{$a} } keys %deriv_creators_cnt)
        . "\n\n";

    print "\nDERIVATIONAL CLUSTERS\n";

    my %signature_cnt;
    my %signature_example;
    my %touched;
    my %cluster_sizes;
    my %roots;
    my $max_depth = 0;
    my $i;

    foreach my $lexeme ($dict->get_lexemes) {
        my $root = $lexeme->get_root_lexeme;
        $cluster_sizes{$root}++;
        $roots{$root} = $root;

        my $depth_sound = $lexeme;
        my $depth = 1;
        while ($depth_sound->source_lexeme) {
            $depth++;
            $depth_sound = $depth_sound->source_lexeme;
            if ($depth > 10000) { # TODO add proper cycle detection
                log_warn("A probable cycle detected around lemma " . $depth_sound->lemma);
                $depth = 0;
                last;
            }
        }
        $max_depth = $depth if $depth > $max_depth;

        if (not $touched{$lexeme}) {
            my $signature = $dict->_get_subtree_pos_signature($root,\%touched);
            $signature_cnt{$signature}++;
            $signature_example{$signature}{$root->lemma} = 1;
        }
    }

    my %sizes;
    map { $sizes{$cluster_sizes{$_}}++; } keys %cluster_sizes;
    my @sorted_sizes = sort { $b <=> $a } keys %sizes;

    if ($self->singletons_file) {
        open my $SINGLE, '>:utf8', $self->singletons_file or log_fatal("Couldn't open file '" . $self->singletons_file. ": $!");

        print $SINGLE join("\n", sort map { $roots{$_}->lemma . "\t" . $roots{$_}->mlemma . "\t" . $roots{$_}->pos; } grep { $cluster_sizes{$_} == 1 } keys %roots);

        close $SINGLE;
    }

    print "  Biggest cluster: " . $sorted_sizes[0] . "\n"
        . "  Number of singleton clusters: " . $sizes{'1'} . "\n"
        . "  Number of clusters: " . scalar(keys %roots) . "\n"
        . "  Maximal cluster depth: $max_depth\n\n"
        . "  Sizes of clusters:\n    " . join("\n    ", (map { "$_:\t" . $sizes{$_} } @sorted_sizes)) . "\n\n";

    print "  Types of derivational clusters:\n";
    my @signatures = sort {$signature_cnt{$b}<=>$signature_cnt{$a}} keys %signature_cnt;
    foreach my $signature (@signatures) {
        print "    $signature_cnt{$signature} $signature: ";
        my @examples = keys %{$signature_example{$signature}};
        print join " ",grep {$_} @examples[0..20];
        print "\n";
    }

    return $dict;
}

1;
