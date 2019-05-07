import requests
import json
import time 


if __name__ == "__main__":
        import config
else:
        from . import config

import re





pat = re.compile(r"code\s+is\s+(\d{4,12})")



def get_number():

        url = "https://cloudsms.io/api/number?key={key}&service=0&tier={tier}"
        url = url.format(key=config.cloudsms_key,tier=config.cloudsms_tier)
        
        
        
        
        print(url)
        try:
                resp = requests.get(url)
        except:
                try:
                        resp = requests.get(url)
                except:
                        try:
                                resp = requests.get(url)
                        except:
                                try:
                                        resp = requests.get(url)
                                except Exception as e:
                                        raise e

        body = resp.content.decode("utf-8")
        paydata = json.loads(body)
        if paydata["status"] == "success":
                return paydata["number"]
        else:
                print(paydata)
                raise Exception("cloudsms: "+ paydata["error"])






def get_sms(number):
        count = 0
        while config.read_message_trials > count:
                print("trial: %d" % count)
                url = "https://cloudsms.io/api/number/messages?number={number}&key={key}"
                url = url.format(key=config.cloudsms_key,number=number)
                
                
                
                
                print(url)
                try:
                        resp = requests.get(url)
                except:
                        try:
                                resp = requests.get(url)
                        except:
                                try:
                                        resp = requests.get(url)
                                except:
                                        try:
                                                resp = requests.get(url)
                                        except Exception as e:
                                                raise e

                body = resp.content.decode("utf-8")
                paydata = json.loads(body)
                print(paydata)
                if paydata["status"] == "success":
                        if len(paydata["messages"]) >= 1:
                                a = paydata["messages"]
                                

                                print(str(a))


                                #print(a[:-1])
                                #print(type(a[:-1]))
                                #a = a["text"]
                                return pat.search(str(a)).groups()[0]
                        else:
                                pass
                else:
                        raise Exception("cloudsms: "+ paydata["error"])

                time.sleep(config.read_message_delay)
                count+=1




if __name__ == "__main__":
        #print(pat.search("hhek 37378 dhd").group())
        print(get_sms("3106908876"))