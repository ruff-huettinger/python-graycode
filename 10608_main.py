import RPi.GPIO as GPIO
import time
import pygame

DEBUG = True

COLOR_BG = '#ffffff'
FPS = 25

PLANET_NAME = [
    'Sun',
    'Mercury',
    'Venus',
    'Earth',
    'Mars',
    'Jupiter',
    'Saturn',
    'Uranus',
    'Neptune',
    'Kuiper Belt',
    'Space'
]

TEXTS = {
    'SCREENSAVER' : "Select a planet and choose your energy to travel.",
    'Sun': ["Select a planet and choose your energy to travel.","Select a planet and choose your energy to travel.","Select a planet and choose your energy to travel."],
    'Mercury': ["No need to use nuclear energy at Mercury, where sunlight is very abundant.","Only small batteries needed for when spacecraft is in the shadow of Mercury.","Solar panels provided all the power needed at Mercury. In fact, the sun is so powerful that the spacecraft needs to be shielded from sunlight (see Mariner 10 suspended spacecraft and the MESSENGER model)."],
    'Venus': ["Nuclear energy would be needed for a lander lasting more than a few hours, but orbiters can use abundant sunlight for power.","Only small batteries needed for when spacecraft is in the shadow of Venus.", "Solar panels can provided power to Magellan in orbit around Venus, where sunlight is abundant.  Soviet landers used battery power to operate for a couple of hours before the intense heat destroyed the electronics. "],
    'Earth': ["Nuclear energy was used for some military satellites orbiting Earth, but its hazards upon falling to Earth make this a bad option.", "Only small batteries needed for when spacecraft is in the shadow of the Earth.", "Solar panels can provide needed power in orbit at Earth, where sunlight is plentiful."],
    'Mars': ["Nuclear energy was used on the Curiosity rover, allowing it to operate some instruments during the night.  See Curiosity model in Rocky Planets section.", "Good batteries were used on the MER rovers, to keep the spacecraft warm through the cold nights.  See MER model in Rocky Planets section.", "Solar panels provide power to numerous spacecraft while in orbit around Mars, where sunlight is still strong.  The MER rovers used solar panels to operate during the day and to charge batteries for the night.  However, dust build-up on solar panels is a big problem for long-term surface operations on Mars."],
    'Jupiter': ["Nuclear energy was critical to power the Voyager missions to the outer planets.  The Galileo also used decaying nuclear material to power its orbital mission at Jupiter.", "Batteries are needed for when spacecraft is in the shadow of Jupiter or its large moons.", "Huge solar panels powered the Juno orbiter at Jupiter, the only spacecraft so far to use solar panels this far from the sun."],
    'Saturn': ["Nuclear energy was critical to power the Voyager missions to Saturn, as well as the Cassini mission that orbited Saturn for many years.","Batteries are needed for when spacecraft is in the shadow of Saturn or its large moons.","Solar panels could not provide enough electricity to power spacecraft at Saturn or beyond.  Sunlight is not strong enough far from the sun to provide much power."],
    'Uranus': ["Nuclear energy was critical to power the Voyager 2 mission when it flew by Uranus in 1986.","Batteries cannot store enough energy to operate much equipment at great distances from the sun.","Solar panels could not provide enough electricity to power spacecraft at Uranus or beyond.  Sunlight is not strong enough far from the sun to provide much power."],
    'Neptune':["Nuclear energy was critical to power the Voyager 2 mission when it flew by Neptune in 1989.","Batteries cannot store enough energy to operate much equipment at great distances from the sun.","Solar panels could not provide enough electricity to power spacecraft at Neptune or beyond.  Sunlight is not strong enough far from the sun to provide much power."],
    'Kuiper Belt': ["Select a planet and choose your energy to travel.","Select a planet and choose your energy to travel.","Select a planet and choose your energy to travel."],
    'Space': ["Select a planet and choose your energy to travel.","Select a planet and choose your energy to travel.","Select a planet and choose your energy to travel."]
}

