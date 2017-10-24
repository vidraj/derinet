#!/usr/bin/env perl

use utf8;
use strict;
use warnings;
use feature 'unicode_strings';

binmode STDIN, "utf8";
binmode STDOUT, "utf8";
binmode STDERR, "utf8";

my $old_db_name = $ARGV[0];
my $new_db_name = $ARGV[1];

my $retval = 0; # The final return value. This is set to 1 on recoverable errors.


sub read_db {
	my $filename = shift;
	open my $db_file, '<:encoding(UTF-8)', $filename
		or die "Can't open file $filename: $!\n";
	
	my @db;
	my %lemma_db;
	
	# Read lexemes, objectify them and store into @db
	while (<$db_file>) {
		chomp;
		my $line = $_;
		my ($id, $lemma, $techlemma, $pos, $parent_id) = split /\t/, $line;
		
		# TODO check that all the required fields have been successfully parsed.
		unless ($id =~ /^[0-9]+$/ and $lemma and $techlemma and $pos and $parent_id =~ /^[0-9]*$/) {
			die "Line '$line' is not parseable.\n";
		}
		
		if (defined $db[$id]) {
			die "ID $id defined multiple times!\n";
		}
		
		$db[$id] = {
			id => $id,
			lemma => $lemma,
			techlemma => $techlemma,
			pos => $pos,
			parent_id => $parent_id,
			parent => undef,
		};
	}
	
	for my $lexeme (@db) {
		next unless $lexeme; # IDs don't have to be strictly sequential. Skip nonexisting ones.
		
		my $lemma = $lexeme->{lemma} . '#' . $lexeme->{pos};
		
		if ($lexeme->{parent_id}) {
			$lexeme->{parent} = $db[$lexeme->{parent_id}];
		}
		
		if (defined $lemma_db{$lemma}) {
			push @{$lemma_db{$lemma}}, $lexeme;
		} else {
			$lemma_db{$lemma} = [$lexeme];
		}
	}
	
	return %lemma_db;
}

sub plex {
	my $lexeme = shift;
	return $lexeme->{techlemma} . '#' . $lexeme->{pos};
}

sub cmp_deriv {
	my ($old_lexeme, $new_lexeme) = @_;
	
	if (defined $new_lexeme->{parent}) {
		if (defined $old_lexeme->{parent}) {
			if ($new_lexeme->{parent}->{techlemma} ne $old_lexeme->{parent}->{techlemma} or $new_lexeme->{parent}->{pos} ne $old_lexeme->{parent}->{pos}) {
				if ($new_lexeme->{parent}->{lemma} ne $old_lexeme->{parent}->{lemma} or $new_lexeme->{parent}->{pos} ne $old_lexeme->{parent}->{pos}) {
					print 'Reconnected ' . plex($new_lexeme) . ' from ' . plex($old_lexeme->{parent}) . ' to ' . plex($new_lexeme->{parent}) . "\n";
				} else {
					# Only the parent techlemmas are different.
# 					print 'Soft reconnect of ' . plex($new_lexeme) . ' from ' . plex($old_lexeme->{parent}) . ' to ' . plex($new_lexeme->{parent}) . "\n";
				}
			} else {
				# No change
			}
		} else {
			print 'Newly connected ' . plex($new_lexeme) . ' to ' . plex($new_lexeme->{parent}) . "\n";
		}
	} elsif (defined $old_lexeme->{parent}) {
		print 'Disconnected: ' . plex($new_lexeme) . ' from ' . plex($old_lexeme->{parent}) . "\n";
	} else {
		# Never connected, no change. Move along.
	}
}



my %old_db = read_db($old_db_name);
my %new_db = read_db($new_db_name);

