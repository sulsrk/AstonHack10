from plyer import notification
import simpleaudio as sa
import time

SLOUCH_ALLOWANCE_TIME = 4
SLOUCH_REGAIN_TIME = 1

"""
    Toggles a snooze option which turns on and off the notifications regardless of slouching.

    Args:
        snooze (bool): The snooze option to toggle.
        slouching (bool): The current state of slouching.
        timerStart (float): The time the user started slouching.
"""
"""def snoozeToggle() -> None:
    global snooze, slouching, timerStart
    snooze = not snooze
    print('snooze ' + str(snooze))
    timerStart = time.time() if slouching and not snooze else None"""

"""
    Toggles the slouching state of the user and starts a timer if the user is slouching.

    Args:
        slouching (bool): The current state of slouching.
        timerStart (float): The time the user started slouching.
"""
"""def spacePressed() -> None:
    global slouching, timerStart
    slouching = not slouching
    print(slouching)
    timerStart = time.time() if slouching else None"""

# keyboard.on_press_key('space', lambda e: spacePressed())
# keyboard.on_press_key('s', lambda e: snoozeToggle())

class Notify():
    timerEnd = None
    timerEnderEnd = None

    def checkSlouching(self) -> None:
        """
            Checks if the user is slouching and if they are, starts a timer to display a notification after some time.
        """
        if self.timerEnd is None:
            self.timerEnd = time.time() + SLOUCH_ALLOWANCE_TIME
        elif time.time() >= self.timerEnd:
            Notify.popup('Slouch detected!')
            Notify.playSound()
            self.timerStart = None
    
    def endTimer(self) -> None:
        """
            Sets a timer to end the current notification timer after some amount of 'regain' time.
        """
        if self.timerEnd is not None and self.timerEnderEnd is None:
            self.timerEnderEnd = time.time() + SLOUCH_REGAIN_TIME
        elif self.timerEnd is not None and time.time() >= self.timerEnderEnd:
            self.timerEnd = None
            self.timerEnderEnd = None

    def playSound() -> None:
        """
            Plays a sound during the notification when the user is slouching.
        """
        wave_obj = sa.WaveObject.from_wave_file('./alert.wav')
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def popup(display_message) -> None:
        """
            Displays a notification to the user if they are slouching.

            Args:
                display_message (str): The message to display in the notification.
        """
        notification.notify(
        title = 'Slouch Detected',
        message = 'Posture correction recommended',
        )