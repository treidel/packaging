#!/usr/bin/python

import argparse
import os
import subprocess
import ConfigParser
 
# parse the arguments
parser = argparse.ArgumentParser(description="create a bootable disk image for beaglebone black")
parser.add_argument('--input', required=True)
parser.add_argument('--config', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--partition', required=True)
args = parser.parse_args()

# parse the config file
config = ConfigParser.RawConfigParser()
config.read(args.config)

# extract config params
start = config.getint(args.partition, 'start')
end = config.getint(args.partition, 'end')

# call dd to do the extraction
subprocess.call(['dd', "if=" + args.input, "of=" + args.output, "skip=" + str(start), "count=" + str(end - start + 1)])