for my $new_lemma (keys %new_db) {
	my @new_lexemes = @{$new_db{$new_lemma}};
	my @old_lexemes;
	
	if (exists $old_db{$new_lemma}) {
		@old_lexemes = @{$old_db{$new_lemma}};
	} else {
		for my $new_lexeme (@new_lexemes) {
			if (defined $new_lexeme->{parent}) {
				print 'New lexeme ' . plex($new_lexeme) . ' connected to ' . plex($new_lexeme->{parent}) . "\n";
			} else {
				print 'New lexeme ' . plex($new_lexeme) . " without a parent.\n";
			}
		}
		delete $new_db{$new_lemma};
		next;
	}
	
	# Try to solve the simple case of 1-to-1 mapping.
	if (@new_lexemes == 1 and @old_lexemes == 1) {
		my $new_lexeme = $new_lexemes[0];
		my $old_lexeme = $old_lexemes[0];
		my $eq_pos = $new_lexeme->{pos} eq $old_lexeme->{pos};
		my $eq_techlemma = $new_lexeme->{techlemma} eq $old_lexeme->{techlemma};
		
		if ($eq_techlemma and $eq_pos) {
			# No change, great.
		} elsif (not $eq_pos) {
			# Change in POS, possibly with a change in techlemma as well.
			print 'POS change from ' . plex($old_lexeme) . ' to ' . plex($new_lexeme) . "\n";
		} else { # not $eq_techlemma
			# Change in techlemma. But the two lexemes are guaranteed to be equivalent, since there are no more equivalent lexemes in the DB.
			print 'Simple techlemmatical change from ' . plex($old_lexeme) . ' to ' . plex($new_lexeme) . "\n";
		}
		
		# Compare the derivations.
		cmp_deriv($old_lexeme, $new_lexeme);
		
		delete $new_db{$new_lemma};
		delete $old_db{$new_lemma};
		next;
	}
	
	# At least one of the lexeme list is nontrivially long.
	
	# Try to connect lexemes exactly – matching both POSes and techlemmas.
	for (my $i = 0; $i < @new_lexemes; $i++) {
		my $new_lexeme = $new_lexemes[$i];
		my $found = 0;
		
		for (my $j = 0; $j < @old_lexemes; $j++) {
			my $old_lexeme = $old_lexemes[$j];
			
			if ($new_lexeme->{techlemma} eq $old_lexeme->{techlemma} and $new_lexeme->{pos} eq $old_lexeme->{pos}) {
				$found++;
				
				cmp_deriv($old_lexeme, $new_lexeme);
				
				# remove $old_lexeme from the database
				splice(@old_lexemes, $j, 1);
				$j--; # Prevent skipping over a lexeme
			}
		}
		
		if ($found > 1) {
			print 'Found multiple cross-db matches for lexeme ' . plex($new_lexeme) . "\n";
			# TODO solve this case!
			# FIXME hack.
			print STDERR 'Error in lexeme ' . plex($new_lexeme) . "\n";
			$retval = 1;
			splice(@new_lexemes, $i, 1);
			$i--;
		} elsif ($found == 1) {
			# Found a single good techlemmatical match.
			# Remove the matched lexeme
			splice(@new_lexemes, $i, 1);
			$i--; # Prevent skipping over the next one since the array has been shortened.
		} else {
			# Techlemmas don't match.
			if (@old_lexemes) {
# 				print 'Techlemmatical change from ' . plex($old_lexemes[0]) . (@old_lexemes > 1 ? ' (and other variants)' : '') . ' to ' . plex($new_lexeme) . "\n";
				print 'Techlemmatical change from ' . join(', ', map { plex($_) } @old_lexemes) . ' to ' . plex($new_lexeme) . "\n";
			} else {
				# If there are no old lexemes, then this lexeme is new.
				print 'New techlemmatical variant ' . plex($new_lexeme) . "\n";
			}
		}
	}
	
	# If we've paired or printed all the possible techlemmas, delete their keys from the databases.
# 	if (not @old_lexemes) {
		delete $old_db{$new_lemma};
# 	}
# 	if (not @new_lexemes) {
		delete $new_db{$new_lemma};
# 	}
}


for my $old_lemma (keys %old_db) {
	my @old_lexemes = @{$old_db{$old_lemma}};
# 	next if (not @old_lexemes); # TODO je to potřeba?
	
	my @new_lexemes;
	
	if ($new_db{$old_lemma} and @{$new_db{$old_lemma}}) {
		print 'Something went wrong with ' . join(', ', map { plex($_) } @{$new_db{$old_lemma}}) . ', was ' . join(', ', map { plex($_) } @old_lexemes) . "\n";
		@new_lexemes = @{$new_db{$old_lemma}};
	} else {
		print 'Deleted lexeme' . (@old_lexemes > 1 ? 's: ' : ': ') . join(', ', map { plex($_) } @old_lexemes) . "\n";
		delete $old_db{$old_lemma};
		next;
	}
	
	# TODO solve the case when the lemma is preserved, but the POS or techlemmas have changed
}

exit($retval);
