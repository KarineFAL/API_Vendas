from flask import Flask
from app import app
from flask_basicauth import BasicAuth



app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = '1234'

basic_auth = BasicAuth(app)

app.config['BASIC_AUTH_FORCE'] = True

basic_auth.init_app(app)
