# Author: Eric Fan
# Written for the 2017-2018 UW SARP Team
#   Hardcoded GUI version of RFC using command lines.
#   IMPORTANT: All pi libraries and methods are commented out in this
#   file for build. Uncomment for hardware testing.

from Tkinter import *
import os, sys, time
import copy
import threading

# import RPi.GPIO as GPIO
# Relays are active low

open = 1
nopen = 0

p1 = 26  # N20
p2 = 13  # N2
p3 = 21  # Backpressure
p4 = 27  # Main fill
p5 = 4  # Stand Vent
p6 = 23  # rocket valve

# booleans to keep track of open status
as1 = False  # N20
as2 = False  # N2
as3 = False  # Back pressure
as4 = False  # Main fill
as5 = False  # Stand Vent
sv1 = False  # rocket valve

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(p1, GPIO.OUT)
# GPIO.output(p1, nopen)
# GPIO.setup(p2, GPIO.OUT)
# GPIO.output(p2, nopen)
# GPIO.setup(p3, GPIO.OUT)
# GPIO.output(p3, nopen)
# GPIO.setup(p4, GPIO.OUT)
# GPIO.output(p4, nopen)
# GPIO.setup(p5, GPIO.OUT)
# GPIO.output(p5, nopen)
# GPIO.setup(p6, GPIO.OUT)
# GPIO.output(p6, nopen)        


threads = []


root = Tk()

as1status = StringVar()
as1status.set("Closed")
as2status = StringVar()
as2status.set("Closed")
as3status = StringVar()
as3status.set("Closed")
as4status = StringVar()
as4status.set("Closed")
as5status = StringVar()
as5status.set("Closed")
sv1status = StringVar()
sv1status.set("Closed")


class bgthread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name
        toCSV()
        print "Exiting " + self.name


def printt(t):
    display.config(state=NORMAL)
    display.insert(INSERT, t + "\n")
    display.see("end")
    display.config(state=DISABLED)


def checkclose(v):
    if v:
        printt("valve already opened")
        return False
    return True


def op(v):
    global as1, as2, as3, as4, as5, sv1
    if v == "as1":
        if checkclose(as1) and not as2 and not as3 and not as5:
            as1 = True
            printt(v + " opened")
            # GPIO.output(p1, open)
            as1status.set("Opened")
        else:
            printt("cannot open: as2, as3, or as5 is opened")
    elif v == "as2":
        if checkclose(as2) and not as1 and not as3 and not as5:
            as2 = True
            printt(v + " opened")
            # GPIO.output(p2, open)
            as2status.set("Opened")
        else:
            printt("cannot open: as1, as3, or as5 is opened")
    elif v == "as3":
        if checkclose(as3) and not as1 and not as2 and not as5:
            as3 = True
            printt(v + " opened")
            # GPIO.output(p3, open)
            as3status.set("Opened")
        else:
            printt("cannot open: as1, as2, or as5 is opened")
    elif v == "as4":
        if checkclose(as4):
            as4 = True
            printt(v + " opened")
            # GPIO.output(p4, open)
            as4status.set("Opened")
    elif v == "as5":
        if checkclose(as5) and not as2 and not as3:
            as5 = True
            printt(v + " opened")
            # GPIO.output(p5, open_v)
            as5status.set("Opened")
        else:
            printt("cannot open: as2 or as3 is opened")
    elif v == "sv1":
        if checkclose(sv1):
            sv1 = True
            printt(v + " opened")
            # GPIO.output(p6, open)
            sv1status.set("Opened")
    else:
        printt("no such valve")


def checkopen(v):
    if not v:
        printt("valve already closed")
        return False
    return True


def cl(v):
    global as1, as2, as3, as4, as5, sv1
    if v == "as1":
        if checkopen(as1):
            as1 = False
            printt(v + " closed")
            # GPIO.output(p1, nopen)
            as1status.set("Closed")
    elif v == "as2":
        if checkopen(as2):
            as2 = False
            printt(v + " closed")
            # GPIO.output(p2, nopen)
            as2status.set("Closed")
    elif v == "as3":
        if checkopen(as3):
            as3 = False
            printt(v + " closed")
            # GPIO.output(p3, nopen)
            as3status.set("Closed")
    elif v == "as4":
        if checkopen(as4):
            as4 = False
            printt(v + " closed")
            # GPIO.output(p4, nopen)
            as4status.set("Closed")
    elif v == "as5":
        if checkopen(as5):
            as5 = False
            printt(v + " closed")
            # GPIO.output(p5, nopen)
            as5status.set("Closed")
    elif v == "sv1":
        if checkopen(sv1):
            sv1 = False
            printt(v + " closed")
            # GPIO.output(p6, nopen)
            sv1status.set("Closed")
    else:
        printt("no such valve")


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


def quit_app():
    root.quit()


