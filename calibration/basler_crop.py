# This code lets user draws a rectangle box to define the region of interest (ROI)
# After running the code and selected the region, the coordinates of 2 corners (x1,y1) (x2,y2)
# will be exported to file "crop"


from pypylon import pylon
import cv2
import numpy as np
import imutils

# conecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Set up the parameters
camera.Open()
# camera.ExposureTimeAbs.SetValue(300000)                         # for monochrome camera
camera.ExposureOverlapTimeMaxRaw.SetValue(17375)              # for RGB camera
# camera.Width.SetValue(3840)
# camera.Height.SetValue(2748)
camera.AcquisitionFrameRateEnable.SetValue(True)
camera.AcquisitionFrameRateAbs.SetValue(30)
# print(camera.ExposureTime.GetValue())

# Grabing Continuously (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        img = image.GetArray()
        img = imutils.resize(img, height=int(600))
        img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite("static_frame_from_video.jpg",img)
        break   
    break

# Load the captured frame
img_path = "static_frame_from_video.jpg"
img = cv2.imread(img_path)

# Select ROI from the image
roi = cv2.selectROI(img)
x1,y1,x2,y2 = roi

print(roi)

cv2.waitKey(1)

file = open("crop","w")
file.write(str(x1)+"\n")
file.write(str(y1)+ "\n")
file.write(str(x2)+ "\n")
file.write(str(y2)+ "\n")
file.close()
