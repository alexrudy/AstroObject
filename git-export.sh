#!/usr/bin/env bash
# 
#  git-export.sh
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-12.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

EXE=$0
BRANCH="master"
EXCLUDE="EXCLUDE.txt"
USAGE="
Usage for bump-version

	$EXE path/to/destination/directory
	
	Will export branch $BRANCH to the destination directory, excluding files listed in $EXCLUDE
"

if [ "$#" -ne 1 ]
then
	echo "$USAGE"
	exit
fi

DESTINATION=$1

echo "Exporting branch $BRANCH to $DESTINATION"
echo " $ git archive $BRANCH | tar x -C $DESTINATION"
git archive $BRANCH | tar x -C $DESTINATION

if [ -f $DESTINATION/$EXCLUDE ]; then
    files=`cat $DESTINATION/$EXCLUDE`
elif [ -f $EXCLUDE ]; then
    echo "No Exclusions File found in source, using active copy..."
    files=`cat $EXCLUDE`
else
    files=''
fi

for file in $files
do
    if [ -f "$DESTINATION/$file" ]; then
    	echo "Removing $DESTINATION/$file"
    	rm -r "$DESTINATION/$file"
    else
        echo "File $DESTINATION/$file not found in soruce, ignoring..."
    fi
done

    
echo "Done."
