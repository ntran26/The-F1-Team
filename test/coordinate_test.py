from pypylon import pylon
import cv2
import numpy as np
import imutils

file = open("../calibration/crop","r")
roi_coor = file.read().split("\n")
x1 = int(roi_coor[0])
y1 = int(roi_coor[1])
x2 = int(roi_coor[2])
y2 = int(roi_coor[3])
print(x1,y1,x2,y2)

# Mouse click
def input_point(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # cv2.circle(img, (x, y), 5, (0, 0, 0), -1)
        x = x*pixel_width
        y = y*pixel_height

        x_new = y
        y_new = x
        print('%.2f' % x_new," ",'%.2f' % y_new)     # display x and y with 2 decimal places

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
        img = img[y1:y1+y2,x1:x1+x2]

        height, width, channels = img.shape

        # real coordinate height and width in mm
        real_height = 270
        real_width = 272

        pixel_height = real_height/height
        pixel_width = real_width/width

        cv2.imshow('Output',img)
        cv2.setMouseCallback("Output", input_point)

        key = cv2.waitKey(1)
        if key == 27:
            break
    grabResult.Release()

camera.StopGrabbing()
cv2.destroyAllWindows