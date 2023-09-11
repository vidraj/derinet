package Treex::Tool::Lexicon::Generation::CS;

use feature 'unicode_strings';
use Encode qw(decode);
use Moose;
use Treex::Core::Log;
use Ufal::MorphoDiTa;

has dict_name => (is=>'ro', isa=>'Str', default=>'czech-morfflex2.0-220710.dict');
has dict_path => (is=>'ro', isa=>'Str', lazy_build=>1);
has tool  => (is=>'ro', lazy_build=>1);

sub _build_dict_path {
    my ($self) = @_;
    return decode('UTF-8', $ENV{'DERIMOR_MAIN_DIR'}) . '/data/models/morphodita/cs/' . $self->dict_name;
}

# tool can be shared by more instances (if the dictionary file is the same)
my %TOOL_FOR_PATH;
sub _build_tool {
    my ($self) = @_;
    my $path = $self->dict_path;
    my $tool = $TOOL_FOR_PATH{$path};
    return $tool if $tool;
    $tool = Ufal::MorphoDiTa::Morpho::load($path) or log_fatal("Can't load morphology from '$path'");
    $TOOL_FOR_PATH{$path} = $tool;
    return $tool;
}

# Shared global variables
my $lemmas_forms = Ufal::MorphoDiTa::TaggedLemmasForms->new();
my $tagged_lemmas = Ufal::MorphoDiTa::TaggedLemmas->new();

sub BUILD {
    my ($self) = @_;
    # The tool is lazy_build, so load it now
    $self->tool;
    return;
}

sub analyze_form {
    my ($self, $form, $use_guesser) = @_;
    $use_guesser = $use_guesser ? $Ufal::MorphoDiTa::Morpho::GUESSER : $Ufal::MorphoDiTa::Morpho::NO_GUESSER;
    $self->tool->analyze($form, $use_guesser, $tagged_lemmas);
    my @analyzes;
    for my $i (0 .. $tagged_lemmas->size()-1){
          my $tagged_lemma = $tagged_lemmas->get($i);
          push @analyzes, {tag=>$tagged_lemma->{tag}, lemma=>$tagged_lemma->{lemma}};
    }
    return @analyzes;
}

1;

__END__

=head1 NAME

Treex::Tool::Lexicon::Generation::CS

=head1 SYNOPSIS

 use Treex::Tool::Lexicon::Generation::CS;
 my $generator = Treex::Tool::Lexicon::Generation::CS->new();
 
 ### ANALYZIS
 my @analyzes = $generator->analyze_form('stane');
 my $use_guesser = 1;
 foreach my $an (@analyzes, $use_guesser) {
     print "$an->{tag} $an->{lemma}\n";
 }

=head1 DESCRIPTION

Wrapper for state-of-the-art Czech morphological analyzer and synthesizer MorphoDiTa
by Milan Straka and Jana Straková.

=head1 TODO

rename this module, as it now offers not only synthesis, but also analyzis

=head1 AUTHOR

Martin Popel <popel@ufal.mff.cuni.cz>

=head1 COPYRIGHT AND LICENSE

Copyright © 2014 by Institute of Formal and Applied Linguistics, Charles University in Prague

This module is free software; you can redistribute it and/or modify it under the same terms as Perl itself.
