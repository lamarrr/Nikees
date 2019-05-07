import json
import hashlib
import os.path
import requests
import names
import random
import aliaser

# get current absolute directory path for this script
paths = __file__.split(os.path.sep)[:-1]

# root dir
ROOT = os.path.sep.join(paths)

hash_id = hashlib.md5("abcdefg".encode("utf-8")).hexdigest()

# store under 'used_emails' directory
file_path = ROOT+os.path.sep+"logs"+os.path.sep+hash_id
user_exists = os.path.exists(file_path)

print(user_exists)



PATH = __file__.split(os.path.sep)
EMAILS_PATH = os.path.sep.join((*PATH[:-1],"db","emails.txt"))
EMAIL_USAGE_LOG_PATH = os.path.sep.join((*PATH[:-1],"logs","emails.json"))



def gen_catchall_email(domain):
    fn = names.get_first_name()
    sn = names.get_last_name()
    label = "".join([random.randint(0,9) for _ in range(4)])
    return fn+sn+label+"@"+domain





def pop_random_email():
    try:
        with open(EMAILS_PATH,"r") as emails_f:
            emails = emails_f.readlines()
            new_email = emails[0].replace("\n","")
        with open(EMAILS_PATH,"w") as emails_f:
            emails_f.writelines(emails[1:])
        return new_email
    except:
        raise Exception("Sorry, You have no emails (random) left for account generation")    


def count_random_emails():
        s = 0
        with open(EMAILS_PATH,"r") as emails_f:
            s = len(emails_f.readlines())
        return s




"""
def _cpop_random_email():
    try:
        with open(EMAILS_PATH,"r") as emails_f:
            emails = emails_f.readlines()
            new_email = emails[0].replace("\n","")
        with open(EMAILS_PATH,"w") as emails_f:
            emails_f.writelines(emails[1:])
        return new_email
    except:
        return None   

def purge_random_emails():
    new_mails = []
    mail = _cpop_random_email()
    while not(mail == None):
        new_mails.append(mail)
        mail = _cpop_random_email()
    return new_mails

def log_mails(mails):
    payload = dict()
    for mail in mails:
        payload.update({mail: {
            "used": [],
            "unused": aliaser.generate_alias(mail)["."]
        }
        })
    mail_log = None
    with open(EMAIL_USAGE_LOG_PATH,"r") as k:
        mail_log = json.load(k)
    if mail_log:
        mail_log.update(payload)
        with open(EMAIL_USAGE_LOG_PATH,"w") as w:
            json.dump(mail_log,w)

"""









if __name__ == "__main__":
    pass