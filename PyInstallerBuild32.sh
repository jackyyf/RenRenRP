#!/bin/bash

PYTHON_BINARY='python32'
PYINSTALLER_SCRIPT="E:\\python27\\pyinstaller-2.0\\pyinstaller.py"
PYINSTALLER_FLAGS='-F -c'
SOURCE_FILE='src\\renren.py'
BUILD_NAME='RenRenRP-x86'
ICON_PATH=''
LOG_FILE="${BUILD_NAME}.log"

if [ -d build ]  # Check and remove old build directory.
then
	echo 'Removing last build ...'
	rm -Rf build
fi

echo 'Build job start ...'

$PYTHON_BINARY $PYINSTALLER_SCRIPT $PYINSTALLER_FLAGS -n $BUILD_NAME $SOURCE_FILE | tee $LOG_FILE

if [ ! $? -eq 0 ] # Error occured
then
	echo "Build failure (Non-zero exitcode)."
	exit 1
fi

echo 'Build success.'
echo 'Do some cleaning job ...'
rm -Rf build
echo 'Everything OK.'
exit 0
