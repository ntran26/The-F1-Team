import cv2
import numpy as np
import imutils
from centroid_tracker import CentroidTracker
from os.path import exists
from pypylon import pylon


class MainCamera:
    def __init__(self):
        # Initialize the parameters
        self.confThreshold = 0.70  #Confidence threshold
        self.nmsThreshold = 0.4   #Non-maximum suppression threshold
        self.inpWidth = 416       #Width of network's input image
        self.inpHeight = 416      #Height of network's input image

        # real coordinate height and width in mm
        self.real_height = 297   # 30cm  (belt's height)
        self.real_width = 211    # 210cm (A4 paper width)

        # parser = argparse.ArgumentParser(description='Object Detection using YOLO in OPENCV')

        # parser.add_argument('--video', help='Path to video file.')
        # args = parser.parse_args()

        # Load names of classes
        self.classes = ['cashew_bad']

        # Give the configuration and weight files for the model and load the network using them.
        self.modelConfiguration = "yolov4-tiny-custom2.cfg"
        self.modelWeights = "yolov4-tiny-custom_best_latest.weights"

        # load our serialized model from disk
        print("[INFO] loading model...")
        self.net = cv2.dnn.readNetFromDarknet(self.modelConfiguration, self.modelWeights)
        # net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        # net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)

        # instantiate our centroid tracker, then initialize a list to store
        # each of our dlib correlation trackers, followed by a dictionary to
        # map each unique object ID to a TrackableObject
        self.ct = CentroidTracker(maxDisappeared=3, maxDistance=20)
        self.trackers = []
        self.trackableObjects = {}

        self.layer_names = self.net.getLayerNames()
        if (np.ndim(self.net.getUnconnectedOutLayers()) > 1):
            self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        else:
            self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

        self.resultCoordination =[]
        # Remove the bounding boxes with low confidence using non-maxima suppression

        # Import ROI coordinates from "crop"
        f = open("../calibration/crop","r")
        roi = f.read().split("\n")
        self.x1 = int(roi[0])
        self.y1 = int(roi[1])
        self.x2 = int(roi[2])
        self.y2 = int(roi[3])
        # print(x1,y1,x2,y2)

        # temporary frame value
        self.hasFrame = False

    def checkDeleted(self, objectID):
        junk = open("junk", 'r')
        deletedFile = junk.read().split("\n")
        junk.close()
        return str(objectID) in deletedFile

    def postprocess(self, frame, outs):
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        rects = []

        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if classId == 0 and confidence > self.confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)
        for i in indices:
            # i = i[0]
            if not np.isscalar(i):
                i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            # if classIds[i] == 0:
            rects.append((left, top, left + width, top + height))
            # use the centroid tracker to associate the (1) old object
            # centroids with (2) the newly computed object centroids
        objects = self.ct.update(rects)
        for (objectID, bbox) in objects.items():
            x1, y1, x2, y2 = bbox       # set the 4 values as coordinates to bbox and conert to int
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            cX = int((x1+x2)/2)         # centroid x of the rectangle box
            cY = int((y1+y2)/2)         # centroid y of the rectangle box

            cX2 = -(cX*pixel_width)+700-15
            cY2 = -(cY*pixel_height)+144

            new_cX2 = cY2
            new_cY2 = cX2

            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            if cX > self.trigger_point:
                if (not exists("./coordinate/" + str(objectID))) and (not self.checkDeleted(objectID)):
                    print("Sending: ",'%.2f' % cX2, '%.2f' % cY2, " with ID: ", objectID)
                    file = open('./coordinate/'+str(objectID),'a')
                    file.write('{} {}'.format('%.2f' % cY2, '%.2f' % cX2))
                    file.close()

    def startCameraDetection(self, showCameraWindow):
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
                self.frame = image.GetArray()
                self.frame = imutils.resize(self.frame, height=int(600))
                self.frame = cv2.rotate(self.frame, cv2.cv2.ROTATE_90_CLOCKWISE)
                self.frame = self.frame[self.y1:self.y1+self.y2,self.x1:self.x1+self.x2]

                frameHeight, frameWidth, channels = self.frame.shape

                global pixel_height, pixel_width
                pixel_height = self.real_height/frameHeight
                pixel_width = self.real_width/frameWidth

                self.trigger_point = frameWidth*4//5

                # Create a 4D blob from a frame.
                blob = cv2.dnn.blobFromImage(self.frame, 1/255, (self.inpWidth, self.inpHeight), [0, 0, 0], 1, crop=False)

                # Sets the input to the network
                self.net.setInput(blob)

                # Runs the forward pass to get output of the output layers
                # outs = net.forward(getOutputsNames(net))

                outs = self.net.forward(self.output_layers)

                # Remove the bounding boxes with low confidence
                self.postprocess(self.frame, outs)

                # # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
                # t, _ = net.getPerfProfile()
                # label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
                # cv2.putText(frame, label, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

                # Write the frame with the detection boxes

                # vid_writer.write(frame.astype(np.uint8))
                trigger_line = cv2.line(self.frame, (self.trigger_point, 0), (self.trigger_point, frameHeight), (0, 0, 255), 2)

                fps = int(camera.ResultingFrameRateAbs.GetValue())

                self.hasFrame = True
                if showCameraWindow:
                    cv2.imshow('video', imutils.resize(self.frame, height=600))

                    key = cv2.waitKey(1)
                    if key == 27:   # ESC pressed
                        open("junk", 'w').close()
                        break

        # video.release()
        cv2.destroyAllWindows()

    def getFrame(self):
        return self.frame

    def getHasFrame(self):
        return self.hasFrame


if __name__ == "__main__":
    mainCamera = MainCamera()
    mainCamera.startCameraDetection(True)
    print(mainCamera.getFrame().shape)
