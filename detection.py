import cv2
import mediapipe as mp
import time
import math

CALIBRATION_TIME = 10
ESTIMATED_CHANGE_PROPORTION = 5

# Wrapper class to store coordinates
class Coordinate():
    def __init__(self, x, y, z=None):
        """Constructor method for a coordinate object."""
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return f"({self.x},{self.y},{self.z})"


# Wrapper class to store important data regarding body part positions
class LandmarkData():
    def __init__(self, OPTIMAL=None):
        """
        Constructor method for important body data - initialises fields.
        
        Args:
            SHOULDER_OPTIMAL (Coordinate): Optimal shoulder values to compare against (where x=width between shoulders, y=average height, z=-10z)
            EYE_OPTIMAL (Coordinate): Optimal eye values to compare against (where x=width between eyes, y=average height, z=-10z)
        """
        # Values to change with every frame (show current coordinates)
        self.left_shoulder = None
        self.right_shoulder = None
        self.left_eye= None
        self.right_eye = None
        self.head_top_left = None #2D
        # Values to compare with after calibration
        self.OPTIMAL = OPTIMAL

class PostureDetection():
    # Initialize MediaPipe Holistic
    holistic = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    # mp_drawing = mp.solutions.drawing_utils

    def __init__(self) -> None:
        # Create an empty store of important landmark data
        self.landmark_data = LandmarkData()

    def calibrate(self, cap) -> Coordinate:
        """
        Calibrates the display to find initial 'optimal' positions for the shoulders and eyes for good posture.
        
        Args:
            cap (VideoCapture): Object currently streaming and capturing video from user.

        Return:
            (Coordinate): Calibrated coordinates to be used for 'optimal' posture.
        """
        # Initialise MediaPipe
        mp_drawing = mp.solutions.drawing_utils
        # Sum the heights and widths of shoulders and eyes
        total_shoulder_x = total_shoulder_y = total_eye_y = total_z = count = 0
        # Timer for 10 seconds 
        end_time = time.time() + CALIBRATION_TIME
        while (cap.isOpened() and time.time() < end_time):
            ret, frame = cap.read()

            if not ret:
                break

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame and get the landmarks
            results = self.holistic.process(rgb_frame)

            # Draw landmarks on the frame
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS)

            if results.pose_landmarks:
                # Get coordinates of the left and right shoulders (landmarks 11 and 12)
                left_shoulder = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_SHOULDER]

                # Get coordinates of the left and right eyes (landmarks 159 and 463)
                left_eye = results.face_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_EYE]
                right_eye = results.face_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_EYE]

                # Convert normalised coordinates to pixel values and store
                height, width, _ = frame.shape

                # Sum to the total the distance between the shoulders/eyes and their average height
                total_shoulder_x += int(left_shoulder.x * width) - int(right_shoulder.x * width)
                total_shoulder_y += (int(right_shoulder.y * height) + int(left_shoulder.y * height)) / 2

                total_eye_y += (int(right_eye.y * height) + int(left_eye.y * height)) / 2

                # Get total distance away
                total_z += right_eye.z + left_eye.z + right_shoulder.z + left_shoulder.z
                
                # Extra frame analysed so increment count
                count += 1

            # Display the frame
            cv2.imshow("MediaPipe Holistic", frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Store landmark calibration data
        self.landmark_data.OPTIMAL = Coordinate(total_shoulder_x/count, (total_shoulder_y - total_eye_y)/count, total_z/(-4 * count))

        print(self.landmark_data.OPTIMAL)

        return self.landmark_data.OPTIMAL



    def obtain_landmark_data(self, frame) -> Coordinate:
        """
        Populates landmark data store to hold important data from the frame. 
        CALL BEFORE ATTEMPTING TO FIND POSTURE LEVEL.
        
        Args:
            frame (MatLike): Frame to extrapolate data from.

        Return:
            (Coordinate): Top left of head and shoulder - use for drawing box.
        """
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and get the landmarks
        results = self.holistic.process(rgb_frame)

        if results.pose_landmarks:
            # Get coordinates of the left and right shoulders (landmarks 11 and 12)
            left_shoulder = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = results.pose_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_SHOULDER]

            # Get coordinates of the left and right eyes (landmarks 159 and 463)
            left_eye = results.face_landmarks.landmark[mp.solutions.holistic.PoseLandmark.LEFT_EYE]
            right_eye = results.face_landmarks.landmark[mp.solutions.holistic.PoseLandmark.RIGHT_EYE]

            # Convert normalised coordinates to pixel values and store
            height, width, _ = frame.shape

            self.landmark_data.left_shoulder = Coordinate(int(left_shoulder.x * width), int(left_shoulder.y * height), left_shoulder.z)

            self.landmark_data.right_shoulder = Coordinate(int(right_shoulder.x * width), int(right_shoulder.y * height), right_shoulder.z)

            self.landmark_data.right_eye = Coordinate(int(right_eye.x * width), int(right_eye.y * height), right_eye.z)

            self.landmark_data.left_eye = Coordinate(int(left_eye.x * width), int(left_eye.y * height), left_eye.z)

            # Get coordinates for the top of the forehead (landmark 10)
            top_center_forehead = results.face_landmarks.landmark[10]

            # Store top left origin for shape trace in the application
            self.landmark_data.head_top_left = Coordinate(int(right_shoulder.x * width), int(top_center_forehead.y * height), top_center_forehead.z * -1)

            return self.landmark_data.head_top_left
        
    def get_posture_value(self) -> Coordinate:
        """
        Returns a value between 0.0 and 1.0 for how close to the original calibration the posture currently is.

        Return:
            (Coordinate): 0.0 if posture is very good, 1.0 for very bad posture.
                        x denotes shoulder rounding.
                        y denotes neck/back rounding.
                        z denotes distance from the screen (use for normalising).
        """
        # Find how much to scale values by to account for distance from camera
        distance_scalar = (self.landmark_data.left_shoulder.z + self.landmark_data.right_shoulder.z + self.landmark_data.left_eye.z + self.landmark_data.right_eye.z)
        distance_scalar = (distance_scalar / -4)

        # Calculate difference value for height
        height_diff = ((self.landmark_data.left_shoulder.y + self.landmark_data.right_shoulder.y) / 2) - ((self.landmark_data.left_eye.y + self.landmark_data.right_eye.y)) / 2
        # Distance from calibration
        height_diff = self.landmark_data.OPTIMAL.y - height_diff
        # Normalise
        if (height_diff < 0):
            height_diff = 0
        else:
            height_diff = math.tanh((ESTIMATED_CHANGE_PROPORTION/self.landmark_data.OPTIMAL.y) * height_diff)

        # Calculate difference value for shoulder width
        width_diff = self.landmark_data.left_shoulder.x - self.landmark_data.right_shoulder.x
        # Distance from calibration
        width_diff = self.landmark_data.OPTIMAL.x - width_diff
        # Normalise
        if (width_diff < 0):
            width_diff = 0
        else:
            width_diff = math.tanh((ESTIMATED_CHANGE_PROPORTION/self.landmark_data.OPTIMAL.x) * width_diff)

        return Coordinate(width_diff, height_diff, distance_scalar)
"""
    def main(self):
        # Set up the webcam
        cap = cv2.VideoCapture(0)

        self.calibrate(cap)

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)

            self.obtain_landmark_data(frame)

            # Display the frame
            cv2.imshow("MediaPipe Holistic", frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

thing = PostureDetection()
thing.main()
"""