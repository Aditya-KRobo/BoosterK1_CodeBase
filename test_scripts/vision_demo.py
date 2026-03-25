# demo.py
# to execute this demo, please run following
# source /opt/ros/humble/setup.bash
# python demo.py

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import numpy as np
import string
import pyttsx3

class ImageSubscriber(Node):

  def __init__(self):
    super().__init__('image_subscriber')
    self.color_subscription = self.create_subscription(
      Image,
      '/StereoNetNode/rectified_image',
      self.color_listener_callback,
      10)
    
    self.bgr_image = np.zeros((480, 640, 3), dtype=np.uint8)
    self.hsv_image = np.zeros((480, 640, 3), dtype=np.uint8)

    self.bridge = CvBridge()

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

    # --- ORB setup for picture_hunter ---
    # Points to a folder of reference images named after the object, e.g. "apple.jpg"
    self.reference_dir = os.path.join(os.path.dirname(__file__), 'res')
    self.orb = cv2.ORB_create(nfeatures=300)  # Keep low for performance
    self.bf_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    self.reference_data = self._load_references()

  def _load_references(self):
    """
    Pre-loads and computes ORB descriptors for all reference card images.
    Reference images should be placed in the 'reference_cards/' folder,
    named after the object they represent (e.g. 'apple.jpg', 'cup.png').
    Returns a list of (label, keypoints, descriptors) tuples.
    """
    references = []
    if not os.path.isdir(self.reference_dir):
      self.get_logger().warn(f"Reference directory not found: {self.reference_dir}")
      return references

    for filename in os.listdir(self.reference_dir):
      if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        continue

      label = os.path.splitext(filename)[0]  # e.g. "apple" from "apple.jpg"
      img_path = os.path.join(self.reference_dir, filename)
      img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

      if img is None:
        self.get_logger().warn(f"Could not load reference image: {img_path}")
        continue

      kp, des = self.orb.detectAndCompute(img, None)

      if des is not None and len(des) > 0:
        references.append((label, kp, des))
        self.get_logger().info(f"Loaded reference: '{label}' ({len(kp)} keypoints)")
      else:
        self.get_logger().warn(f"No descriptors found for: {filename}")

    return references

  def color_listener_callback(self, msg):
    self.get_logger().info('Receiving color image')
    yuv = np.frombuffer(msg.data, dtype=np.uint8).reshape((msg.height * 3 // 2, msg.width))
    self.bgr_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV12)
    self.hsv_image = cv2.cvtColor(self.bgr_image, cv2.COLOR_BGR2HSV)

  def color_hunter(self, req_color: string):
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

  def picture_hunter(self):
    """
    Compares the current bgr_image against pre-loaded reference card images
    using ORB feature matching. Announces the best-matched object label.

    To use:
      - Populate the 'reference_cards/' folder with labelled images of your cards.
      - Call this method from an external program or ROS2 service callback.

    Match quality thresholds:
      - good_match_ratio:  fraction of matches that must pass the distance filter
      - min_good_matches:  absolute floor — avoids false positives on near-blank frames
    """
    GOOD_MATCH_DISTANCE = 50   # Lower = stricter; ORB Hamming distance threshold
    MIN_GOOD_MATCHES    = 15   # Minimum matches required to trust a result

    if not self.reference_data:
      print("No reference images loaded. Add images to 'reference_cards/' folder.")
      return

    # Convert current frame to grayscale for ORB
    frame_gray = cv2.cvtColor(self.bgr_image, cv2.COLOR_BGR2GRAY)
    kp_frame, des_frame = self.orb.detectAndCompute(frame_gray, None)

    if des_frame is None or len(des_frame) == 0:
      print("No features detected in current frame.")
      return

    best_label  = None
    best_count  = 0

    for label, kp_ref, des_ref in self.reference_data:
      matches = self.bf_matcher.match(des_ref, des_frame)
      # Filter to only strong matches by Hamming distance
      good_matches = [m for m in matches if m.distance < GOOD_MATCH_DISTANCE]

      if len(good_matches) > best_count:
        best_count = len(good_matches)
        best_label = label

    engine = pyttsx3.init()
    if best_label and best_count >= MIN_GOOD_MATCHES:
      message = f"I can see a {best_label} on the card!"
      print(message)
      engine.say(message)
    else:
      message = "I'm not sure what is on the card."
      print(message)
      engine.say(message)
    engine.runAndWait()


def main(args=None):
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()
    try:
        print("vision_demo running. Press Ctrl+C to stop.")
        rclpy.spin(image_subscriber)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, stopping vision_demo...")
    finally:
        try:
            image_subscriber.color_hunter('green')
        except Exception as e:
            print(f"color_hunter skipped: {e}")
        image_subscriber.destroy_node()
        rclpy.shutdown()
        print("vision_demo shutdown complete.")

if __name__ == '__main__':
    main()
```

---

### How to set it up

**1. Create your reference image folder** alongside `demo.py`:
```
your_project/
├── demo.py
└── reference_cards/
    ├── apple.jpg
    ├── cup.png
    ├── book.jpg
    └── ...