import os
from jinja2 import Environment, FileSystemLoader


BITBUCKET_USERNAME = ""
BITBUCKET_PASS = ""
WORDPRESS_VERSION = "4.0"
THEME_REPO = ""


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)