PLANET_LIGHT = {
	'Sun': ["out","out","out"],
    'Mercury': ["red","green","green"],
    'Venus': ["green","green","green"],
    'Earth': ["red","green","green"],
    'Mars': ["green","green","green"],
    'Jupiter': ["green","green","green"],
    'Saturn': ["green","green","red"],
    'Uranus': ["green","red","red"],
    'Neptune':["green","red","red"],
    'Kuiper Belt': ["red","green","green"],
    'Space': ["out","out","out"]
}

GRAYCODE_TABLE = [
    '0000',
    '1000',
    '1001',
    '0001',
    '0011',
    '1011',
    '1010',
    '0010',
    '0110',
    '1110',
    '1111',
]

BUTTON_NAMES    = ['NUCLEAR', 'BATTERY', 'SOLAR', 'INFEASIBLE']
BUTTON_PINS_IN  = [ 4, 17, 27, 22]
BUTTON_PINS_OUT = [ 5,  6, 13, 19, 26]
GRAYCODE_PINS = [25, 18, 23, 24]

##################################
RUNNING        = False
global start_time
global last_grayCode
global timeoutRunning

timeoutRunning = True
start_time = time.time()
last_grayCode = '0000'
##################################

def drawTextBox(surface, text, color, rect, font, aa=False, bkg=None):
	rect = pygame.Rect(rect)
	y = rect.top
	lineSpacing = 0
	
	#get height of font
	fontHeight = font.size("Tg")[1]
	
	while text:
		i=1
		
		#determine if text will be outside area
		if y + fontHeight > rect.bottom:
			break
		#determine max width of line
		while font.size(text[:i])[0] < rect.width and i < len(text):
			i += 1
			
		#if we wrapped text, then adjust the wrap to last word
		if i < len(text):
			i = text.rfind(" ", 0, i) + 1
		#render line and blit to surface
		if bkg:
			image = font.render(text[:i], 1, color, bkg)
			image.set_colorkey(bkg)
		else:
			image = font.render(text[:i], aa, color)
			
		surface.blit(image, (rect.left, y))
		y += fontHeight + lineSpacing
		
		#remove text we blittered
		text = text[i:]
	return text

def drawText(_screen, _text, _x, _y, _font, _color, _isRight):
	try:
		font = _font
		#print(wrapline(_text,font,120))
		text = font.render(str(_text), True, _color)
		text_rect = text.get_rect()
		text_rect.top = _y
		if _isRight:
			text_rect.left = _x -text.get_width()
		else:
			text_rect.left = _x
			
		_screen.blit(text, text_rect)
	except Exception as e:
		print('Font Error')
		raise e

def changeLight(_index):
    chIndex = 0
    while chIndex < len(BUTTON_PINS_OUT):
        GPIO.output(BUTTON_PINS_OUT[chIndex], 0)
        chIndex = chIndex + 1
        
    if _index < len(BUTTON_PINS_OUT) and _index > -1:
        GPIO.output(BUTTON_PINS_OUT[_index], 1)          

def turnAllLights(onoff):
    for pin in BUTTON_PINS_OUT:
        GPIO.output(pin, onoff)
    GPIO.output(BUTTON_PINS_OUT[3], 0)
    GPIO.output(BUTTON_PINS_OUT[4], 0)

def blinkLights():
	global timeoutRunning
	if (timeoutRunning):
		print("blink")
		time.sleep(0.5)
		turnAllLights(0)
		time.sleep(0.5)
		turnAllLights(1)

def init():
	global screen
	global font
	
	pygame.init()
	pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
	screen = pygame.display.set_mode((800,480), pygame.NOFRAME)
	
	font = pygame.font.Font(pygame.font.match_font('FS Aldrin'), 32)
	
	GPIO.setmode(GPIO.BCM)
	
	for pin in BUTTON_PINS_IN:
		GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	
	for pin in GRAYCODE_PINS:
		GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	
	for pin in BUTTON_PINS_OUT:
		print(pin)
		#print(GPIO.RPI_INFO)
		GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
		print(GPIO.input(pin))
		#GPIO.output(pin, 1)


