import time
from utils_1805093 import *

rounds = {128: 10, 192: 12, 256: 14}

def key_schedule(key, KEY_SIZE):
  KEY_WORDS = KEY_SIZE // 32
  KEY_LEN = KEY_SIZE // 8

  # make key KEY_SIZE bits or truncate if longer
  key = key.zfill(KEY_LEN)
  key = key[:KEY_LEN]
  # print("Your key is: ", key)

  # split KEY_LEN byte key into sets of 4 bytes(32 bits)
  # 4*4 for 128 bit key, 6*4 for 192 bit key, 8*4 for 256 bit key
  w = [key[i:i+4] for i in range(0, len(key), 4)]
  # print(w, type(w), len(w), type(w[0]), len(w[0]))

  # convert key to hex
  for r in range(len(w)):
    w[r] = w[r].encode('utf-8').hex()
    w[r] = [w[r][j:j+2] for j in range(0, len(w[r]), 2)]
    # print(w[r], type(w[r]), len(w[r]))

  # number of round 
  round = rounds[KEY_SIZE]

  # key generation
  rc = 1
  for r in range(1, round+1):
    hex_list = w[(r*KEY_WORDS)-1]
    # print("r", r, "- before rotate: ", hex_list, type(hex_list), len(hex_list))

    # rotate left
    hex_list = hex_list[1:] + hex_list[:1]
    # print("r", r, "- after rotate: ", hex_list, type(hex_list), len(hex_list))

    # substitute bytes
    hex_list = sub_bytes_list(hex_list)
    # print("r", r, "- after sub: ", hex_list, type(hex_list), len(hex_list))

    # xor with round constant
    # then we get g(w[3]), g(w[7]), g(w[11]) ...
    if rc > 0x80:
      rc = (rc ^ 0x1B) & 0xFF
    # print("r", r, "- rc: ", hex(rc))

    hex_list[0] = hex(int(hex_list[0], 16) ^ rc)[2:].zfill(2)
    # print("r", r, "- after rounding: ", hex_list, type(hex_list), len(hex_list))

    # calculate rc for next round
    rc = rc << 1

    for j in range(KEY_WORDS):
      to_xor = w[(r-1)*KEY_WORDS + j]

      # if N>6 and i mod N = 4
      i = (r-1)*KEY_WORDS + j
      if KEY_WORDS > 6 and i % KEY_WORDS == 4:
        # substitute bytes
        to_xor = sub_bytes_list(to_xor)

      xored = []
      for k in range(len(hex_list)):
        xored.append(hex(int(hex_list[k], 16) ^ int(to_xor[k], 16))[2:].zfill(2))
        
      # print("r", r, "- to xor: ", to_xor, type(to_xor), len(to_xor))
      # print("r", r, "- to xor: ", hex_list, type(hex_list), len(hex_list))
      # print("r", r, "- after xor: ", xored, type(xored), len(xored))
      w.append(xored)
      hex_list = xored

  # print all keys
  for r in range(round+1):
    print("Round ", r, ":", w[r*KEY_WORDS:(r+1)*KEY_WORDS])

  return w


def encrypt(plain_text, w, KEY_SIZE):

  # split text in KEY_SIZE bit blocks if longer
  texts = [plain_text[i:i+16] for i in range(0, len(plain_text), 16)]
  # pad last block with 100... if shorter
  if len(texts[-1]) < 16:
    texts[-1] = texts[-1] + '1'
    texts[-1] = texts[-1].ljust(16, '0')
  # print(texts, type(texts), len(texts), type(texts[0]), len(texts[0]))

  cipher_hex = ''
  cipher_text = ''

  # iterate over each block of text
  for text in texts:
    # convert text to hex
    text = text.encode('utf-8').hex()
    text = [text[i:i+2] for i in range(0, len(text), 2)]
    # print(text, type(text), len(text))

    # text to column major order
    state = [[text[i+j] for i in range(0, len(text), 4)] for j in range(4)]
    # print("state:", state)

    round = rounds[KEY_SIZE]
    # round 0 to last round
    for r in range(0, round+1):
      # substitute bytes
      if r != 0:
        state = sub_bytes_matrix(state)
        # print("r", r, "- state after sub: ", state)

      # shift rows
      if r != 0:
        for i in range(1, len(state)):
          state[i] = state[i][i:] + state[i][:i]
        # print("r", r, "- state after shift: ", state)

      # mix columns
      if r!= 0 and r != round:
        state = mix_column(state)
        # print("r", r, "- state after mix: ", state)

      # add round key
      # applicable for all rounds
      # round key matrix in column major order
      round_key = [[w[r*4 + i][j] for i in range(4)] for j in range(4)]
      # xor state with round key
      state = [[hex(int(state[i][j], 16) ^ int(round_key[i][j], 16))[2:].zfill(2) for j in range(4)] for i in range(4)]
      # print("r", r, "- state after round: ", state)

    # transpose state
    state = [[state[i][j] for i in range(4)] for j in range(4)]
    # add to the cipher text in hex
    cipher_hex += ''.join([''.join(state[i]) for i in range(4)])

    # add to the cipher text in ascii
    for i in range(4):
      for j in range(4):
        b = BitVector(hexstring=state[i][j])
        cipher_text += b.get_bitvector_in_ascii()

  return cipher_hex, cipher_text


