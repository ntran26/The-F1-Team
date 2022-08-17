# The-F1-Team

Follow these steps to run the program

**Prepare Weight and Config file**
1. Download Yolov4-custom-best.weight or Yolov4-tiny-custom-best.weight
2. Download Yolov4-custom-best.config or Yolov4-tiny-custom-best.config
3. Put in the root folder (CashewNut-YoloV4)
4. On "main.py" file, make sure line 28 and 29 have the path of both weights and config files
Ex: 
    modelConfiguration = "yolov4-tiny-custom.cfg"
    modelWeights = "yolov4-tiny-custom_best.weights"

LINK FOR DOWNLOADS: 
https://rmiteduau-my.sharepoint.com/:f:/g/personal/s3694863_rmit_edu_vn/ElY-z_BW1yxAsqrHVQ-4ebYBGNjtJSn49ozPrg5TiywYtw?e=fnB4xh

**Running the file**
1. Open terminal of root folder (Ctrl + Shift + `)
2. Type in ".\start.bat"
3. If error, try the following steps: 
(A) Comment out line 4 and 5 on "start.bat" file. 
(B) Try line 7-8 or 10-11 instead. 
(C) Otherwise, run manually the main file, then switch to listener.py and run using Ctrl+F5.
4. The program should start 2 scripts: main.py and listener.py 
5. The main file detects and send the nuts' coordinate to listener.py

**DO NOT REMOVE "junk" FILE AND "coordinate" FOLDER. THEY WILL BE USED DURING OPERATION.**
