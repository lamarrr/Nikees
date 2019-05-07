#convert to queue and pop
import os.path
from util import kolor

PATH = __file__.split(os.path.sep)
PROXIES_DUMP = os.path.sep.join((*PATH[:-1],"db","proxies_dump.txt"))
NEW_PROXIES = os.path.sep.join((*PATH[:-1],"db","new_proxies.txt"))



def get_proxy():
    try:
        avail_proxies = []
        
        with open(NEW_PROXIES,"r") as proxies_f:
            for proxy in proxies_f.readlines():
                avail_proxies.append(proxy.replace("\n",""))
        
        new_proxy = "https://"+avail_proxies[0]
        avail_proxies = avail_proxies[1:]

        # pop
        with open(NEW_PROXIES,"w") as proxies_f:
            proxies_f.write("\n".join(avail_proxies))
        
        # dump
        with open(PROXIES_DUMP,"a") as proxies_f:
            proxies_f.write(new_proxy+"\n")

        return new_proxy

    except IndexError:
        raise Exception(kolor.foreground(kolor.bold("You've run out of Proxies"),color="red"))






if __name__ == "__main__":
    print(get_proxy())