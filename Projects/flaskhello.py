from flask import Flask, render_template, request
import os;

class AList:
    def __init__(self, id, date):
        self.id = id
        self.date = date



app = Flask(__name__)
lists=[AList(1, '12.03.2018'), AList(2, '13.03.2018'), AList(3, '14.03.2018')]

@app.route('/index.html', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        os.system("mpiexec -n 4 python mpts.py " + request.form['number'])
        return render_template("index.html", alists=lists)
    else:
        return render_template("index.html", alists=lists)

    
@app.route('/calc_history.html')
def hist():
    return render_template("calc_history.html", alists=lists)

@app.route('/login.html')
def login():
    return render_template("login.html", alists=lists)


if __name__ == "__main__":
    app.run()
