from plyer import notification
import simpleaudio as sa
import time

SLOUCH_ALLOWANCE_TIME = 4
SLOUCH_REGAIN_TIME = 1

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

    def popup(title) -> None:
        """
            Displays a notification to the user if they are slouching.

            Args:
                display_message (str): The message to display in the notification.
        """
        notification.notify(
        title = title,
        message = 'Posture correction recommended',
        )