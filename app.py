import os
from flask import Flask, render_template, json, request, redirect, url_for, send_from_directory
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bucketlist'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mysql.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/showSignUp")
def showSignUp():
	return render_template('signup.html')

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            
            # All Good, let's call MySQL
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            #cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            cursor.execute("insert into tbl_user (user_name,user_username,user_password) values (%s,%s,%s)",(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                #return json.dumps({'message':'User created successfully !'})
                return render_template('index.html')
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route("/showData")
def showData():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("select * from tbl_user")
        data = cursor.fetchall()
        return render_template('datashow.html',data=data)
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route("/showDataid/<id>",methods=['GET'])
def showDataid(id):
	conn = mysql.connect()
	cur = conn.cursor()
	cur.execute("select * from tbl_user where user_id = %s",int(id))
	data = cur.fetchall()
	return render_template('datashow.html', data=data)

@app.route("/editDataid/<id>",methods=['GET','POST'])
def editDataid(id):
	conn   = mysql.connect()
	cur    = conn.cursor()
	cur.execute("select * from tbl_user where user_id = %s",int(id))
	data   = cur.fetchall()
	return render_template('editdata.html', data=data)

@app.route('/updateData/<id>',methods=['POST'])
def update(id):
    conn    = mysql.connect()
    cursor  = conn.cursor()
    result  = cursor.execute("UPDATE tbl_user SET user_name = %s, user_username = %s, user_password = %s WHERE user_id = %s",(request.form['inputName'],request.form['inputEmail'],generate_password_hash(request.form['inputPassword']),int(id)))
    conn.commit()
    conn.close()
    if(result):
        return redirect("/showData")
    else:
        return json.dumps({'updated':'false'})

@app.route("/uploadImg",methods=['GET','POST'])
def uploadImg():
    if request.method == 'GET':
        return """
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form action="" method=post enctype=multipart/form-data>
            <p><input type=file name=file>
            <input type=submit value=Upload>
            </form>"""
    else:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('main'))


@app.route("/login",methods=['GET'])
def login():
	return render_template('login.html')


@app.route("/checkUser",methods=['post'])
def checkUser():
    email = request.form['inputEmail']
    password = request.form['inputPassword']
    conn = mysql.connect() 
    cursor  = conn.cursor()
    cursor.execute("SELECT user_username,user_password FROM tbl_user WHERE user_username ='"+email+"' and user_password ='"+generate_password_hash(password)+"'")
    user = cursor.fetchone()
    if user == None:
        return render_template('index.html')
    else:
        return redirect(url_for("main"))
        

app.run()