from developershub import db, mail
from flask_mail import Mail, Message
from developershub.models import Questions, Notifications
from flask import session, render_template, flash, redirect, url_for
from functools import wraps

def notif_dislike(currentUser, question_id):
	question = Questions.query.filter_by(id=question_id).first()

	if question.user.username == session['user']:
		pass
	else:
		new_notif = Notifications(notif_desc=f"{currentUser.username} disliked your post", post_id=question_id, user_id=question.user_id)
		db.session.add(new_notif)

def notif_like(currentUser, question_id):
	question = Questions.query.filter_by(id=question_id).first()

	if question.user.username == session['user']:
		pass
	else:
		new_notif = Notifications(notif_desc=f"{currentUser.username} liked your post", post_id=question_id, user_id=question.user_id)
		db.session.add(new_notif)

def notif_comment(currentUser, question_id):
	question = Questions.query.filter_by(id=question_id).first()
	
	if question.user.username == session['user']:
		pass
	else:
		new_notif = Notifications(notif_desc=f"{currentUser.username} commented your post", post_id=question_id, user_id=question.user_id)
		db.session.add(new_notif)

# Login Required Decorator
def login_required(function):
	@wraps(function)
	def wrapper_function(*args, **kwargs):
		if 'user' not in session:
			flash('ACCESS DENIED')
			return redirect(url_for('login'))

		return function(*args, **kwargs)
	return wrapper_function

# Jinja2 Filter to compare two lists
def intersect(a, b):
    return set(a).intersection(b)


def email_code(query, forgot):
	if forgot:
		template = 'reset-pass/forgot-email.html'
	else:
		template = 'email.html'

	msg = Message(
			subject='Developers Hub Confirmation', 
			recipients=[query.email],
			html=render_template(f'{template}', no_nav=True, name=query.fname, confirmation_number=query.confirmation_number))

	mail.send(msg)