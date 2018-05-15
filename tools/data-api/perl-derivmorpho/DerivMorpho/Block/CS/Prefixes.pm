package Treex::Tool::DerivMorpho::Block::CS::Prefixes;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';

use utf8;

sub process_dictionary {

    my ($self, $dict) = @_;

    foreach my $lexeme ( grep {not $_->source_lexeme} $dict->get_lexemes ) {

        if ($lexeme->lemma =~ /^(pseudo|mikro|anti|dys|meta|super|pra)(.+)/) {
            my $deprefixed_lemma = $2;
            next if $lexeme->lemma =~ /^(antika|antikorový|antikující|antilský|prach|pracák|prahnout|prahnutí|prahnutý|prajs|prakšicky|prakšický|pralinka|pralinkový|pranosticky|pranostický|prase|prasecí|prasetník|prasečení|prasečený|prasečící|prasitelný|praskot|praskací|praskaný|pravačka|pravice|pravidlový|pravička|pravívací|pravívající|pravívaný|pravívat|pravívatelný|pravívání|pravívávací|pravívávající|pravívávaný|pravívávat|pravívávatelný|pravívávání|praženka|pražitel|pražitelka|pražitelný|pražitelčin|pražitelův|metadon|metalista|metamorficky)$/;

            my ($source_lexeme) = grep {$_->pos eq $lexeme->pos} $dict->get_lexemes_by_lemma($deprefixed_lemma); # TODO add homonym number chooser

            ## Try to find an appropriate lexeme by uppercasing the deprefixed lemma.
            ##  Connects antikrist to Krist, but also pražan to Žan etc. Not worth it.
            #if (!$source_lexeme) {
            #    ($source_lexeme) = grep {$_->pos eq $lexeme->pos} $dict->get_lexemes_by_lemma(ucfirst($deprefixed_lemma));
            #    if ($source_lexeme) {
            #        log_info('Uppercased ' . $lexeme->lemma . ' to get ' . ucfirst($deprefixed_lemma));
            #    }
            #}

            if ($source_lexeme) {
#                print $source_lexeme->lemma ." --> ".$lexeme->lemma."\n";
                $dict->add_derivation({
                    source_lexeme => $source_lexeme,
                    derived_lexeme => $lexeme,
                    deriv_type => $source_lexeme->pos."2".$lexeme->pos,
                    derivation_creator => $self->signature,
                });
            }
        }
    }

    return $dict;
}


1;
