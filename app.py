import cv2
from detection import PostureDetection, Coordinate

# Open the default camera
cam = cv2.VideoCapture(0)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

BOX_THICKNESS: int = 5
TEXT_THICKNESS: int = 3

running: bool = True
head_width: int = 640
head_height: int = 700

current_head_x: int = 640
current_head_y: int = 200

posture_value: float = 0.9

def colour_gradient(posture_value: int) -> tuple:
    """
        Calculates the approrpiate green -> red colour gradient depending on the posture value.

        Args:
            posture_value (int): The posture value for the current frame.

        Returns:
            tuple: The (B,G,R) colour value as a gradient from green -> red calculated off of the posture value.

        Raises:
            ValueError: If posture_value is negative or greater than 1.
    """
    if posture_value < 0 or posture_value > 1:
        raise ValueError("posture_value must be between 0 and 1 inclusive")
    if posture_value <= 0.5:
        return (0, 255, 255 * (posture_value / 0.5)) # Green -> Yellow
    else:
        return (0, 255 * (1 - ((posture_value - 0.5) / 0.5)), 255) # Yellow -> Red
    
def display_message(posture_value: int) -> str:
    """
        Displays the appropriate message from their current posture. 

        Args:
            posture_value (int): The posture value for the current frame.

        Returns: 
            str: The appropriate message corresponding with the current posture value.

        Raises:
            ValueError: If posture_value is negative or greater than 1.
    """
    if posture_value < 0 or posture_value > 1:
        raise ValueError("posture_value must be between 0 and 1 inclusive")
    if posture_value <= 0.33:
        return "Good Posture"
    elif posture_value <= 0.66:
        return "OK Posture"
    else:
        return "Bad Posture"

def draw_box(posture_value, frame, current_head_x, current_head_y, head_width, head_height) -> None:
    """
        Draws the box around the head with the approriate colour and message depending on their posture.

        Args:
            posture_value (int): The posture value for the current frame. 
            frame (MatLike): The current frame being captured.
            current_head_x (int): The current x-coordinate of the head (top left).
            current_head_y (int): The current y-coordinate of the head (top left).
            head_width (int): The width of the head after calibration.
            head_height (int): The height of the head after calibration.
    """
    colour = colour_gradient(posture_value)

    # Draws the box around the head for each frame 
    box = cv2.rectangle(frame, (current_head_x, current_head_y), (current_head_x + head_width, current_head_y + head_height), colour, BOX_THICKNESS)
    
    # Displays the message under the box
    cv2.putText(box, display_message(posture_value), (current_head_x + head_width, current_head_y + head_height + 30), 1, 2.5, colour, TEXT_THICKNESS)

posture = PostureDetection()

# Calculations and displays while camera is running
while running:
    ret, frame = cam.read()
    frame = cv2.flip(frame, 1)
    current_pos = posture.obtain_landmark_data(frame)

    if current_pos != None:
        draw_box(posture_value, frame, current_pos.x, current_pos.y, head_width, head_height)

    # Display the captured frame
    cv2.imshow('Posture Corrector 3000', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        running = False

# Release the capture objects
cam.release()
cv2.destroyAllWindows()