package Treex::Tool::Lexicon::CS;

# This source was taken and abbreviated from Treex Git commit e0895287440fba5b8172eefe037881c016519345 (Thu Oct 19 13:23:38 2017 +0200)

use strict;
use warnings;
use utf8;
use autodie;

# This truncates Czech morphological lemmas, leaving out the explanatory part.
# If the second parameter is set to true, the number for homonymous lemmas is truncated as well.
# See http://ufal.mff.cuni.cz/pdt2.0/doc/manuals/en/m-layer/html/ch02s01.html
sub truncate_lemma {
    my ($lemma, $strip_numbers) = @_;

    $lemma =~ s/((?:(`|_;|_:|_,|_\^|))+)(`|_;|_:|_,|_\^).+$/$1/;

    # Lemma cannot be empty (e.g. "`a la" instead of "à la" in ČNK)
    if ($lemma eq ''){
        $lemma = $_[0];
    }
    if ($strip_numbers){
        $lemma =~ s/(.+)-[0-9].*$/$1/;
    }
    return $lemma;
}

1;
