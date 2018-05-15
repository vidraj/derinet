package Treex::Tool::DerivMorpho::Block::CS::AddConfirmedMluvCandidatesMonosource;
use utf8;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';
use Treex::Core::Log;

##### zapracovani dat od Magdy z emailu z 12.3., puvodni nazev souboru: vymazat_s_hvezdickou_ostatni_do_databaze


has file => (
    is            => 'ro',
    isa           => 'Str',
    documentation => q(file name to load),
);


sub process_dictionary {

    my ($self, $dict) = @_;
    
    my $file_name = ($self->file || $self->my_directory."manual.AddConfirmedMluvCandidatesMonosource.txt");

    open my $R, '<:utf8', $file_name or log_fatal($!);
    my %allowed_rules;
    log_info("Loading manually annotated instances");
    my ($source_pos,$source_suffix,$target_pos,$target_suffix);

  LINE:
    while (<$R>) {

        if ( /TRYING TO APPLY RULE (\w)-(\w+) --> (\w)-(\w+)/ ) { # TRYING TO APPLY RULE V-it --> N-ba
            ($source_pos,$source_suffix,$target_pos,$target_suffix) = ($1,$2,$3,$4);
        }

        elsif (/(\w+) --> (\w+)/) { # chodit --> chodba
            my ($source_lemma,$target_lemma) = ($1,$2);

            my ($source_lexeme, $target_lexeme) = $dict->find_lexeme_pair($source_lemma, $source_pos, $target_lemma, $target_pos);

            if (not $source_lexeme or not $target_lexeme) {
                # TODO: resolve nonexisting lexemes by manually adding them to the database.
                #  This is partially done manually by adding lexemes from extra_lexemes.tsv
                next LINE;
            }

            if (/\*/) {
                if ( $source_lexeme eq ($target_lexeme->source_lexeme()||'')) {
                    log_info('Deleting relation ' . $source_lexeme->mlemma . ' -> ' . $target_lexeme->mlemma . ' made by ' . ($target_lexeme->get_derivation_creator() || 'unknown author'));
                    $target_lexeme->set_source_lexeme(undef);
                }
            }

            else {
                if ( $source_lexeme eq ($target_lexeme->source_lexeme()||'')) {
                    log_info("LINK ALREADY PRESENT: $source_lemma -> $target_lemma");
                }
                else {
                    log_info("Adding new relation: $source_lemma -> $target_lemma");
                    $dict->add_derivation({
                        source_lexeme => $source_lexeme,
                        derived_lexeme => $target_lexeme,
                        deriv_type => $source_pos.'2'.$target_pos,
                        derivation_creator => $self->signature . ": $file_name",
                    });
                }
            }
        }
    }

    return $dict;
}

1;
