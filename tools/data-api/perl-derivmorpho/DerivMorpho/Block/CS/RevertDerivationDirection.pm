package Treex::Tool::DerivMorpho::Block::CS::RevertDerivationDirection;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';
use Treex::Core::Log;

##### zapracovani dat od Magdy z emailu z 12.3., puvodni nazev souboru: vymazat_s_hvezdickou_ostatni_do_databaze

has file => (
    is            => 'ro',
    isa           => 'Str',
    documentation => q(file name to store),
);

sub process_dictionary {

    my ($self, $dict) = @_;

    my $filename = $self->file ||  $self->my_directory."manual.RevertDerivationDirection.txt";

    open my $R, '<:utf8', $filename or log_fatal($!);
    log_info("Loading manually annotated instances from $filename");


  LINE:
    while (<$R>) {

        if (/(\w+) --> (\w+)/) { # analytik --> analytika
            my ($target_lemma,$source_lemma) = ($1,$2);

            my ($source_lexeme, $target_lexeme) = $dict->find_lexeme_pair($source_lemma, 'N', $target_lemma, 'N');

            if (not $source_lexeme or not $target_lexeme) {
                # TODO: resolve nonexisting lexemes
                next LINE;
            }

            if ( $target_lexeme eq ($source_lexeme->source_lexeme()||'')) {
                print "OPPOSITE LINK ALREADY PRESENT: $source_lemma -> $target_lemma\n";
                $source_lexeme->set_source_lexeme(undef);
            }

            print "Adding new relation: $source_lemma -> $target_lemma\n";
            $dict->add_derivation({
                source_lexeme => $source_lexeme,
                derived_lexeme => $target_lexeme,
                deriv_type => 'N2N',
                derivation_creator => $self->signature,
            });
        }
    }

    return $dict;
}

1;
