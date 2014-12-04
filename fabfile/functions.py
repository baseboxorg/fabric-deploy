import os
import requests
import json
from config import *



class Site():

	@classmethod 
	def make_site_dir(self, site_name):
		return os.path.join(PATH, "../Sites/%s/" % site_name)

	@classmethod 
	def make_wordpress_dir(self, site_name):
		return os.path.join(PATH, "../Sites/%s/" % site_name)

	@classmethod 
	def make_theme_dir(self, site_name):
		return os.path.join(PATH, "../Sites/%(site_name)s/wp-content/themes/%(site_name)s/" % {"site_name":site_name, "site_name":site_name})

	@classmethod 
	def make_config_dir(self, site_name):
		return os.path.join(PATH, "../Sites/%s/" % site_name)

	@classmethod 
	def repo(self, repo):
		self.repository = repo

	@classmethod 
	def vagrant(self, site_name):

		config_dir = self.make_config_dir(site_name)
		settings = get_config_file(config_dir)

		self.replacements = [ settings['stage']['url'], settings['production']['url'] ]
		self.server = settings['vagrant']
		self.repository = settings['site']['site_repository']

	@classmethod 
	def stage(self, site_name):

		config_dir = self.make_config_dir(site_name)
		settings = get_config_file(config_dir)

		self.replacements = [ settings['vagrant']['url'], settings['production']['url'] ]
		self.server = settings['stage']
		self.repository = settings['site']['site_repository']

	@classmethod 
	def production(self, site_name):

		config_dir = self.make_config_dir(site_name)
		settings = get_config_file(config_dir)

		self.replacements = [ settings['stage']['url'], settings['vagrant']['url'] ]
		self.server = settings['production']
		self.repository = settings['site']['site_repository']

	@classmethod
	def wordpress(self, site_name):

		settings = get_config_file(self.make_config_dir(site_name))
		self.wordpress = settings['wordpress']

	
	def __init__(self, site_name):

		# Local File
		self.site_name = site_name
		self.site_dir = self.make_site_dir(site_name)
		self.wordpress_dir = self.make_wordpress_dir(site_name)
		self.theme_dir = self.make_theme_dir(site_name)
		self.config_dir = self.make_config_dir(site_name)
		


#---------------------
# Templating
#---------------------


def render_template(template_filename, context):
	return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

#---------------------
# Base Config Json
#---------------------

def make_base_config(site):

	config_file = site.config_dir + 'settings.json'

	context = {
		'site_name' : site.site_name,
		'site_repository' : site.repository
	}

	with open(config_file, 'w') as f:
		output = render_template('_base_config.json', context)
		f.write(output)

def make_gitignore(site):

	gitignore_file = site.config_dir + '.gitignore'

	context = {}

	with open(gitignore_file, 'w') as f:
		output = render_template('_gitignore', context)
		f.write(output)


def get_config_file(config_dir):
	
	config = config_dir + 'settings.json'
	json_data=open(config)
	
	data = json.load(json_data)
	return data

#---------------------
# Wordpress Config
#---------------------

def get_wordpress_salts():
	r = requests.get('https://api.wordpress.org/secret-key/1.1/salt/')
	return r.text

 
def create_wp_config(site):
    
	config_file = '/tmp/wp-config.php'

	settings = get_config_file(site.config_dir)
	salts = get_wordpress_salts()

	# Get wordpress settings

	context = {
		'database_name': site.server['database'],
		'username' : site.server['database_user'],
		'password' : site.server['database_password'],
		'salts' : salts,
		'table_prefix' : site.wordpress['table_prefix']
	}

	with open(config_file, 'w') as f:
		output = render_template('_wp-config.php', context)
		f.write(output)

	return config_file

def create_htaccess(site):
    
	config_file = '/tmp/.htaccess'

	context = {
		
	}

	with open(config_file, 'w') as f:
		output = render_template('_htaccess', context)
		f.write(output)

	return config_file

#---------------------
# Apache Config
#---------------------

def create_apache_config(site):

	config_file = '/tmp/%s.conf' % site.site_name

	# Get apache settings

	context = {
		'siteurl': site.server['url'],
		'sitepath' : site.server['path'],
	}

	with open(config_file, 'w') as f:
		output = render_template('_apache.conf', context)
		f.write(output)

	return config_file

















