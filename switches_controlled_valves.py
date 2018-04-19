# Author: Sabrina Tong
# Written for the 2017-2018 UW SARP Team
#   Program functions as the remote fill control. Six valves and the
#   fill disconnect are controlled via relays. Data is read from two
#   pressure transducers and a load cell. The status of all
#   controlled entities are written out to a file chosen by the user.
#   The intention is that this runs on both Python 2.7 and 3.0

import RPi.GPIO as GPIO
import os, sys, time
import sensors
import numpy as np
import pigpio
import copy

# Different for Python versions
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

#--------------------------------------------------------------------#
#   PROGRAM CONSTANTS                                                #
#--------------------------------------------------------------------#

# Pi where switches exist
slave = pigpio.pi('192.168.1.105')

# Condition for valves to open
# GPIO.HIGH for active low systems
# GPIO.LOW  for active high systems
v_open = GPIO.LOW

# Write frequency to console and file
write_frequency = 2 #(Hz)

# Valves Names
# MUST CORRESPOND WITH FOLLOWING ORDER
# AS1, AS2, AS3, AS4, AS5, SV1
v_names = ["AS1", "AS2", "AS3", "AS4", "AS5", "SV1"]

#--------------------------------------------------------------------#
#   PIN ASSIGNMENTS                                                  #
#--------------------------------------------------------------------#

# ADC: MCP3008 model
adc = sensors.adc(clock = 19, d_out = 20, d_in = 12, cs = 22)

# Load Cell ADC: HX711 model
# lc = sensors.hx711(,)
# sck = 3, dt = 4

# Valve out pins
# MUST CORRESPOND WITH FOLLOWING ORDER
# AS1, AS2, AS3, AS4, AS5, SV1
v_out = [ 23,  5, 25, 24, 18, 17]

# Valve switch pins (exist on the slave pi)
v_sw  = [16,  6,  5, 25, 24, 17]

# Disconnect and corresponding switch
#d_out = 17
#d_sw  = 3

#--------------------------------------------------------------------#
#   SETUP                                                            #
#--------------------------------------------------------------------#

# Define pin mode
GPIO.setmode(GPIO.BCM)

# Setup v_out
GPIO.setup(v_out, GPIO.OUT)
GPIO.output(v_out, not v_open)

# Setup v_sw pins
for x in v_sw:
    slave.set_mode(x, pigpio.INPUT)
    slave.set_pull_up_down(x, pigpio.PUD_DOWN)

#--------------------------------------------------------------------#
#   GLOBAL VARIABLES                                                 #
#--------------------------------------------------------------------#

# List to hold the state of switches
global sw_state
sw_state = [False, False, False, False, False, False]

#--------------------------------------------------------------------#
#   FUNCTION DEFINITIONS                                             #
#--------------------------------------------------------------------#

#
# Wrapper for user input function because python backwards
# compatability is stupid.
# Returns user input from console
#
def user_in():

    # PYTHON 2
    if sys.version_info[0] < 3: return raw_input()
    # PYTHON 3
    else: return input()

#
# Prompts user for a data file name through the console.
# Returns chosen name
#
def prompt_filename():
    filename = ""
    while True:
        print("What would you like to name your csv file?")
        filename = user_in() + ".csv"

        if os.path.isfile(filename):
            print("A file named " + filename + " already exists!")
            print("Would you like to overwrite it? (y/n)")
            if user_in().startswith("y"): break
        else:
            print("Creating " + filename)
            break
    return filename

#
# Identifies errors in valve inputs. 
# Returns 1 if an error exists
# Returns 0 otherwise
#
def v_error():

    # Valid valve combinations
    combo = [sw_state[0] and sw_state[3], # as1 as4
             sw_state[1] and sw_state[3], # as2 as4
             sw_state[2] and sw_state[3], # as3 as4
             sw_state[0] and sw_state[4], # as1 as5
             sw_state[3] and sw_state[4]] # as4 as5

    sw_count = sw_state[:-1].count(1)
    return (sw_count > 2) or (sw_count == 2 and not (combo.count(1) == 1))

#
# Provide valve status.
# 1 == open
# 0 == closed
# Returns a list of corresponding to the valves in v_names
#
def valve_status():

    v_status = copy.copy(sw_state)
    if v_error(): v_status = [0] * len(sw_state)
    return v_status

#
# Callback for pigpio valve switches
# Changes ouput to v_out as necessary
#
def valve_callback(gpio, level, tick):

    sw_state[v_sw.index(gpio)] = level
    state = valve_status()
    for i in range(0, len(state)):
        GPIO.output(v_out[i], not (state[i] ^ v_open))

#
# Ensure that all switches are in the off 
# position
#
def ensure_off():

    input_state = [slave.read(x) for x in v_sw]
    if input_state.count(1) > 0:
        print("Unable to start until all switches are off")
    while (input_state.count(1) > 0):
        input_state = [slave.read(x) for x in v_sw]

#
# Print status to console.
#
def print_status(p1, p2):

    state = valve_status()
    str_names  = ""
    str_status = ""
    for i in range(0, len(state)):
        str_names += v_names[i] + "\t"
        if state[i]: str_status += " ON\t"
        else:        str_status += "OFF\t"

    to_print = "\n"
    if v_error(): to_print += "\tERROR: INVALID VALVE COMBINATION"
    to_print += "\n\t\t" + str_names + "\n\t\t" + str_status + "\n"
    to_print += "\n\t\tPressure 1: {:.2f} psi".format(np.mean(p1))
    to_print += "\n\t\tPressure 2: {:.2f} psi".format(np.mean(p2))
    to_print += "\n"

    os.system('clear')
    print(to_print)

#--------------------------------------------------------------------#
#   MAIN FUNCTION                                                    #
#--------------------------------------------------------------------#

def main():

    # Open a file to write in
    # "w+" says to create the file if it doesn't already exist
    f = open(prompt_filename(), "w+")

    # Ensure switches are off before beginning
    ensure_off()

    # Add callbacks to all switches
    for x in v_sw:
        slave.callback(x, pigpio.EITHER_EDGE, valve_callback)

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
            v_state = valve_status()

            line += ",{:.3}".format(p1[len(p1) - 1])
            line += ",{:.3}".format(p2[len(p2) - 1])

            for i in range(0, len(v_state)):
                line += ",{}".format(v_state[i])

            if len(p1) > 10: p1.pop(0)
            if len(p2) > 10: p1.pop(0)

            f.write(line + "\n")
            print_status(p1, p2)

            delay = -1.0
            while delay < 0.0:
                next += period
                delay = next - time.time()
            time.sleep(delay)

    finally:
        f.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Goodbye!")
    finally:
        GPIO.cleanup()
        slave.stop()



