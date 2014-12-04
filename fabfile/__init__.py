from fabric.api import *
from fabric.contrib import *
from config import *
from repo import *
from functions import *
import datetime
import time
import random
import string

#----------------------------------
#	Set Up Project Repository
#----------------------------------

def repo(site_name):

	site = Site(site_name)
	repo = create_new_repo(BITBUCKET_USERNAME, BITBUCKET_PASS, site.site_name)
	site.repo(repo)

	local("mkdir Sites/%s" % site.site_name)
	with lcd(site.site_dir):
		local(
			"git clone -b %(version)s-branch https://github.com/WordPress/WordPress.git %(directory)s" 
			% { "version": WORDPRESS_VERSION, "directory": "./" }
		)

	with lcd(site.wordpress_dir):
		local("rm -rf .git")
		local("git init")	
		local("git remote add origin %s" % repo)		

	local("mkdir %s" % site.theme_dir)
	with lcd(site.theme_dir): 
		local(
			"git clone %(repo)s ./" 
			% { "repo": THEME_REPO }
		)
	
	with lcd(site.theme_dir):
		local("rm -rf .git")
		with settings(warn_only=True):
			local("bower install && npm install")

	make_gitignore(site)
	make_base_config(site)

#----------------------------------
#	Work on an Existing Project
#----------------------------------

# fab workon:site_name='mysite',repo='https://repo/url' 
# Work on an existing repository

def workon_repo(site_name, repo):

	site = Site(site_name)
	site.repo(repo)

	local("mkdir Sites/%s" % site.site_name)
	with lcd(site.site_dir):
		local(
			"git clone %(repo)s %(directory)s" 
			% { "repo": repo, "directory": "./" }
		)		

	make_gitignore(site)
	make_base_config(site)

#----------------------------------
#	Configure Environments
#----------------------------------

def vagrant(site_name):
	env.site = Site(site_name)
	env.site.vagrant(site_name)
	env.site.wordpress(site_name)
	
	env.hosts = [ env.site.server['server'] ]
	env.password = env.site.server['password']

def stage(site_name):
	env.site = Site(site_name)
	env.site.stage(site_name)
	env.site.wordpress(site_name)
	
	env.hosts = [ env.site.server['server'] ]
	env.password = env.site.server['password']

def production(site_name):	
	env.site = Site(site_name)
	env.site.production(site_name)
	env.site.wordpress(site_name)
	
	env.hosts = [ env.site.server['server'] ]
	env.password = env.site.server['password']



#----------------------------------
#	Run Tasks for the Environment
#----------------------------------

# fab <environment>:<site_name> check_connection
# Make sure you can connect to a particular server and get to your site directory

def check_connection():
	print "Server: " + env.site.server['server']
	print "Password: " + env.site.server['password']
	print "----------------------------------------\n"
	print "Checking connection..."

	with cd(env.site.server['path']):
		run("pwd")
		run("ls")


# fab <environment>:<site_name> clean_slate
# Clean out all files in the site path

def clean_slate():

	with cd(env.site.server['path']):
		answer = prompt("Are you sure you want to delete everything in the 'current' directory? [Yn]")
		if answer == 'Y':
			doublecheck = prompt("Seriously. Are you Sure? [Yn]")
			if doublecheck == 'Y':
				run("rm -rf *")
				run("touch index.html")
			else:
				print "Not deleting..."
		else:
			print "Not deleting..."
		


# fab <environment>:<site_name> setup
# Set up the server environment for wordpress install

