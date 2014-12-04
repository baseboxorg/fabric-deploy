# Wordpress Deployment Framework using Fabric

Tool that deploys wordpress sites to multiple servers quickly and safely (with git) as well as sets up a development environment using Vagrant. You'll need a vagrant base box set up with the right software installed: php, mysql, apache... probably a bunch of other stuff too... and with apache's configs set to the right directory... Eventually I'll have time to add details about this to the readme...

## Installation

Clone this repository into a folder where you want to keep your projects, then install dependencies:
	
	git clone http://repository/url myprojectfolder
	cd myprojectfolder/scripts 
	./installer.sh

Run vagrant up to start a new vagrant machine for your new sites.

## Setting Up your Site:

First, edit the details in

	/fabfile/_config.py
	
THEME_REPO should be the repository for the base theme you want to use. Rename this file to config.py (without the underscore).

Create a repository, download wordpress, and get your base theme with this command:

	fab repo:mysite	

Now edit your settings.json file here: /Sites/mysite/settings.json

Setup your environment with this command:

	fab vagrant:mysite setup

The vagrant setup will create a database for you, but for staging and production, you will have to create the database on your own.

The only setup for staging and production servers are manually creating the database and any apache configuration. The path that apache serves as the website should always end with "/current". For example: "/var/www/vhosts/site.com/current". 

You can run this command to generate the correct apache configuration file before deploying:

	fab stage:mysite apache

### Deploying Files

Deploying your site is simple:

	fab vagrant:mysite commit
	fab stage:mysite deploy
	fab production:mysite deploy

The first command commits and pushes your latest changes to your remote repository and creates a backup of your vagrant database. The second two commands clone your repo to the staging or production environment, then puts the uploads folder on the remote server.


### Working with the Database

There are commands to pull a database and to push a database. The push command will take an export of _whichever database was most recently pulled_ and push it to the environment you specify. So if you want to take your vagrant database and push it to staging, run these commands:

	fab vagrant:mysite pull
	fab stage:mysite push

Or from staging to production:

	fab stage:mysite pull
	fab production:mysite push

Or from production to vagrant:
	
	fab production:mysite pull
	fab vagrant:mysite push

_Be careful not to push the wrong database. Every push command must be preceeded by a pull command of the database you want to work with._

If you are concerned about getting it right, backup your database first:

	fab vagrant:mysite backup
	fab stage:mysite backup
	fab production:mysite backup


##  Working on Existing Projects

To work on an existing project, first run the command to clone the existing repository:

	fab workon_repo:site_name="mysite",repo="https://repo/url"

Once this command runs, edit your settings.json file in the site directory (Sites/mysite/) with the correct information. Then run the following command to import the database and move your uploads folder into the correct place. Of course, you can do this manually as well.

	fab vagrant:mysite workon_setup:database="/path/to/database.sql",uploads="/path/to/uploads"




