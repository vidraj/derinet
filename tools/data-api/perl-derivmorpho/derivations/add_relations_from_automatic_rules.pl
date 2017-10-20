#!/usr/bin/env perl

use strict;
use warnings;

use Treex::Tool::Lexicon::DerivDict::Dictionary;
use Treex::Tool::Lexicon::CS;
use Treex::Tool::DerivMorpho::Lexeme;

my ( $rules_file, $input_file, $output_file ) = @ARGV;
if ( not $rules_file or not $input_file or not $output_file ) {
    die "Wrong usage";
}

my %rules;
open my $R, '<:utf8', $rules_file or die $!;
my $number_of_rules;

while (<$R>) {

    $number_of_rules++;
    last if $number_of_rules > 100;

    s/^\s\d+\s//;
    if (/([ADVN])-(\w*) ([ADVN])-(\w*)/) {
        my ($source_pos,$source_suffix,$target_pos,$target_suffix) = ($1,$2,$3,$4);
        $rules{$target_suffix}{$target_pos}{$source_suffix}{$source_pos} = 1;
    }
}


my $dict = Treex::Tool::Lexicon::DerivDict::Dictionary->new();
$dict->load($input_file);

TARGET:
foreach my $target_lexeme (grep {not $_->source_lexeme} $dict->get_lexemes) {
    my $target_lemma = $target_lexeme->lemma;

    foreach my $len (reverse(0..3)) { # nebo od nejkratsich?
#    print "X2\n";
        if ($target_lemma =~ /^(.+)(.{$len})$/) {
#    print "X3\n";
            my ($target_stem,$target_suffix) = ($1,$2);
            if ($rules{$target_suffix}{$target_lexeme->pos}) {
#    print "X4\n";
                foreach my $source_suffix (%{$rules{$target_suffix}{$target_lexeme->pos}}) {
#    print "X5\n";

                    my $source_lemma = $target_lemma;
                    $source_lemma =~ s/$target_suffix$/$source_suffix/ or die "tohle by se nikdy nemelo stat";

                    foreach my $source_lexeme ($dict->get_lexemes_by_lemma($source_lemma)) {
#    print "X6\n";
                        foreach my $source_pos (%{$rules{$target_suffix}{$target_lexeme->pos}{$source_suffix}}) {
#                            print "X7\n";
                            if ($source_lexeme->pos eq $source_pos) {
                                print "novy par: $source_lemma --> $target_lemma\t pravidlo: $source_pos-$source_suffix --> ".$target_lexeme->pos."-$target_suffix\n";

                                $dict->add_derivation({
                                    source_lexeme => $source_lexeme,
                                    derived_lexeme => $target_lexeme,
                                    deriv_type => $source_lexeme->pos."2".$target_lexeme->pos,
                                    derivation_creator => 'add_relations_from_automatic_rules.pl'
                                });
                                #next TARGET;
                            }

                        }
                    }
                }
            }
        }
    }
}


$dict->save($output_file);
