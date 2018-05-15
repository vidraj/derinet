#!/usr/bin/env perl

use strict;
use warnings;

use Treex::Tool::Lexicon::DerivDict::Dictionary;
use Treex::Tool::Lexicon::CS;

my ( $input_file ) = @ARGV;

my $dict = Treex::Tool::Lexicon::DerivDict::Dictionary->new();
$dict->load($input_file);

$dict->print_statistics;
