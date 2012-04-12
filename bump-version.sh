#!/usr/bin/env bash
# 
#  bump-version.sh
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-17.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 


EXE=$0
USAGE="
Usage for bump-version

	$EXE x.x.x
	
	change the version number to x.x.x

"

if [ "$#" -ne 1 ]
then
	echo "$USAGE"
	exit
fi


SELECTREGEX="[0-9a-zA-Z\.\+\-]+"
SPLITREGEX="([0-9]+)\.([0-9]+)(\.([0-9]+))?(-p([0-9]+))?($SELECTREGEX)?"
VERSIONFILE="AstroObject/version.py"

VERSION=`python $VERSIONFILE`
NEWVERSION=$1

MAJOR=`echo $NEWVERSION | sed -Ee "s/$SPLITREGEX/\1/"`
MINOR=`echo $NEWVERSION | sed -Ee "s/$SPLITREGEX/\2/"`
BUGFIX=`echo $NEWVERSION | sed -Ee "s/$SPLITREGEX/\4/"`
PATCH=`echo $NEWVERSION | sed -Ee "s/$SPLITREGEX/\6/"`


echo "Version is currently $VERSION, changing to $MAJOR . $MINOR . $BUGFIX -p $PATCH"

if [ "$BUGFIX" == '' ]
then
    BUGFIX='None'
fi


if [ "$PATCH" == '' ]
then
    PATCH='None'
fi

echo "Manipulating Python (.py) file comments"
files=`find AstroObject/*.py`

for file in $files
do
	sed -i '' -Ee "s/# +Version $SELECTREGEX/#  Version $NEWVERSION/" $file
	echo "  Changed Version Comment to $NEWVERSION in $file"
done

files=`find *.md`

echo "Manipulating Markdown (.md) files"
for file in $files
do
	sed -i '' -Ee "s/ +Version $SELECTREGEX/  Version $NEWVERSION/" $file
	echo "  Changed Version to $NEWVERSION in $file"
done

echo "Manipulating Special File $VERSIONFILE:"
sed -i '' -Ee "s/major += +$SELECTREGEX/major = $MAJOR/" $VERSIONFILE
sed -i '' -Ee "s/minor += +$SELECTREGEX/minor = $MINOR/" $VERSIONFILE
sed -i '' -Ee "s/bugfix += +$SELECTREGEX/bugfix = $BUGFIX/" $VERSIONFILE
sed -i '' -Ee "s/patch += +$SELECTREGEX/patch = $PATCH/" $VERSIONFILE




echo "Done."