def get_input(event):
    # Get the value stored in the entries
    user_input = console.get()
    printt(user_input)
    user_input = user_input.lower().split(" ")
    if len(user_input) > 2:
        printt("unknown command")
    else:
        if user_input[0] == "v":
            printt("as1\nas2\nas3\nas4\nas5\nsv1")
        elif user_input[0] == "menu":
            printt("menu\n -v : show valve IDs \n -open 'valve ID': opens valve \n -close 'valve ID': closes "
                   "valve \n -status: show valves status \n -menu: show all commands \n -quit")
        elif user_input[0] == "open":
            op(user_input[1])
        elif user_input[0] == "close":
            cl(user_input[1])
        elif user_input[0] == "status":
            printt(status())
        elif user_input[0] == "quit":
            quit_app()
        else:
            printt("unknown command")
    console.delete(0, END)

#Below section is copied from Sabrina's code
#
# Prompts user for a data file name through the console.
# Returns chosen name
#
def prompt_filename():
    filename = ""
    while True:
        print("What would you like to name your csv file?")
        filename = raw_input() + ".csv"

        if os.path.isfile(filename):
            print("A file named " + filename + " already exists!")
            print("Would you like to overwrite it? (y/n)")
            if user_in().startswith("y"): break
        else:
            print("Creating " + filename)
            break
    return filename


def toCSV():

    # Open a file to write in
    # "w+" says to create the file if it doesn't already exist
    f = open(prompt_filename(), "w+")

    # Lists to hold the last 10 pressure values for both transducers
    p1 = []
    p2 = []

    try:

        f.write("Time,Pressure1,Pressure2,as1,as2,as3,as4,as5,sv1\n")

        period = 1.0 / write_frequency
        start = time.time()
        next = time.time() + period

        while True:
            line = "{:.3}".format(time.time() - start)
            p1.append(adc.get_pressure(0))
            p2.append(adc.get_pressure(1))
            v_state = status()

            line += ",{:.3}".format(p1[len(p1) - 1])
            line += ",{:.3}".format(p2[len(p2) - 1])

            for i in range(0, len(v_state)):
                line += ",{}".format(v_state[i])

            if len(p1) > 10: p1.pop(0)
            if len(p2) > 10: p1.pop(0)

            f.write(line + "\n")

            delay = -1.0
            while delay < 0.0:
                next += period
                delay = next - time.time()
            time.sleep(delay)

    finally:
        f.close()

#--------------------------------------------------------------------#
#   GUI                                                              #
#--------------------------------------------------------------------#
# grid method is for positioning widgets

# construct window and title
frame = Frame(root)
root.title("Remote Fill GUI")

# binds enter key to submit
root.bind("<Return>", get_input)

# row one: Enter command button, input, and submit
# mouseclick onto submit and return key both works
Label(root, text="Enter Command").grid(row=0, column=0, sticky=W)
console = Entry(root, width=40)
console.grid(row=0, column=1, columnspan=2, sticky="w")
console.focus_force()
enter = Button(root, text="Submit")
enter.bind("<Button-1>", get_input)
enter.grid(row=0, column=3, sticky="w")


# command menu
commandmenu = LabelFrame(root, text="Command Menu (omit '-')")
commandmenu.grid(row=1, sticky="w", column=2, rowspan=5, padx=5, ipadx=5)
Label(commandmenu, text="-open 'valve ID': opens valve").grid(row=0, column=0, sticky='W', padx=5)
Label(commandmenu, text="-close 'valve ID': closes valve").grid(row=1, column=0, sticky='W', padx=5)
Label(commandmenu, text="-status: prints valve status").grid(row=2, column=0, sticky='W', padx=5)
Label(commandmenu, text="-quit: quits program").grid(row=3, column=0, sticky='W', padx=5)


# valve status list
Label(root, text="N2O (as1)").grid(row=1, column=0, sticky=W)
Label(root, text="N2 (as2)").grid(row=2, column=0, sticky=W)
Label(root, text="Back Pressure (as3)").grid(row=3, column=0, sticky=W)
Label(root, text="Main Fill (as4)").grid(row=4, column=0, sticky=W)
Label(root, text="Stand Vent (as5)").grid(row=5, column=0, sticky=W)
Label(root, text="Rocket Valve (sv1)").grid(row=6, column=0, sticky=W)
Label(root, textvariable=as1status, relief=RIDGE).grid(row=1, column=1, sticky=W)
Label(root, textvariable=as2status, relief=RIDGE).grid(row=2, column=1, sticky=W)
Label(root, textvariable=as3status, relief=RIDGE).grid(row=3, column=1, sticky=W)
Label(root, textvariable=as4status, relief=RIDGE).grid(row=4, column=1, sticky=W)
Label(root, textvariable=as5status, relief=RIDGE).grid(row=5, column=1, sticky=W)
Label(root, textvariable=sv1status, relief=RIDGE).grid(row=6, column=1, sticky=W)

# console and scrollbar
display = Text(root, borderwidth=3, height=20, width=20, relief="sunken")
display.config(font=("consolas", 12), undo=True, wrap='word')
display.grid(row=7, column=0, columnspan=3, padx=2, pady=2, sticky='nsew')
scrollbar = Scrollbar(root, command=display.yview)
scrollbar.grid(row=7, column=3, sticky='nsw')
display['yscrollcommand'] = scrollbar.set

threats = []
t = threading.Thread(target = toCSV)
threads.append(t)
t.start()

root.mainloop()
