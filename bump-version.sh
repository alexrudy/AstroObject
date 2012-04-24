#!/usr/bin/env bash
# 
#  bump-version.sh
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-17.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 


EXE=$0

SELECTREGEX="[0-9a-zA-Z\.\+\-]+"
SPLITREGEX="([0-9]+)\.([0-9]+)(\.([0-9]+))?(-p([0-9]+))?(\-)?($SELECTREGEX)?"
VERSIONFILE="AstroObject/version.py"

VERSION=`python $VERSIONFILE`

USAGE="
Usage for bump-version:
	
    $EXE x.x.x
	
Help
	
    change the version number to x.x.x 
    
    current version: \"$VERSION\"

"


if [ "$1" == "-v" ]; then
    echo "Version is $VERSION"
    exit
fi

if [ "$1" == "-t" ]; then
    nargs=2
    NEWVERSION=$2
else
    nargs=1
    NEWVERSION=$1
fi

if [ "$#" -ne $nargs ]; then
	echo "$USAGE"
	exit
fi


MAJOR=`echo $NEWVERSION | grep -E "$SPLITREGEX" | sed -Ee "s/$SPLITREGEX/\1/"`
MINOR=`echo $NEWVERSION | grep -E "$SPLITREGEX" | sed -Ee "s/$SPLITREGEX/\2/"`
BUGFIX=`echo $NEWVERSION | grep -E "$SPLITREGEX" | sed -Ee "s/$SPLITREGEX/\4/"`
PATCH=`echo $NEWVERSION | grep -E "$SPLITREGEX" | sed -Ee "s/$SPLITREGEX/\6/"`
DEVSTR=`echo $NEWVERSION | grep -E "$SPLITREGEX" | sed -Ee "s/$SPLITREGEX/\8/"`

if [ "$MAJOR" == '' ] || [ "$MINOR" == '' ]; then
    echo "Cannot parse version: \"$NEWVERSION\""
    echo "  Found: major=$MAJOR minor=$MINOR bugfix=$BUGFIX patch=$PATCH devstr=$DEVSTR"
    exit
fi

echo "Version is currently $VERSION, changing to $NEWVERSION"
echo " extracted as major=$MAJOR minor=$MINOR bugfix=$BUGFIX patch=$PATCH devstr=$DEVSTR"

if [ "$BUGFIX" == '' ]; then
    BUGFIX='None'
fi


if [ "$PATCH" == '' ]; then
    PATCH='None'
fi

if [ "$DEVSTR" == '' ]; then
	DEVSTR='None'
	ISDEV='False'
else
	DEVSTR="\"$DEVSTR\""
	ISDEV='True'
fi

echo " entered as major=$MAJOR minor=$MINOR bugfix=$BUGFIX patch=$PATCH devstr=$DEVSTR"

if [ "$1" == "-t" ]; then
    exit
fi

echo "Manipulating Python (.py) file comments"
files=`find . -name '*.py' -not -path '*build*'`
for file in $files
do  
    found=`grep -E "# +Version" $file`
    if [ "$found" == '' ]; then
        echo "  No Version Comment in $file"
    else
    	sed -i '' -Ee "s/# +Version $SELECTREGEX/#  Version $NEWVERSION/" $file
    	echo "  Changed Version Comment to $NEWVERSION in $file"
    fi
done

files=`find . -name '*.md'`

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
sed -i '' -Ee "s/^devstr += +\\\"?$SELECTREGEX\\\"?/devstr = $DEVSTR/" $VERSIONFILE
echo "   Version variables set to major=$MAJOR minor=$MINOR bugfix=$BUGFIX patch=$PATCH devstr=$DEVSTR"
echo "Version Settings:"
echo "  major  = $MAJOR"
echo "  minor  = $MINOR"
echo "  bugfix = $BUGFIX"
echo "  patch  = $PATCH"
echo "  devstr = $DEVSTR"


echo "Done."
