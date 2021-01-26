import RPi.GPIO as GPIO
import time
import pygame

##################################

DEBUG               = False
COLOR_BG            = '#ffffff'
FPS                 = 25

##################################
RUNNING        = False
global start_time
global last_grayCode
##################################

PINS_IN         = [4, 17, 27, 22]
PINS_OUT        = [ 5, 6, 13, 19]
BUTTON_NAMES    = ['Nuclear', 'Battery', 'Solar', 'Infeasible']
GRAYCODE_PINS   = [25, 18, 23, 24]

PLANET_NAME = [
    'Sun'
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

def changeLight(_index):
    chIndex = 0
    while chIndex < len(PINS_OUT):
        GPIO.output(PINS_OUT[chIndex], 0)
        chIndex = chIndex + 1
        
    if _index < len(PINS_OUT) and _index > -1:
        GPIO.output(PINS_OUT[_index], 1)          

def turnOnAllLights():
    for pin in PINS_OUT:
        GPIO.output(pin, 1)

def update():
    global start_time
    global last_grayCode
    
    
    # fills the screen with a color 
    screen.fill(pygame.Color(COLOR_BG))   
    updated_text = time.strftime("Press a button - %M:%S.", time.gmtime())
    #screen.blit(img_net, (700,20))
    
    graycode = []
    for i in range(len(GRAYCODE_PINS)):
        if GPIO.input[GRAYCODE_PINS[i]]:
            graycode[i] = 1
        else:
            graycode[i] = 0
    print("GRAYCODE :")
    print(*graycode)
    if last_grayCode != graycode:
        last_grayCode = graycode
        start_time = time.time()
    else:
        print("same graycode")

    text_arr= []
    for ind in range(len(GRAYCODE_TABLE)):
        if (GRAYCODE_TABLE[ind] == str(graycode)):
            print(ind)
            print(PLANET_NAME[ind]) 
            text_arr =  TEXTS[PLANET_NAME[ind]]

    turnOnAllLights()

    text = TEXTS['SCREENSAVER']
    #Buttons
    for i in range(len(PINS_IN)):
        if GPIO.input(PINS_IN[i]):
            print(BUTTON_NAMES[i])
            print(text_arr[i])
            text = text_arr[i]
            changeLight(i)


    drawText(screen, text, 400, 20, font, color_black, False)

    
    pygame.display.update()

def main():
    global screen
    global color_black
    global font
    global img_net

    time.sleep(1)
        
    pygame.init()
    pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

    screen = pygame.display.set_mode((800, 480), pygame.NOFRAME)
    #print('system font :', sysfont)
   
    GPIO.setmode(GPIO.BCM)
    

    for pin in PINS_IN:
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    
    for pin in GRAYCODE_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    for pin in PINS_OUT:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    color_black = pygame.Color("#000000")
    img_net = pygame.image.load(dir + '/images/network_strength.png')   
    
    font = pygame.font.Font(pygame.font.match_font('FS ALdrin'), 16)
    
  
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
last_grayCode = ""

# main game loop
while RUNNING:
    
    update()

    time.sleep(0.1)
    now_time = time.time()
    elapsed_time = now_time - start_time
    #print(elapsed_time)
    if (elapsed_time >= timeout_seconds):
        timeout()


    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            RUNNING = False
            pygame.quit()
            GPIO.cleanup()
            
    pygame.time.Clock().tick(FPS)
#End
