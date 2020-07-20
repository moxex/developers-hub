from developershub import db
from datetime import datetime

class Users(db.Model):
	__searchable__ = ['fname', 'username', 'email']
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	fname = db.Column(db.String(60), nullable=False)
	lname = db.Column(db.String(60), nullable=False)
	username = db.Column(db.String(60), unique=True, nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(100), nullable=False)

	confirmed = db.Column(db.Boolean, nullable=False, default=False)
	confirmation_number = db.Column(db.String(5), nullable=True)

	created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

	# User Details
	profession = db.Column(db.String(60), nullable=False, default="Developer")
	aboutme = db.Column(db.String(450), nullable=False, default="No Description")
	phone = db.Column(db.Numeric(20,0), nullable=False, default="00000000000")
	location = db.Column(db.String(60), nullable=False, default="Unknown City")

	skills = db.relationship('Skill', backref='user')
	experiences = db.relationship('Experience', backref='user')
	education = db.relationship('Education', backref='user')
	questions = db.relationship('Questions', backref='user')

	# User Accounts
	facebook = db.Column(db.String(100), nullable=True)
	github = db.Column(db.String(100), nullable=True)
	linkedin = db.Column(db.String(100), nullable=True)

	# User Image Filename
	image = db.Column(db.String(120), nullable=False, default="default.png")

	# Lists of liked/disliked/commments in a posts/questions
	likes = db.relationship('QuestionLikes', backref='user')
	dislikes = db.relationship('QuestionDislikes', backref='user')
	comments = db.relationship('QuestionComments', backref='user')

	# List of received notifications of the user
	Notifications = db.relationship('Notifications', backref='user')


	def __init__(self, fname, lname, username, email, password, confirmation_number):
		self.fname = fname
		self.lname = lname
		self.username = username
		self.email = email
		self.password = password
		self.confirmation_number = confirmation_number

class Notifications(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	notif_desc = db.Column(db.String(120), nullable=True)
	post_id = db.Column(db.Numeric(10,0), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Skill(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	skill = db.Column(db.String(60), nullable=True)
	skillExp = db.Column(db.String(60), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Experience(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	title = db.Column(db.String(60), nullable=True)
	job = db.Column(db.String(60), nullable=True)
	description = db.Column(db.String(160), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Education(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	school = db.Column(db.String(100), nullable=True)
	fromDate = db.Column(db.String(5), nullable=True)
	toDate = db.Column(db.Numeric(5,0), nullable=True)
	description = db.Column(db.String(160), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Questions(db.Model):
	# For flask-whooshalchemy, searchable through it's title and description
	__searchable__ = ['title', 'description']
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	title = db.Column(db.String(100), nullable=True)
	description = db.Column(db.String(500), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	likes = db.relationship('QuestionLikes', backref='question')
	dislikes = db.relationship('QuestionDislikes', backref='question')
	comments = db.relationship('QuestionComments', backref='question')

class QuestionLikes(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

	def __init__(self, user, question_id):
		self.user = user
		self.question_id = question_id

class QuestionDislikes(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

	def __init__(self, user, question_id):
		self.user = user
		self.question_id = question_id

class QuestionComments(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	comment = db.Column(db.String(500), nullable=True)
	question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

db.create_all()
db.session.commit()