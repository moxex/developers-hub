from flask import request
from developershub import db, s3
from developershub.models import Users, Experience, Skill, Education
import os, secrets

class FormRequest:
	def requests(query):
		# Profession
		if request.method == 'POST' and 'profession' in request.form:
			profession = request.form['profession']

			query.profession = profession
			db.session.commit()

		# About Me
		if request.method == 'POST' and 'aboutme' in request.form:
			aboutme = request.form['aboutme']

			query.aboutme = aboutme
			db.session.commit()

		# Contact Information
		if request.method == 'POST' and 'phone' in request.form:
			phone = request.form['phone']
			location = request.form['location']

			query.location = location
			query.phone = phone
			db.session.commit()

		# Add Skill
		if request.method == 'POST' and 'skill' in request.form:
			skill = request.form['skill']
			skillExp = request.form['skillExp']

			new_skill = Skill(skill=skill, skillExp=skillExp, user_id=query.id)
			db.session.add(new_skill)
			db.session.commit()

		# Accounts
		if request.method == 'POST' and 'facebook' in request.form:
			facebook = request.form['facebook']
			github = request.form['github']
			linkedin = request.form['linkedin']

			query.facebook = facebook
			query.github = github
			query.linkedin = linkedin

			db.session.commit()

		# Experience/Projects
		if request.method == 'POST' and 'job' in request.form:
			title = request.form['title']
			job = request.form['job']
			description = request.form['description']

			new_exp = Experience(title=title, job=job, description=description, user_id=query.id)
			db.session.add(new_exp)
			db.session.commit()

		#Education
		if request.method == 'POST' and 'school' in request.form:
			school = request.form['school']
			fromDate = request.form['fromdate']
			toDate = request.form['todate']
			description = request.form['description']

			new_educ = Education(school=school, fromDate=fromDate, toDate=toDate, description=description, user_id=query.id)
			db.session.add(new_educ)
			db.session.commit()

		#Picture
		if request.method == 'POST' and 'picture' in request.files:
			picture = request.files['picture']
			username = query.username

			filename, extension = os.path.splitext(picture.filename)
			uni = secrets.token_hex(8)
			filename = f'{username}{uni}{extension}'

			s3.Bucket('developershub-files').put_object(Key=filename, Body=picture)

			query.image = filename
			db.session.commit()