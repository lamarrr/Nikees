import os.path
import enum
import json



PATH = __file__.split(os.path.sep)
ORDERS_PATH = os.path.sep.join((*PATH[:-1],"db","orders.txt"))
AUTH_PATH = os.path.sep.join((*PATH[:-1],"logs","auth.json"))

# to check order details
def get_order(uid,order_number):
    entries = None
    with open(ORDERS_PATH,"r") as orders_f:
        entries = tuple(x.replace("\n","") for x in orders_f.readlines())
    for entry in entries:
        f_uid,f_order_number,country,qty,account_type = entry.split(",")
        country = country.upper()
        if f_uid == uid and order_number == f_order_number:
            return f_uid,f_order_number,country,qty,account_type
    return None


# to remove order for processing
def pop_order(order_number):
    with open(ORDERS_PATH,"r") as orders_f:
        entries = tuple(x.replace("\n","") for x in orders_f.readlines())
    index = 0
    for entry in entries:
        _,f_order_number,*_ = entry.split(",")
        if f_order_number == order_number:
            f,b = entries[:index],entries[index+1:]
            entries = list()
            entries.extend((*f,*b))
            entries = tuple(map(lambda x: x+"\n",entries))
            with open(ORDERS_PATH,"w") as orders:
                orders.writelines(entries) 
            return
        index += 1
    raise Exception("No such order number: %s " % order_number)



# check if user is authorized to execute ordering commands with constraints
def is_auth(uid,country,qty,acc_type):
    #print(uid,country,qty,acc_type)
    auths = json.load(open(AUTH_PATH))
    for c_auth in auths:
        if c_auth["uid"] == uid and c_auth["total"] == qty and c_auth["country"].upper() == country.upper() and c_auth["tag"] == acc_type:
            #print("Available")
            return True
    return False



# log authorized user's order details for future commands
def log_auth(uid,order_number,country,qty,account_type):
    auths = json.load(open(AUTH_PATH))
    auths.append({"uid": uid, "orderNumber": order_number, "total":qty, "country": country.upper(), "tag": account_type})
    json.dump(auths,open(AUTH_PATH,"w"))

# pop auth for task initiation
def pop_auth(uid,qty,country,tag):
    entries = json.load(open(AUTH_PATH))
    index = 0
    for entry in entries:
        if uid == entry["uid"] and qty == entry["total"] and country.upper() == entry["country"].upper() and tag.lower() == entry["tag"].lower():
            f,b = entries[:index],entries[index+1:]
            entries = list()
            entries.extend((*f,*b))
            #entries = tuple(map(lambda x: x+"\n",entries))
            with open(AUTH_PATH,"w") as auths:
                 json.dump(entries,auths)
            return entry
        index += 1
    raise Exception("No pending order for user: %s " % uid)

"""
request accs:
is auth?
pop from auth.json
init task
add to tasks.json
notify user
fire notification to queue
"""





if __name__ == "__main__":
    #log_auth(*get_order("lamar#3456","1234667"))
    #pop_order("1234667")
    pop_auth("lamarrr#5536","99","US","random")


#pop_order("1234567")

#print(log_auth(*get_order("lamar#3456","123456")))