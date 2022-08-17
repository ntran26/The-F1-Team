from pypylon import pylon
import cv2
import imutils

# conecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Set up the parameters
camera.Open()
camera.ExposureOverlapTimeMaxRaw.SetValue(300000)    # monochrome camera
# camera.ExposureTimeAbs.SetValue(70000)            # RGB camera
# camera.Width.SetValue(2046)           # set frame width
# camera.Height.SetValue(2046)          # set frame height
width = 1500
height = 1700
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
        # Access the image data
        image = converter.Convert(grabResult)
        img = image.GetArray()
        img = imutils.resize(img, height=int(700))
        img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE)

        fps = int(camera.ResultingFrameRateAbs.GetValue())   
        # print(fps)
        cv2.imshow('title', img)
        k = cv2.waitKey(1)
        if k == 27:
            break

    grabResult.Release()
    
# Releasing the resource    
camera.StopGrabbing()
cv2.destroyAllWindows()
# vid_writer.release()