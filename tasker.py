import os.path
import json
from apis import config
import makeme
import mailman
import aliaser
from util import kolor as kr
import driver
import queue
import discord


err = kr.StyleRule(foreground="red",bold=True)

PATH = __file__.split(os.path.sep)
TASKS_PATH = os.path.sep.join((*PATH[:-1],"logs","tasks.json"))
PROCESSING_ORDERS_PATH = os.path.sep.join((*PATH[:-1],"processed_orders","processing.json"))
PROCESSING_ORDERS_PATH_UP1 = os.path.sep.join((*PATH[:-1],"processed_orders/"))

# pops task for processing
def pop_any_task():
    tasks = None
    with open(TASKS_PATH,"r") as f:
        tasks = json.load(f)
    try:
        order_number,details = tasks.popitem()
        with open(TASKS_PATH,"w") as f:
            json.dump(tasks,f)
        return order_number,details
    except KeyError:
        return None




"""
names,dob and reg data to be generated at runtime

# adds 
def add_task(order_number,i_d,uid,display_name,qty,country,tag,iwith=""):
    # all properties except phone number generated here
    payload = {
        # check if random or catchall or gmail first
        order_number: {
            "id": i_d,
            "uid": uid,
            "displayName": display_name,
            "tag": tag, #"random|catchall|gmail",
            "with":iwith, # None or value
            "qty": qty,
            "country": country.upper()
        }
    }

    tasks = None
    with open(TASKS_PATH,"r") as f:
        tasks = json.load(f)
    tasks.update(payload)
    with open(TASKS_PATH,"w") as f:
        json.dump(tasks,f)

"""


# fills to be processed task with required registration data
def init_task(iid,display_name,auth_order,target=None):
    order_number = auth_order["orderNumber"]
    payload = {   
    order_number: {
            "id": iid,
            "displayName": display_name,
            "tag": auth_order["tag"], 
            "uid": auth_order["uid"], 
            "qty": auth_order["total"],
            "country": auth_order["country"], # US, GB, CN
            "processed": [ 
                                  ],
            "unprocessed": [] # {email: , password: , firstname, lastname, dob}
    }
    }

    if auth_order["tag"] == "random":
        count = 0
        rlen = int(auth_order["total"])
        if rlen > mailman.count_random_emails():
            raise Exception(err.style("[Tasker] Insufficient email addresses to finish request, please add more."))
        while count < rlen:
            fn,sn = makeme.get_name()
            mail = mailman.pop_random_email()
            payload[order_number]["unprocessed"].append({"email":mail, "password":config.default_nike_accounts_password, "firstName":fn,"secondName":sn,"dob":makeme.get_dob()})
            count+=1

    elif auth_order["tag"] == "catchall":
        domain = target
        count = 0
        while count < int(auth_order["total"]):
            (fn,sn),unique = makeme.get_unique_catchall()
            payload[order_number]["unprocessed"].append({"email":unique+"@"+domain, "password":config.default_nike_accounts_password, "firstName": fn, "secondName": sn,"dob":makeme.get_dob()})          
            count+=1


    elif auth_order["tag"] == "gmail":
        gmail = target
        mail_alias = aliaser.generate_alias(gmail)["."]
        count = 0
        while count < int(auth_order["total"]):
            (fn,sn),_ = makeme.get_unique_catchall()
            payload[order_number]["unprocessed"].append({"email": mail_alias[count], "password": config.default_nike_accounts_password,"firstName":fn,"secondName":sn,"dob":makeme.get_dob()})
            count += 1

    
    return payload



def log_task(task):
    tasks = dict()
    with open(TASKS_PATH) as tasks_f:
        tasks :dict = json.load(tasks_f)
        tasks.update(task)
    with open(TASKS_PATH,"w") as tasks_f:
        json.dump(tasks,tasks_f)






    """
    if tag=="random":
        payload[order_number]["emails"]["unused"].append(aliaser.generate_alias(mailman.pop_random_email())["."])
    elif tag=="catchall":
        payload[order_number]["emails"]["unused"].append(mailman.gen_catchall_email(iwith))
    """


