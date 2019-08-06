###############################
#  Imports for reading keyboard
##############################
import sys, os
import termios, fcntl

# used to slow down our main loop
import time

import random

from evdev import InputDevice, categorize, ecodes

gamepad = InputDevice('/dev/input/event1')

#add error checking here to make sure we've got an input device...

d_up = 544
d_down = 545
d_left = 546
d_right = 547

def get_dir():
  
  global gamepad
  global d_up
  global d_down
  global d_left
  global d_right

  # Note:  I'm currently doing an extra map to [ijkl], because that's the old input
  # that the game expected.  May be better to eventually change this to the dir, but this 
  # way I don't have to re-write the mapping in the main loop
  ''' OLD
  for event in gamepad.read_loop():
    if event.type ==ecodes.EV_KEY:
      if event.value == 1:
        if event.code == d_up:
          print("UP")
          return "i"
        elif event.code == d_down:
          print("DOWN")
          return "k"
        elif event.code == d_left:
          print("LEFT")
          return "j"
        elif event.code == d_right: 
          print("RIGHT")
          return "l"
        else:
          return "No input"
   
  NEW: 
  '''

  event = gamepad.read_one()
  if event == None:
     return "NoInput"

  if event.type ==ecodes.EV_KEY:
    if event.value == 1:
        if event.code == d_up:
          print("UP")
          return "i"
        elif event.code == d_down:
          print("DOWN")
          return "k"
        elif event.code == d_left:
          print("LEFT")
          return "j"
        elif event.code == d_right: 
          print("RIGHT")
          return "l"
        else:
          return "ERROR in get_dir()"
   

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# this is the size of ONE of our matrixes. 
matrix_rows = 64 
matrix_columns = 64 

# how many matrixes stacked horizontally and vertically 
matrix_horizontal = 1 
matrix_vertical = 1

matrix_size = 64

total_rows = matrix_rows * matrix_vertical
total_columns = matrix_columns * matrix_horizontal

options = RGBMatrixOptions()
options.rows = matrix_rows 
options.cols = matrix_columns 
options.chain_length = matrix_horizontal
options.parallel = matrix_vertical 

#options.hardware_mapping = 'adafruit-hat-pwm' 
#options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.hardware_mapping = 'regular'  

options.gpio_slowdown = 2

matrix = RGBMatrix(options = options)

sprite_size = 1

# the "draw size" for the apple
apple_size = 7  #apple_size needs to be odd or it will look weird 

###################################################
#Creates global data
##############################3#####################
startRange = (matrix_size/4)
wormStartLength = 10
headX = random.randint(matrix_size/2-startRange,matrix_size/2+startRange)
headY = random.randint(matrix_size/2-startRange,matrix_size/2+startRange)

worm = [[headX,headY]]
for i in range(1,wormStartLength):
    worm.append([headX,headY+i])

appleX = 0
appleY = 0
    
worm_color = (255,0,100)
apple_color = (0,255,50)
stem_color = (146,98,13)
black = (0,0,0)

# initial score is 0
score = 0

# initial speed is set with a delay between moving of .1
speed_delay = .14
#print worm

###################################################
# show_worm
################################################### 
def show_worm(show):
  if show:
    temp_color = worm_color
  else:
    temp_color = black

  temp_image = Image.new("RGB", (sprite_size, sprite_size))
  temp_draw = ImageDraw.Draw(temp_image)

  # Start with a worm as an list of x,y coordinates.
  temp_draw.rectangle((0,0,sprite_size-1,sprite_size-1), outline=temp_color, fill=temp_color)
  for segment in worm:
    matrix.SetImage(temp_image, segment[0],segment[1])

####################################################
# show_head
####################################################
def show_head(): 
  worm_color= (255,0,100)
  temp_image = Image.new("RGB", (sprite_size, sprite_size))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,sprite_size-1,sprite_size-1), outline=worm_color, fill=worm_color)
  matrix.SetImage(temp_image, worm[0][0],worm[0][1])

####################################################
# delete_tail
####################################################
def delete_tail(): 
  worm_color = (0,0,0)  
  temp_image = Image.new("RGB", (sprite_size,sprite_size))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.rectangle((0,0,sprite_size-1,sprite_size-1), outline=black, fill=black)
  matrix.SetImage(temp_image, worm[-1][0],worm[-1][1])


####################################################
# worm_death
####################################################
def worm_death():
  #hide worm
  show_worm(False)  
  
  #animate worm explosion  
  death_color = (255,0,0)
  death_fill = (255,255,255)
  for deathloop in range(3,13,2):
    ellipse_offset = (deathloop-1)/2
    temp_image = Image.new("RGB", (deathloop,deathloop))
    temp_draw = ImageDraw.Draw(temp_image)
    temp_draw.ellipse((0,0,deathloop-1,deathloop-1), outline=death_color, fill=death_fill)
    matrix.SetImage(temp_image, worm[0][0]-ellipse_offset,worm[0][1]-ellipse_offset)
    time.sleep(.1)


