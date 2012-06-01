from fabric.api import env, settings, execute, run
from time import sleep

env.user = 'aegir'
env.shell = '/bin/bash -c'

def build(site, makefile, buildname, webserver, dbserver, profile):
    '''Creates or migrates an Aegir site to a new or existing platform.

    If a sites does not exist and the platform does not exist the first time this
    script is ran, it will create a new platform and install a new site on that
    platform. If there is a platform, the new site will be created on the existing
    platform. If there is an existing site, the script will either create a
    new platform and migrate the site to it or migrate the site to an existing
    platform.

    See the github page for more info: https://github.com/zachseifts/aegir_deployment

    '''

    # Create a new platform
    with settings(warn_only=True):
      platform_result = run('drush @platform_%s status' % (buildname,))

    if platform_result.failed:
      # No platform exists, create a new one
      execute(build_platform, makefile=makefile, buildname=buildname)
    
    # Check and see if the site exists
    with settings(warn_only=True):
        site_result = run('drush @%s status' % (site,))

    # If the site does not exist, we need to create the alias and install it
    if site_result.failed:
        execute(save_alias, site=site, buildname=buildname, webserver=webserver, dbserver=dbserver, profile=profile)
        execute(install_site, site=site, buildname=buildname)
        return

    # If the site exists, migrate it to the new platform, save alias, and import the migrated site.
    execute(migrate_site, site=site, buildname=buildname)
    execute(save_alias, site=site, buildname=buildname, webserver=webserver, dbserver=dbserver, profile=profile)
    execute(import_site, site=site, buildname=buildname)

def build_platform(makefile, buildname):
    ''' Builds a new platform for the site.
    '''
    run("drush make %s /var/aegir/platforms/%s" % (makefile, buildname))
    run("drush --root='/var/aegir/platforms/%s' provision-save '@platform_%s' --context_type='platform'" % (buildname, buildname))
    run("drush @hostmaster hosting-import '@platform_%s'" % (buildname,))
    run("drush @hostmaster hosting-dispatch")

def migrate_site(site, buildname):
    '''Migrates a site to a new platform.
    '''
    run("drush @%s provision-migrate '@platform_%s'" % (site, buildname))

def save_alias(site, buildname, webserver, dbserver, profile):
    ''' Saves an alias for the site.
    '''
    run("drush provision-save @%s --context_type=site --uri=%s --platform=@platform_%s --server=@server_%s --db_server=@server_%s --profile=%s --client_name=admin" % (site, site, buildname, webserver, dbserver, profile))

def install_site(site, buildname):
    ''' Imports a site into a platform
    '''
    run("drush @%s provision-install" % (site,))
    run("drush @hostmaster hosting-task @platform_%s verify" % (buildname,))
    sleep(5)
    run("drush @hostmaster hosting-dispatch")
    sleep(5)
    run("drush @hostmaster hosting-task @%s verify" % (site,))

def import_site(site, buildname):
    ''' Imports a site into the frontend.
    '''
    run("drush @hostmaster hosting-import @%s" % (site,))
    run("drush @hostmaster hosting-task @platform_%s verify" % (buildname,))
    run("drush @hostmaster hosting-import @%s" % (site,))
    run("drush @hostmaster hosting-task @%s verify" % (site,))

