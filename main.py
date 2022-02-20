import freeton
import hashlib
f = freeton.wrapper()
def Authority():
    while True:
        print(f"{5 * '='}Choose your request{5 * '='}")
        print("1) Create root")
        print("2) Create new user")
        print("3) Add new info to user")
        print("4) Go back")
        ans = input("Write number of your request: ")
        if ans == "1":
            signs = []
            count = input("Write here count of signers: ")
            for i in range(int(count)):
                signs.append(input(f"Write pubkey #{i}: "))
            a = f.create_root(signs)
            print(a)
        elif ans == "2":
            adr = input("Write address of root: ")
            metadata = input("Write data of user: ")
            metadata = hashlib.sha256(metadata.encode('utf-8')).hexdigest()
            f.create_user(adr,metadata)
        elif ans == "3":
            adr = input("Write address of user: ")
            metadata = input("Write data of user: ")
            print(f.add_user_data(adr, metadata))
        elif ans == "4":
            break

def User():
    while True:
        print(f"{5 * '='}Choose your request{5 * '='}")
        print("1) Get info")
        # print("2) Create new user")
        # print("3) Add new info to user")
        print("4) Go back")
        ans = input("Write number of your request: ")
        if ans == "1":
            adr = input("Write your address: ")
            a = f.get_info(adr)
            print(a)
        elif ans == "2":
            adr = input("Write address of root: ")
            metadata = input("Write data of user: ")
            metadata = hashlib.sha256(metadata.encode('utf-8')).hexdigest()
            f.create_user(adr, metadata)
        elif ans == "3":
            adr = input("Write address of user: ")
            metadata = input("Write data of user: ")
            print(f.add_user_data(adr, metadata))
        elif ans == "4":
            break

def GenKeys():
    pass


if __name__ == "__main__":
    while True:
        print(f"{5 * '='}Choose your role{5 * '='}" )
        print("1) Authority")
        print("2) User")
        print("3) Generate keys")
        ans = input("Write number of your role: ")
        if ans == "1":
            Authority()
        elif ans == "2":
            User()
        elif ans == "3":
            GenKeys()