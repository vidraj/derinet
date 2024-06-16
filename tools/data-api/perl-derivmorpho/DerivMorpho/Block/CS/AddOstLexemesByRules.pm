package Treex::Tool::DerivMorpho::Block::CS::AddOstLexemesByRules;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

use utf8;

use Treex::Core::Log;
use Treex::Tool::Lexicon::CS;
use Treex::Tool::Lexicon::Generation::CS;

has add_lexemes => (
    is => 'ro',
    isa => 'Bool',
    documentation => q(create required lexemes if not already present in the database)
);

sub acceptable_adj { # adjectives that are not recognized by JH's morphology but are more or less acceptable
    my $adj = shift;
    return $adj =~ /^(bezdějinný|bezprincipiální|dosebezahleděný|držebný|dvojpolární|dvojtvářný|glasný|házivý|jaký|kazivý|kovnatý|mačkavý|metaznalý|mikrotvrdý|mrtvorozený|nasáklivý|neprůzvučný|neslučivý|obložný|osobivý|podposloupný|podujatý|podzaměstnaný|prazkušený|propojištěný|pseudoskutečný|pseudoudálý|pufrovitý|pórézní|předvádivý|přináležitý|příležitý|působný|různočnělečný|sebedůležitý|sebelítý|sebezahleděný|slučivý|soběpodobný|soudružný|soumezný|spolupůsobný|střečkovitý|subkontrární|supermocný|supermožný|svalovčitý|ujímavý|videospolečný|vzcházivý|váživý|špinivý|žánrovitý)$/
}

