###############################
#  Imports for reading keyboard
##############################
import sys, os
import termios, fcntl

# used to slow down our main loop
import time

import random
################################
#  Initialize keyboard reading. 
#  Save the old terminal configuration, and
#  tweak the terminal so that it doesn't echo, and doesn't block.
################################
fd = sys.stdin.fileno()
newattr = termios.tcgetattr(fd)

oldterm = termios.tcgetattr(fd)
oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)

newattr[3] = newattr[3] & ~termios.ICANON
newattr[3] = newattr[3] & ~termios.ECHO

fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

termios.tcsetattr(fd, termios.TCSANOW, newattr)

##################################
# Non-blocking character read function.
#################################
def getch_noblock():
  try:
    return sys.stdin.read()
  except (IOError, TypeError) as e:
    return None

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# our led matrix is 64x64.
matrix_size = 64

# the "draw size" for each segment of the worm
sprite_size = 1

# the "draw size" for the apple
apple_size = 7  #apple_size needs to be odd or it will look weird 

options = RGBMatrixOptions()
options.rows = matrix_size 
options.cols = matrix_size 
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)

###################################################
#Creates global data
##############################3#####################
startRange = (matrix_size/4)
wormStartLength = 17
headX = random.randint(matrix_size/2-startRange,matrix_size/2+startRange)
headY = random.randint(matrix_size/2-startRange,matrix_size/2+startRange)

worm = [[headX,headY]]
for i in range(1,wormStartLength):
    worm.append([headX,headY+i])

appleX = 0
appleY = 0
    
worm_color = (255,0,100)
apple_color = (0,255,50)
black = (0,0,0)

# initial score is 0
score = 0
print worm

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
  if show:
    temp_color = apple_color
  else:
    temp_color = black

  temp_image = Image.new("RGB", (apple_size, apple_size))
  temp_draw = ImageDraw.Draw(temp_image)

  appleX = random.randint(matrix_size/2-startRange,matrix_size/2+startRange)
  appleY = random.randint(matrix_size/2-startRange,matrix_size/2+startRange)
 # temp_draw.ellipse((1,2,5,6), outline=temp_color, fill=temp_color)
  temp_draw.ellipse((1,2,apple_size-2,apple_size-1), outline=temp_color, fill=temp_color)
  temp_draw.line(((apple_size+1)/2,0,(apple_size-1)/2,1), fill=worm_color)
 # temp_draw.line((4,0,3,1), fill=worm_color)
 #  temp_draw.point((0,0),fill=worm_color)
  matrix.SetImage(temp_image, appleX, appleY)


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
  if(((passedX >= appleX+2) & (passedX <= appleX+6)) & ((passedY >= appleY+2) & (passedY <= appleY+6))):
    return True
  return False



###################################
# Main loop 
###################################

# player starts in the middle of the screen
show_worm(True)
show_apple(True)

# player starts without motion
current_dir = "up"

print "controls:  i=up, j=left, k=down, l=right, s=stop, q=quit"
while True:
  key = getch_noblock()

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
        delete_tail()
        del worm[-1]
        newX = worm[0][0]
        newY = worm[0][1]-1
        if check_self_collision(newX,newY):
            worm_death()
            break
        if check_apple_collision(newX,newY):
            print "apple hit"
            score=score+1
            show_apple(False)
            sleep(.2)
            show_apple(True)     
        worm.insert(0,[newX,newY])
        show_head()
     else:
        worm_death()
        break
 
  if current_dir == "left":
     # only move the player if there is room to go up.
     if worm[0][0] > 0:
        delete_tail()
        del worm[-1]
        newX = worm[0][0]-1
        newY = worm[0][1]
        if check_self_collision(newX,newY):
            worm_death()
            break
        worm.insert(0,[newX,newY])
        show_head()
     else:
        worm_death()
        break

  if current_dir == "right":
     # only move the player if there is room to go up.
     if worm[0][0] < 63:
        delete_tail()
        del worm[-1]
        newX = worm[0][0]+1
        newY = worm[0][1]
        if check_self_collision(newX,newY):
            worm_death()
            break
        worm.insert(0,[newX,newY])
        show_head()
     else:
         worm_death()
         break

  if current_dir == "down":
     # only move the player if there is room to go up.
     if worm[0][1] < 63:
        delete_tail()
        del worm[-1]
        newX = worm[0][0]
        newY = worm[0][1]+1
        if check_self_collision(newX,newY):
            worm_death()
            break
        worm.insert(0,[newX,newY])
        show_head()
     else:
         worm_death()
         break

    #still need to add death when worm eats itself

    #still need to add apple and add interaction between head of worm and apple

  time.sleep(.1)


###################################
# Show score after While Loop is broken
###################################
temp_image = Image.new("RGB", (64, 64))
temp_draw = ImageDraw.Draw(temp_image)
#temp_draw.point((1,1), fill=(255,0,0))
temp_draw.text((1,1),str(score), fill=(255,0,0))

matrix.SetImage(temp_image,0,0)

time.sleep(1)


###################################
# Reset the terminal on exit
###################################
termios.tcsetattr(fd, termios.TCSANOW, oldterm)

fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