def setup():
	
	if "127.0.0.1" in env.hosts[0]:
		config = create_wp_config(env.site)
		run("mkdir -p %s" % env.site.server['path'])
		with cd(env.site.server['path']):
			put(config, './')

		
		with cd(env.site.server['path']):
			
			
			# Create Database
			run("mysql -u%(database_user)s -p'%(database_password)s' -e 'create database %(database)s'"
				% { 
					"database_user" : env.site.server['database_user'], 
					"database_password" : env.site.server['database_password'], 
					"database" : env.site.server['database'] 
				}
			)
			
			
			# Install Wordpress
			r = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(20)])
			run(
				"wp core install --url=%(url)s --title='%(title)s' --admin_user=%(admin_user)s --admin_password='%(admin_password)s' --admin_email=%(admin_email)s"
				% { 
					"url" : env.site.server['url'], 
					"title" : env.site.wordpress['site_title'], 
					"admin_user" : env.site.wordpress['wordpress_user_name'], 
					"admin_password" : r, 
					"admin_email" : env.site.wordpress['wordpress_user_email']
				}
			)

		print "\n\nThe password for your new site is: " + r
	else:
		print "Setup is only run on the local Vagrant host."


# fab <environment>:<site_name> workon_setup:database="/path/to/database.sql",uploads="/path/to/uploads"
# Set up the server environment for an existing project

def workon_setup(database, uploads):
	
	if "127.0.0.1" in env.hosts[0]:
		config = create_wp_config(env.site)
		htaccess = create_htaccess(env.site)
		run("mkdir -p %s" % env.site.server['path'])
		with cd(env.site.server['path']):
			put(config, './')
			put(htaccess, './')

		
		with cd(env.site.server['path']):
			
			with settings(warn_only=True):
				# Create Database
				run("mysql -u%(database_user)s -p'%(database_password)s' -e 'create database %(database)s'"
					% { 
						"database_user" : env.site.server['database_user'], 
						"database_password" : env.site.server['database_password'], 
						"database" : env.site.server['database'] 
					}
				)


			run('mkdir -p .db/')
			put(database, ".db/import.sql")
			run(
				"mysql -u%(database_user)s -p'%(database_password)s' %(database)s < .db/import.sql" 
				% { 
					"database_user" : env.site.server['database_user'], 
					"database_password" : env.site.server['database_password'], 
					"database" : env.site.server['database'] 
				}
			)

			for replacement in env.site.replacements:
				if replacement != "":
					run(
						"wp search-replace '%(replacement)s' '%(url)s'" 
						% { "replacement" : replacement, "url" : env.site.server['url'] }
					)

			run("rm -f .db/import.sql")

		with cd('%s/wp-content' % env.site.server['path']):

			put(uploads, "./")
			
	
	else:
		print "Setup is only run on the local Vagrant host."


# fab <environment>:<site_name> apache
# Set up the apache config files on a remote server

def apache():
	
	config = create_apache_config(env.site)
	put(config, "/etc/apache2/sites-available/", use_sudo=True)
	sudo("a2ensite %s.conf" % env.site.site_name)
	sudo("service apache2 reload")


# fab vagrant:<site_name> commit
# commits all changes and pushes to repo
# gets vagrant database and stages for push to another server

def commit():

	if "127.0.0.1" not in env.hosts[0]:
		abort('You must run this command with vagrant as your environment: fab vagrant:<site_name> commit')

	else:
		with lcd(env.site.site_dir):
			with settings(warn_only=True):
				local("git add --all && git commit -a -m 'Deployment Commit'") 
				local("git push origin master")
		pull()


# fab <environment>:<site_name> backup
# backs up remote database in local site folder with timestamp

def backup():

	with cd(env.site.server['path']):
		# Get Database
		run('mkdir -p .db/')
		run("mysqldump -u%(database_user)s -p'%(database_password)s' --no-create-db %(database)s > .db/%(database)s.sql"
			% { 
				"database_user" : env.site.server['database_user'], 
				"database_password" : env.site.server['database_password'], 
				"database" : env.site.server['database'] 
			}
		)

	ts = time.time()
	timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
	
	with lcd(env.site.site_dir):
		local("mkdir -p db")
		with cd(env.site.server['path']):
			get(".db/%s.sql" % env.site.server['database'], "db/backup_%(name)s_%(timestamp)s.sql" % {"name" : env.site.server['database'], "timestamp" : timestamp })

	with cd(env.site.server['path']):
		run("rm -f .db/%s.sql" % env.site.server['database'])

# fab <environment>:<site_name> backup
# gets local copy of database and stages it to push to a site

