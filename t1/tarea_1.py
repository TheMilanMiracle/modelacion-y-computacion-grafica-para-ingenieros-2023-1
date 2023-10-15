from pyglet.window import Window
from pyglet.app import run
from pyglet.shapes import Star, Triangle, Rectangle
from pyglet.graphics import Batch
from random import randrange, randint
from numpy import sin

############# WINDOW #############
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


############# BACKGROUND ############# 
#batch for figures
globalBatch = Batch()

#background figure
background = Rectangle(0, 0, window.width, window.height, color = pallete["background"], batch= globalBatch)


############# STARS #############
#class for stars
class StarShape:
    """
    A class to represent a star figure and its behaviour
    
    Attributes
    ----------
    shape : pyglet.shape.Star
        the pyglet shape of a star
        
    Methods
    -------
    update(multiplier)
        updates the position of the shape of the star from top to bottom,
        moving it back to the top when going off bottom limit
    """
    
    def __init__(self, scale, color):
        """
        Parameters
        ----------
        scale : float
            defines how big the star shape will be
        color : str
            name of the color for the star, this string has to be a key from the color pallete 
        """
        
        self.shape = Star(randrange(0,window.width),randrange(0,window.height * 2), 2+scale, 4+scale,num_spikes= 6, color = pallete[color],batch=globalBatch)

    def update(self, multiplier):
        """
        Parameters
        ----------
        multiplier : float
            defines how fast the shape will move
        """
        
        #if the star still on screen it keeps going down
        if self.shape.y > 0:
            self.shape.y -= 1 * multiplier
        else:#if it is out of borders it goes back to the top in a random x position
            self.shape.y = window.height + randrange(0, window.width)


#in order to create a parallax effect the stars will be grouped in 3 (lists) layers,
#each one with a different size, speed, and quantity associated
frontN = 30
frontSpeed = 4.5
frontStars = [StarShape(0.8, "white") for i in range(frontN)]
midN = 50
midSpeed = 2.5
midStars = [StarShape(0.4, "light_gray") for i in range(midN)]
backN = 100
backSpeed = 1.5
backStars = [StarShape(0.2, "dark_gray") for i in range(backN)]


def updateStars():
    """
    Function that iterates the (lists) layers of stars, calling to update their positions
    """
    
    for f in range(frontN):
        frontStars[f].update(frontSpeed)
    for m in range(midN):
        midStars[m].update(midSpeed)
    for b in range(backN):
        backStars[b].update(backSpeed)


############# AIRSHIPS #############
class Airship:
    """
    A class to represent the composed figure of an airship and its behaviour
    
    Attributes
    ----------
    r1 : pyglet.shape.Rectangle
        the pyglet shape of a rectangle, representing the back of the airship
    t1 : pyglet.shape.Triangle
        the pyglet shape of a triangle, representing the left side of the frame of the ship
    t2 : pyglet.shape.Triangle
        the pyglet shape of a triangle, representing the right side of the frame of the ship
    t3 : pyglet.shape.Triangle
        the pyglet shape of a triangle, representing the gray section of left wing of the ship
    t4 : pyglet.shape.Triangle
        the pyglet shape of a triangle, representing the gray section of right wing of the ship
    t5 : pyglet.shape.Triangle
        the pyglet shape of a triangle, representing the top side of the blue section of the right wing of the ship
    t6 : pyglet.shape.Triangle
        the pyglet shape of a triangle, representing the bottom side of the blue section of the right wing of the ship
    t7 : pyglet.shape.Triangle
        the pyglet shape of a triangle, representing the top side of the blue section of the left wing of the ship
    t8 : pyglet.shape.Triangle
        the pyglet shape of a triangle, representing the bottom side of the blue section of the left wing of the ship
    y_oscillation : float
        current value for the oscillation in the y axis
    y_speed : float
        defines how fast the ship will oscillate in the y axis
        
    Methods
    -------
    shapesList()
        returns a list with all of the shapes that forms the airship
    update()
        updates the airhship position, simulating movement by oscilating in the y and x axis
    """
    def __init__(self, x, y):
        self.r1 = Rectangle(x-8, y-15, 16, 80, color=pallete["gray"], batch=globalBatch) #back side
        self.t1 = Triangle(x-1, y-30, x-1, y+100, x-30, y, color=pallete["gray"], batch=globalBatch) #left side frame
        self.t2 = Triangle(x+1, y-30, x+1, y+100, x+30, y, color=pallete["gray"], batch=globalBatch) #right side frame
        self.t3 = Triangle(x-25,y,x-55,y+20,x-100,y-40,color=pallete["gray"],batch=globalBatch) #left wing
        self.t4 = Triangle(x+25,y,x+55,y+20,x+100,y-40,color=pallete["gray"],batch=globalBatch) #right wing
        self.t5 = Triangle(x+15,y,x+40,y,x+30,y+70,color=pallete["blue"],batch=globalBatch) #top right wing
        self.t6 = Triangle(x+15,y,x+40,y,x+35,y-40,color=pallete["blue"],batch=globalBatch) #bottom right
        self.t7 = Triangle(x-15,y,x-40,y,x-30,y+70,color=pallete["blue"],batch=globalBatch) #top left wing
        self.t8 = Triangle(x-15,y,x-40,y,x-35,y-40,color=pallete["blue"],batch=globalBatch) #bottom left
        
        #this values has some randomness in their initialization so the aiships don't move all the same
        self.y_oscillation = 0 + (randint(-9,9) / 100)
        self.y_speed = 1.2 + (randint(-9,9) / 100)

    
    def shapesList(self):
        """
        Returns
        -------
        list
            a list of the shapes that forms the airship
        """
        return [self.r1, self.t1, self.t2, self.t3, self.t4, self.t5, self.t6, self.t7, self.t8]
    
    
    def update(self):
        self.y_oscillation += 0.1
        for shape in self.shapesList():
            shape.y = shape.y + (0.9 * sin(self.y_oscillation * self.y_speed))
            
                                
#creating the ships
centralAirship = Airship((window.width//2),(window.height//2)-20)
leftAirship = Airship((window.width//2)-300,(window.height//2)-150)
rightAirship = Airship((window.width//2)+300,(window.height//2)-150)
backAirship = Airship((window.width//2),(window.height//2)-220)


############# ON RUNNING #############
@window.event
def on_draw():
    #clearing the window before drawing anything
    window.clear()

    #drawing all the shapes
    globalBatch.draw()

    #movemment of the airships
    centralAirship.update()
    leftAirship.update()
    rightAirship.update()
    backAirship.update()
    
    #movement of the stars
    updateStars()

#we run the app window
run()