package Treex::Tool::DerivMorpho::Block::CS::AddManuallyConfirmedAutorules;
use Moose;
extends 'Treex::Tool::DerivMorpho::Block';
use Treex::Core::Log;

#use CzechMorpho;
#my $analyzer = CzechMorpho::Analyzer->new();

has rules => (
    is            => 'ro',
    isa           => 'Str',
    documentation => q(filename of the file with rules),
    default       => sub {
                my $self = shift;
                return $self->my_directory."manual.AddManuallyConfirmedAutorules.rules.tsv";
            },
);

has instances => (
    is            => 'ro',
    isa           => 'Str',
    documentation => q(filename of the file with confirmed instances),
    default       => sub {
                my $self = shift;
                return $self->my_directory."manual.AddManuallyConfirmedAutorules.instances.tsv";
            },
);

sub process_dictionary {

    my ($self, $dict) = @_;

    open my $R, '<:utf8', $self->rules or log_fatal($!);
    my %allowed_rules;
    log_info("Loading rules");
    while (<$R>) {
        if (/^\*\s*\d+\s+(\w-\w* \w-\w+)/) {
            $allowed_rules{$1}++;
        }
    }

    log_info("Loading confirmed instances");
    open my $I, '<:utf8', $self->instances or log_fatal($!);
    while (<$I>) {
        next if /^@/;
        if (/^novy par: (\w+) --> (\w+)\s+pravidlo: (\w)-(\w*) --> (\w)-(\w*)$/) {
            my ($source_lemma, $target_lemma, $source_pos,$source_suffix,$target_pos,$target_suffix) = ($1,$2,$3,$4,$5,$6);
            if ($allowed_rules{"$source_pos-$source_suffix $target_pos-$target_suffix"}) {


                my ($source_lexeme, $target_lexeme) = $dict->find_lexeme_pair($source_lemma,$source_pos,$target_lemma,$target_pos);

                if ($source_lexeme and $target_lexeme) {
                    if (!$target_lexeme->source_lexeme or $target_lexeme->source_lexeme ne $source_lexeme) {
                        $dict->add_derivation({
                            source_lexeme => $source_lexeme,
                            derived_lexeme => $target_lexeme,
                            deriv_type => $source_pos.'2'.$target_pos,
                            derivation_creator => $self->signature . ': ' . $self->instances,
                        });
                    }
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
