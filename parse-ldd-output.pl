#!/usr/bin/perl

use strict;

sub trim($)
{
        my $string = shift;
        $string =~ s/^\s+//;
        $string =~ s/\s+$//;
        return $string;
}

# read from stdin
while (<STDIN>)
{
    # get the line
    my $line = $_;
    # run the matching regex
    my @results = $line =~ /(.+)*[=][>](.+)*\((.+)*\)/;
    # extract the filename
    my $filename = trim($results[1]);
    print "$filename\n";
}