sub process_dictionary {
    my ($self,$dict) = @_;

    my $analyzer = Treex::Tool::Lexicon::Generation::CS->new();


    my %non_deadj;
    open my $N, '<:utf8', $self->my_directory.'/manual.AddOstLexemesByRules.nondeadjective.tsv' or die $!;
    while (<$N>) {
        chomp;
        my ($noun,$source) = split /\t/;
        $non_deadj{$noun} = 1;
    }

    open my $R, '<:utf8',  $self->my_directory.'/manual.AddOstLexemesByRules.suffix.tsv' or die $!;

    # Eat the first line, which contains comments.
    readline $R;

    my @rules;
    while (<$R>) {
        next if $.==0;
        chomp;

        s/, +/,/g;
        s/\s/\|/g;
        my ($old_suffix, $new_suffix, $type, $dummy, $exceptions, $exception_type) = split /\|/;

        next if not $old_suffix;

        if ($dummy ne '') {
            # Process exceptional exceptions.
            $dummy =~ s/\s//g;
            foreach my $exception (split /,/, $dummy) {
                log_info("Processing phonological change $exception.");
                my ($noun, $source) = split /</, $exception;
                if ($noun and $source) {
                    # Prevent further analysis of this noun.
                    $non_deadj{$noun} = 1;

                    # Add derivation according to the annotation.
                    my ($source_lexeme, $target_lexeme) = $dict->find_lexeme_pair($source, 'A', $noun, 'N');
                    log_info('Adding exceptional derivation ' . $source_lexeme->mlemma . ' -> ' . $target_lexeme->mlemma);
                    $dict->add_derivation({
                        source_lexeme => $source_lexeme,
                        derived_lexeme => $target_lexeme,
                        deriv_type => 'A2N',
                        derivation_creator => $self->signature,
                    });
                } else {
                    log_warn("Malformatted phonological exception '$exception' in string '$dummy' found.")
                }
            }
        }

        my $rule = {
            old_suffix => $old_suffix,
            new_suffix => $new_suffix,
            type => $type,
            exceptions => {},
            exception_type => $exception_type,
        };

        if ($exceptions) {
            $exceptions =~ s/\s//g;
            foreach my $exception (split /,/,$exceptions) {
                $rule->{exceptions}{$exception} = 1;
                #            log_info("old: $old_suffix EX: $exception");
            }
        }

        push @rules, $rule;
    }



    foreach my $lexeme ($dict->get_lexemes) {
        if ( $lexeme->lemma =~ /ost$/ and $lexeme->pos eq 'N'
                 and $lexeme->lemma !~ /\p{IsUpper}/
                     and not $non_deadj{$lexeme->lemma} ) {
            my $orig_source_lexeme = $lexeme->source_lexeme;

            my $success;
            my $msg;
          RULES:
            foreach my $rule (@rules) {
                my $old_suffix = $rule->{old_suffix};
                my $new_suffix = $rule->{new_suffix};
#            log_info("Trying rule $old_suffix");

                my $source_lemma = $lexeme->lemma;
                if ($old_suffix eq 'ičnost') { # this rule is exceptional and must be hardwired (3 types of derivations)
                    log_info("Got exceptional word with -ičnost: $source_lemma");
                    if ( $source_lemma =~
                             /^(antimoničnost|bromičnost|dusičnost|jodičnost|břidličnost|červenopšeničnost|cvičnost|dědičnost|hořčičnost|krupičnost|kukuřičnost|kvasničnost|kýchavičnost|křivičnost|medovohořčičnost|motoličnost|mravoličnost|mrtvičnost|neštovičnost|nedědičnost|olejopryskyřičnost|prostocvičnost|protikřivičnost|pryskyřičnost|pšeničnost|přerozličnost|příjičnost|siřičnost|soupatřičnost|spolupatričnost|spolupatřičnost|patřičnost|tělocvičnost|úplavičnost|ustavičnost|ústřičnost|vichřičnost|zimničnost|záličnost|žitnopšeničnost|živičnost|doličnost|rozličnost|sličnost|přesličnost|dýchavičnost)$/
                        # desetislabičnost, dvaatřicetislabičnost, různoslabičnost, šestiradličnost etc.
                        or $source_lemma =~ /slabičnost$|radličnost$/ ) {
                        $new_suffix = 'ičný';
                    }
                    elsif ( $source_lemma =~ /^(tradičnost|kontradičnost|netradičnost|hraničnost|bezhraničnost|polovičnost|opozičnost|oposičnost|kompozičnost|podbráničnost|bráničnost)$/ ) {
                        $new_suffix = 'iční';
                    }
                    else {
                        $new_suffix = 'ický';
                    }
                }

                elsif ($lexeme->lemma =~ /$old_suffix/ and $rule->{exceptions}{$lexeme->lemma}) {
                    log_info("EXCEPTION catched: before $new_suffix");
                    $new_suffix =~ s/ý$/í/ or $new_suffix =~ s/í$/ý/;
                    log_info("\tafter: $new_suffix");
                }

                if ($source_lemma =~ s/$old_suffix$/$new_suffix/) {
                    my $check_source_lexeme;
                    if ($orig_source_lexeme) {
                        if ($orig_source_lexeme->lemma eq $source_lemma) {
                            $msg =  "SITUATION-1 - unchanged source lemma\t noun=".$lexeme->lemma." JH=rules=".$source_lemma;
                        }
                        else {
                            $msg = "SITUATION-2 - different source lemma\t noun=".$lexeme->lemma
                                ." JH=".$orig_source_lexeme->lemma." rules=$source_lemma";
                            $check_source_lexeme = 1;
                        }
                    }
                    else {
                        $msg = "SITUATION-3 - no source lexeme specified before\t noun=".$lexeme->lemma
                            ." rules=$source_lemma";
                        $check_source_lexeme = 1;
                    }

                    if ($check_source_lexeme) {
                        my @new_source_lexemes = grep { $_->pos eq 'A'} $dict->get_lexemes_by_lemma($source_lemma);
                        my $new_source_lexeme = $dict->select_best_parent_lexeme($lexeme, \@new_source_lexemes);

                        if (not $new_source_lexeme) {
                            my @long_lemmas = map { $_->{lemma} } grep { $_->{tag} =~ /^AAMS1/ and $source_lemma eq Treex::Tool::Lexicon::CS::truncate_lemma($_->{lemma}, 1) } $analyzer->analyze_form($source_lemma);
                            # TODO: muze jich byt vic, nemusi byt zadny

                            if (@long_lemmas==0 and not acceptable_adj($source_lemma)) {
                                log_info("ERROR: no analysis for new source lemma $source_lemma");
                            }
                            
                            my $long_lemma = $long_lemmas[0] || $source_lemma;

                            if ($self->add_lexemes) {
                                $new_source_lexeme = $dict->create_lexeme({
                                    lemma  => $source_lemma,
                                    mlemma => $long_lemma,
                                    pos => 'A',
                                    lexeme_creator => $self->signature,
                                });
                                log_info("NEW LEXEME CREATED: $source_lemma");
                            }
                            else {
                                log_warn("NEW LEXEME SHOULD BE CREATED: $source_lemma");
                            }
                        }

                        if ($new_source_lexeme) {
                            log_info('Adding derivation ' . $new_source_lexeme->mlemma . ' -> ' . $lexeme->mlemma);
                            $dict->add_derivation({
                                source_lexeme => $new_source_lexeme,
                                derived_lexeme => $lexeme,
                                deriv_type => 'A2N',
                                derivation_creator => $self->signature,
                            });
                        }
                    }

                    $success = 1;
                    last RULES;
                }
            }

            if (not $success) {
                $msg = "SITUATION-0 - no rule applies\t noun=".$lexeme->lemma;
            }

            log_info($msg);

        }
    }

    return $dict;
}

1;
