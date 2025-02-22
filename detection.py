import cv2
import mediapipe as mp
import time

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
    def __init__(self, SHOULDER_OPTIMAL=None, EYE_OPTIMAL=None):
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
        self.SHOULDER_OPTIMAL = SHOULDER_OPTIMAL
        self.EYE_OPTIMAL = EYE_OPTIMAL

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
        """
        # Initialise MediaPipe
        mp_drawing = mp.solutions.drawing_utils
        # Sum the heights and widths of shoulders and eyes
        total_shoulder_x = total_shoulder_y = total_eye_x = total_eye_y = total_z = count = 0
        # Timer for 10 seconds 
        end_time = time.time() + 5
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

                total_eye_x += int(left_eye.x * width) - int(right_eye.x * width)
                total_eye_y += (int(right_eye.y * height) + int(left_eye.y * height)) / 2

                # Get total distance away
                total_z += (right_eye.z + left_eye.z + right_shoulder.z + left_shoulder.z) * -10
                
                # Extra frame analysed so increment count
                count += 1

            # Display the frame
            cv2.imshow("MediaPipe Holistic", frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        total_z /= (count*2)
        # Store landmark calibration data
        self.landmark_data.SHOULDER_OPTIMAL = Coordinate(total_shoulder_x/count, total_shoulder_y/count, total_z)
        self.landmark_data.EYE_OPTIMAL = Coordinate(total_eye_x/count, total_eye_y/count, total_z)

        print(self.landmark_data.SHOULDER_OPTIMAL, self.landmark_data.EYE_OPTIMAL)

        return Coordinate(self.landmark_data.SHOULDER_OPTIMAL.x, self.landmark_data.EYE_OPTIMAL.y - self.landmark_data.SHOULDER_OPTIMAL.y, total_z)



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
            self.landmark_data.head_top_left = Coordinate(int(right_shoulder.x * width), int(top_center_forehead.y * height), top_center_forehead.z * -10)

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
        distance_scalar = (self.landmark_data.left_shoulder.z + self.landmark_data.right_shoulder.z + self.landmark_data.left_eye.z + self.landmark_data.right_eye.z) * -10
        distance_scalar = (distance_scalar / 4)

        # Calculate difference value for height
        height_diff = (self.landmark_data.left_shoulder.y + self.landmark_data.right_shoulder.y) / 2
        height_diff = (self.landmark_data.left_eye.y + self.landmark_data.right_eye.y) / 2 - height_diff
        height_diff = height_diff/(self.landmark_data.EYE_OPTIMAL.y - self.landmark_data.SHOULDER_OPTIMAL.y)
        if (height_diff > 1):
            height_diff = 1.0

        # Calculate difference value for shoulder width
        width_diff = self.landmark_data.right_shoulder.x - self.landmark_data.left_shoulder.x
        width_diff = width_diff/self.landmark_data.SHOULDER_OPTIMAL.x
        if (width_diff > 1):
            width_diff = 1.0

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