def decrypt(cipher_text, w, KEY_SIZE):

  # split cipher text into KEY_SIZE bit blocks if longer
  ciphers = [cipher_text[i:i+16] for i in range(0, len(cipher_text), 16)]
  # no need to pad since we know the length of the cipher text is a multiple of 16
  # print("ciphers:", ciphers, type(ciphers), len(ciphers), type(ciphers[0]), len(ciphers[0]))

  retrieved_text = ''

  # iterate over each block
  for cipher in ciphers:
    # convert cipher to hex
    cipher = ''.join(format(ord(i), '02x') for i in cipher)
    cipher = [cipher[i:i+2] for i in range(0, len(cipher), 2)]
    # print("cipher:", cipher, type(cipher), len(cipher), type(cipher[0]), len(cipher[0]))

    # cipher in column major order
    state = [[cipher[i+j] for i in range(0, len(cipher), 4)] for j in range(4)]
    # print("state:", state, type(state), len(state), type(state[0]), len(state[0]))

    round = rounds[KEY_SIZE]
    # round 0 to last round
    for r in range(0, round+1):
      # inverse shift rows
      if r != 0:
        for i in range(4):
          state[i] = state[i][-i:] + state[i][:-i]
        # print("r", r, "- state after shift:", state)

      # inverse sub bytes
      if r != 0:
        state = inv_sub_bytes_matrix(state)
        # print("r", r, "- state after sub:", state)

      # add round key
      # round key matrix in column major order
      round_key = [[w[(round-r)*4 + i][j] for i in range(4)] for j in range(4)]
      # print("round key:", round_key)
      # xor state with round key
      state = [[hex(int(state[i][j], 16) ^ int(round_key[i][j], 16))[2:].zfill(2) for j in range(4)] for i in range(4)]
      # print("r", r, "- state after round: ", state)

      # inverse mix columns
      if r != 0 and r != round:
        state = inv_mix_column(state)
        # print("r", r, "- state after mix: ", state)

    # get plain text from state
    state = [[state[i][j] for i in range(4)] for j in range(4)]
    for i in range(4):
      for j in range(4):
        retrieved_text += chr(int(state[i][j], 16))

  return retrieved_text

def cleanup(retrieved_text): # get rid of the padding
  original_text = ''
  for i in range(len(retrieved_text)-1, 1, -1):
    if retrieved_text[i] == '0':
      original_text = retrieved_text[:i]
    else:
      break
  if len(original_text) > 1 and original_text[-1] == '1':
    original_text = original_text[:-1]

  return original_text

def main():
  KEY_SIZE = input("Enter key size (128, 192, 256): ")
  KEY_SIZE = int(KEY_SIZE)
  if KEY_SIZE not in [128, 192, 256]:
    print("Invalid key size")
    exit(0)
  # KEY_SIZE = 256

  # key = 'Thats my Kung Fu'
  key = input("Enter key: ")
  # plain_text = 'Two One Nine Two'
  plain_text = input("Enter text: ")

  start = time.time()
  w = key_schedule(key, KEY_SIZE)
  end = time.time()
  print("key schedule time:", end-start)

  start = time.time()
  cipher_hex, cipher_text = encrypt(plain_text, w, KEY_SIZE)
  end = time.time()
  print("cipher hex:", cipher_hex)
  print("cipher text:", cipher_text)
  print("encryption time:", end-start)

  start = time.time()
  retrieved_text = decrypt(cipher_text, w, KEY_SIZE)
  end = time.time()
  print("retrieved text:", retrieved_text)
  print("decryption time:", end-start)
  
  original_text = cleanup(retrieved_text)
  print("original text:", original_text)

if __name__ == '__main__':
  main()