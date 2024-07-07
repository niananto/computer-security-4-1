import socket
from aes_1805093 import key_schedule, encrypt, decrypt, cleanup
from dh_1805093 import getPrime, getPrimitiveRoot, power

s = socket.socket()        
port = 12345     
 
# s.bind(('', port)) # accept connections from any address
s.bind(('127.0.0.1', port)) # only accept connections from localhost    
print("socket binded to", port)
 
s.listen(5)    
print ("socket is listening")   

c, addr = s.accept()    
print ('Got connection from', addr)

# take key size as input
# KEY_SIZE = input("Enter key size (128, 192, 256): ")
# KEY_SIZE = int(KEY_SIZE)
# if KEY_SIZE not in [128, 192, 256]:
#   print("Invalid key size")
#   exit(0)
KEY_SIZE = 128

##############################################################
# # take key as input
# key = input("Enter key: ")
# key = 'Thats my Kung Fu'
##############################################################

##############################################################
# generate prime number and primitive root
p = getPrime(KEY_SIZE)
g = getPrimitiveRoot(2, p - 2, p)

# send p and g to client
c.send(str(p).encode())
c.send(str(g).encode())

# generate a and A
a = getPrime(KEY_SIZE//2)
A = power(g, a, p)

# send A to client
c.send(str(A).encode())

# receive B from client
B = int(c.recv(1024).decode())

# generate key
key = power(B, a, p)
key = str(key)
##############################################################

w = key_schedule(key, KEY_SIZE)

while True:
  # take input and send to client
  text = input("Enter text: ")

  # encrypt text
  cipher_hex, cipher_text = encrypt(text, w, KEY_SIZE)

  # send cipher text to client
  c.send(cipher_text.encode())

  # receive cipher text from client
  received = c.recv(1024).decode()

  # decrypt cipher text
  retrieved_text = decrypt(received, w, KEY_SIZE)
  print("retrieved text:", retrieved_text)
  original_text = cleanup(retrieved_text)
  print("original text:", original_text)

  # c.close()
   
  # break