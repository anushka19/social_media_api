from functools import wraps
from flask import render_template, flash, redirect, url_for, session, logging, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash, request
from flask import jsonify
from db import update_config
from flask import Flask
import pymysql

# from flask_mysqldb import MySQL
# from flaskext.mysql import MySQL

app = Flask(__name__,)

mysql = update_config(app)
urls = [url for url in app.url_map.iter_rules()]


@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        _json = request.json
        _name = _json['name']
        _email = _json['email']
        _username = _json['username']
        _password = _json['password']

        # validate the received values
        if _name and _email and _password and request.method == 'POST':
            # hash password
            _hashed_password = generate_password_hash(_password)

            # save changes

            query = "INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)"
            data = (_name, _email, _username, _hashed_password)
            # Connect mysql
            conn = mysql.connect
            # Create Cursor
            cur = conn.cursor()
            # Execute query
            cur.execute(query, data)
            # Commit To DB
            conn.commit()

            res = jsonify('Users Registered successfully!')
            res.status_code = 200
            return res
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        # Close Connection
        cur.close()
        conn.close()


# Users


@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    # cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    res = jsonify(rows)
    res.status_code = 200
    return res
    cur.close()


# Single user


@app.route('/user/<string:id>')
def user(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id=%s", id)
        row = cur.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cur.close()


@app.route('/update_user', methods=['POST'])
def update_user():
    # try:
    _json = request.json
    _id = _json['id']
    _name = _json['name']
    _email = _json['email']
    _username = _json['username']
    _password = _json['password']

    # validating the data
    if _name and _email and _password and _id and request.method == 'POST':
        # hashing password
        _hashed_password = generate_password_hash(_password)

        # save edits
        query = "UPDATE users SET name=%s,email=%s,username=%s,password=%s WHERE id=%s"
        data = (_name, _email, _username, _hashed_password, _id)

        # Connect mysql
        conn = mysql.connect
        # Create Cursor
        cur = conn.cursor()

        # cur = mysql.connection.cursor()
        # Execute query
        cur.execute(query, data)
        conn.commit()
        res = jsonify('Users Updated successfully!')
        res.status_code = 200
        return res

    else:
        return not_found()
    # except Exception as e:
    #     print(e)
    # finally:
    # Close Connection
    cur.close()

    # conn.close()


@app.route('/delete_user/<string:id>')
def delete_user(id):
    try:
        conn = mysql.connect
        cur = conn.cursor()
        # cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (id,))
        conn.commit()
        resp = jsonify('User deleted successfully!')
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        # Close Connection
        cur.close()
        conn.close()


# Page Not Found


# User Login

@app.route('/login', methods=['POST'])
def login():
    try:
        # if request.method == 'POST':
        # Get
        _json = request.json
        #_id = _json['id']
        _username = _json['username']
        _password = _json['password']

        if _username and _password and request.method == 'POST':

            # create connection,cursor
            conn = mysql.connect
            cur = conn.cursor()

            #cur = mysql.connection.cursor()

            # get user by username
            # username should be equal to the one we pass
            result = cur.execute(
                "SELECT * FROM users WHERE username= %s", [_username])
            conn.commit()

            if result > 0:

                # pwd = row['password']  # pass mysql config for dict

                # compare passwords
                # while result != 0:
                #     if check_password_hash(_password, pwd):
                #         # Passed
                #         session['logged_in'] = True
                #         session['username'] = _username

                row = cur.fetchone()
                pwd = row['password']

            if check_password_hash(_password, pwd):
                session['logged_in'] = True
                session['username'] = _username

                #res = jsonify(row)
            res = jsonify('User Logged in successfully!')
            res.status_code = 200
            return res
        else:
            return not_found()

    except Exception as e:
        print(e)
    finally:
        cur.close()

        # Close Connection

        conn.close()

        # Check if user is logged in


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # try:
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return not_found()
        # except Exception as e:
            # print(e)
    return wrap


# Logout


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    message = {
        'status': 200,
        'message': 'User logged out successfully! ',
    }
    res = jsonify(message)
    res.status_code = 200
    return res


# create feeds


@app.route('/feeds', methods=['POST'])
@is_logged_in
def feeds():
    try:
        # create cursor
        conn = mysql.connect()
        cur = conn.cursor()

        # get latest postws
        result = cur.execute("SELECT * FROM posts ORDER BY id DESC")

        if result > 0:
            rows = cur.fetchall()
            res = jsonify(rows)
            res.status_code = 200
            return res
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


# Add Article


@app.route('/add_post', methods=['POST'])
@is_logged_in
def add_post():
    try:
        _json = request.json
        _title = _json['title']
        _author = session['username']
        _body = _json['body']

        # validate
        if _title and _body and request.method == 'POST':
            query = "INSERT INTO posts(title,author,body) VALUES(%s, %s, %s)"
            data = (_title, _author, _body)
            conn = mysql.connect
            cur = conn.cursor()
            cur.execute(query, data)
            conn.commit()

            res = jsonify('Post added successfully!')
            res.status_code = 200
            return res
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


# Posts

@app.route('/posts')
def posts():
    try:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM posts")
        rows = cur.fetchall()
        res = jsonify(rows)
        res.status_code = 200
        return res
    except Exception as e:
        print(e)
    finally:
        cur.close()
        cur.close()


# Single post
@app.route('/post/<int:id>')
def post(id):
    try:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM posts WHERE id=%s", id)
        row = cur.fetchone()
        res = jsonify(row)
        res.status_code = 200
        return res
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


# Update Posts


@app.route('/update_post', methods=['POST'])
@is_logged_in
def update_article():
    try:

        # Create cursor
        # conn = mysql.connect()
        # cur = conn.cursor()

        # # get the post by the id
        # result = cur.execute("SELECT * FROM posts WHERE id=%s", [id])

        # post = cur.fetchone()

        # get post
        _json = request.json
        _id = request.json['id']
        _title = _json['title']
        _body = _json['body']
        _author = session['username']

        # after comparing then validating sending the post request
        if _title and _author and _body and _id and request.method == 'POST':

            # _title = _json['title']
            # _body = _json['body']

            # create cursor
            conn = mysql.connect()
            cur = conn.cursor()
            query = "UPDATE posts SET title=%s,body=%s WHERE id=%s"
            data = (_title, _body, _id)
            cur.execute(query, data)
            conn.commit()
            resp = jsonify('Post updated successfully!')
            resp.status_code = 200
            return resp
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


# Delete post

@app.route('/delete_post/<int:id>', methods=['POST'])
@is_logged_in
def delete_post(id):
    try:

        # Create Cursor
        conn = mysql.connect()
        cur = conn.cursor()
        # Execute
        cur.execute("DELETE FROM posts WHERE id= %s", (id,))

        # Commit to DB
        conn.commit()
        res = jsonify('Post deleted successfully!')
        res.status_code = 200
        return res
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


# Comments
@app.route('/add_comment', methods=['GET', 'POST'])
@is_logged_in
def add_comment():
    try:
        _json = request.json
        _comment_id = _json['comment_id']
        _post_id = _json['post_id']
        _author = _json['comment_author']
        _parent_comment = _json['parent_comment']
        _child_comment = _json['child_comment']
        _email = _json['comment_email']

        # create connection,cursor
        conn = mysql.connect()
        cur = conn.cursor()

        # get user by username
        # username should be equal to the one we pass
        result = cur.execute(
            "SELECT * FROM posts WHERE id= %s", [_post_id])
        row = []
        if result > 0:
            row = cur.fetchone()
            _id = row['id']
            _title = row['title']  # pass mysql config for dict
            _author = row['author']
            _body = row['body']

        if _id == _post_id and _child_comment is None and _author == session['username'] and _email == session['email']:
            query = cur.execute(
                "INSERT INTO comments(post_id,comment_author,parent_comment,child_comment,comment_email) VALUES(%s,%s,%s,%s,%s")
            data = (_post_id, _author, _parent_comment, _child_comment, _email)
            cur.execute(query, data)
            conn.commit()
            res = jsonify('Comment added successfully!')
            res.status_code = 200
            return res
        elif _child_comment == 1:
            res = jsonify('Cannot have more than one replies!')
            res.status_code = 200
            return res
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


# Update Comment
@app.route('/update_comment', methods=['GET', 'POST'])
@is_logged_in
def update_comment():
    try:
        _json = request.json
        _comment_id = _json['comment_id']
        _post_id = _json['post_id']
        _author = _json['comment_author']
        _parent_comment = _json['parent_comment']
        _child_comment = _json['child_comment']
        _email = _json['comment_email']

        # create connection,cursor
        conn = mysql.connect()
        cur = conn.cursor()

        # get user by username
        # username should be equal to the one we pass
        result = cur.execute(
            "SELECT * FROM posts WHERE id= %s", [_post_id])
        row = []
        if result > 0:
            row = cur.fetchone()
            _id = row['id']
            _title = row['title']  # pass mysql config for dict
            _author = row['author']
            _body = row['body']

        if _child_comment is not None and _author == session['username'] and _email == session['email']:

            query = cur.execute(
                "UPDATE comments SET(child_comment=%s) VALUES WHERE comment_id=%s")

            data = (_child_comment, _comment_id)
            cur.execute(query, data)
            conn.commit()
            res = jsonify('Comment updated successfully!')
            res.status_code = 200
            return res

        elif _parent_comment is not None and _author == session['username'] and _email == session['email']:

            query = cur.execute(
                "UPDATE comments SET(parent_comment=%s) VALUES WHERE comment_id=%s")

            data = (_parent_comment, _comment_id)
            cur.execute(query, data)
            conn.commit()
            res = jsonify('Comment updated successfully!')
            res.status_code = 200
            return res
        elif _child_comment == 1:
            res = jsonify('Cannot have more than one replies!')
            res.status_code = 200
            return res

        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


# Delete comment

@app.route('/delete_comment/<int:id>')
@is_logged_in
def delete_comment(id):
    _json = request.json
    _author = session['username']
    _email = session['email']
    try:
        if _author and _email is True:
            # Create Cursor
            conn = mysql.connect()
            cur = conn.cursor()

            # Execute
            cur.execute("DELETE FROM comments WHERE id= %s", (id,))

            # Commit to DB
            conn.commit()
            res = jsonify('Comment deleted successfully!')
            res.status_code = 200
            return res
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