#def gen_mail()

    







def execute_task(order_no,task):
    print('executing tasks')
    if task["country"] == "US":
        index = 0
        for acct in task["unprocessed"]:
            try:
                print("executing task: %d" %index)
                email,password,fn,sn,dob = acct["email"],acct["password"],acct["firstName"],acct["secondName"],acct["dob"]
                driver.register_us(email,password,fn,sn,dob)
                acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                task["processed"].append(acct)
                task["unprocessed"] = task["unprocessed"][index+1:]
                append_acc_processing(order_no,task,acct)

            except:
                try:
                    email = mailman.pop_random_email()
                    driver.register_us(email,password,fn,sn,dob)
                    acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                    task["processed"].append(acct)
                    task["unprocessed"] = task["unprocessed"][index+1:]
                    append_acc_processing(order_no,task,acct)

                except:
                    try:
                        email = mailman.pop_random_email()
                        driver.register_us(email,password,fn,sn,dob)
                        acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                        task["processed"].append(acct)
                        task["unprocessed"] = task["unprocessed"][index+1:]
                        append_acc_processing(order_no,task,acct)
                    
                    except:
                        try:
                            email = mailman.pop_random_email()
                            driver.register_us(email,password,fn,sn,dob)
                            acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                            task["processed"].append(acct)
                            task["unprocessed"] = task["unprocessed"][index+1:]
                            append_acc_processing(order_no,task,acct)
                        except Exception as e:
                            raise e
            index+=1
            print("done: %d" %index)

    elif task["country"] == "GB":
        index = 0
        for acct in task["unprocessed"]:
            try:
                print("executing task: %d" %index)
                email,password,fn,sn,dob = acct["email"],acct["password"],acct["firstName"],acct["secondName"],acct["dob"]
                driver.register_gb(email,password,fn,sn,dob)
                acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                task["processed"].append(acct)
                task["unprocessed"] = task["unprocessed"][index+1:]
                append_acc_processing(order_no,task,acct)

            except:
                try:
                    email = mailman.pop_random_email()
                    driver.register_gb(email,password,fn,sn,dob)
                    acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                    task["processed"].append(acct)
                    task["unprocessed"] = task["unprocessed"][index+1:]
                    append_acc_processing(order_no,task,acct)

                except:
                    try:
                        email = mailman.pop_random_email()
                        driver.register_gb(email,password,fn,sn,dob)
                        acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                        task["processed"].append(acct)
                        task["unprocessed"] = task["unprocessed"][index+1:]
                        append_acc_processing(order_no,task,acct)
                    
                    except:
                        try:
                            email = mailman.pop_random_email()
                            driver.register_gb(email,password,fn,sn,dob)
                            acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                            task["processed"].append(acct)
                            task["unprocessed"] = task["unprocessed"][index+1:]
                            append_acc_processing(order_no,task,acct)
                        except Exception as e:
                            raise e
            index+=1
            print("done: %d" %index)





    elif task["country"] == "CN":
        index = 0
        for acct in task["unprocessed"]:
            try:
                email,password,fn,sn,dob = acct["email"],acct["password"],acct["firstName"],acct["secondName"],acct["dob"]
                #driver.register_cn(email,password,fn,sn,dob)
                raise NotImplementedError("Chinese Accounts")
                acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                task["processed"].append(acct)
                task["unprocessed"] = task["unprocessed"][index+1:]
                append_acc_processing(order_no,task,acct)

            except:
                try:
                    email = mailman.pop_random_email()
                    #driver.register_cn(email,password,fn,sn,dob)
                    raise NotImplementedError("Chinese Accounts")
                    acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                    task["processed"].append(acct)
                    task["unprocessed"] = task["unprocessed"][index+1:]
                    append_acc_processing(order_no,task,acct)
                except:
                    try:
                        email = mailman.pop_random_email()
                        #driver.register_cn(email,password,fn,sn,dob)
                        raise NotImplementedError("Chinese Accounts")
                        acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                        task["processed"].append(acct)
                        task["unprocessed"] = task["unprocessed"][index+1:]
                        append_acc_processing(order_no,task,acct)
                    except:
                        try:
                            email = mailman.pop_random_email()
                            #driver.register_cn(email,password,fn,sn,dob)
                            raise NotImplementedError("Chinese Accounts")
                            acct = {"email":email,"password":password,"firstName":fn,"secondName":sn, "dob":dob}
                            task["processed"].append(acct)
                            task["unprocessed"] = task["unprocessed"][index+1:]
                            append_acc_processing(order_no,task,acct)
                        except Exception as e:
                            raise e
                #raise e
            index+=1
    proc_id :str = task["uid"]
    proc_id = proc_id.replace("#","") + "N"+ order_no + ".txt"
    payload = open(PROCESSING_ORDERS_PATH_UP1+proc_id).read()
    
    print(payload)
    print(task["uid"])

    """
    for u in ibot.get_all_members():
        if str(u) == task["uid"]:
            print(u)
            yield from ibot.send_message(u,payload)
    """
    #notif.put((payload,task["id"],task["displayName"],task["uid"]))