####################################################
# show_apple
####################################################
def show_apple(show):
  global appleX
  global appleY
  if show:
    temp_color = apple_color
    temp_color_stem = stem_color
    appleX = random.randint(matrix_size/2-startRange,matrix_size/2+startRange)
    appleY = random.randint(matrix_size/2-startRange,matrix_size/2+startRange)
  
  else:
    temp_color = black
    temp_color_stem = black

  temp_image = Image.new("RGB", (apple_size, apple_size))
  temp_draw = ImageDraw.Draw(temp_image)
  temp_draw.ellipse((1,2,apple_size-2,apple_size-1), outline=temp_color, fill=temp_color)
  temp_draw.line(((apple_size+1)/2,0,(apple_size-1)/2,1), fill=temp_color_stem)
  matrix.SetImage(temp_image, appleX, appleY)


# temp_draw.line((4,0,3,1), fill=worm_color)
# temp_draw.point((0,0),fill=worm_color)


#######################################################
# check_self_collision
#######################################################
def check_self_collision(passedX, passedY):
  for segment in worm:
    if(segment[0] == passedX) & (segment[1] == passedY):
      return True
  return False

#######################################################
# check_apple_collision
#######################################################
def check_apple_collision(passedX, passedY):
  global wormStartLength
  global speed_delay
  global score
  for segment in worm:
    if(((passedX >= appleX+1) & (passedX <= appleX+5)) & ((passedY >= appleY+2) & (passedY <= appleY+6))):
      wormStartLength= wormStartLength + 1
      score = score + 1
      show_score()
      speed_delay = speed_delay*.9
      return True
  return False

#########################################################
# Print Updates to Terminal
########################################################
def print_updates():
  print "apples hit=", score, "wormLength =", wormStartLength, "speed_delay =", speed_delay

###################################
# show_Score Show score after While Loop is broken
###################################
def show_score():
    global score
    temp_image = Image.new("RGB", (24, 12))
    temp_draw = ImageDraw.Draw(temp_image)
#temp_draw.point((1,1), fill=(255,0,0))
    temp_draw.text((0,0),str(score), fill=(255,0,0))
    matrix.SetImage(temp_image,3,0)





###################################
# Main loop 
###################################

# player starts in the middle of the screen
show_worm(True)
show_apple(True)
show_score()
# player starts going up 
current_dir = "up"

print "use ps3 controller to move snake"
while True:
  key = get_dir()
 # show_score()
  if key == 'q':
     break    
  if (key == 'i') & (current_dir != "down"):
    current_dir = "up" 
  if (key == 'k') & (current_dir != "up"):
    current_dir = "down" 
  if (key == 'j') & (current_dir != "right"):
    current_dir = "left" 
  if (key == 'l') & (current_dir != "left"):
    current_dir = "right" 
  if key == 's':
    current_dir = "stop"

  if current_dir == "up":
     # only move the player if there is room to go up.
     if worm[0][1] > 0:
        newX = worm[0][0]
        newY = worm[0][1]-1
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print_updates()
            show_apple(False)
            show_worm(True)
            show_apple(True)     
        else:
            delete_tail()
            del worm[-1]

        worm.insert(0,[newX,newY])

        show_head()
     else:
        worm_death()
        break
 
  if current_dir == "left":
     # only move the player if there is room to go up.
     if worm[0][0] > 0:
        newX = worm[0][0]-1
        newY = worm[0][1]
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print_updates()
            show_apple(False)
            show_worm(True)
            show_apple(True)     
        else:
            delete_tail()
            del worm[-1]

        worm.insert(0,[newX,newY])

        show_head()
     else:
        worm_death()
        break

  if current_dir == "right":
     # only move the player if there is room to go up.
     if worm[0][0] < 63:
        newX = worm[0][0]+1
        newY = worm[0][1]
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print_updates()
            show_apple(False)
            show_worm(True)
            show_apple(True)     
        else:
            delete_tail()
            del worm[-1]

        worm.insert(0,[newX,newY])

        show_head()
     else:
        worm_death()
        break

  if current_dir == "down":
     # only move the player if there is room to go up.
     if worm[0][1] < 63:
        newX = worm[0][0]
        newY = worm[0][1]+1
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print_updates()
            show_apple(False)
            show_worm(True)
            show_apple(True)     
        else:
            delete_tail()
            del worm[-1]

        worm.insert(0,[newX,newY])

        show_head()
     else:
        worm_death()
        break

  time.sleep(speed_delay)

show_score()
time.sleep(2)

