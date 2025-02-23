from plyer import notification
import simpleaudio as sa
import keyboard
import time

SLOUCH_ALLOWANCE_TIME = 2
slouching = True
running = True
timerStart = None
snooze = False

"""
    Toggles a snooze option which turns on and off the notifications regardless of slouching.

    Args:
        snooze (bool): The snooze option to toggle.
        slouching (bool): The current state of slouching.
        timerStart (float): The time the user started slouching.
"""
def snoozeToggle() -> None:
    global snooze, slouching, timerStart
    snooze = not snooze
    print('snooze ' + str(snooze))
    timerStart = time.time() if slouching and not snooze else None

"""
    Toggles the slouching state of the user and starts a timer if the user is slouching.

    Args:
        slouching (bool): The current state of slouching.
        timerStart (float): The time the user started slouching.
"""
def spacePressed() -> None:
    global slouching, timerStart
    slouching = not slouching
    print(slouching)
    timerStart = time.time() if slouching else None

# keyboard.on_press_key('space', lambda e: spacePressed())
# keyboard.on_press_key('s', lambda e: snoozeToggle())

class Notify():
    timerStart = None

    def checkSlouching(self) -> None:
        """
        Checks if the user is slouching and if they are, starts a timer to display a notification after 10 seconds.
        
        Args:
            slouching (bool): The current state of slouching.
            snooze (bool): The current state of snooze.
            timerStart (float): The time the user started slouching.
        """
        if self.timerStart is None:
            self.timerStart = time.time()
        elif time.time() - timerStart >= SLOUCH_ALLOWANCE_TIME:
            Notify.popup()
            Notify.playSound()
            self.timerStart = None
            print("STOP SLOUCHING")

    def playSound() -> None:
        """
        Plays a sound during the notification when the user is slouching.
        """
        wave_obj = sa.WaveObject.from_wave_file('./bruh.wav')
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def popup(display_message) -> None:
        """
        Displays a notification to the user if they are slouching.

        Args:
            display_message (str): The message to display in the notification.
        """
        notification.notify(
        title='FIX UP',
        message="STOP SLOUCHING BOMBACLAT",
        )