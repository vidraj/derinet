#!/usr/bin/env perl

use strict;
use warnings;

my $current_cluster;
while (<>) {
    $current_cluster .= $_;
    if (!/\w/) {
        if ($current_cluster =~ /CHANGE/sxm) {
            print $current_cluster;
        }
        $current_cluster = '';
    }
}
