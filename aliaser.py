"""        
        abcde

        a.bcde
        ab.cde
        abc.de
        abcd.e

        a.b.cde
        ab.c.de
        abc.d.e

        a.b.c.de
        ab.c.d.e

        a.b.c.d.e
"""

def alias_sym(email: str, symbol: str) -> set:
    assert email.find("@") != -1, "Invalid Email"
    emails = set()
    user,domain = email.split("@")
    length = len(user)
    symbolss = [symbol*count for count in range(1,length)]
    for pos in range(length):
        for symbols in symbolss:
                index = pos
                new_user = user[0:index+1]
                for sym in symbols:
                    if index+1 != length:
                        index+=1
                        new_user+=sym
                        new_user+=user[index]
                if index+1 != length:
                    index+=1
                    new_user+=user[index:length]
                emails.add(new_user+"@"+domain)
    emails.remove(email)
    return tuple(emails)







def generate_alias(email: str) -> dict:
    alias_emails = {
        #"+": None,
        ".": []
    }
    for k in alias_emails.keys():
        alias_emails[k] = alias_sym(email,k)
    
    return alias_emails





if __name__ == "__main__":
    print("\n".join(generate_alias("ryanxclusive@gmail.com")["."]))
    print("generated",len(generate_alias("ryanxclusive@gmail.com")["."])," total emails from:"," ryanxclusive@gmail.com")