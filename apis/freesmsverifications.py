
if __name__ == "__main__":
        import config
else:
        from . import config

import requests
import json
import re
"""
/smsapi/GetNumbers?apiId={ID}&secret={SEC}

{"Status":"Success","Number":"44xxxxxxxxxx","DateAllocated":"2017-xx-xx","ServiceName":"xxxx","ErrorCode":"Non","Error":null,"Message":null}
"""


pat = re.compile(r"\d{4,12}")




def get_number():
        try:
                resp = requests.get(
                        "http://www.freesmsverifications.com/smsapi/GetNumbers?apiId={ID}&secret={SEC}".format(ID=config.freesmsverifications_ID,SEC=config.freesmsverifications_secret))
        except:
                try:
                        resp = requests.get(
                                "http://www.freesmsverifications.com/smsapi/GetNumbers?apiId={ID}&secret={SEC}".format(ID=config.freesmsverifications_ID,SEC=config.freesmsverifications_secret))
                except:
                        try:
                                resp = requests.get(
                                        "http://www.freesmsverifications.com/smsapi/GetNumbers?apiId={ID}&secret={SEC}".format(ID=config.freesmsverifications_ID,SEC=config.freesmsverifications_secret))        
                        except:
                                try:
                                        resp = requests.get(
                                                "http://www.freesmsverifications.com/smsapi/GetNumbers?apiId={ID}&secret={SEC}".format(ID=config.freesmsverifications_ID,SEC=config.freesmsverifications_secret))
                                except Exception as e:
                                        raise e


        data = json.loads(resp.content.decode("utf-8"))
        print(data)
        if data["Status"] == "Success":
                # (('7441911768',"44....." 'FE8CE40C9D57D97'), None) ==> ((number,int'l format,id), error_code)
                return data["Number"][2:]
        else:
                raise Exception("freesmsverifications: "+str(data))




"""
{"Status":"Success","Messages":[
        
{Message:"xxxxxxxx","MessageId":"xxx-xxx-xxx",Number:"xxxxxxxx"},

{Message:"xxxxxxxx","MessageId":"xxx-xxx-xxx",Number:"xxxxxxxx"}],

"ErrorCode":"Non","Error":null,"NumberOfMessages":2,"TimeOfLastMessage":"31/Jan/17 03:13:15"}
"""

def get_message(number):
        """ without country code """
        count = 0

        while config.read_message_trials > count:
                try:
                        resp = requests.get(
                                "http://www.freesmsverifications.com/smsapi/GetMessages?apiId={ID}&secret={SEC}&number=44{NUM}".format(ID=config.freesmsverifications_ID,SEC=config.freesmsverifications_secret,NUM=number))
                except:
                        try:
                                resp = requests.get(
                                "http://www.freesmsverifications.com/smsapi/GetMessages?apiId={ID}&secret={SEC}&number=44{NUM}".format(ID=config.freesmsverifications_ID,SEC=config.freesmsverifications_secret,NUM=number))
                        except:
                                try:
                                        resp = requests.get(
                                "http://www.freesmsverifications.com/smsapi/GetMessages?apiId={ID}&secret={SEC}&number=44{NUM}".format(ID=config.freesmsverifications_ID,SEC=config.freesmsverifications_secret,NUM=number))


                                except:
                                        try:
                                                resp = requests.get(
                                "http://www.freesmsverifications.com/smsapi/GetMessages?apiId={ID}&secret={SEC}&number=44{NUM}".format(ID=config.freesmsverifications_ID,SEC=config.freesmsverifications_secret,NUM=number))


                                        except Exception as e:
                                                raise e


                data :dict = json.loads(resp.content.decode("utf-8"))
                
                if data["Status"] != "Success":
                        raise Exception(str(data))
                
                count+=1

                if len(data.get("Messages",[]) or []) > 0:
                        return pat.search(data["Messages"][:-1]["Message"]).group()
                else:
                        
                        continue
                

        print(data)
        raise Exception(str(data))
        






"""

def get_msg(number: str, iD: str):
    resp = requests.get("http://www.smsaccs.com/api/v1/?token={token}&action=get_sms&service=nike&id={iD}&number={number}".format(token=config.smsaccs_token,iD=iD,number=number))
    data = json.loads(resp.content.decode("utf-8"))
    #print(data)
    if data["status"] == 0:
        return None, data["msg"]
    msgcode = data.get("code",False)
    if msgcode:
        return data["code"], MsgState.RECEIVED
    else:
        return None, MsgState.WAITING
"""


#print(get_number())
