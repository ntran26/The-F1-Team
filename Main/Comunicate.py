from fileinput import close
from re import S
from turtle import done, onclick
import serial
import time
import math
import keyboard 
import sys

serialcomm = serial.Serial('COM9',115200) #conveyor
serialcomm.timeout =1
#f = open('Coor.text','r')

def position(e):
    gcode = bytes("Position", 'utf-8')
    serialcomm.write(gcode + b'\r\n')
    string = serialcomm.readline().decode('ascii')
    L = string.split(',')
    X = 0
    Y = 0
    Z = 0 
    if e =="x":
        X = float(L[0])
        return X
    elif e =="y":
        Y = float(L[1])
        return Y
    elif e =="z":
        Z = float(L[2])
        return Z
def send(a,i):
    if i == "x":
        string = f"G01 X{a}"
    elif i == "y":
        string = f"G01 Y{a}"
    elif i == "z":
        string = f"G01 Z{a}"
    gcode_byte = bytes(string, 'utf-8')
    serialcomm.write(gcode_byte + b'\r\n')
    time.sleep(0.8)
    print(serialcomm.readline().decode('ascii'))

def setpara(a,f,s,e):
    serialcomm.write(f"G01 A{a} F{f} S{s} E{e}".encode() + b'\r\n')
    print(serialcomm.readline().decode('ascii'))



i = input ("Press s: ")
while True:
    if i  == "done":
        break
    if i == "s":
        while True:
            a= input("Insert Gcode:")
            if(a == "done"):
                break 
            else:
                gcode_byte = bytes(a, 'utf-8')
                serialcomm.write(gcode_byte + b'\r\n')
                time.sleep(0.5)
                print(serialcomm.readline().decode('ascii'))
        i == "done"
        break
    # elif i == "m":
    #     line = f.readline()
    #     if not line:
    #         print("No line")
    #         break
    #     line = line.rstrip("\n") 
    #     line = line.strip()
    #     line = bytes(line, 'utf-8')
    #     serialcomm.write(line + b'\r\n')
    #     time.sleep(0.5)
    #     print(serialcomm.readline().decode('ascii'))
    elif i =="keyboard":
        while True:
            if keyboard.is_pressed('w') == True:
                x = round(position("x")+50, 2)
                send(x,"x")
                sys.stdout.flush()
            if keyboard.is_pressed('s') == True:
                x = round(position("x")-50, 2)
                send(x,"x")
                sys.stdout.flush()
            if keyboard.is_pressed('d') == True:
                y = round(position("y")+50, 2)
                send(y,"y")
                sys.stdout.flush()
            if keyboard.is_pressed('a') == True:
                y = round(position("y")-50, 2)
                send(y,"y")
                sys.stdout.flush()
            if keyboard.is_pressed('+') == True:
                z = round(position("z")+5, 2)
                send(z,"z")
                sys.stdout.flush()
            if keyboard.is_pressed('-') == True:
                z = round(position("z")-5, 2)
                send(z,"z")
                sys.stdout.flush()
            if keyboard.is_pressed('p') == True:     
                A,F,S,E = input("Insert Acceleration, Velocity, Start speed, End speed: ").split()
                setpara(A,F,S,E)
            if keyboard.is_pressed('1') == True:
                serialcomm.write("M03 D0".encode() + b'\r\n')
                print(serialcomm.readline().decode('ascii'))
            if keyboard.is_pressed('0') == True:    
                serialcomm.write("M05 D0".encode() + b'\r\n')
                print(serialcomm.readline().decode('ascii'))
            if keyboard.is_pressed('alt') == True:
                break
        i == "done"
        break
            
serialcomm.close()