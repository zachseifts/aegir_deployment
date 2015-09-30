# Aegir Continuous Integration with Fabric

This is a collection of fabric commands that do awesome stuff with sites 
hosted in Aegir. It gives you the ability to create sites and migrate them
between platforms automatically.

Based on [mig5's aegir\_cid project](https://github.com/mig5/aegir_cid).

## Requirements

 - Fabric 1.4.2
 - virtualenv
 - A working Aegir instance
 - A Jenkins instance that has the ability to ssh to the Aegir instance with a public key

## Features

 - Creates a new platform and site the first time it is ran
 - If a site exists, it will create a new platform and migrate the site
   to the new platform
 - If the platform exists, it will migrate the site to the existing platform

## Install

If you're using Ubuntu 10.04 you need to run:

    $ sudo aptitude install build-essential python-dev

As your Jenkins user, clone this repo and make sure that the use can ssh to the
Aegir servers you want to deploy code to.

    $ su jenkins
    $ cd 
    $ mkdir -p scripts
    $ cd scripts
    $ git clone git://github.com/zachseifts/aegir_deployment.git
    $ cd aegir_deployment

If you do not already have virtualenv installed, install it and create a virtualenv.

    $ virtualenv env

Now download fabric

    $ ./env/bin/pip install -r requirements.txt

That's it. You should have everything setup and ready to go.

## Usage

Make sure the fab command is in your path and create a jenkins job that runs
this command when changes are made to the master branch of your project:

    fab -H aegir.example.com -f /path/to/fabric.py build:site=testing.example.com,makefile=/path/to/makefile.make,buildname=NameOfBuild,webserver=master,dbserver=localhost,profile=ProfileName,version=7
 
Of you can use the deploy.sh script like this:

    MAKEFILE=/path/to/the/makefile.make
    FABFILE=/path/to/the/fabfile.py
    SITE=example.com
    AEGIR=aegir1.example.com,aegir2.example.com,aegir3.example.com
    PROFILE=profilename
    VERSION=7
    BUILDNAME=NameOfBuild
    ./deploy.sh -s $SITE -a $AEGIR -m $MAKEFILE -f $FABFILE -p $PROFILE -v $VERSION -b $BUILDNAME

And it will do everything automaticaly. If you are using remote Aegir
instances, run your database on a different server, or use clusters you
may need to specify the webserver and database server. You can do that by
adding the `-w WEBSERVERNAME` and `-d DBSERVERNAME` to the `deploy.sh`
command. Use `deploy.sh -h` to get the full list of options.

You can also use individual commands like `build_platform`:

    fab -H aegir.example.com -f /path/to/fabric.py build_platform:makefile=/path/to/makefile.make,buildname=NameOfBuild,version=7

### Fabric commands

    $ fab --list
    Available commands:

        aegir_cron         Runs the aegir hosting-dispatch job.
        build              Creates or migrates an Aegir site to a new or existing platform.
        build_platform     Builds a new platform.
        clear_all_caches   Clears the drupal cache and varnish cache for a site.
        drush_make         Runs drush make on a make file.
        import_site        Imports a site into the frontend.
        install_site       Provisions a new site.
        make_platform_dir  Creates a directory for platforms.
        migrate_site       Migrates a site to a platform.
        save_alias         Saves an alias a site.
        save_platform      Saves a new platform.

### Deploy script options

    $ ./deploy.sh -h
    usage:
    ./deploy.sh [-h] -s example.com -a aegir.example.com -m /path/to/makefile.make -f /path/to/fabfile.py -p profilename -v 6|7 -b NameOfBuild -w master -d localhost

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

