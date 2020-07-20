from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import os, boto3
from flask_recaptcha import ReCaptcha
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = '6f95265d2f676e59f9f615e390112405'
app.config['WHOOSH_BASE'] = 'whoosh'

# Email Sending Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['TESTING'] = False;
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'dsb.developers.hub@gmail.com'
app.config['MAIL_PASSWORD'] = 'gypgftinfxpokqhx'
app.config['MAIL_DEFAULT_SENDER'] = 'dsb.developers.hub@gmail.com'
app.config['MAIL_SUPPRESS_END'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail= Mail(app)

# For Recaptcha
app.config.update(dict(
	RECAPTCHA_ENABLED = True,
	RECAPTCHA_SITE_KEY = '6LfrlK8ZAAAAALlZ8p68-5NKiXMri1buf_1fx4D7',
	RECAPTCHA_SECRET_KEY = '6LfrlK8ZAAAAABNF9wVC8DbCTaSfLXylgouD7KcP' 
))
recaptcha = ReCaptcha(app=app)

# AWS Configuration
S3_KEY = os.environ.get('S3_KEY')
S3_SECRET = os.environ.get('S3_SECRET')
DATABASE = os.environ.get('DATABASE')

s3 = boto3.resource(
   's3',
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET)	

# Environment Settings
env = 'dev'

if env == 'dev':
	app.config['DEBUG'] = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.sqlite3'
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
	app.config['DEBUG'] = False


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

from developershub.utils import intersect
app.jinja_env.filters['intersect'] = intersect

from developershub import routes