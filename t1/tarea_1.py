from pyglet.window import Window
from pyglet.app import run
from pyglet.shapes import Star, Triangle, Rectangle
from pyglet.graphics import Batch
import numpy.random as nr

#window settings
WIDTH = 1280
HEIGHT = 720
WINDOW_TITTLE = "Tarea 1 - CC3501"
FULLSCREEN = False 
RESIZABLE = False

#window creation
window = Window(WIDTH, HEIGHT, WINDOW_TITTLE, resizable = RESIZABLE)
window.set_fullscreen(FULLSCREEN)

#color pallete
pallete = {
    "white":[255,255,255],
    "light_gray":[150,150,150],
    "dark_gray":[50,50,50],
    "blue":[60,35,130],
    "gray":[210,210,210],
    "background":[10,10,10]
}

#batch for figures
globalBatch = Batch()

#background figure
background = Rectangle(0, 0, window.width, window.height, color = pallete["background"], batch= globalBatch)

#class that stores a figure of a star and defines its behaviour
class Stars:
    #scale = defines the size of the star
    #color = defines the color that the star will have when drawn
    def __init__(self, scale, color):
        self.S = Star(nr.randint(0,window.width),nr.randint(0,window.height * 2), 2+scale, 4+scale,num_spikes= 6, color = pallete[color],batch=globalBatch)

    #a star will only move from top to bottom in the window
    def move(self, multiplier):
        self.S.y -= 1 * multiplier


    def reset(self, multiplier):
        if self.S.y > 0:
            self.move(multiplier)
        else:
            self.S.y = window.height + nr.randint(0,30)
            self.S.x = nr.randint(0,window.width)

#creating stars
frontStars = []
midStars = []
bgStars = []
def createStars(n, q, k):
    for i in range(0, n):
        frontStars.append(Stars(0.8, "white"))
    for t in range(0, q):
        midStars.append(Stars(0.4, "light_gray") )
    for j in range(0, k):
        bgStars.append(Stars(0.2,"dark_gray"))
        
def drawStars(multiplier_front, multiplier_midg, multiplier_bg):
    for k in range(0, len(frontStars)):
        frontStars[k].reset(multiplier_front)
    for p in range(0, len(midStars)):
        midStars[p].reset(multiplier_midg)
    for l in range(0, len(bgStars)):
        bgStars[l].reset(multiplier_bg)

createStars(30, 50, 100) #front to back quantities
   
class Airship:
    def __init__(self, x, y):
        self.r1 = Rectangle(x-8, y-15, 16, 80, color=pallete["gray"], batch=globalBatch)
        self.t1 = Triangle(x-1, y-30, x-1, y+100, x-30, y, color=pallete["gray"], batch=globalBatch) #left side
        self.t2 = Triangle(x+1, y-30, x+1, y+100, x+30, y, color=pallete["gray"], batch=globalBatch) #right side
        self.t3 = Triangle(x-25,y,x-55,y+20,x-100,y-40,color=pallete["gray"],batch=globalBatch) #ala izq
        self.t4 = Triangle(x+25,y,x+55,y+20,x+100,y-40,color=pallete["gray"],batch=globalBatch) #ala der
        self.t5 = Triangle(x+15,y,x+40,y,x+30,y+70,color=pallete["blue"],batch=globalBatch) #top right wing
        self.t6 = Triangle(x+15,y,x+40,y,x+35,y-40,color=pallete["blue"],batch=globalBatch) #bottom right
        self.t7 = Triangle(x-15,y,x-40,y,x-30,y+70,color=pallete["blue"],batch=globalBatch) #top left wing
        self.t8 = Triangle(x-15,y,x-40,y,x-35,y-40,color=pallete["blue"],batch=globalBatch) #bottom left

    
    def list(self):
        return [self.r1, self.t1, self.t2, self.t3, self.t4, self.t5, self.t6, self.t7, self.t8]
    
    
    
    
    def shake(self, multiplier):
        strengh = nr.randint(0,2) * multiplier
        direction = nr.randint(-1,1)
        if direction == 0:
            for i in self.list():
                i.y += strengh
        else:
            for j in self.list():
                j.y -= strengh
                                
#creating the ships
centralAirship = Airship((window.width//2),(window.height//2)-20)
leftAirship = Airship((window.width//2)-300,(window.height//2)-150)
rightAirship = Airship((window.width//2)+300,(window.height//2)-150)
backAirship = Airship((window.width//2),(window.height//2)-220)

shakerMultiplier = 0.6

@window.event
def on_draw():
    #clearing the window before drawing anything
    window.clear()

    globalBatch.draw()
    
    centralAirship.shake(shakerMultiplier)
    leftAirship.shake(shakerMultiplier)
    rightAirship.shake(shakerMultiplier)
    backAirship.shake(shakerMultiplier)

    
    drawStars(4, 2, 1)#front to back velocities

run()