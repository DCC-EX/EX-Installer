#!/bin/bash

#
# © 2024 Harald Barth
# 
# This file is part of EX-Installer
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CommandStation.  If not, see <https://www.gnu.org/licenses/>.
#
#

INSTALLER_URL="https://github.com/DCC-EX/EX-Installer"
INSTALLER_TAG="v0.0.19-Devel"

function need () {
    type -p $1 > /dev/null && return
    dpkg -l $1 2>&1 | egrep ^ii >/dev/null && return
    sudo apt-get install $1
    type -p $1 > /dev/null && return
    echo "Could not install $1, abort"
    exit 255
}

function tryinst () {
    dpkg -l $1 2>&1 | egrep ^ii >/dev/null && return
    sudo apt-get install $1
}

function goodpython () {
$1 <<EOF
import platform
ver=platform.python_version().split('.')[1]
print('3.' + ver)
if int(ver) >= 10:
  exit (0)
exit (1)
EOF
}

need git

if cat /etc/issue | egrep '^Raspbian' 2>&1 >/dev/null ; then
    # we are on a raspi where we do not support graphical
    echo "Sorry, this does not work on an Raspi, abort"
    exit 255
fi

if [ x$DISPLAY != x ] ; then
    # we have DISPLAY, do the graphic thing
    tryinst python3
    PYTHON3=`compgen -c python3| egrep '^python3.?[0-9]*$'|sort -t. -k2 -n | tail -1`
    if VER=`goodpython $PYTHON3` ; then
	: echo $VER
    else
	need python3.10
	if VER=`goodpython python3.10` ; then
	    : echo $VER
	else
	    echo 'Can not find good enough python version (>=3.10)'
	    echo 'Please install manually'
	fi
	PYTHON3=python3.10
    fi

    need python3-tk
    need python${VER}-venv
    mkdir -p ~/ex-installer/venv
    $PYTHON3 -m venv ~/ex-installer/venv || exit 255
    cd ~/ex-installer/venv || exit 255
    source ./bin/activate
    git clone --filter=tree:0 $INSTALLER_URL
    cd EX-Installer || exit 255
    git pull -r --autostash origin $INSTALLER_TAG
    git checkout $INSTALLER_TAG
    pip3 install -r requirements.txt
    exec $PYTHON3 -m ex_installer
fi
echo "To run a graphical installer, you need a DISPLAY"
exit 255
