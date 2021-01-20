import RPi.GPIO as GPIO
import time
import pygame
import sys
import glob
import os
import random
from rpi_backlight import Backlight
from pygame.mixer  import *
##################################

DEBUG               = False

COLOR_BG            = '#59b9f5'
FPS                 = 25
BUTTONS_COUNT       = 6
MAX_FREQUENCE_STEPS = 10

PLANET_NAME = [
    'Mercury',
    'Venus',
    'Earth',
    'Mars',
    'Jupiter',
    'Saturn',
    'Uranus',
    'Neptune',
    'Kuiper Belt'
    ]

TEXTS = {
    'SCREENSAVER' : "Select a planet and choose your energy to travel.",
    'Mercury': ["No need to use nuclear energy at Mercury, where sunlight is very abundant.","Only small batteries needed for when spacecraft is in the shadow of Mercury.","Solar panels provided all the power needed at Mercury.  In fact, the sun is so powerful that the spacecraft needs to be shielded from sunlight (see Mariner 10 suspended spacecraft and the MESSENGER model)."],
    'Venus': ["Nuclear energy would be needed for a lander lasting more than a few hours, but orbiters can use abundant sunlight for power.","Only small batteries needed for when spacecraft is in the shadow of Venus.", "Solar panels can provided power to Magellan in orbit around Venus, where sunlight is abundant.  Soviet landers used battery power to operate for a couple of hours before the intense heat destroyed the electronics. "],
    'Earth': ["Nuclear energy was used for some military satellites orbiting Earth, but its hazards upon falling to Earth make this a bad option.", "Only small batteries needed for when spacecraft is in the shadow of the Earth.", "Solar panels can provide needed power in orbit at Earth, where sunlight is plentiful."],
    'Mars': ["Nuclear energy was used on the Curiosity rover, allowing it to operate some instruments during the night.  See Curiosity model in Rocky Planets section.", "Good batteries were used on the MER rovers, to keep the spacecraft warm through the cold nights.  See MER model in Rocky Planets section.", "Solar panels provide power to numerous spacecraft while in orbit around Mars, where sunlight is still strong.  The MER rovers used solar panels to operate during the day and to charge batteries for the night.  However, dust build-up on solar panels is a big problem for long-term surface operations on Mars."],
    'Jupiter': ["Nuclear energy was critical to power the Voyager missions to the outer planets.  The Galileo also used decaying nuclear material to power its orbital mission at Jupiter.", "Batteries are needed for when spacecraft is in the shadow of Jupiter or its large moons.", "Huge solar panels powered the Juno orbiter at Jupiter, the only spacecraft so far to use solar panels this far from the sun."],
    'Saturn': ["Nuclear energy was critical to power the Voyager missions to Saturn, as well as the Cassini mission that orbited Saturn for many years.","Batteries are needed for when spacecraft is in the shadow of Saturn or its large moons.","Solar panels could not provide enough electricity to power spacecraft at Saturn or beyond.  Sunlight is not strong enough far from the sun to provide much power."],
    'Uranus': ["Nuclear energy was critical to power the Voyager 2 mission when it flew by Uranus in 1986.","Batteries cannot store enough energy to operate much equipment at great distances from the sun.","Solar panels could not provide enough electricity to power spacecraft at Uranus or beyond.  Sunlight is not strong enough far from the sun to provide much power."],
    'Neptune':["Nuclear energy was critical to power the Voyager 2 mission when it flew by Neptune in 1989.","Batteries cannot store enough energy to operate much equipment at great distances from the sun.","Solar panels could not provide enough electricity to power spacecraft at Neptune or beyond.  Sunlight is not strong enough far from the sun to provide much power."],
    'Kuiper Belt': ["","",""]
}

GRAYCODE_TABLE = [
    '0000',
    '0001',
    '0011',
    '0010',
    '0110',
    '0111',
    '0101',
    '0100',
    '1100',
    '1101',
    '1111',
    '1010',
    '1011',
    '1001',
    '1000'
]

