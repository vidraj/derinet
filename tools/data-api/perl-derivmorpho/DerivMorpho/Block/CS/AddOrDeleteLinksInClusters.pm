package Treex::Tool::DerivMorpho::Block::CS::AddOrDeleteLinksInClusters;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';
use Treex::Core::Log;


sub process_dictionary {

    my ($self, $dict) = @_;

    my $file_name = 'manual.RestructureClusters/s-hvezdickou-smazat_a_ostatni-do-databaze.txt';
    open my $R, '<:utf8', $self->my_directory . $file_name or log_fatal($!);

    while (<$R>) {

        my $to_delete = ($_ =~ s/^\s*\*\s*//);

        if (/^(\S+)\t(\S+)\t([A-Z])-.+?([A-Z]+)/) {
            my ($source_lemma, $target_lemma,$source_pos,$target_pos) = ($1,$2,$3,$4);

            my ($source_lexeme, $target_lexeme) = $dict->find_lexeme_pair($source_lemma, $source_pos, $target_lemma, $target_pos);

            if ($to_delete and /PRESENT/) {
                if ($source_lexeme and $target_lexeme and $source_lexeme eq ($target_lexeme->source_lexeme || '')) {
                    log_info("Deleting $source_lemma->$target_lemma");
                    $target_lexeme->set_source_lexeme(undef);
                }
            }

            if (not $to_delete and not /PRESENT/) {
                log_info("Trying to add $source_lemma -> $target_lemma");
                if ($source_lexeme and $target_lexeme) {
                    if ($target_lexeme->source_lexeme and $target_lexeme->source_lexeme eq $source_lexeme) {
                        log_info("\tLink already present.");
                    } else {
                        log_info("\tSuccess");
                        $dict->add_derivation({
                            source_lexeme => $source_lexeme,
                            derived_lexeme => $target_lexeme,
                            deriv_type => $source_pos . '2' . $target_pos,
                            derivation_creator => $self->signature # . ": $file_name", # Enable this if you ever need more than one filename.
		        });
                    }
                }

            }
        }
    }

    # TODO: hvezdicka je tam nekdy kvuli tomu, ze se par lemmat chybne objevuje dvakrat - doresit !!!

    return $dict;
}

1;
