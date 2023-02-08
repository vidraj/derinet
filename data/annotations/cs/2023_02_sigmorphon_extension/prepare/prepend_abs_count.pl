#!/usr/bin/perl

while(<>) {
    if (/"absolute_count": (\d+)/) {
	print "$1\t$_"
    }

}
    
