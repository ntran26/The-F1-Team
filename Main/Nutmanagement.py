from logging import NullHandler
import math
from pickle import TRUE
from cv2 import sqrt
import serial
import time
import keyboard
from asyncio.windows_events import NULL
from Nut import Nut
import datetime
import cmath
import os
from pathlib import Path
#from PickPlace.Test3 import readcor

def checkDeleted(objectID):
    junk = open("junk",'r')
    deletedFile = junk.read().split("\n")
    junk.close()
    return str(objectID) in deletedFile

def checkDeleted(objectID):
    junk = open("junk",'r')
    deletedFile = junk.read().split("\n")
    junk.close()
    return str(objectID) in deletedFile

class Nutmanagement:
    def __init__(self):
        self.target_X = 0.0
        self.target_Y = 0.0
        self.i = 0
        self.prevt = 0.0 
        self.idarray=[]
        self.flag = False
        self.stop = False
        self.tw = 0.1
        self.prevX = 0.0
        self.pickY = 0.0
        self.t_begin = 0.0
        self.listnut = []
        self.Vconveyor = 0.0
        self.ENdis = 0.0
        self.serial_encoder = serial.Serial('COM10', 115200)
        self.serial_encoder.timeout = None
    serialcomm = serial.Serial('COM3',115200)   #robot
    serialcomm.timeout =1
    serialcomm1 = serial.Serial('COM7',115200)  #conveyor
    serialcomm1.timeout=1

    def generateID(self):
        maxId = 1
        if (self.nutnum() > 0):
            maxId = self.listnut[0]._id
            for nut in self.listnut:
                if (maxId < nut._id):
                    maxId = nut._id
            maxId = maxId + 1
        return maxId

    def cal_time(self, x,y,v):
        y_f = float(math.sqrt(pow(300,2)- pow(x,2)))
        t = (y - y_f)/v 
        return t 

    def nutnum(self):
        return self.listnut.__len__()

    def insert_coor(self,X,Y):
        ID = self.generateID()
        x = X
        y = Y
        t = self.cal_time(X,Y,10)
        nut = Nut(ID,x,y,t)
        self.listnut.append(nut)
    
    def del_nut(self,arr,i):
        if len(self.listnut) > 0:
            print("Successfully removed",arr[i])
            #del arr[0]
        #return arr

    def kills(self):
        while True:
            if keyboard.is_pressed('A') == True:
                self.convey()
                self.stop = True
                break

    def frame(self,x,y):
        """
        Create a new coordinate to match with coordinate of camera and robot
        """
        new_x = 150.0 - y
        new_y = x + 750.0
        return new_x, new_y

    def Update_Conveyor_Pos(self,v):
        #clear input buffer
        self.serial_encoder.flushInput()
        self.serialcomm1.write(b'M310 1' + b'\r\n')
        self.serialcomm1.write(f"M311 -{v}".encode() + b'\r\n')

        while True:
            line = self.serial_encoder.readline().decode('ascii')
            self.ENdis = float(line)
            self.update_var(self.ENdis)

    def speed_monitor(self):
        while True:
            if keyboard.is_pressed('S') == True:
                break
            self.Vconveyor = self.ENdis/0.2

    '''
    def clk(self,v):
        self.serialcomm1.write(b'M310 1' + b'\r\n')
        self.serialcomm1.write(f"M311 {-v}".encode() + b'\r\n')
        prev = time.time()
        while keyboard.is_pressed('A') == False:
            a = time.time()- prev
            if a >= 0.1000:
                self.update_var(v*round(a,1)) 
                prev = time.time()
            
        #self.serialcomm1.write(b'M311 0' + b'\r\n')
        #self.update_var(v*( time.time()- prev))        
    '''

    def update_var(self,displace_val):
            for k in range (0, len(self.listnut)):
                self.listnut[k]._corY = self.listnut[k]._corY + displace_val
            if self.i < len(self.listnut):
                #id = self.idarray[self.i]
                #self.target_X = round(self.listnut[id-1]._corX,2)
                #self.target_Y = round(self.listnut[id-1]._corY,2)
                self.target_X = round(self.listnut[self.i]._corX,2)
                self.target_Y = round(self.listnut[self.i]._corY,2)
                # if self.prevX != self.target_X and self.target_Y > 340 and self.i >0:
                #     self.flag = True
                # self.prevX = self.target_X 
                #print(self.target_X, self.target_Y)
            else:
                self.target_X = None
                self.target_Y = None
            #print(round(self.listnut[0]._corY,1))
               
    def pick_order(self):
        while True:
            if keyboard.is_pressed('A') == True:
                break
            if(len(self.listnut)> len(self.idarray)):
                #if (len(s)!= len(self.listnut)):
                self.idarray = []
                for n in range (0,len(self.listnut)) :
                    self.idarray.append(self.listnut[n]._id) 
                for i in range(0, len(self.idarray) - 1):
                    for j in range(i + 1, len(self.idarray)):
                        if self.findByID(self.idarray[i]) > self.findByID(self.idarray[j]):
                            tmp = self.idarray[i]
                            self.idarray[i] = self.idarray[j]
                            self.idarray[j] = tmp
                #print(self.idarray[self.i])
            else:
                self.idarray = self.idarray

    def incircle(self,x,y,r):
        if (pow(x,2)+ pow(y,2) ) <= pow(r,2):
            result = True
            self.serialcomm.write(b'M03 D0' + b'\r\n')
        else:
            result = False
        return result 

    def str2num (self,str):
        X = ""
        Y = ""
        str = str.rstrip("\n") 
        str = str.strip()
        if str != "":  
            for i in range (1,len(str)-1):
                if str[i] == ",":
                    for a in range (i+1,len(str)-1):
                        Y = Y + str[a]
                    break
                X = X+ str[i]
            X = float(X)
            Y = float(Y)
        return X,Y
    
    
    # insert code here 
        

        
    # ----------------
    

    # read the coordinate
    def readcor(self):
        # i = 0
        # f = open('Coor.text','r')
        # once = False
        a = time.time()
        while True:
            
            if time.time() - a >= 0.1:
                if keyboard.is_pressed('A') == True:
                    break
                a = time.time()        
    
            files = os.listdir("./coordinate/")
            paths = sorted(Path("./coordinate/").iterdir(),key=os.path.getmtime)
            paths = list(map(lambda p: str(p),list(paths)))
            if(len(files) > 0):
                f = open(paths[0],'r')
                # f = open("./coordinate/demofile.txt", "r")
                t = f.read().split(" ")
                f.close()
                
                x = float(t[0])
                y = float(t[1])
                
                # logic
                print("Receiving: ", x, y, " ; New coordinate: ", x, y)
                # new_x, new_y = self.frame(x,y)
                
                # create nut object 
                self.insert_coor(x,y)
                
                # clean up already read files
                junk2 = open("junk",'a+')
                if (not checkDeleted(files[0])):
                    junk2.write(files[0] + "\n")
                    junk2.close()
                    os.remove(f.name)
            
            # # read data from file
            # line = f.readlines() # array
            
            # if time.time() - a >= 0.1:
            #     if keyboard.is_pressed('A') == True:
            #         break
            #     a = time.time()        
             
            # # logic of the function    
            # if line != []:
                
            #     # circumstance: ?
            #     if len(line) == 1:
                    # x, y = self.str2num(line[i])
            #         new_x, new_y = self.frame(x,y)
                    
            #         # create nut object 
            #         self.insert_coor(new_x,new_y)
            #         #print(line)
            #         if not once:
            #             i = i + 1
            #             once = True
                        
            #     # có toạ độ
            #     if len(line) > 1:
            #         for k in range(len(line)):
            #             if line[k] != '\n': 
            #                 x, y = self.str2num(line[k])
            #                 new_x, new_y = self.frame(x,y)
            #                 self.insert_coor(new_x,new_y)
            #                 #print(x)
            #                 #print(y)
        f.close()

    def findByID(self, ID):
        Time_Result = None
        if (len(self.listnut) > 0):
            for nut in self.listnut:
                if (nut._id == ID):
                    Time_Result = nut._time 
        return Time_Result


    def wait(self, coor_X):
        string = f"G01 X{coor_X} Z-757"
        gcode_byte = bytes(string, 'utf-8')
        self.serialcomm.write(gcode_byte + b'\r\n') #send Gcode move to object position
        # self.serialcomm.write(b'M03 D0' + b'\r\n')
        
    def pnp2(self,S,E,a_arm,v_arm,j,v_belt):
        # self.serialcomm.write(f"G01 X{self.target_X}".encode() + b'\r\n')
        #self.serialcomm.write(b'M03 D0' + b'\r\n')
        '''
        t_prev = time.time()
        while time.time() - t_prev < self.tw: #(cashew.tw): #1 while t_curent - t_prev < t_required 
            continue
        '''
        offset= self.offset(S,E,a_arm,v_arm, j,math.fabs(v_belt))
        #self.serialcomm.write(f"G01 X{self.target_X}".encode() + b'\r\n')
        self.serialcomm.write(f"G01 X{self.target_X} Y{self.target_Y - offset-5.375-2}".encode() + b'\r\n') #5.24-v50
        #self.pickY =self.target_Y - offset-5.375-2
        self.serialcomm.write(b'G01 Z-793' + b'\r\n')
        self.serialcomm.write(b'G01 Z-757' + b'\r\n') #move to drop off position
        self.serialcomm.write(b'G01 X250 Y0' + b'\r\n')
        self.serialcomm.write(b'M05 D0' + b'\r\n')   #turn off vacuum
        startT = time.time()
        while time.time() - startT < 0.2:
            continue

    def convey(self):
        self.serialcomm1.write(b'M311 0' + b'\r\n')

    def home(self, v, a, j, S, E):
        self.serialcomm.write(b'G28' + b'\r\n')
        self.serialcomm.write(f"M210 F{v} A{a} J{j} S{S} E{E}".encode() + b'\r\n')
        self.serialcomm.write(b'G01 X250 Y0 Z-757' + b'\r\n')
    
    def offset(self,S,E,amax, vmax,j,vbelt):
        # pre
        # if self.i > 0:
        #     self.tw += self.t_wait(250,self.target_X, S,E,amax, vmax,j) #self.t_wait(0,math.sqrt(pow(self.listnut[self.i-1]._corX -250,2)+pow(self.pickY,2)), S,E,amax, vmax,j)            #self.tw= 0.0
        #     self.tw += 0.215
        #     # print(self.tw)
       
        # print(self.tw)
        #t0t1
        #to = self.t_wait(250, self.target_X,S,E,amax,vmax,j)+self.tw
        #self.target_Y -= 5
        # if self.i == 0:
        #     self.tw = self.t_wait(250, self.target_X,S,E,amax,vmax,j):
        if self.i == 0:
            new_y = self.target_Y
        else:
            new_y = self.pickY - vbelt * (time.time() - self.t_begin)
        #print(new_y, self.target_Y)
        X_o = -math.sqrt(pow(self.target_X -250,2)+pow(new_y,2))
        t1 = (amax/j)
        v1 = S + (0.5*j*pow(t1,2))
        x1 = X_o + S*t1 + ((1/6)*pow(t1,3)*j)
        #t2t3
        v2 = vmax -(amax*t1) - (0.5*j*pow(t1,2))
        #t1t2
        t2 = ((v2-v1)/amax)+t1
        t3 = t2 + t1
        x2 = x1 + v1*(t2-t1)+ (0.5*amax*pow((t2-t1),2))
        x3 = x2 + v2*(t3-t2)+ 0.5*amax*pow((t3-t2),2)- ((1/6)*j*pow((t3-t2),3))
        #t3t4
        v4 = vmax
        x4 = x3 #vmax*(t7 - t1-t2-t3)
        #t4t5
        v5 = vmax - (0.5*j*pow(t1,2))
        x5 = x4 + (v4*t1) - ((1/6)*j*pow(t1,3))
        #t5t6
        x6 = x5 + v5*(t2 -t1)- (0.5*amax*pow((t2-t1),2))
        #t6t7
        v6 = E - (amax*t1)- (0.5*j*pow(t1,2))
        x7 = x6 + (v6*t1)- 0.5*amax*pow(t1,2)+ ((1/6)*j*pow((t1),3))
        #t7 = ((x7_final - x7)/vmax)+(t1 + t2 + t3)
        ### Calculate time and point robot meets nut
        #t7 = (X_onut-(vbelt*tw)-x7+ vmax*(t1 +t2+t3))/(vmax+vbelt)
        t7 = (0-x7+ vmax*(t1 +t2+t3))/(vmax+vbelt)
        ofset = t7*vbelt #+ self.tw*vbelt
        self.tw = 2*(t7 + 0.1075) + 0.2
        #print(self.tw)
        #ofset = t7*vbelt + to*vbelt
        #print(t7+self.tw)
        #print(x1,x2,x3,x4,x5,x6)
        if self.i < len(self.listnut) - 1:
            #id = self.idarray[self.i+1]
            self.pickY = round(self.listnut[self.i+1]._corY,2)
        return ofset

    def t_wait(self, X_o,x7_final,S,E,amax, vmax,j):
        if (X_o > x7_final):
            tmp = X_o
            X_o = x7_final
            x7_final = tmp
        #t0t1
        t1 = amax/j
        v1 = S + (0.5*j*pow(t1,2))
        x1 = X_o + S*t1 + ((1/6)*pow(t1,3)*j)
        #t2t3
        v2 = vmax -(amax*t1) - (0.5*j*pow(t1,2))
        #t1t2
        t2 = ((v2-v1)/amax)+t1
        t3 = t2 + t1
        x2 = x1 + v1*(t2-t1)+ (0.5*amax*pow((t2-t1),2))
        x3 = x2 + v2*(t3-t2)+ 0.5*amax*pow((t3-t2),2)- ((1/6)*j*pow((t3-t2),3))
        #t3t4
        v4 = vmax
        x4 = x3 #vmax*(t7 - t1-t2-t3)
        #t4t5
        v5 = vmax - (0.5*j*pow(t1,2))
        x5 = x4 + (v4*t1) - ((1/6)*j*pow(t1,3))
        #t5t6
        x6 = x5 + v5*(t2 -t1)- (0.5*amax*pow((t2-t1),2))
        #t6t7
        v6 = E - (amax*t1)- (0.5*j*pow(t1,2))
        x7 = x6 + (v6*t1)- 0.5*amax*pow(t1,2)+ ((1/6)*j*pow((t1),3))
        t7 = ((x7_final - x7)/vmax)+(t1 + t2 + t3)
        ### Calculate time and point robot meets nut
        #t7 = (X_onut-x7+vmax*(t1 +t2+t3))/(vmax+vbelt)
        #ofset = t7*vbelt
        return t7
        
    def t_required(self,S,E,amax, vmax,j):
        # print(self.i)
        if self.i < len(self.listnut):
            self.tw = 2*self.tw + 2*0.1075
            print(self.tw)
            # self.tw += self.t_wait(250,self.listnut[self.i+1]._corX, S,E,amax, vmax,j) +self.t_wait(0,math.sqrt(pow(self.target_X -250,2)+pow(self.pickY,2)), S,E,amax, vmax,j) + 0.1075
            #self.tw += self.t_wait(0,math.sqrt(pow(self.target_X -250,2)+pow(self.pickY,2)), S,E,amax, vmax,j) 
            #print(self.tw)


    
    


        

    
    
    