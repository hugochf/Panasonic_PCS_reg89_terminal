import reg89_terminal_mqtt
from reg89_terminal_mqtt import *
from tkinter import *
from tkinter import ttk
import threading
import time

root = Tk()
root.title('Panasonic PCS reg89 control v0.03')
root.geometry("420x136") #Mac windows size
#root.geometry("420x136") #Win windows size
root.resizable(0, 0)

# CRC cal
def modbusCrc(msg:str) -> int: 
    crc = 0xFFFF
    for n in range(len(msg)):
        crc ^= msg[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def connectMQTT():
    reg89_terminal_mqtt.meter_id = meter_id.get()
    if clicked3.get() == "IIL":
        reg89_terminal_mqtt.server_ip = "34.96.156.219"
    else:
        reg89_terminal_mqtt.server_ip = "52.156.56.170"
    # Run MQTT client in background
    t1 = threading.Thread(target=reg89_terminal_mqtt.connect_mqtt())
    t1.start()
    time.sleep(1)

    state_update()
    if (reg89_terminal_mqtt.mqtt_status != "Failed to connect..."):
        OnButton.config(state = "normal")
        OffButton.config(state = "normal")
        readButton.config(state = "normal")
    else:
        OnButton.config(state = "disabled")
        OffButton.config(state = "disabled")
        readButton.config(state = "disabled")
        

def pcs_on():
    # Set baud rate
    if clicked.get() == "9600":
        baud = "03"
    else:
        baud = "04"
    # Set meter type
    if clicked2.get() == "Sub":
        type = "2"
    else:
        type = "C"
    # Set CRC
    msg = bytes.fromhex(clicked1.get() + "0600590000")
    crc = modbusCrc(msg)  
    ba = crc.to_bytes(2, byteorder='little')
    command = type + "84A" + meter_id.get().strip("J?") + "F00" + baud + "02080108" + clicked1.get() + "0600590000" + str("%02X%02X"%(ba[0], ba[1])) +"0000000000000000000000"
    print(command)
    reg89_terminal_mqtt.publish_mqtt(command)
    state_update()

def pcs_off():
    # Set baud rate
    if clicked.get() == "9600":
        baud = "03"
    else:
        baud = "04"
    # Set meter type
    if clicked2.get() == "Sub":
        type = "2"
    else:
        type = "C"
    # Set CRC
    msg = bytes.fromhex(clicked1.get() + "0600590501")
    crc = modbusCrc(msg)  
    ba = crc.to_bytes(2, byteorder='little')
    command = type + "84A" + meter_id.get().strip("J?") + "F00" + baud + "02080108" + clicked1.get() + "0600590501" + str("%02X%02X"%(ba[0], ba[1])) +"0000000000000000000000"
    print(command)
    reg89_terminal_mqtt.publish_mqtt(command)
    state_update()

def read():
    # Set baud rate
    if clicked.get() == "9600":
        baud = "03"
    else:
        baud = "04"
    # Set meter type
    if clicked2.get() == "Sub":
        mtype = "2"
    else:
        mtype = "C"
    # Set CRC
    msg = bytes.fromhex(clicked1.get() + "0300590001")
    crc = modbusCrc(msg)  
    ba = crc.to_bytes(2, byteorder='little')
    #c84a220005571f 00 03 02 08 01 08   01 03 00 57 00 04 f5d9 0000000000000000000000
    command = mtype + "84A" + meter_id.get().strip("J?") + "F00" + baud + "02080108" + clicked1.get() + "0300590001" + str("%02X%02X"%(ba[0], ba[1])) +"0000000000000000000000"
    print(command)
    reg89_terminal_mqtt.publish_mqtt(command)
    state_update()

def state_update():
    status.config(text=reg89_terminal_mqtt.mqtt_status)
    root.after(100, state_update)

# Drop down list init
clicked = StringVar()
clicked.set("9600")
baud = "03"
clicked1 = StringVar()
clicked1.set("01")
clicked2 = StringVar()
clicked2.set("Sub")
mtype = "Sub"
clicked3 = StringVar()
clicked3.set("IIL")

# Status bar
status = Label(root, text="Ready", bd=1, relief=SUNKEN, anchor=E)
status.grid(row=4, column=0, columnspan=5, sticky=E+W+S)

# Meter ID input field
meterLabel = Label(root, text="Meter ID")
meterLabel.grid(row=0, column=0, padx=5, pady=10, sticky=W)
meter_id = Entry(root, width=10)
meter_id.grid(row=0, column=1, columnspan=2, padx=5, sticky=W+E)
serDrop = OptionMenu(root, clicked3, "IIL", "ESI")
serDrop.grid(row=0, column=3, padx=5, sticky=W)
connectButton = Button(root, text="Connect", command=connectMQTT)
connectButton.grid(row=0, column=4, padx=5, sticky=W)
# PCS setting input fields
BaudLabel = Label(root, text="Baud rate")
BaudLabel.grid(row=1, column=0, padx=5, sticky=W)
BaudDrop = OptionMenu(root, clicked, "9600", "19200")
BaudDrop.grid(row=1, column=1, padx=10, sticky=W)
NodeLabel = Label(root, text="Node")
NodeLabel.grid(row=1, column=2, padx=10, sticky=W),
NodeDrop = OptionMenu(root, clicked1, "00", "01", "02", "03", "04", "05", "06", "08", "09", "0A", "0B", "0C", "0D", "0E", "0F", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "1A", "1B", "1C", "1D", "1F", "20")
NodeDrop.grid(row=1, column=3, padx=10, sticky=W)
meterDrop = OptionMenu(root, clicked2, "PV", "Sub")
meterDrop.grid(row=1, column=4, padx=5, sticky=E)

# Big ON OFF button
OnButton = Button(root, text="Disable (0x89=0x00)", command=pcs_on, fg='red', state="disabled")
OnButton.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky=W)
OffButton = Button(root, text="Enable (0x89=0x01)", command=pcs_off, fg='green', state="disabled")
OffButton.grid(row=2, column=3, columnspan=2, pady=10, sticky=E)
readButton = Button(root, text="Read", command=read, state="disabled")
readButton.grid(row=2, column=2, sticky=W)

root.mainloop()