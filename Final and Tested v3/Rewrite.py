# Author: Eric Fan & Sabrina Tong
# Written for the 2017-2018 UW SARP Team
#   Program functions as the remote fill control. Six valves and the
#   fill disconnect are controlled via relays. Data is read from two
#   pressure transducers and a load cell. The status of all
#   controlled entities are written out to a file chosen by the user.
#   The intention is that this runs on both Python 2.7 and 3.0 but
#   currently this is limited by the hx711 library (2.7 only)

import RPi.GPIO as GPIO
import os, sys, time
import sensors
import numpy as np
import pigpio
import copy
import threading
from hx711 import HX711

# Different for Python versions
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

#--------------------------------------------------------------------#
#   PROGRAM CONSTANTS                                                #
#--------------------------------------------------------------------#

# Pi where switches exist
ground_control = pigpio.pi('192.168.1.103')

# Condition for relays to open
# GPIO.HIGH for active high systems
# GPIO.LOW  for active low  systems
on_signal = GPIO.LOW

# Write frequency to file
write_frequency = 2 #(Hz)

#--------------------------------------------------------------------#
#   PIN ASSIGNMENTS                                                  #
#--------------------------------------------------------------------#

# Pressure Transducers ADC: MCP3008 model
pt = sensors.adc(clock = 19, d_out = 20, d_in = 12, cs = 22)

# Load Cell ADC: HX711 model
lc = HX711(pd_sck = 27, dout = 21)

# Valve out pins
# MUST CORRESPOND WITH FOLLOWING ORDER
#              AS1, AS2, AS3, AS4, AS5, SV1
pin_val_out = [ 23,   5,  6,   24, 18,   25]

# Valve switch pins (exist on the ground_control pi)
# MUST CORRESPOND WITH FOLLOWING ORDER
#              AS1, AS2, AS3, AS4, AS5, SV1
pin_val_in  = [ 16,   6,   5,  25,  24,  22]

# Disconnect out pin
pin_dis_out = 4

# Disconnect button pins (exist on the groun_control pi)
pin_dis_in  = [18, 17]

#--------------------------------------------------------------------#
#   SETUP                                                            #
#--------------------------------------------------------------------#

# Define pin mode
GPIO.setmode(GPIO.BCM)

# Setup v_out
GPIO.setup( (pin_val_out + [pin_dis_out]), GPIO.OUT)
GPIO.output((pin_val_out + [pin_dis_out]), not on_signal)

# Setup v_sw pins
for x in (pin_val_in + pin_dis_in):
    ground_control.set_mode(x, pigpio.INPUT)
    ground_control.set_pull_up_down(x, pigpio.PUD_DOWN)

# Tare the load cell
lc.set_reading_format("LSB", "MSB")
lc.set_reference_unit(-6597.8647686833)
#lc.set_reference_unit(92)
lc.reset()
lc.tare()

#------------------------------------------------------------------#
#  Gather File Name for CSV
#------------------------------------------------------------------#

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

file_name = prompt_filename()

#--------------------------------------------------------------------#
#   GUI SETUP                                                        #
#--------------------------------------------------------------------#

root = tk.Tk()

str_error = tk.StringVar()
str_error.set("")

str_val_names = tk.StringVar()
str_val_names.set("as1\tas2\tas3\tas4\tas5\tsv1")

str_val_out = tk.StringVar()
str_val_out.set("OFF\tOFF\tOFF\tOFF\tOFF\tOFF")

str_pressure_0 = tk.StringVar()
str_pressure_0.set("{:.3}".format(pt.get_pressure(channel = 0)))

str_pressure_1 = tk.StringVar()
str_pressure_1.set("{:.3}".format(pt.get_pressure(channel = 1)))

str_weight = tk.StringVar()
str_weight.set("{}".format(lc.get_weight(5)))

frame = tk.Frame(root)
root.title("Remote Fill Control")

tk.Label(root, textvariable=str_error).grid(row=0, columnspan = 5, sticky='s')

tk.Label(root, textvariable=str_val_names).grid(row=2, columnspan=5, sticky='n')
tk.Label(root, textvariable=str_val_out  ).grid(row=3, columnspan=5, sticky='n')

tk.Label(root, text='\nPressure 0').grid(row=4, column=0, rowspan=2, sticky='s')
tk.Label(root, textvariable=str_pressure_0).grid(row=6, column=0, sticky='n')

tk.Label(root, text='\nPressure 1').grid(row=4, column=2, rowspan=2, sticky='s')
tk.Label(root, textvariable=str_pressure_1).grid(row=6, column=2, sticky='n')

tk.Label(root, text='\nWeight').grid(row=4, column=4, rowspan=2, sticky='s')
tk.Label(root, textvariable=str_weight).grid(row=6, column=4, sticky='n')

#--------------------------------------------------------------------#
#   GLOBAL VARIABLES                                                 #
#--------------------------------------------------------------------#

state_val_in  = [0, 0, 0, 0, 0, 0]
state_val_out = [0, 0, 0, 0, 0, 0]

state_dis_in = [0, 0]
state_dis_out = 0

