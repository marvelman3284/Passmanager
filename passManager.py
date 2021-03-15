import os
import pickle
from getpass import getpass

import mysql.connector
from colorama import Back, Fore, Style

import encrypt as cryptic

import mail
import totp

db = mysql.connector.connect(
    host="192.168.86.5", user="root", passwd="starwars285", db="passwordManager"
)

c = db.cursor()

key = cryptic.get_key()

with open("email.pickle", "r+b") as f:
    emailPass = pickle.load(f)
    f.close()


def validate(s):
    """
    Credit to Sci Prog on stackoverflow for the code.
    https://stackoverflow.com/questions/35857967/python-password-requirement-program
    """
    SPECIAL = "@$#!&*()[].,?+=-"

    Cap, Low, Num, Spec, Len = False, False, False, False, False
    for i in s:
        if i.isupper():
            Cap = True
        elif i.islower():
            Low = True
        elif i.isdigit():
            Num = True
        elif i in SPECIAL:
            Spec = True
    if len(s) >= 8:
        Len = True

    if Cap and Low and Num and Spec and Len:
        return True
    else:
        return False


def quit():
    stop = input(
        "Would you like to do more operations? (Y for yes | Any other key for no):"
    )
    stopValid = ["y", "yes", "Y", "Yes"]
    for i in stop:
        if i in stopValid:
            continue
        elif i not in stopValid:
            exit()


MASTERPASS = ""
USERPASS = ""
empty = False

with open("save.pickle", "r+b") as f:
    if os.path.getsize("save.pickle") == 0:
        empty = True
        f.close()

if empty == True:
    MASTERPASS = input(
        Fore.LIGHTCYAN_EX
        + "Welcome. To use this program you must first set a master password for you account. This master password must contain at leat 1 lowercase, 1 uppercase, 1 number, and 1 special character. Your password must also be at least 8 characters long. Make sure this is something you can remember as you cannot change this later. Please enter your password here: "
        + Style.RESET_ALL
    )

    print("Welcome to user setup.")
    user = input("Please enter the username you would like to login as:")
    email = input("Please enter your email: ")
    USERPASS = input("Please enter the password you would like to login with: ")
    mail.send_test("dev87460@gmail.com", email, emailPass)

    secret = totp.generate_shared_secret()
    # print(
    #     Fore.RED
    #     + Back.WHITE
    #     + "THIS IS VERY IMPORTANT! YOU MUST SAVE THIS KEY AS IT ALLOWS YOU TO USE THE MANAGER. SAVE THIS KEY SOMEWHERE: "
    #     + secret
    #     + Style.RESET_ALL
    # )

    PASS = cryptic.encrypt(USERPASS, key)

    c.execute(
        "INSERT INTO secrets (username, email, pass, secret) VALUES (%s, %s, %s, %s)",
        (user, email, PASS, secret),
    )
    db.commit()

    if validate(MASTERPASS) == True:
        with open("save.pickle", "r+b") as f:
            pickle.dump(MASTERPASS, f)
            f.close()

    elif validate(MASTERPASS) == False:
        while True:
            MASTERPASS = input(
                Fore.LIGHTCYAN_EX
                + "Welcome. To use this program you must first set a master password. This master password must contain at leat 1 lowercase, 1 uppercase, 1 number, and 1 special character. Your password must also be at least 8 characters long. Please enter your password here: "
                + Style.RESET_ALL
            )

            if validate(MASTERPASS) == True:
                with open("save.pickle", "r+b") as f:
                    pickle.dump(MASTERPASS, f)
                    f.close()
                break

            else:
                print(
                    Fore.RED
                    + "\nTry Again! Make sure your password is at least 8 charaters long and contaions 1 lowercase, 1 uppercase, 1 number, and 1 special character. \n"
                    + Style.RESET_ALL
                )

if empty == False or MASTERPASS is not None:
    with open("save.pickle", "r+b") as f:
        MASTERPASS = pickle.load(f)
        f.close()

log = getpass()

if log == MASTERPASS:
    loginUser = input("Enter your username: ")

    c.execute("SELECT username FROM secrets WHERE username=%s", (loginUser,))

    for x in c:
        dataUser = x

    loginUser_ = f"('{loginUser}',)"

    if str(loginUser_) == str(dataUser):
        c.execute("SELECT pass FROM secrets WHERE username=%s", (loginUser,))

        for x in c:
            dataPass = str(x)
            
        
        dataPass = cryptic.decrypt(dataPass, key)

        loginPass = input("Enter your password: ")
        loginPass = bytes(str(loginPass), 'utf8')
        print(dataPass, loginPass)
        print(type(dataPass))
        print(type(loginPass))

        if loginPass == dataPass:
            c.execute("SELECT email FROM secrets WHERE username=%s", (loginUser,))

            for x in c:
                dataEmail = x

            c.execute("SELECT secret FROM secrets WHERE username=%s", (loginUser,))

            for y in c:
                secret = str(y)

            tbotp = totp.generate_totp(secret)
            mail.send_secret("dev87460@gmail.com", dataEmail, emailPass, tbotp)
            enterTotp = input("Enter the code that was emailed to you: ")

            if tbotp == enterTotp:
                validation = totp.validate_totp(enterTotp, secret)

                if validate:
                    print("Your code is valid, proceed on!")

                else:
                    print("Sorry your code is not valid :(")
                    quit()

        else:
            quit()

if log != MASTERPASS:
    '''for i in range(2):
        i += 1
        log = getpass("Try again:")

        if log == MASTERPASS:
            pass

    if i == 2: '''
    print(Fore.RED + "Sorry, wrong password" + Style.RESET_ALL)
    exit()

while True:
    what = int(
        input(
            "What would you like to do? \n1.Add information \n2.Get information \n3.Delete information \n4.Exit \nEnter a number 1, 2, 3, or 4: "
        )
    )
    valid = [1, 2, 3, 4]

    """
    try:
        i = int(what)
        if i in valid:
            break
        
    except ValueError:
        print(Fore.RED + "You didn't enter a number" + Style.RESET_ALL)
    """
    if int(what) == 1:
        site = input("Enter the site (include 'https://'): ")
        user = input("Enter the username: ")
        passwd = input("Enter the password: ")
        c.execute(
            "INSERT INTO passwords (site, username, password) VALUES (%s,%s,%s)",
            (site, user, passwd),
        )
        db.commit()
        print(Fore.GREEN + "Successfully inserted data into table!" + Style.RESET_ALL)

        quit()

    elif int(what) == 2:
        c.execute("SELECT * FROM passwords")
        for x in c:
            print(x)

        quit()

    elif int(what) == 3:
        delete = input("What would you like to delete(Enter the id):")
        code = """DELETE FROM passwords WHERE id = %s"""
        id_ = int(delete)
        c.execute(code, (id_,))
        db.commit()
        print("Succesfully deleted!")

        stop = input(
            "Would you like to do more operations? (Y for yes | Any other key for no):"
        )

        quit()

    elif int(what) == 4:
        exit()
