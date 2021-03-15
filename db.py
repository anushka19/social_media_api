from flask_mysqldb import MySQL
#from flaskext.mysql import MySQL


# MySQL config


def update_config(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'social_media'  # give name
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    return MySQL(app)