#--------------------------------------------------------------------#
#   FUNCTION DEFINITIONS                                             #
#--------------------------------------------------------------------#

#
# Ensure that all inputs are in the off position
#
def ensure_off():
    input_state  = [ground_control.read(x) for x in pin_val_in]
    input_state += [ground_control.read(x) for x in pin_dis_in]
    if input_state.count(1) > 0:
        print("Unable to start until all inputs are off")
    while (input_state.count(1) > 0):
        input_state  = [ground_control.read(x) for x in pin_val_in]
        input_state += [ground_control.read(x) for x in pin_dis_in]

#
# Catch input errors
#
def input_error():
    global str_error
    v_inputs = copy.copy(state_val_in)
    d_inputs = copy.copy(state_dis_in)

    if (d_inputs.count(1) > 0 and v_inputs.count(1) > 0) \
      or v_inputs[0:3].count(1) > 1:
        str_error.set("INPUT ERROR")
        return True

    str_error.set("")
    return False

#
# Callback function for when valve switches are turned
# on and off
#
def callback_valve(gpio, level, tick):
    global state_val_in
    global state_val_out

    state_val_in[pin_val_in.index(gpio)] = level
    state_val_out = state_val_in

    output()

#
# Callback function for when disconnect buttons are
# pressed
#
def callback_disconnect(gpio, level, tick):
    global state_dis_in
    global state_dis_out

    state_dis_in[pin_dis_in.index(gpio)] = level
    if state_dis_in.count(1) == 2: state_dis_out = 1
    else: state_dis_out = 0

    output()

#
# Outputs to pins on the Remote Fill box
# Catches errors and prevents erroneous output
#
def output():
    global state_val_in
    global state_val_out
    global state_dis_in
    global state_dis_out

    if input_error():
        state_val_out = [0] * len(state_val_out)
        state_dis_out = 0

    out_state = state_val_out + [state_dis_out]
    out_pin   =   pin_val_out +   [pin_dis_out]

    for x in range(0, len(out_state)):
        GPIO.output(out_pin[x], not (out_state[x] ^ on_signal))

    str_status = ''
    for i in range(0, len(state_val_out)):
        if state_val_out[i]: str_status += " ON\t"
        else:        str_status += "OFF\t"
    str_val_out.set(str_status[:-1])

#
# Thread to write to a chosen csv file and update the GUI
#
class WritingThread(threading.Thread):
    def __init__(self, file_name, p0, p1, weight):
        super(WritingThread, self).__init__()
        self.stoprequest = threading.Event()
        self.file = open(file_name, "w+")
        self.p0 = p0
        self.p1 = p1
        self.weight = weight
        self.file.write("Time,Pressure 0,Pressure 1,Weight,as1,as2,as3,as4,as5,sv1,disconnect\n")

    def run(self):
        period = 1.0/write_frequency
        start = time.time()
        next = time.time() + period

        global str_pressure_0
        global str_pressure_1
        global str_weight

        while not self.stoprequest.isSet():
            self.file.write("{:.3}".format(time.time() - start))

            self.p0.append(pt.get_pressure(channel = 0))
            self.p1.append(pt.get_pressure(channel = 1))
            self.weight.append(lc.get_weight(5))

            self.file.write(",{}".format(self.p0[-1]))
            self.file.write(",{}".format(self.p1[-1]))
            self.file.write(",{}".format(self.weight[-1]))

            toWrite = ""
            for i in range(0, len(state_val_out)):
                toWrite += ",{}".format(state_val_out[i])

            toWrite += ",{}".format(state_dis_out)

            self.file.write(toWrite + "\n")

            lc.power_down()
            lc.power_up()

            try:
                str_pressure_0.set("{:f.3}".format(self.p0[-1]))
                str_pressure_1.set("{:f.3}".format(self.p1[-1]))
                str_weight.set("{}".format(self.weight[-1]))
            else:
                break

            if len(self.p0) > 10:
                self.p0.pop(0)
                self.p1.pop(0)
                self.weight.pop(0)

            delay = -1.0
            while delay < 0.0:
                next += period
                delay = next - time.time()

            time.sleep(delay)

    def join(self, timeout = None):
        self.stoprequest.set()
        super(WritingThread, self).join(timeout)
        self.file.close()

#--------------------------------------------------------------------#
#   MAIN FUNCTION                                                    #
#--------------------------------------------------------------------#

def main():

    global state_val_out
    global file_name

    p0 = []
    p1 = []
    weight = []

    write = WritingThread(file_name, p0, p1, weight)

    ensure_off()

    # Add callbacks to all switches
    for x in pin_val_in:
        ground_control.callback(x, pigpio.EITHER_EDGE, callback_valve)

    # Add callbacks to all switches
    for x in pin_dis_in:
        ground_control.callback(x, pigpio.EITHER_EDGE, callback_disconnect)

    try:

        write.start()

        root.mainloop()

    finally:
	print("Exiting main loop")
        write.join()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Goodbye!")
    finally:
        GPIO.cleanup()
        ground_control.stop()
