import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import numpy as np
import string
import pyttsx3


class VisionSubscriber(Node):

    def __init__(self):
        super().__init__('vision_subscriber')
        self.color_subscription = self.create_subscription(
            Image,
            '/StereoNetNode/rectified_image',
            self.vision_listener_callback,
            10)

        self.bgr_image = np.zeros((480, 640, 3), dtype=np.uint8)
        self.hsv_image = np.zeros((480, 640, 3), dtype=np.uint8)

        self.bridge = CvBridge()
        self.detector = cv2.QRCodeDetector()

        self.green_l = np.array([36, 50, 70])
        self.green_u = np.array([89, 255, 255])
        self.yellow_l = np.array([25, 50, 70])
        self.yellow_u = np.array([35, 255, 255])
        self.red_l = np.array([0, 50, 70])
        self.red_u = np.array([9, 255, 255])
        self.blue_l = np.array([90, 50, 70])
        self.blue_u = np.array([128, 255, 255])
        self.orange_l = np.array([10, 50, 70])
        self.orange_u = np.array([24, 255, 255])

    def vision_listener_callback(self, msg):
        self.get_logger().info('Receiving color image')
        yuv = np.frombuffer(msg.data, dtype=np.uint8).reshape((msg.height * 3 // 2, msg.width))
        self.bgr_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
        self.hsv_image = cv2.cvtColor(self.bgr_image, cv2.COLOR_BGR2HSV)


    def picture_hunter(self):
        
        detector = cv2.QRCodeDetector()
        data, points, straight_qrcode = detector.detectAndDecode(self.bgr_image)

        while data == None:

            data, points, straight_qrcode = detector.detectAndDecode(self.bgr_image)

            # if points is not None and data:
            #     points = points.astype(int).reshape(-1, 2)

            #     for i in range(len(points)):
            #         p1 = tuple(points[i])
            #         p2 = tuple(points[(i + 1) % len(points)])

            print("QR data:", data)

    def color_hunter(self, req_color:String):
        if req_color == 'green':
            mask = cv2.inRange(self.hsv_image, self.green_l, self.green_u)
        elif req_color == 'yellow':
            mask = cv2.inRange(self.hsv_image, self.yellow_l, self.yellow_u)
        elif req_color == 'red':
            mask = cv2.inRange(self.hsv_image, self.red_l, self.red_u)
        elif req_color == 'blue':
            mask = cv2.inRange(self.hsv_image, self.blue_l, self.blue_u)
        elif req_color == 'orange':
            mask = cv2.inRange(self.hsv_image, self.orange_l, self.orange_u)
            
        white_pixels_count = cv2.countNonZero(mask)
        total_pixels = mask.size
        percentage = (white_pixels_count / total_pixels) * 100

        engine = pyttsx3.init()
        if percentage > 75:
            engine.say("I see a lot of " + req_color + " color!")
        else:
            engine.say("I don't see much " + req_color + " color.")
        engine.runAndWait()