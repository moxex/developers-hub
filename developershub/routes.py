from developershub import app, db, s3, recaptcha, bcrypt

from flask import render_template, redirect, url_for, request, session, flash

# Models
from developershub.models import (
	Users, Experience, Skill, Education, 
	Questions, QuestionLikes, QuestionDislikes,
	QuestionComments, Notifications)

from developershub.PSFormRequest import FormRequest

from developershub.utils import notif_like, notif_dislike, notif_comment, login_required, email_code

from developershub import flask_whooshalchemyplus as whooshalchemy
from random import randint

whooshalchemy.whoosh_index(app, Questions)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if 'user' in session:
		return redirect(url_for('profile', username=session['user']))

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		query = Users.query.filter_by(username=username).first()

		if query:
			if bcrypt.check_password_hash(query.password, password):
				session['user'] = username

				# If account is not confirmed redirect to confirmation page
				if not query.confirmed:
					return redirect(url_for('account_confirmation'))

				# Refresh search index
				whooshalchemy.index_all(app)

				# If the information given is valid then go to user's profile page
				return redirect(url_for('profile', username=query.username))
			else:
				flash('WRONG PASSWORD')
		else:
			flash("USERNAME NOT FOUND")

	return render_template('login.html', title='Login', no_nav=True, login='active')


@app.route('/register', methods=['POST', 'GET'])
def register():
	if 'user' in session:
		return redirect(url_for('profile', username=session['user']))

	if request.method == 'POST':
		if recaptcha.verify():
			fname = request.form['fname']
			lname = request.form['lname']
			username = request.form['username']
			email = request.form['email']
			password = request.form['password']
			confirm_password = request.form['confirm-password']

			queryUsername = Users.query.filter_by(username=username).first()
			queryEmail = Users.query.filter_by(email=email).first()

			if password == confirm_password:
				if queryUsername or queryEmail:
					flash("Sorry, There's an existing user with this info.")
				else:
					# Generating Random Confirmation Number
					confirmation_number = ''.join(["{}".format(randint(0, 9)) for num in range(0, 5)])
					hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

					# Creating the user, and saving it to the database
					new_user = Users(fname, lname, username, email, hashed_password, confirmation_number)
					db.session.add(new_user)
					db.session.commit()

					session['user'] = username


					query = Users.query.filter_by(username=username).first()
					# Sending a confirmation code the user's email
					email_code(query, False)

					# Redirect to confirmation page
					return redirect(url_for('account_confirmation'))
			else:
				flash("PASSWORDS DOESN'T MATCH")
		else:
			flash('ReCaptcha Failed')

	return render_template('register.html', title='Register', no_nav=True, register='active')

# If the user doesnt receive an email
@app.route('/account/confirmation/email/try-again')
@login_required
def email_again():
	currentUser = session['user']

	query = Users.query.filter_by(username=currentUser).first()

	email_code(query, False)

	return redirect(url_for('account_confirmation'))

@app.route('/account/confirmation', methods=['POST', 'GET'])
@login_required
def account_confirmation():
	currentUser = session['user']
	query = Users.query.filter_by(username=currentUser).first()

	# Check if the user already confirmed his account
	if query.confirmed:
		return redirect(url_for('profile', username=currentUser))

	if request.method == 'POST':
		codeInput = request.form['code']

		# If the given code is correct
		if codeInput == query.confirmation_number:
			query.confirmed = True
			query.confirmation_number = None
			db.session.commit()
			return redirect(url_for('profile', username=currentUser))
		else:
			flash('THE CODE YOU ENTERED IS INCORRECT')

	return render_template('confirmation.html', no_nav=True)


@app.route('/profile/<username>', methods=['POST', 'GET'])
def profile(username):
	# Query user in the URL Parameter
	userParameter = Users.query.filter_by(username=username).first()
	
	if 'user' in session:
		currentUser = Users.query.filter_by(username=session['user']).first()

		if not currentUser.confirmed:
			return redirect(url_for('account_confirmation'))


	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		query = Users.query.filter_by(username=username).first() 

		if query:
			if bcrypt.check_password_hash(query.password, password):
				session['user'] = username

				# If account is not confirmed redirect to confirmation page
				if not query.confirmed:
					return redirect(url_for('account_confirmation'))

				# If the information given is valid then go to user's profile page
				return redirect(request.referrer)
			else:
				flash('WRONG PASSWORD')
				return redirect(url_for('login'))
		else:
			flash("USERNAME NOT FOUND")
			return redirect(url_for('login'))

	return render_template('profile.html', user=userParameter, profile='active')


