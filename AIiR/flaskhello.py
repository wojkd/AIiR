from flask import Flask, render_template, request, session, redirect,  escape, json, flash
from multiprocessing import Process
import pymysql
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from time import sleep

import os;

mysql=MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pass'
app.config['MYSQL_DATABASE_DB'] = 'aiir'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

class mpi_user(object): 
    def __init__(self, user, task, result, progress):
        self.user=user
        self.task=task
        self.progress=progress
        if result == "b'\\x00'":
            self.result="Not prime"
        else:
            self.result="Prime"

def run_mpi_script(num, proc):
    os.system("mpiexec -n " + proc + " python mpts.py " + num)



connection = pymysql.connect(host = 'localhost',
                                 user = 'root',
                                 password = 'pass',
                                 db = 'aiir')

cursor = connection.cursor()

def pick_uid():
    s = "SELECT * FROM aiir.Users WHERE user_username='" + str(escape(session['username'])) + "'"
    cursor.execute(s)
    data = cursor.fetchall()
    for dt in data:
        uid = int(dt[0])
    return uid

app = Flask(__name__)
app.secret_key = b'\x7f\x14\xa8G\xa5!R3t\x04\xba\xb5\xb5f\r\xe4'

@app.route('/index.html', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect('/userHome')
    else:
        return redirect('/login.html')

    
@app.route('/calc_history')
def hist():
    if session.get('username'):
        if 'username' in session:
            uid = pick_uid()
            sql = "SELECT * FROM aiir.Tasks WHERE user_id=" + str(uid) +" order by Task_Date desc"
            cursor.execute(sql)
            data = cursor.fetchall()
            tlist = []
            for dt in data:     
                if str(dt[4]) == "200":
                    ob = mpi_user("You", int(dt[2]), str(dt[3]), 'Done')
                else:
                    ob = mpi_user("You", int(dt[2]), str(dt[3]), dt[4])
                print("objtask" + str(ob.result))
                tlist.append(ob)
        return render_template("calc_history.html", data=tlist, uname = escape(session['username']))
    else:
        return redirect('/showSignIn')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    session.pop('username', None)
    if request.method == 'POST':
        log = request.form['login']
        pw = request.form['password']
        sql = "SELECT * FROM aiir.Users WHERE user_username='" + str(log) + "' AND Password='" + str(pw) + "'"
        cursor.execute(sql)
        rc = cursor.rowcount
        if rc != 0:
            session['username'] = log
            return redirect('index.html')      
    return render_template("login.html")

@app.route('/showSignUp')
def showSignup():
    return render_template("signup.html")

@app.route('/signUp',methods=['POST', 'GET'])
def signUp():
    try:
        _name = request.form['userName']
        _password = request.form['inputPassword']

        if _name and _password:

            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_newUser',(_name,_hashed_password))

            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                flash('Registration successfull!')
                return redirect('login.html')
            else:
                return render_template('error.html',error = str(data[0]))
        else:
            return render_template('error.html',error = 'Fill in all fields!')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/showSignIn')
def showSignIn():
    return render_template("login.html")

@app.route('/userHome', methods=['GET','POST'])
def userHome():
    if session.get('user'):
        if request.method == 'POST':
            num = request.form['number']
            if num:
                if int(num) >= 0:
                    num = int(num)
                else:
                    num = 0
            else:
                num = 0
            proc = request.form['proc']
            if proc:
                if int(proc) >= 1 and int(proc) <= 32:
                    proc = int(proc)
                else:
                    proc = 1
            else:
                proc = 1
            uid = pick_uid()
            sql = "INSERT INTO aiir.Tasks (User_ID, Task, Processors) VALUES (" + str(uid) + ", " + str(num) + ", " + str(proc) +")"
            cursor.execute(sql)
            connection.commit()
            return render_template("userHome.html", welcome=session.get('username'))
        return render_template('userHome.html',welcome=session.get('username'))
    else:
        return render_template('/login.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    session.pop('username',None)
    return redirect('index.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username=request.form['inputUsername']
        _password=request.form['inputPassword']

        con=mysql.connect()
        cursor=con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data=cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][2]),_password):
                session['user'] = data[0][0]
                session['username'] = data[0][1]
                return redirect('/userHome')
            else:
                return render_template('error.html',error='Wrong username or password.')
        else:
            return render_template('error.html',error='Wrong username or password.')

    except Exception as e:
        return render_template('error.html',error=str(e))

    finally:
        cursor.close()
        con.close()

@app.route('/_stuff', methods= ['GET'])
def stuff():
    cpu=round(getCpuLoad())
    ram=round(getVmem())
    disk=round(getDisk())
    return jsonify(cpu=cpu, ram=ram, disk=disk)

if __name__ == "__main__":
    app.run(threaded=True)
