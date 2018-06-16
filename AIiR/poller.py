import os
import time
import pymysql

def run_mpi_script(num, proc, taskid):
    os.system("mpiexec -np " + proc + " python3 mpts.py " + num + " " + taskid)


connection = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = 'pass',
                             db = 'aiir')

cursor = connection.cursor()

sql = "UPDATE Cluster SET CLStatus=0 WHERE CL_ID=1"
cursor.execute(sql)
connection.commit()

print("waiting for tasks...")

while True:
    connection.commit()

    sql = "SELECT * FROM aiir.Tasks WHERE TStatus=300"
    cursor.execute(sql)
    data = cursor.fetchall()

    sql = "SELECT * FROM aiir.Cluster WHERE CLStatus=0"
    cursor.execute(sql)
    clst = cursor.rowcount
    for dt in data:
        num = int(dt[2])
        tid = int(dt[0])
        status = int(dt[4])
        proc = int(dt[6])
        if status == 300 and clst != 0:
            sql = "UPDATE Cluster SET CLStatus=1 WHERE CL_ID=1"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * FROM aiir.Tasks WHERE TStatus=300"
            print("calculating number: " + str(num))
            run_mpi_script(str(num), str(proc), str(tid))
        time.sleep(2)
