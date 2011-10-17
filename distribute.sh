#!/usr/bin/env bash
# 
#  distribute.sh
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-17.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

EXE=$0
USAGE="

	$EXE path/to/dest
	
	Copies the required module files to distribute this module as part of another package
"

if [ $# -ne '1' ]
then
	echo "$USAGE"
	exit
fi

DEST=$1

FILES=`find *.py`

for file in $FILES
do
	if [ $file = "oldTest.py" ]
	then
		echo "Skipping oldTest.py"
	else
		echo "Copying $file"
		cp $file $DEST
	fi
done	