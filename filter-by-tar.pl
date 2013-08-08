#!/usr/bin/perl

use strict;
use Archive::Tar;

sub trim($)
{
        my $string = shift;
        $string =~ s/^\s+//;
        $string =~ s/\s+$//;
        return $string;
}

# check args
if (1 != ($#ARGV + 1))
{
  print STDERR "usage: filter-by-tar.pl <tar-file>\n";
  exit 1;
}

#extract args
my $tarfile = $ARGV[0];

# open the tar file
my $tar = Archive::Tar->new($tarfile);

# get a list of files in the tar file
my @files = $tar->get_files();

# setup the hash lookup of the filenames
my %filenames = ();

# iterate through the files
for my $file (@files)
{
  # get the filename 
  my $filename = "/" . $file->{'name'};

  # skip directories
  if ($filename =~ /\/$/)
  {
    next;
  }

  # store the filename
  $filenames{$filename} = 1;
}

# read in the list of files from stdin
while (<STDIN>)
{  
    my $line = trim($_);
    if (! exists $filenames{$line})
    {
        print "$line\n";
    }
}
