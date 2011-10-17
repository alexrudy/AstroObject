#!/usr/bin/env bash

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

VSPECFILE="VERSION"

VERSION=`cat $VSPECFILE`

echo "Version is currently $VERSION, changing to $1"

echo "$1" > $VSPECFILE

VERSION=`cat $VSPECFILE`

echo "New Version $VERSION"

files=`find *.py`

for file in $files
do
	sed -i '' -Ee "s/# +Version [0-9\.]+/#  Version $VERSION/" $file
done

files=`find *.md`

for file in $files
do
	sed -i '' -Ee "s/ +Version [0-9\.]+/  Version $VERSION/" $file
done

sed -i '' -Ee "s/__version__ += +\'[0-9\.]+\'/__version__ = \'$VERSION\'/" '__init__.py'