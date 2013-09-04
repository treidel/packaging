#!/usr/bin/perl

use strict;

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
  print STDERR "usage: files-to-filespec.pl <staging>\n";
  exit 1;
}

#extract args
my $staging = $ARGV[0];

# read in the list of files from stdin
while (<STDIN>)
{  
    my $file = trim($_);

    # lookup the file in the file system
    (my $dev, my $ino, my $mode, my $nlink, my $uid, my $gid, my $rdev, my $size, my $atime, my $mtime,my $ctime, my $blksize, my $blocks) = stat("$staging/$file");

    # see what kind of file this is
    if (-f $file)
    {
        printf '  <file name="%s" user="%s" group="%s" mode="%o"/>', $file, getpwuid($uid), getgrgid($gid), $mode;
    }
    elsif (-d $file)
    {
        printf '  <dir name="%s" user="%s" group="%s" mode="%o"/>', $file, getpwuid($uid), getgrgid($gid), $mode;
    }
    elsif (-l $file)
    {
        printf '  <sym name="%s" link="%s" user="%s" group="%s" mode="%o"/>', $file, readlink($file), getpwuid($uid), getgrgid($gid), $mode;
    }
    elsif (-p $file)
    {
        printf '  <fifo name="%s" user="%s" group="%s" mode="%o"/>', $file, getpwuid($uid), getgrgid($gid), $mode;
    }
    elsif (-b $file)
    {
        printf '  <blk name="%s" user="%s" group="%s" mode="%o"/>', $file, getpwuid($uid), getgrgid($gid), $mode;
    }
    elsif (-c $file)
    {
        printf '  <chr name="%s" user="%s" group="%s" mode="%o"/>', $file, getpwuid($uid), getgrgid($gid), $mode;
    }
    else
    {
        print STDERR "unknown file type: $file\n";
        exit 1;
    }

    print "\n";

#    if tarinfo.isfile():
#        print '  <file name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
#    elif tarinfo.isdir():
#        print '  <dir name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
#    elif tarinfo.issym():
#        print '  <sym name="%s" link="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.linkname, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
#    elif tarinfo.islnk():    
#        print '  <lnk name="%s" link="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.linkname, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
#    elif tarinfo.ischr():
#        print '  <chr name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
#    elif tarinfo.isblk():
#        print '  <blk name="%s" user="%s" group="%s" mode="%s"/>' % (tarinfo.name, tarinfo.uname, tarinfo.gname, str(oct(tarinfo.mode)))
#    elif tarinfo.isfifo():
#        print '  <fifo na
}