@app.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
	currentUser = session['user']
	query = Users.query.filter_by(username=currentUser).first()

	# Handle all POST form requests
	FormRequest.requests(query)

	return render_template('profile-settings.html', user=query)


@app.route('/remove/skill/<id>')
@login_required
def remove_skill(id):
	sessionUser = session['user']
	loggedUser = Users.query.filter_by(username=sessionUser).first()
	skill = Skill.query.filter_by(id=id).first()

	if loggedUser.id == skill.user_id:
		db.session.delete(skill)
		db.session.commit()

	return redirect(request.referrer)


@app.route('/remove/experience/<id>')
@login_required
def remove_exp(id):
	sessionUser = session['user']
	loggedUser = Users.query.filter_by(username=sessionUser).first()
	experience = Experience.query.filter_by(id=id).first()

	if loggedUser.id == experience.user_id:
		db.session.delete(experience)
		db.session.commit()
		
	return redirect(request.referrer)


@app.route('/remove/education/<id>')
@login_required
def remove_educ(id):
	sessionUser = session['user']
	loggedUser = Users.query.filter_by(username=sessionUser).first()
	education = Education.query.filter_by(id=id).first()

	if loggedUser.id == education.user_id:
		db.session.delete(education)
		db.session.commit()
		
	return redirect(request.referrer)


@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
	page = request.args.get('page', 1, type=int)
	currentUser = Users.query.filter_by(username=session['user']).first()

	if 'search' in request.args:
		questions = Questions.query.order_by(Questions.id.desc()).whoosh_search(request.args.get('search')).paginate(page=page, per_page=8)
	else:
		questions = Questions.query.order_by(Questions.id.desc()).paginate(page=page, per_page=8)

	# Like a post
	if 'like' in request.form and request.method == 'POST':
		question_id = request.form['like']

		query_like = QuestionLikes.query.filter_by(user_id=currentUser.id, question_id=question_id).first()
		query_dislike = QuestionDislikes.query.filter_by(user_id=currentUser.id, question_id=question_id).first()

		if query_like:
			db.session.delete(query_like)
			db.session.commit()
		elif query_dislike:
			db.session.delete(query_dislike)
			db.session.commit()

			new_like = QuestionLikes(currentUser, question_id)
			db.session.add(new_like)

			notif_like(currentUser, question_id)

			db.session.commit()
		else:
			new_like = QuestionLikes(currentUser, question_id)
			db.session.add(new_like)

			notif_like(currentUser, question_id)

			db.session.commit()

		return redirect(request.referrer)

	# Dislike a post
	if 'dislike' in request.form and request.method == 'POST':
		question_id = request.form['dislike']

		query_like = QuestionLikes.query.filter_by(user_id=currentUser.id, question_id=question_id).first()
		query_dislike = QuestionDislikes.query.filter_by(user_id=currentUser.id, question_id=question_id).first()

		if query_dislike:
			db.session.delete(query_dislike)
			db.session.commit()
		elif query_like:
			db.session.delete(query_like)
			db.session.commit()

			new_dislike = QuestionDislikes(currentUser, question_id)
			db.session.add(new_dislike)

			notif_dislike(currentUser, question_id)

			db.session.commit()
		else:
			new_dislike = QuestionDislikes(currentUser, question_id)
			db.session.add(new_dislike)

			notif_dislike(currentUser, question_id)

			db.session.commit()

		return redirect(request.referrer)

	if 'ask' in request.form and request.method == 'POST':
		title = request.form['title']
		ask = request.form['ask']

		new_post = Questions(title=title, description=ask, user_id=currentUser.id)
		db.session.add(new_post)
		db.session.commit()

		return redirect(request.referrer)

	return render_template('home.html', user=currentUser, home='active',questions=questions)

