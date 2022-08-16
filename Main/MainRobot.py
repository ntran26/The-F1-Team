from re import S
import time
from tkinter import E
import serial
from asyncio.windows_events import NULL
from Nutmanagement import Nutmanagement
from threading import Thread
import keyboard

cashew = Nutmanagement()
#X_rec = [220,225,230,280,250,260,50]
#Y_rec = [300,310,320,330,340,350,360]
# serialcomm = serial.Serial('COM3',115200)
# serialcomm.timeout =1
X_rec =[]
Y_rec =[]
seq =[]

lisT = cashew.listnut
i= 0
TarX, TarY = 0, 0
v_belt = 15.0
v_arm = 700.0
a_arm = 10000.0
s = 50.0
e = 30.0
j = 1500000.0
time_end = time.time()
cashew.home(v_arm,a_arm, j,s,e)
#cashew.check()
#cashew.readcor()
time.sleep(15) #12.3s
t =  Thread(target= cashew.clk, args=[v_belt])
t0 = Thread(target= cashew.readcor)
#t1 = Thread(target= cashew.convey)  ##Update every 0.2s 15.19
t2 = Thread(target= cashew.pick_order) 
t3 = Thread(target= cashew.kills)


t.start()
t0.start()
#t1.start()
t3.start()
t2.start()
a = time.perf_counter()
t_prev = 0
t_wait = 0

# while True:
#     if cashew.target_X != 0.0 or cashew.target_Y != 0.0:
#         break

t_prev = time.time()

while True:
        cashew.t_begin = time.time()
        if keyboard.is_pressed('A') == True:
                break
        if (time.time()- t_prev >= cashew.tw):
            if cashew.i < len(cashew.listnut):
                if cashew.target_X != None and cashew.target_Y != None:
                    print(cashew.target_X, cashew.target_Y)
                    # cashew.wait(cashew.target_X)
                    if cashew.incircle(cashew.target_X, cashew.target_Y,300) == True:
                        cashew.pnp2(s,e,a_arm,v_arm,j, v_belt)
                        print("Completeted: ",cashew.i+1)
                        #cashew.t_required(s,e,a_arm,v_arm,j)
                        cashew.i = cashew.i + 1
                        #while time.time() - t_prev < cashew.tw: #(cashew.tw): #1 while t_curent - t_prev < t_required 
                            #continue
                        #if cashew.target_X == None and cashew.target_Y == None:
                           #break
                else:
                    print("Target = NULL")

            elif cashew.i == len(cashew.listnut) and cashew.i != 0:
                cashew.i = 0
                cashew.idarray = []
                cashew.listnut = []
            #     print('Finish')
            #     break
            t_prev = time.time()

t.join()
t0.join()
#t1.join()
t2.join()
t3.join()