PINS_IN = {
    'Nuclear': 4,
    'Battery': 17,
    'Solar': 27,
    'Nothing': 22,
    'GreyCode_0': 26,
    'GreyCode_1': 18,
    'GreyCode_2': 23,
    'GreyCode_3': 24,
    }

PINS_OUT = {
    'Nuclear': 5,
    'Battery': 6,
    'Solar': 13,
    'Infeasible': 19,
    }

##################################
RUNNING        = False
audiofiles     = []
btnAudioIndies = []
dir            = "/home/pi/Desktop/huettinger"

isOn          = False
pressedPower  = False
pressedPrev   = False
pressedNext   = False
audioIndex    = 0
##################################

def drawText(_screen, _text, _x, _y, _font, _color, _isRight):
    try:
        font = _font
        text = font.render(str(_text), True , _color)
        text_rect = text.get_rect()
        text_rect.top = _y
        if _isRight:
            text_rect.left = _x - text.get_width()
        else:
            text_rect.left = _x
            
        _screen.blit(text, text_rect)
    except Exception as e:
        print('Font Error, saw it coming')
        raise e

def changeAudio(_index):
    if (pygame.mixer.music.get_busy() == True):
        #pygame.mixer.fadeout(250)
        pygame.mixer.music.stop()
        print('stop')
    
    if _index > -1 and _index < len(audiofiles):
        pygame.mixer.music.load(audiofiles[_index])
        pygame.mixer.music.play(-1)
        print('playing')

def changeLight(_index):
    chIndex = 0
    while chIndex < BUTTONS_COUNT:
        chIndex = chIndex + 1
        GPIO.output(PINS_OUT['CH_' + str(chIndex)], 0)
        
    if _index < BUTTONS_COUNT and _index > -1:
        GPIO.output(PINS_OUT['CH_' + str( _index + 1)], 1)      

def setPower(_on):
    Backlight().power = _on
    if _on:
        GPIO.output(PINS_OUT['POWER'], 0)
        audioIndex = 0       
        changeLight(btnAudioIndies[audioIndex])
        changeAudio(audioIndex)
    else:
        GPIO.output(PINS_OUT['POWER'], 1)
        changeLight(-1)
        changeAudio(-1)

def update():
    global start_time
    global isOn
    global pressedPower
    global pressedPrev
    global pressedNext
    global audioIndex
    
    # fills the screen with a color 
    screen.fill(pygame.Color(COLOR_BG))   
    updated_text = time.strftime("Press a button - %M:%S.", time.gmtime())
    screen.blit(img_net, (700,20))
    
    #POWER
    if GPIO.input(PINS_IN['POWER']) and not pressedPower:
        start_time = time.time()
        pressedPower = True
        isOn = not isOn
        setPower(isOn)
        print('Power is ' + str(isOn) )
        if not isOn:
            changeAudio(-1)
    elif not GPIO.input(PINS_IN['POWER']) and pressedPower:
        pressedPower = False
    
    if not isOn:
        return True
    
    #NEXT
    if GPIO.input(PINS_IN['NEXT']) and not pressedPrev:
        pressedPrev = True
        GPIO.output(PINS_OUT['NEXT'], 1)
        audioIndex = audioIndex - 1
                    
        if audioIndex < 0:
            audioIndex = 0
            
        changeLight(btnAudioIndies[audioIndex])
        changeAudio(audioIndex)
        print('audioIndex is ' + str(audioIndex) )
        
    elif not GPIO.input(PINS_IN['NEXT']) and pressedPrev:
        pressedPrev = False
        GPIO.output(PINS_OUT['NEXT'], 0)
    
    #PREV
    if GPIO.input(PINS_IN['PREV']) and not pressedNext:
        pressedNext = True
        GPIO.output(PINS_OUT['PREV'], 1)
        audioIndex = audioIndex + 1
        
        if audioIndex > len(audiofiles) - 1:
            audioIndex = len(audiofiles) - 1
        
        changeLight(btnAudioIndies[audioIndex])
        changeAudio(audioIndex)
        print('audioIndex is ' + str(audioIndex) )
        
    elif not GPIO.input(PINS_IN['PREV']) and pressedNext:
        pressedNext = False
        GPIO.output(PINS_OUT['PREV'], 0)

    for key in PINS_IN:
        if GPIO.input(PINS_IN[key]):        
            if key.find('CH_') > -1:                
                findIndex = 0
                btnIndex = int(key.replace('CH_', '')) - 1;
                print("btnIndex " + str(btnIndex) )
                while findIndex < len(btnAudioIndies):
                    if btnAudioIndies[findIndex] == btnIndex:
                        audioIndex = findIndex
                        break
                    findIndex = findIndex + 1
                    
                changeLight(btnIndex)
                changeAudio(audioIndex)
                
            if DEBUG:
                drawText(screen, 'PIN ' + key, 400, 20, font_1, color_white, False)
        #else:
            #GPIO.output(PINS_OUT[key], 0)
    
    drawText(screen, str(audioIndex), 20, 50, font_1, color_white, False)
    drawText(screen, PLANET_TIME[audioIndex], 680, 50, font_1, color_white, True)
    drawText(screen, SONG_NAME[audioIndex], 20, 140, font_3, color_white, False)
    drawText(screen, INTERPRET_NAME[audioIndex], 20, 280, font_2, color_white, False)
    
    # updates the frames of the game 
    pygame.display.update()

