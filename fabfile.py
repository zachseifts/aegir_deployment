from fabric.api import env, settings, execute, run, hide, task
from time import sleep

env.user = 'aegir'
env.shell = '/bin/bash -c'

@task
def build(site, makefile, buildname, webserver, dbserver, profile, version):
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
        with hide('output'):
            platform_result = run('drush @platform_%s status' % (buildname,))

    if platform_result.failed:
        # No platform exists, create a new one
        execute(build_platform, makefile=makefile, buildname=buildname, version=version)
    
    # Check and see if the site exists
    with settings(warn_only=True):
        with hide('output'):
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

@task
def build_platform(makefile, buildname, version):
    ''' Builds a new platform.
    '''
    run('mkdir -p /var/aegir/platforms/%s.x/' % (version))
    execute(drush_make, makefile=makefile, buildname=buildname, version=version)
    execute(save_platform, buildname=buildname, version=version)

@task
def drush_make(makefile, buildname, version):
    ''' Runs drush make on a make file.
    '''
    run("drush make %s /var/aegir/platforms/%s.x/%s" % (makefile, version, buildname))

@task
def save_platform(buildname, version):
    ''' Saves a new platform.
    '''
    run("drush --root='/var/aegir/platforms/%s.x/%s' provision-save '@platform_%s' --context_type='platform'" % (version, buildname, buildname))
    run("drush @hostmaster hosting-import '@platform_%s'" % (buildname,))
    execute(aegir_cron);

@task
def migrate_site(site, buildname):
    ''' Migrates a site to a platform.
    '''
    run("drush @%s provision-migrate '@platform_%s'" % (site, buildname))

@task
def save_alias(site, buildname, webserver, dbserver, profile):
    ''' Saves an alias a site.
    '''
    run("drush provision-save @%s --context_type=site --uri=%s --platform=@platform_%s --server=@server_%s --db_server=@server_%s --profile=%s --client_name=admin" % (site, site, buildname, webserver, dbserver, profile))

@task
def install_site(site, buildname):
    ''' Provisions a new site.
    '''
    run("drush @%s provision-install" % (site,))
    # Sometimes the hosting-task verify is already running for the platform
    with settings(warn_only=True):
        run("drush @hostmaster hosting-task @platform_%s verify" % (buildname,))
    sleep(5)
    execute(aegir_cron);
    sleep(5)
    run("drush @hostmaster hosting-task @%s verify" % (site,))

@task
def import_site(site, buildname):
    ''' Imports a site into the frontend.
    '''
    run("drush @hostmaster hosting-import @%s" % (site,))
    # Sometimes the hosting-task verify is already running for the platform
    with settings(warn_only=True):
        run("drush @hostmaster hosting-task @platform_%s verify" % (buildname,))
    run("drush @hostmaster hosting-import @%s" % (site,))
    run("drush @hostmaster hosting-task @%s verify" % (site,))

@task
def aegir_cron():
    ''' Runs the aegir hosting-dispatch job.
    '''
    run('drush @hostmaster hosting-dispatch')

@task
def test_run(site, tests):
    ''' Runs drush test-run on a site.
    '''
    run('drush @%s en -y simpletest' % (site,))
    run('drush @%s test-run %s' % (site, tests))
    run('drush @%s dis -y simpletest' % (site,))

@task
def clear_all_caches(site):
  ''' Clears the drupal cache and varnish cache for a site.
  '''
  run('drush @%s cc all' % (site,))
  run('drush @%s vpa' % (site,))