def makeGrayCodeString(arr):
	str1 = ""
	for ele in arr:
		str1 += str(ele)
	return str1

def findChosenPlanet(_str):
	str_planet = 'Space'
	for ind in range(len(GRAYCODE_TABLE)):
		if GRAYCODE_TABLE[ind] == _str:
			#print(ind)
			str_planet = str(PLANET_NAME[ind])
	return str_planet

def findCorrectText(pl, _txts, _lights):
	_txt = TEXTS['SCREENSAVER']
	for i in range(len(BUTTON_PINS_IN)):
		if GPIO.input(BUTTON_PINS_IN[i]):
			_txt = _txts[i]
			if (_lights[i] == "red"):
				changeLight(3)
			elif (_lights[i] == "green"):
				changeLight(4)
			else:
				turnAllLights(0)
	return _txt

def timeout():
	global start_time
	global timeoutRunning
	timeout_seconds = 5
	
	now_time = time.time()
	elapsed_time = now_time - start_time
	
	if (elapsed_time >= timeout_seconds):
		start_time = time.time()
		timeoutRunning = True
		print("timeout")
	else:
		timeoutRunning = False

def update():
	global start_time
	global last_grayCode
    
	screen.fill(pygame.Color(COLOR_BG))
	
	graycode = [0,0,0,0]
	for i in range(len(BUTTON_NAMES)):
		#drawText(screen, BUTTON_NAMES[i], 200, 20+i*10, font, pygame.Color("#ffffff"), False)
		#drawText(screen, "GREYCODE " +str(i), 200, 300+i*10, font, pygame.Color("#ffffff"), False)
		
		if GPIO.input(BUTTON_PINS_IN[i]):
			#print(BUTTON_NAMES[i])
			start_time = time.time()
			#turnAllLights(0)
			drawText(screen, BUTTON_NAMES[i] + str(BUTTON_PINS_IN[i]), 400, 20+i*10, font, pygame.Color("#ffffff"), False)
			changeLight(i)

		if GPIO.input(GRAYCODE_PINS[i]):
			#drawText(screen, "GREYCODE " + str(GRAYCODE_PINS[i]), 400, 300+i*10, font, pygame.Color("#ffffff"), False)
			graycode[i] = 1
			
        if not GPIO.input(GRAYCODE_PINS[i]):
            graycode[i] = 0
            
	str_graycode = makeGrayCodeString(graycode)
	#drawText(screen, "GREYCODE " + str(graycode), 400, 400, font, pygame.Color("#ffffff"), False)
	
	#print(str_graycode)
	planettext = TEXTS["SCREENSAVER"]
	if str_graycode != last_grayCode:
		last_grayCode = str_graycode
	# maybe ask for last graycode
	else:
		#print(str_graycode)
		planet = findChosenPlanet(str_graycode)
		if (planet == "Kuiper Belt" or planet == "Sun" or planet == "Space"):
			turnAllLights(0)
		else:
			turnAllLights(1)
		text_arr = TEXTS[planet]
		light_arr = PLANET_LIGHT[planet]
		
		drawText(screen, "PLANET "+ planet, 50, 100, font, pygame.Color("#000000"), False)
		planettext = findCorrectText(planet, text_arr, light_arr)
    	#drawText(screen, planettext, 50, 150, font, pygame.Color("#ffffff"), False)
    	textbox = pygame.Rect(50,150, 500, 100)
    	drawTextBox(screen, planettext, pygame.Color("#000000"), textbox, font, True)
    	
	pygame.display.update()
	
if __name__ == '__main__':
	try:
		init()
	except KeyboardInterrupt:
		pass
	finally: 
		RUNNING = True
		print("finally")


while RUNNING:
	update()
	timeout()
	blinkLights()
	
	for event in pygame.event.get():
		if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			RUNNING = False
			pygame.quit()
			GPIO.cleanup()
	pygame.time.Clock().tick(FPS)

