from plyer import notification
import simpleaudio as sa
import keyboard
import time

slouching = False
running = True
timerStart = None
snooze = False

def snoozeToggle() -> bool:
    global snooze, slouching, timerStart
    snooze = not snooze
    print('snooze ' + str(snooze))
    timerStart = time.time() if slouching and not snooze else None

def spacePressed() -> bool:
    global slouching, timerStart
    slouching = not slouching
    print(slouching)
    timerStart = time.time() if slouching else None

def popup() -> None:
    notification.notify(
    title='Here is the title',
    message='I like men',
    )

def playSound() -> None:
    wave_obj = sa.WaveObject.from_wave_file('C:/Users/pickf/Documents/Hackathon/bruh.wav')
    play_obj = wave_obj.play()
    play_obj.wait_done()

def checkSlouching():
    global slouching, timerStart
    if slouching and not snooze:
        if timerStart is None:
            timerStart = time.time()
    
        if time.time() - timerStart >= 10:
            popup()
            playSound()
            slouching = False
            timerStart = None

keyboard.on_press_key('space', lambda e: spacePressed())
keyboard.on_press_key('s', lambda e: snoozeToggle())

while running:
    
    checkSlouching()
    
    if keyboard.is_pressed('esc'):
        running = False