def pull():

	with cd(env.site.server['path']):
		# Get Database
		run('mkdir -p .db/')
		run("mysqldump -u%(database_user)s -p'%(database_password)s' --no-create-db %(database)s > .db/%(database)s.sql"
			% { 
				"database_user" : env.site.server['database_user'], 
				"database_password" : env.site.server['database_password'], 
				"database" : env.site.server['database'] 
			}
		)

	with lcd(env.site.site_dir):
		local("mkdir -p db")
		with cd(env.site.server['path']):
			get(".db/%s.sql" % env.site.server['database'], "db/export.sql")

	with cd(env.site.server['path']):
		run("rm -f .db/%s.sql" % env.site.server['database'])

# fab <environment>:<site_name> push
# pushes local staged copy of database to remote site

def push():
	
	with lcd(env.site.site_dir):
		
		with cd(env.site.server['path']):
			run('mkdir -p .db/')
			put("db/export.sql", ".db/import.sql")
			run(
				"mysql -u%(database_user)s -p'%(database_password)s' %(database)s < .db/import.sql" 
				% { 
					"database_user" : env.site.server['database_user'], 
					"database_password" : env.site.server['database_password'], 
					"database" : env.site.server['database'] 
				}
			)

		with cd(env.site.server['path']):
			for replacement in env.site.replacements:
				if replacement != "":
					run(
						"wp search-replace '%(replacement)s' '%(url)s'" 
						% { "replacement" : replacement, "url" : env.site.server['url'] }
					)

	with cd(env.site.server['path']):
		run("rm -f .db/import.sql")

# fab <evironment>:<site_name> deploy
# clone master repo to remote site, then create config and rsync uploads

def deploy():

	if "127.0.0.1" not in env.hosts[0]:
		config = create_wp_config(env.site)	
		htaccess = create_htaccess(env.site)	
		rootpath = env.site.server['path'].replace('/current', '')

		with cd("%s/wp-content" % env.site.server['path']):
			with settings(warn_only=True):
				run("mv uploads/ %s/uploads" % rootpath)

		with cd(rootpath):
			with settings(warn_only=True):
				run("rm -rf prev_revision")
				run("mv current/ prev_revision/")
			
			run("git clone --depth=1 %s current/" % env.site.repository)
		
		with cd(env.site.server['path']):
			put(config, './')
			put(htaccess, './')

		
		with lcd(env.site.site_dir):
			project.rsync_project("%s/" % rootpath, "wp-content/uploads")
			project.rsync_project("%s/uploads/" % rootpath, "wp-content/uploads", upload=False)
			with settings(warn_only=True):
				if os.path.isdir("wp-content/themes/production-theme"):
					put('wp-content/themes/production-theme', env.site.theme_dir)

		with cd(env.site.server['path']):
			run("mv %s/uploads/ wp-content/" % rootpath)
	
	else:
		print "The deploy command is only run on remote hosts."


# fab <evironment>:<site_name> sync
# only rsync the uploads folder with no other deployment actions

def sync():

	if "127.0.0.1" not in env.hosts[0]:
		rootpath = env.site.server['path'].replace('/current', '')

		with cd("%s/wp-content" % env.site.server['path']):
			with settings(warn_only=True):
				run("mv uploads/ %s/uploads" % rootpath)
		
		with lcd(env.site.site_dir):
			project.rsync_project("%s/" % rootpath, "wp-content/uploads")
			project.rsync_project("%s/uploads/" % rootpath, "wp-content/uploads", upload=False)

		with cd(env.site.server['path']):
			run("mv %s/uploads/ wp-content/" % rootpath)
	
	else:
		print "The deploy command is only run on remote hosts."


# fab <evironment>:<site_name> revert
# revert to the last deploy in case you need to fix a botched update very quickly

def revert():

	if "127.0.0.1" not in env.hosts[0]:
		with cd("%s/../" % env.site.server['path']):
			run("rm -rf revert_backup")
			run("mv current/ revert_backup/")
			run("mv prev_revision/ current/")

	else:
		print "The revert command is only run on remote hosts."


# function for testing new features

def test():
	pass
	