def main():
    global root
    global screen
    global color_white
    global font_1
    global font_2
    global font_3
    global img_black
    global img_net
    global audiofiles
    global btnAudioIndies
    
    time.sleep(1)
    
    audioCount = 0
    files = glob.glob(dir + '/sound/*.wav')
    if len(files) == 0:
        files = glob.glob(dir + '/sound/*.mp3')
  
    for file in files:
        audiofiles.append(file)
        btnAudioIndies.append(audioCount)
        audioCount = audioCount + 1
        print(file)
        
    random.shuffle(audiofiles)
    random.shuffle(btnAudioIndies)

    for fileindex in btnAudioIndies:
        print(fileindex)
        
    for file in audiofiles:
        print(file);
        
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
    pygame.init()
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
    fonts = pygame.font.get_fonts()

    #for f in fonts:
     #   print(f)
    
    screen = pygame.display.set_mode((800, 480), pygame.NOFRAME)
    sysfont = pygame.font.get_default_font()
    #print('system font :', sysfont)
   
    GPIO.setmode(GPIO.BCM)
    
    for key in PINS_IN:
        GPIO.setup(PINS_IN[key], GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    
    for key in PINS_OUT:
        GPIO.setup(PINS_OUT[key], GPIO.OUT)
        GPIO.output(PINS_OUT[key], 0)

    color_white = pygame.Color("#ffffff")
    img_net = pygame.image.load(dir + '/images/network_strength.png')   
    
    font_1 = pygame.font.Font(pygame.font.match_font('Arial', bold=True), 30)
    font_2 = pygame.font.SysFont('Arial', 70)
    font_3 = pygame.font.SysFont(pygame.font.match_font('Arial'), 170)
    
    isOn = False
    setPower(isOn)
  
#####################################################################
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        RUNNING = True
        print("finally")
        #GPIO.cleanup()

def timeout():
    global start_time
    start_time = time.time()
    print("timeout")


start_time = time.time()
timeout_seconds = 60

# main game loop
while RUNNING:
    

    time.sleep(0.1)
    now_time = time.time()
    elapsed_time = now_time - start_time
    #print(elapsed_time)
    if (elapsed_time >= timeout_seconds):
        timeout()

    update()

    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            RUNNING = False
            setPower(True)
            pygame.quit()
            GPIO.cleanup()
            
    pygame.time.Clock().tick(FPS)
#End