def append_acc_processing(order_no,task,new_acc):
    # add acc to file
    # add acc to processing.json log
    #

    proc_id :str = task["uid"]
    proc_id = proc_id.replace("#","") + "N"+ order_no + ".txt"
    with open(PROCESSING_ORDERS_PATH_UP1+proc_id,"a") as pop:
        pop.write("email: %s, password: %s, firstName: %s, lastName: %s" % (new_acc["email"],new_acc["password"],
        new_acc["firstName"],new_acc["secondName"]))
        pop.write("\n")

    procs = None
    with open(PROCESSING_ORDERS_PATH) as procs_f:
        procs = json.load(procs_f)
    procs.update({order_no:task})
    with open(PROCESSING_ORDERS_PATH,"w") as procs_f:
        json.dump(procs,procs_f)
    
    



def log_for_processing(order_no,task):
    with open(PROCESSING_ORDERS_PATH) as procs_f:
        procs :dict = json.load(procs_f)
        procs.update({order_no:task})
    with open(PROCESSING_ORDERS_PATH,"w") as procs_f:
        json.dump(procs,procs_f)
    proc_id :str = task["uid"]
    proc_id = proc_id.replace("#","") + "N" + order_no + ".txt"
    with open(PROCESSING_ORDERS_PATH_UP1+proc_id,"a") as f:
        f.write("order number: " + order_no +", ")
        f.write("country: "+task["country"]+", ")
        f.write("total: "+task["total"]+", ")
        f.write("type: "+task["tag"]+", ")
        f.write("\n\n")


# log to processing.json
# create new txt file for user order
# for each account [key: order_number]:
#   pop from key->unprocessed  
#   register
#   append to key->processed, if exception raised:
#       if recoverable, ignore and continue with the rest, else re-raise
#   
#   update processing.json file and txt file

# send to user via discord
# 



"""
def process_acc(acc):
    email = acc["email"]
    fn = acc["firstName"]
    sn = acc["secondName"]
    dob = acc["dob"]
    password = acc["password"]
    driver.register_cn(email,password,fn,sn,dob)
#process_acc(aee["12346789"]["unprocessed"][0])
"""




















if __name__ == "__main__":
    #task = {"uid": "lamarrr#5536", "orderNumber": "12346789", "total": "1", "country": "US", "tag": "random"}
    order_no,proc_task = pop_any_task()
    log_for_processing(order_no,proc_task)
    #print(proc_task)




#log_task(aee)