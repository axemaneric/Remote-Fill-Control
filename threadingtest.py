import os
import sys
import time
import copy
import threading


write_frequency = 2  # (Hz)


def prompt_filename():
    filename = ""
    while True:
        print("What would you like to name your csv file?")
        filename = raw_input() + ".csv"
        print(filename)
        if os.path.isfile(filename):
            print("A file named " + filename + " already exists!")
            print("Would you like to overwrite it? (y/n)")
            if raw_input().startswith("y"):
                break
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
            p1.append(20)
            p2.append(20)

            if len(p1) > 10:
                p1.pop(0)
            if len(p2) > 10:
                p1.pop(0)

            f.write(line + "\n")

            delay = -1.0
            while delay < 0.0:
                next += period
                delay = next - time.time()
            time.sleep(delay)

    except KeyboardInterrupt:
        f.close()
        print('interrupted!')


toCSV()
