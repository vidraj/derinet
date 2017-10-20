package Treex::Tool::DerivMorpho::Block::CS::AddManuallyConfirmedAutorules2;
use utf8;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';
use Treex::Core::Log;

#use CzechMorpho;
#my $analyzer = CzechMorpho::Analyzer->new();


sub process_dictionary {

    my ($self, $dict) = @_;

    open my $R, '<:utf8', $self->my_directory."manual.AddManuallyConfirmedAutorules2.rules.tsv" or log_fatal($!);
    my %allowed_rules;
    log_info("Loading rules");
    while (<$R>) {
        s/[\*\$]*//g;
        if (/^\+\s*\d+\s+(\w-\w* \w-\w+)/) {
            $allowed_rules{$1}++;
        }
    }

    log_info("Loading confirmed instances");
    open my $I, '<:utf8', $self->my_directory."manual.AddManuallyConfirmedAutorules2.instances.tsv" or log_fatal($!);
    while (<$I>) {
        next if /^@/;
        if (/^novy par: (\w+) --> (\w+)\s+pravidlo: (\w)-(\w*) --> (\w)-(\w*)/) {
            my ($source_lemma, $target_lemma, $source_pos,$source_suffix,$target_pos,$target_suffix) = ($1,$2,$3,$4,$5,$6);
            if ($allowed_rules{"$source_pos-$source_suffix $target_pos-$target_suffix"}) {

                print "Trying to add $source_lemma -> $target_lemma\n";
                my ($source_lexeme, $target_lexeme) = $dict->find_lexeme_pair($source_lemma,$source_pos,$target_lemma,$target_pos);

                if ($source_lexeme and $target_lexeme) {
                    print "  Success\n";
                    $dict->add_derivation({
                        source_lexeme => $source_lexeme,
                        derived_lexeme => $target_lexeme,
                        deriv_type => $source_pos.'2'.$target_pos,
                        derivation_creator => $self->signature,
                    });
                }
            }
        }
        else {
#            print "RULE LINE NOT MATCHING: $_\n";
        }
    }

    return $dict;
}

1;
