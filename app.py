from flask import Flask
#from flask_mysqldb import MySQL
#from flaskext.mysql import MySQL

app = Flask(__name__)


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
