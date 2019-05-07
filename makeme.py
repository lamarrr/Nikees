import names
import random

def get_name():
    return names.get_first_name().lower(), names.get_last_name().lower()



def get_dob():
    # mm,dd,yyyy
    mm = random.randint(1,11)
    dd = random.randint(1,11)
    yyyy = random.randint(1980,1999)
    return "%02d%02d%4d" % (mm,dd,yyyy)




def get_unique_catchall():
    a = str(random.randint(100,200))
    b = str(random.randint(100,200))
    f,s = get_name()
    unq = f+s+a+b
    return (f,s),unq








if __name__ == "__main__":
    print(get_dob())


