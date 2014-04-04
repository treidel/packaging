#!/bin/bash

# process args

#input=0
#output=0
#config=0
#partition=0

while getopts i:o:c:p: opt; do 
    case $opt in 
        i) input=$OPTARG;;
        o) output=$OPTARG;;
        c) config=$OPTARG;;
        p) partition=$OPTARG;;
        \?)
            exit 1
            ;;
        :)
            exit 1
            ;;
    esac
done

# make sure args are provided
if [ -z ${input+x} ] || [ -z ${output+x} ] || [ -z ${config+x} ] || [ -z ${partition+x} ]; then 
    echo "usage: $0 -i <input> -o <output> -c <config> -p <partition>" >&2
    exit 1
fi

# create a temporary directory
tempdirectory=`mktemp -d`

# setup the paths to all of the upgrade image components
swdescription="sw-description"
bankimage="bank.img"

# extract the partition to the temporary file
echo "extracting partition $partition from $input into $tempdirectory/$bankimage"
`./extract-partition.py --input $input --config $config --output "$tempdirectory/$bankimage" --partition $partition`

# change into the temporary directory
cd $tempdirectory

# setup the list of inputs into the output file
FILES="$bankimage"
echo "creating $output using $FILES" 

# start creating the update file
for i in $FILES; do echo $i; done | cpio -ov -H crc > $output

# remove the temporary directory
rm -r $tempdirectory

# done
echo "finished creating upgrade file $output"