@app.route('/post/<id>', methods=['GET', 'POST'])
@login_required
def post_detail(id):
	post = Questions.query.filter_by(id=id).first()
	currentUser = Users.query.filter_by(username=session['user']).first()

	page = request.args.get('page', 1, type=int)
	comments = QuestionComments.query.filter_by(question_id=id).paginate(page=page, per_page=10)

	# Like a post
	if 'like' in request.form and request.method == 'POST':
		question_id = request.form['like']

		query_like = QuestionLikes.query.filter_by(user_id=currentUser.id, question_id=question_id).first()
		query_dislike = QuestionDislikes.query.filter_by(user_id=currentUser.id, question_id=question_id).first()

		if query_like:
			db.session.delete(query_like)
			db.session.commit()
		elif query_dislike:
			db.session.delete(query_dislike)
			db.session.commit()

			new_like = QuestionLikes(currentUser, question_id)
			db.session.add(new_like)

			notif_like(currentUser, question_id)

			db.session.commit()
		else:
			new_like = QuestionLikes(currentUser, question_id)
			db.session.add(new_like)

			notif_like(currentUser, question_id)

			db.session.commit()

		return redirect(request.referrer)

	# Dislike a post
	if 'dislike' in request.form and request.method == 'POST':
		question_id = request.form['dislike']

		query_like = QuestionLikes.query.filter_by(user_id=currentUser.id, question_id=question_id).first()
		query_dislike = QuestionDislikes.query.filter_by(user_id=currentUser.id, question_id=question_id).first()

		if query_dislike:
			db.session.delete(query_dislike)
			db.session.commit()
		elif query_like:
			db.session.delete(query_like)
			db.session.commit()

			new_dislike = QuestionDislikes(currentUser, question_id)
			db.session.add(new_dislike)

			notif_dislike(currentUser, question_id)

			db.session.commit()
		else:
			new_dislike = QuestionDislikes(currentUser, question_id)
			db.session.add(new_dislike)

			notif_dislike(currentUser, question_id)

			db.session.commit()

		return redirect(request.referrer)

	if 'comment' in request.form and request.method == 'POST':
		question_id = request.form['qid']
		comment = request.form['comment']

		new_comment = QuestionComments(user_id=currentUser.id, comment=comment, question_id=question_id)
		db.session.add(new_comment)

		notif_comment(currentUser, question_id)

		db.session.commit()

		return redirect(request.referrer)

	return render_template('post-detail.html', post=post, user=currentUser, comments=comments)

@app.route('/search')
def search():
	questions = Questions.query.whoosh_search(request.args.get('query')).all()
	users = Users.query.whoosh_search(request.args.get('query')).all()

	return render_template('search.html', questions=questions, users=users)

@app.route('/notifications')
@login_required
def notifications():
	page = request.args.get('page', 1, type=int)
	currentUser = Users.query.filter_by(username=session['user']).first()
	notifications = Notifications.query.filter_by(user_id=currentUser.id).order_by(Notifications.id.desc()).paginate(page=page, per_page=10)
	return render_template('notifications.html', notifications='active', notifs=notifications)

@app.route('/forgot-password/success/new-password/<code>/<user>', methods=['POST', 'GET'])
def new_password(code, user):
	query = Users.query.filter_by(username=user).first()
	if query.confirmation_number != code:
		return redirect(url_for('login'))

	if request.method == 'POST':
		password = request.form['password']
		confirm = request.form['confirm']

		if password == confirm:
			query = Users.query.filter_by(username=user).first()
			hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

			query.password = hashed_password
			db.session.commit()

			flash("Successfuly Changed The Password")
			return redirect(url_for('login'))

	return render_template('reset-pass/new-password.html')

@app.route('/forgot-password/confirm/<user>', methods=['POST', 'GET'])
def confirm_forgot(user):
	query = Users.query.filter_by(username=user).first()
	if request.method == 'POST':
		code = request.form['code']

		if code == query.confirmation_number:
			return redirect(url_for('new_password', code=code, user=query.username))
		else:
			flash('Wrong Code')

	return render_template('reset-pass/confirm-forgot.html')

@app.route('/forgot-password', methods=['POST', 'GET'])
def forgot_password():
	if request.method == 'POST':
		username = request.form['username']
		query = Users.query.filter_by(username=username).first()

		# generate random number
		confirmation_number = ''.join(["{}".format(randint(0, 9)) for num in range(0, 5)])
		query.confirmation_number = confirmation_number
		db.session.commit()

		email(query, True)

		return redirect(url_for('confirm_forgot', user=query.username))

	return render_template('reset-pass/forgot-password.html')

@app.route('/logout')
@login_required
def logout():
	session.pop('user')
	return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
	return render_template('error404.html', no_nav=True)