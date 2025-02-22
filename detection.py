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
            SHOULDER_OPTIMAL (Coordinate): Optimal shoulder values to compare against (where x=width between shoulders, y=average height, z=z)
            EYE_OPTIMAL (Coordinate): Optimal eye values to compare against (where x=width between eyes, y=average height, z=z)
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

    def __init__(self):
        # Create an empty store of important landmark data
        self.landmark_data = LandmarkData()

    def calibrate(self, cap):
        """
        Calibrates the display to find initial 'optimal' positions for the shoulders and eyes for good posture.
        
        Args:
            cap (VideoCapture): Object currently streaming and capturing video from user.
        """
        # Initialise MediaPipe
        mp_drawing = mp.solutions.drawing_utils
        # Sum the heights and widths of shoulders and eyes
        total_shoulder_x = total_shoulder_y = total_eye_x = total_eye_y = count = 0
        # Timer for 10 seconds 
        end_time = time.time() + 5
        while (cap.isOpened() and time.time() < end_time):
            ret, frame = cap.read()

            if not ret:
                break

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)

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
                total_shoulder_x += int(right_shoulder.x * width) - int(left_shoulder.x * width)
                total_shoulder_y += (int(right_shoulder.y * height) + int(left_shoulder.y * height)) / 2

                total_eye_x += int(right_eye.x * width) - int(left_eye.x * width)
                total_eye_y += (int(right_eye.y * height) + int(left_eye.y * height)) / 2
                
                # Extra frame analysed so increment count
                count += 1

            # Display the frame
            cv2.imshow("MediaPipe Holistic", frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.landmark_data.SHOULDER_OPTIMAL = Coordinate(total_shoulder_x/count, total_shoulder_y/count)
        self.landmark_data.EYE_OPTIMAL = Coordinate(total_eye_x/count, total_eye_y/count)

        print(self.landmark_data.SHOULDER_OPTIMAL, self.landmark_data.EYE_OPTIMAL)



    def obtain_landmark_data(self, frame) -> None:
        """
        Populates landmark data store to hold important data from the frame. 
        CALL BEFORE ATTEMPTING TO FIND POSTURE LEVEL.
        
        Args:
            frame (MatLike): Frame to extrapolate data from.
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

            # Get coordinates for the top of the forehead (landmark 1)
            top_center_forehead = results.face_landmarks.landmark[1]

            # Store top left origin for shape trace in the application
            self.landmark_data.head_top_left = Coordinate(int(left_shoulder.x * width), int(top_center_forehead.y * height))

            return self.landmark_data.head_top_left
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