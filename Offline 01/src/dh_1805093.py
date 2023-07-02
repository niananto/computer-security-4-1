import time
import random

def power(base, exp, mod):
	res = 1
	base = base % mod
	
	while exp > 0:
		if exp & 1:
			res = (res * base) % mod

		exp >>= 1
		base = (base * base) % mod
	
	return res

def millerRabinTest(d, n):
	a = 2 + random.randint(1, n - 4) # [2..n-2]
	x = power(a, d, n) # Compute a^d % n

	if (x == 1 or x == n - 1):
		return True

	while (d != n - 1):
		x = (x * x) % n
		d *= 2

		if x == 1:
			return False
		if x == n - 1:
			return True

	return False

def isPrime(n, iteration = 5):
	
	if n <= 1 or n == 4:
		return False
	if n <= 3:
		return True

	d = n - 1
	while (d % 2 == 0):
		d >>= 1

	for i in range(iteration):
		if (millerRabinTest(d, n) == False):
			return False
		
	return True

def getPrime(bitlen):
	while True:
		q = random.getrandbits(bitlen)
		p = 2*q + 1
		if isPrime(p, 10) and isPrime(q, 10):
			return p

def getPrimitiveRoot(min, max, p):
	while True:
		g = random.randint(min, max)
		if power(g, (p - 1) // 2, p) != 1 and power(g, 2, p) != 1:
			return g


def main():
  bitlens = [128, 192, 256]
  elapsed = {'p': 0, 'g': 0, 'a': 0, 'b': 0, 'A': 0, 'B': 0, 'Ab': 0, 'Ba': 0}

  for bitlen in bitlens:
    for i in range(5):
      start = time.time()
      p = getPrime(bitlen)
      end = time.time()
      elapsed['p'] += end - start

      start = time.time()
      g = getPrimitiveRoot(2, p - 2, p)
      end = time.time()
      elapsed['g'] += end - start

      start = time.time()
      a = getPrime(bitlen//2)
      end = time.time()
      elapsed['a'] += end - start

      start = time.time()
      b = getPrime(bitlen//2)
      end = time.time()
      elapsed['b'] += end - start

      start = time.time()
      A = power(g, a, p)
      end = time.time()
      elapsed['A'] += end - start

      start = time.time()
      B = power(g, b, p)
      end = time.time()
      elapsed['B'] += end - start

      start = time.time()
      Ab = power(A, b, p)
      end = time.time()
      elapsed['Ab'] += end - start

      start = time.time()
      Ba = power(B, a, p)
      end = time.time()
      elapsed['Ba'] += end - start

    # take the average and print
    elapsed = {k: v/5 for k, v in elapsed.items()}
    # print("bitlen:", bitlen)
    # print("\t", "p:", elapsed['p'])
    # print("\t", "g:", elapsed['g'])
    # print("\t", "a or b:", (elapsed['a']+elapsed['b'])/2)
    # print("\t", "A or B:", (elapsed['A']+elapsed['B'])/2)
    # print("\t", "shared key:", (elapsed['Ab']+elapsed['Ba'])/2)

    # print the same thing in a csv file
    with open('dh_1805093.csv', 'w') as f:
      f.write('bitlen,p,g,a or b,A or B,shared key\n')
      for bitlen in bitlens:
        f.write(str(bitlen) + ',')
        f.write(str(elapsed['p']) + ',')
        f.write(str(elapsed['g']) + ',')
        f.write(str((elapsed['a']+elapsed['b'])/2) + ',')
        f.write(str((elapsed['A']+elapsed['B'])/2) + ',')
        f.write(str((elapsed['Ab']+elapsed['Ba'])/2) + '\n')

if __name__ == '__main__':
	main()