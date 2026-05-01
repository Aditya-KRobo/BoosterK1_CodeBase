import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import numpy as np
import string
import pyttsx3


class QRSubscriber(Node):

  def __init__(self):
    super().__init__('qr_subscriber')
    self.color_subscription = self.create_subscription(
      Image,
      '/StereoNetNode/rectified_image',
      self.qr_listener_callback,
      10)
    
    self.bgr_image = np.zeros((480, 640, 3), dtype=np.uint8)
    self.hsv_image = np.zeros((480, 640, 3), dtype=np.uint8)

    self.bridge = CvBridge()
    self.detector = cv2.QRCodeDetector()


  def qr_listener_callback(self, msg):
    # self.get_logger().info('Receiving color image')
    yuv = np.frombuffer(msg.data, dtype=np.uint8).reshape((msg.height * 3 // 2, msg.width))
    self.bgr_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
    self.hsv_image = cv2.cvtColor(self.bgr_image, cv2.COLOR_BGR2HSV)

    detector = cv2.QRCodeDetector()

    data, points, straight_qrcode = detector.detectAndDecode(self.bgr_image)

    if points is not None and data:
        points = points.astype(int).reshape(-1, 2)

        for i in range(len(points)):
            p1 = tuple(points[i])
            p2 = tuple(points[(i + 1) % len(points)])

        print("QR data:", data)
        



def main(args=None):
    rclpy.init(args=args)
    qr_subscriber = QRSubscriber()
    try:
        rclpy.spin(qr_subscriber)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, stopping ...")
    finally:
        try:
            # qr_subscriber.color_hunter('green')
            qr_subscriber.picture_hunter()
        except Exception as e:
            print(f"qrcode_hunter skipped: {e}")
        qr_subscriber.destroy_node()
        rclpy.shutdown()
        print("vision_demo shutdown complete.")

if __name__ == '__main__':
    main()