import socket
from aes_1805093 import key_schedule, encrypt, decrypt, cleanup
from dh_1805093 import getPrime, power

s = socket.socket()		
port = 12345			
s.connect(('127.0.0.1', port))

# take key size as input
# KEY_SIZE = input("Enter key size (128, 192, 256): ")
# KEY_SIZE = int(KEY_SIZE)
# if KEY_SIZE not in [128, 192, 256]:
#   print("Invalid key size")
#   exit(0)
KEY_SIZE = 128

##############################################################
# take key as input
# key = input("Enter key: ")
# key = 'Thats my Kung Fu'
##############################################################

##############################################################
# receive p and g from server
p = int(s.recv(1024).decode())
g = int(s.recv(1024).decode())

# generate b and B
b = getPrime(KEY_SIZE//2)
B = power(g, b, p)

# send B to server
s.send(str(B).encode())

# receive A from server
A = int(s.recv(1024).decode())

# generate key
key = power(A, b, p)
key = str(key)
##############################################################

w = key_schedule(key, KEY_SIZE)

while True:
  # receive cipher text from server
  received = s.recv(1024).decode()

  # decrypt cipher text
  retrieved_text = decrypt(received, w, KEY_SIZE)
  print("retrieved text:", retrieved_text)
  original_text = cleanup(retrieved_text)
  print("original text:", original_text)

  # take input and send to server
  text = input("Enter text: ")

  # encrypt text
  cipher_hex, cipher_text = encrypt(text, w, KEY_SIZE)

  # send cipher text to server
  s.send(cipher_text.encode())

  # s.close()	