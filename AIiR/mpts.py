from mpi4py import MPI
import sys
import time
import os
import pymysql

if (len(sys.argv) != 3):
    prime = 0
else:
    prime = int(sys.argv[1])


milli_sec = int(round(time.time() * 1000))
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
primes = int(prime ** (1/2))
proc = comm.Get_size()
prime_range = int(primes/proc)
diffrence = primes - prime_range*proc
result = 0

def calc_proc(index):
    value = int(((index/prime_range)*100)/proc)
    return value

connection = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = 'pass',
                             db = 'aiir')
cursor = connection.cursor()

nstat=0
sql = "UPDATE Tasks SET TStatus=" + str(nstat) + " WHERE Task_ID=" + str(sys.argv[2])
cursor.execute(sql)
connection.commit()
sql = "UPDATE Tasks SET TStatus=TStatus+" + str(nstat) + " WHERE Task_ID=" + str(sys.argv[2])
plik = open("result.txt", "w")
dif = 0
oldstat = 0

if rank == 0:
    j = 0
    for i in range((prime_range*proc)+1, primes+1, 1):
        j = j + 1
        if not (j % 30000):
            nstat = calc_proc(j)
            dif=nstat-oldstat
            sql = "UPDATE Tasks SET TStatus=TStatus+" + str(dif) + " WHERE Task_ID=" + str(sys.argv[2])
            cursor.execute(sql)
            connection.commit()
            oldstat=nstat
        if ((i != 1) and (i != prime)): 
            if (prime % i) == 0:
                result = 1
                break
j = 0
print(proc)
for i in range((rank*prime_range)+1, ((rank+1)*prime_range)+1, 1):
    j = j + 1
    if not (j % 30000):
        nstat = calc_proc(j)
        dif=nstat-oldstat
        sql = "UPDATE Tasks SET TStatus=TStatus+" + str(dif) + " WHERE Task_ID=" + str(sys.argv[2])
        cursor.execute(sql)
        connection.commit()
        oldstat=nstat
    if ((i != 1) and (i != prime)):
        if (prime % i) == 0:
            result = 1
            break
data = comm.gather(result, root=0)

if rank == 0:
    for r in data:
        if r == 1:
            result = 1
            break
    milli_sec = int(round(time.time() * 1000)) - milli_sec
    if prime == 0:
        result = 1
    if result == 1:
        sql = "UPDATE Tasks SET Result=0b0, TStatus=200 WHERE Task_ID=" + str(sys.argv[2])
        print("number:", prime, "is not prime")
        print("execution time:", milli_sec, "milliseconds")
        open("result.txt", "w").write("number: " + str(prime) + " is not prime")
    else:
        sql = "UPDATE Tasks SET Result=0b1, TStatus=200 WHERE Task_ID=" + str(sys.argv[2])
        print("number:", prime, "is prime")
        print("execution time:", milli_sec, "milliseconds")
        open("result.txt", "w").write("number: " + str(prime) + " is prime")
    cursor.execute(sql)
    sql = "UPDATE Cluster SET CLStatus=0 WHERE CL_ID=1"
    cursor.execute(sql)
    connection.commit()


