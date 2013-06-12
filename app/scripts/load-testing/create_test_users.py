"""
Run this code from within django shell
	python manage.py shell
See https://docs.djangoproject.com/en/1.3/topics/auth/#creating-users

If running in iPython use %cpaste command to allow pasting of code without
auto-indentation messing things up.
"""

# import user model object
from django.contrib.auth.models import User
from django.db import IntegrityError

# create 1000 test users with password of 'password'
for i in range(1,1001):
	username = 'testuser_'+str(i)
	try:
		user = User.objects.create_user(username, '', 'password')
		user.save()
		print 'Created user '+username
	except IntegrityError:
		print 'User '+username+' already exists'

