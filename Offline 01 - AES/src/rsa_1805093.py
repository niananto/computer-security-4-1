from dh_1805093 import getPrime, power, getPrimitiveRoot

# two large prime numbers p and q
p = getPrime(128)
q = getPrime(128)

n = p * q

# public key
# choose e such that e and (p-1)(q-1) are coprime
temp = (p - 1) * (q - 1)
e = getPrimitiveRoot(2, temp - 1, temp)

# private key
# choose d such that ed = 1 (mod (p-1)(q-1))
d = power(e, -1, (p - 1) * (q - 1))

# take input
msg = input("Enter message: ")

# encrypt
msg = [ord(c) for c in msg]
cipher = [power(m, e, n) for m in msg]
cipher = [str(c) for c in cipher]
print("cipher:", cipher)
cipher = ''.join([str(i) for i in cipher])

# decrypt
cipher = [ord(c) for c in cipher]
cipher = [power(c, d, n) for c in cipher]
cipher = [str(c) for c in cipher]
msg = ''.join([str(i) for i in cipher])

print("original message:", msg)