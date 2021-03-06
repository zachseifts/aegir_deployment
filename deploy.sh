#!/bin/bash

# Creates or migrates an Aegir site.

function usage() {
cat << EOF
usage:
${0#} [-h] -s example.com -a aegir.example.com -m /path/to/makefile.make -f /path/to/fabfile.py -p profilename -v 6|7 -b NameOfBuild -w master -d localhost

Creates or migrates an Aegir site to a new or existing platform.

If a sites does not exist and the platform does not exist the first time this
script is ran, it will create a new platform and install a new site on that
platform. If there is a platform, the new site will be created on the existing
platform. If there is an existing site, the script will either create a
new platform and migrate the site to it or migrate the site to an existing
platform.

See the github page for more info: https://github.com/zachseifts/aegir_deployment

OPTIONS:
   -h                         Display this message
   -s site.domain.com         The domain name of the site
   -a aegir.domain.com        The url of your Aegir instance
   -m /path/to/makefile.make  The path to the drush make file for this site
   -f /path/to/fabfile.py     The path to the fabfile.py
   -r /path/to/fab            The path to the fabric executable
   -p profile                 The name of the install profile for this site
   -b BuildName               The name of this build
   -v [6|7]                   The major Drupal version number, either 6 or 7
   -w webserver               The Aegir webserver this site will run on
                              Do not include the @server_ prefix.
   -d dbserver                The Aegir database server this site will run on
                              Do not include the @server_ prefix.

EOF
}

SITE=
AEGIR=
MAKEFILE=
FABFILE=
PROFILE=
VERSION=
BUILDNAME=
FAB=fab
WEBSERVER=
DBSERVER=
while getopts "hs:m:a:f:r:p:b:v:w:d:" OPTION
do
  case $OPTION in
    h)
      usage
      exit 0
      ;;
    s)
      SITE=$OPTARG
      ;;
    a)
      AEGIR=$OPTARG
      ;;
    m)
      MAKEFILE=$OPTARG
      ;;
    f)
      FABFILE=$OPTARG
      ;;
    r)
      FAB=$OPTARG
      ;;
    p)
      PROFILE=$OPTARG
      ;;
    b)
      BUILDNAME=$OPTARG
      ;;
    v)
      VERSION=$OPTARG
      ;;
    w)
      WEBSERVER=$OPTARG
      ;;
    d)
      DBSERVER=$OPTARG
      ;;
    ?)
      usage
      echo "Invalid option $OPTION specified."
      exit 1
      ;;
  esac
done

if [[ -z $SITE ]] ||
   [[ -z $AEGIR ]] ||
   [[ -z $MAKEFILE ]] ||
   [[ -z $FABFILE ]] ||
   [[ -z $PROFILE ]] ||
   [[ -z $VERSION ]] ||
   [[ -z $WEBSERVER ]] ||
   [[ -z $DBSERVER ]] ||
   [[ -z $BUILDNAME ]]
then
  usage
  exit 1
fi

$FAB -H $AEGIR -f $FABFILE build:site=$SITE,makefile=$MAKEFILE,buildname=$BUILDNAME,webserver=$WEBSERVER,dbserver=$DBSERVER,profile=$PROFILE,version=$VERSION
if [ $? -ne 0 ]
then
  echo "The fabric build command failed."
  exit 1
fi

