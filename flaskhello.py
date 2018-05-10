from flask import Flask, render_template, request
from multiprocessing import Process
import os;



def run_mpi_script(num, proc):
    os.system("mpiexec -n " + proc + " python mpts.py " + num)


app = Flask(__name__)

@app.route('/index.html', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if __name__ == '__main__':
            num = request.form['number']
            proc = "4"
            p = Process(target=run_mpi_script, args=(num, proc))
            p.start()
        return render_template("index.html")
    else:
        return render_template("index.html")

    
@app.route('/calc_history.html')
def hist():
    return render_template("calc_history.html")

@app.route('/login.html')
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run()
