from flask_mysqldb import MySQL
#from flaskext.mysql import MySQL
from app import app

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'social_media'  # give name
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)
