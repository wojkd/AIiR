from mpi4py import MPI
import sys
import time
import os

if (len(sys.argv) != 2):
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
plik = open("result.txt", "w")
if rank == 0:
    for i in range((prime_range*proc)+1, primes+1, 1):
        if ((i != 1) and (i != prime)): 
            if (prime % i) == 0:
                result = 1
                break
for i in range((rank*prime_range)+1, ((rank+1)*prime_range)+1, 1):
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
        print("number:", prime, "is not prime")
        print("execution time:", milli_sec, "milliseconds")
        open("result.txt", "w").write("number: " + str(prime) + " is not prime" + 
		"	execution time: " + str(milli_sec) + " milliseconds")
    else:
        print("number:", prime, "is prime")
        print("execution time:", milli_sec, "milliseconds")
        open("result.txt", "w").write("number: " + str(prime) + " is prime" + 
		"	execution time: " + str(milli_sec) + " milliseconds")