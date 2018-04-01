#!/usr/bin/env python

import time

import RPi.GPIO as GPIO

p1 = 17 # N20
p2 = 27 # N2
p3 = 22 # Backpressure
p4 = 18 # Main fill
p5 = 15 # Stand Vent
p6 = 16 # rocket valve

# booleans to keep track of open status
as1 = False  # N20
as2 = False  # N2
as3 = False  # Back pressure
as4 = False  # Main fill
as5 = False  # Stand Vent
sv1 = False  # rocket valve

GPIO.setmode(GPIO.BCM)
GPIO.setup(p1, GPIO.OUT)
GPIO.setup(p2, GPIO.OUT)
GPIO.setup(p3, GPIO.OUT)
GPIO.setup(p4, GPIO.OUT)
GPIO.setup(p5, GPIO.OUT)
GPIO.setup(p6, GPIO.OUT)


def checkclose(v):
    if v:
        print("valve already opened")
        return False
    return True


def op(v):
    global as1, as2, as3, as4, as5, sv1
    if v == "as1":
        if checkclose(as1) and not as2 and not as3 and not as5:
            as1 = True
            print(v + " opened")
            GPIO.output(p1, 1)
        else:
            print("cannot open: as2, as3, or as5 is opened")
    elif v == "as2":
        if checkclose(as2) and not as1 and not as3 and not as5:
            as2 = True
            print(v + " opened")
            GPIO.output(p2, 1)
        else:
            print("cannot open: as1, as3, or as5 is opened")
    elif v == "as3":
        if checkclose(as3) and not as1 and not as2 and not as5:
            as3 = True
            print(v + " opened")
            GPIO.output(p3, 1)
        else:
            print("cannot open: as1, as2, or as5 is opened")
    elif v == "as4":
        if checkclose(as4):
            as4 = True
            print(v + " opened")
            GPIO.output(p4, 1)
    elif v == "as5":
        if checkclose(as5) and not as2 and not as3:
            as5 = True
            print(v + " opened")
            GPIO.output(p5, 1)
        else:
            print("cannot open: as2 or as3 is opened")
    elif v == "sv1":
        if checkclose(sv1):
            sv1 = True
            print(v + " opened")
            GPIO.output(p6, 1)
    else:
        print("no such valve")


def checkopen(v):
    if not v:
        print("valve already closed")
        return False
    return True



def cl(v):
    global as1, as2, as3, as4, as5, sv1
    if v == "as1":
        if checkopen(as1):
            as1 = False
            print(v + " closed")
            GPIO.output(p1, 0)
    elif v == "as2":
        if checkopen(as2):
            as2 = False
            print(v + " closed")
            GPIO.output(p2, 0)
    elif v == "as3":
        if checkopen(as3):
            as3 = False
            print(v + " closed")
            GPIO.output(p3, 0)
    elif v == "as4":
        if checkopen(as4):
            as4 = False
            print(v + " closed")
            GPIO.output(p4, 0)
    elif v == "as5":
        if checkopen(as5):
            as5 = False
            print(v + " closed")
            GPIO.output(p5, 0)
    elif v == "sv1":
        if checkopen(sv1):
            sv1 = False
            print(v + " closed")
            GPIO.output(p6, 0)
    else:
        print("no such valve")


def status():
    if as1:
        result = "AS1: Open"
    else:
        result = "AS1: Closed"
    if as2:
        result += "\nAS2: Open"
    else:
        result += "\nAS2: Closed"
    if as3:
        result += "\nAS3: Open"
    else:
        result += "\nAS3: Closed"
    if as4:
        result += "\nAS4: Open"
    else:
        result += "\nAS4: Closed"
    if as5:
        result += "\nAS5: Open"
    else:
        result += "\nAS5: Closed"
    if sv1:
        result += "\nSV1: Open"
    else:
        result += "\nSV1: Closed"
    return result

def main():
    try:
        print("menu\n -v : show valve names \n -open 'valve name': opens valve \n -close 'valve name': closes valve \n "
              "-status: show valves status \n -menu: show all commands \n -quit")

        while True:
            user_input = input("enter command: ").lower().split(" ")
            if len(user_input) > 2:
                print("no such command")
            else:
                if user_input[0] == "v":
                    print("as1\nas2\nas3\nas4\nas5\nsv1")
                elif user_input[0] == "menu":
                    print("menu\n -v : show valve names \n -open 'valve name': opens valve \n -close 'valve name': closes "
                          "valve \n -status: show valves status \n -menu: show all commands \n -quit")
                elif user_input[0] == "open":
                    op(user_input[1])
                elif user_input[0] == "close":
                    cl(user_input[1])
                elif user_input[0] == "status":
                    print(status())
                elif user_input[0] == "quit":
                    break
                else:
                    print("no such command")
    finally:  # Execute under all circumstances
        print("Cleanup")

main()

GPIO.cleanup()
