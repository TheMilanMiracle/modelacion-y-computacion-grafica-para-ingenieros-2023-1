from pyglet.window import Window, key
from pyglet.app import run
from pyglet.clock import schedule, schedule_interval
import numpy as np
from OpenGL.GL import *
import lib.transformations as tr
import lib.gpu_shape as gs
import lib.scene_graph as sg
import lib.easy_shaders as es
import lib.basic_shapes as bs
import lib.shaders as sh
from lib.assets_path import getAssetPath
from lib.obj_handler import read_OBJ2

#window and camera configs
WIDTH, HEIGHT = 1000, 700

PERSPECTIVE_PROJECTION = 0
ORTOGRAPHIC_PROJECTION = 1

PROJECTIONS = [
    tr.perspective(60, float(WIDTH)/float(HEIGHT), 0.1, 100),  # PERSPECTIVE_PROJECTION
    tr.ortho(-8, 8, -8, 8, 0.1, 100)  # ORTOGRAPHIC_PROJECTION
]

#assets
ASSETS = {
    "bg_tex": getAssetPath("background3.png"),
    "rock1_tex": getAssetPath("rock1_tex.png"),
    "rock2_tex": getAssetPath("rock2_tex.png"),
    "rock3_tex": getAssetPath("rock3_tex.png"),
    "shadow_tex": getAssetPath("shadow.png"),
    "airship_obj": getAssetPath("airship.obj"),
    "shadow_obj": getAssetPath("shadow.obj"),
    "ring_obj": getAssetPath("ring.obj"),
    "ringShadow_obj": getAssetPath("ring_shadow.obj"),
    "ring_tex": getAssetPath("ring_tex.png"),
    "airship_text": getAssetPath("airship_tex.png"),
    "satelite_tex": getAssetPath("satelite_tex.png"),
    "planet_text": getAssetPath("planet_tex.png")
}



class Controller(Window):
    """
    Class that represents the controller of the window
    
    Attributes
    ----------
    total_time : float
        stores how much time the app has been running
    obj_pipeline : SimpleTextureModelViewProjectionShaderProgram
        pipeline responsible to draw the textured .obj elements of the scenary
    tex_pipeline : SimpleTextureModelViewProjectionShaderProgram_2
        pipeline responsible to draw the textured figures of the scenary
    """
    
    def __init__(self, width, height, title = "Tarea 2 - CC3501"):
        """
        Parameters
        ----------
        width : int
            app's windows width
        height : int 
            app's windows height
        title : str
            app's windows title
        """
        
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.obj_pipeline = es.SimpleTextureModelViewProjectionShaderProgram()
        self.tex_pipeline = es.SimpleTextureModelViewProjectionShaderProgram_2()

        


class Camera:
    """
    Class that represents the camera of the simulation
    
    Attributes
    ----------
    at0 : float
        initial "at" vector for the camera projection
    eye0 : float
        initial "eye" vector for the camera projection
    up0 : float
        initial "up" vector for the camera projection
    avaible_projections : list
        list that contains the transformations for orthographic and perspective projections 
        
    Methods
    -------
    set_projection(projection_index)
        changes the camera projection
    update(follow_position)
        updates the camera position, following a given position
    """

    def __init__(self, at, eye, up):
        """
        Parameters
        ----------
        at : float
            initial "at" vector for the camera projection
        eye : float
            initial "eye" vector for the camera projection
        up : float
            initial "up" vector for the camera projection
        """
        self.at0 = at
        self.eye0 = eye
        self.up0 = up
        self.available_projections = PROJECTIONS
        self.projection = self.available_projections[1]

    def set_projection(self, projection_index):
        """
        Parameters
        ----------
        projection_index : int
            must be 0 or 1, represents the index of a projection in the PROJECTIONS list
        """
        self.projection = self.available_projections[projection_index]

    def update(self, follow_position):
        """
        Parameters
        ----------
        follow_position : 3D vector
            vector that contains the position the camera has to follow
        """
        self.at = self.at0 + follow_position
        self.eye = self.eye0 + follow_position
        self.up = self.up0


#setting up the camera and controller
camera = Camera(np.array([0.0, 0.0, 1.0]), np.array([40.0, 40.0, 40.0]), np.array([0.0, 0.0, 1.0]))  #at / eye / up
controller= Controller(WIDTH, HEIGHT)
objPipeline = controller.obj_pipeline
texPipeline = controller.tex_pipeline


@controller.event
def on_key_press(symbol, modifier):
    """
    Makes the app react to a key press
    
    Parameters
    ----------
    symbol : pyglet.window.key
        key pressed
    """

    if symbol == key.R: 
        print("R pressed")
        a0.angleY = 0
    if symbol == key.A:
        print("A pressed")
        a0.angleZMultiplier += 1
    if symbol == key.D:
        print("D pressed")
        a0.angleZMultiplier -= 1
    if symbol == key.W:
        print("W pressed")
        a0.direction = 1
    if symbol == key.S:
        print("S pressed")
        a0.direction = -1
    if symbol == key.Q:
        print("Q pressed")
        a0.angleYMultiplier = 1
    if symbol == key.E:
        print("E pressed")
        a0.angleYMultiplier = - 1
    if symbol == key.LCTRL:
        print("Holding LCTRL")
        a0.control = True


        
        
@controller.event
def on_key_release(symbol, modifier):
    """
    Makes the app react to a key release
    
    Parameters
    ----------
    symbol : pyglet.window.key
        key released
    """
    
    if symbol == key.A:
        print("A released")
        a0.angleZMultiplier = 0
    if symbol == key.D:
        print("D released")
        a0.angleZMultiplier = 0
    if symbol == key.W:
        print("W released")
        a0.direction = 0
    if symbol == key.S:
        print("S released")
        a0.direction = 0
    if symbol == key.Q:
        print("Q released")
        a0.angleYMultiplier = 0
    if symbol == key.E:
        print("E released")
        a0.angleYMultiplier = 0
    if symbol == key.LCTRL:
        print("LCTRL released")
        a0.control = False
        a0.angleYMultiplier = 0

@controller.event
def on_mouse_motion(x, y, dx, dy):
    """
    Makes the app react to the movement of the mouse
    
    Parameters
    ----------
    symbol : pyglet.window.key
        key being pressed
    """
    
    if dy > 3:
        if a0.control:
            a0.angleYMultiplier = 1
    if dy < -3:
        if a0.control:
            a0.angleYMultiplier = -1
        

class Airship:
    """
    Class that represent the main airship in the scene
    this is the airship that can be controlled by the user
    
    Attributes
    ----------
    control : bool
        stores if the LCTRL key is being pressed
    angleZ : float
        stores the angle of rotation of the airship in the z axis
    angleZSpeed : float
        stores the speed at which the airship rotates in the z axis
    angleYLimit : float
        stores the maximun rotation angle of the ship in the y axis
    angleY : float
        stores the angle of rotation of the airship in the y axis
    angleYSpeed : float
        stores the speed at which the airship rotates in the y axis
    delta : float
        stores the total displacement of the airship from the origin
    deltaSpeed : float
        stores the speed at which the airship moves in any axis
    direction : float
        stores the direction at which the airship points towards
    translateVector : numpy.array
        stores the vector of the position of the airship in axis x,y,z
    movementLimit : int
        stores the limit the airship can move in the xy plane
    Zfloor : int
        stores the minimun height the aiship can have in the z axis
    Zceiling : int
        stores the minimun height the aiship can have in the z axis
    phi : float
        stores the azimuthal angle of rotation of the airship
    theta : float
        stores the zenithal angle of rotation of the airship
    
    
    Methods
    -------
    update()
        updates the current position and orientation of the airship making sure it does not go out of bounds
    updateCords(X,Y,Z)
        allows to update the airship coordinates selectively
    """
    def __init__(self):
        self.control = False
        
        self.angleZ = self.angleZMultiplier = 0
        self.angleZSpeed = 0.1
        
        self.angleYLimit = np.pi / 10
        self.angleY = self.angleYMultiplier = 0
        self.angleYSpeed = 0.02
        
        self.delta = self.direction = 0
        self.deltaSpeed = 0.1
        self.translateVector = np.array([0,0,0],dtype = float)
        
        self.movementLimit = 25
        self.Zfloor = -2
        self.Zceiling = 5
        
        # Movement/Rotation direction
        self.phi = 0 #
        self.theta = 0 #zenital

        
    def update(self):
        self.angleZ += (self.angleZSpeed * self.angleZMultiplier) #SIDES
        
        #limitating the angle
        if (self.angleY < self.angleYLimit and self.angleY > -self.angleYLimit) or (self.angleY > self.angleYLimit and self.angleYMultiplier < 0) or (self.angleY < -self.angleYLimit and self.angleYMultiplier > 0):
            self.angleY += (self.angleYSpeed * self.angleYMultiplier) #UP AND DOWN
        else:
            self.angleY = self.angleY         

        self.theta = self.angleY
        self.phi = self.angleZ
        
        self.delta = self.direction * self.deltaSpeed
        
        # limitating the position
        if self.translateVector[0] < self.movementLimit and self.translateVector[1] < self.movementLimit and self.translateVector[0] > -self.movementLimit and self.translateVector[1] > -self.movementLimit:
            self.updateCoords(True, True)
        else:# border action X/Y
            if self.translateVector[0] > self.movementLimit:
                self.angleZ += np.pi
                self.translateVector[0] -= 2
            if self.translateVector[0] < -self.movementLimit:
                self.angleZ += np.pi
                self.translateVector[0] += 2
            if self.translateVector[1] > self.movementLimit:
                self.angleZ += np.pi
                self.translateVector[1] -= 2         
            if self.translateVector[1] < -self.movementLimit:
                self.angleZ += np.pi
                self.translateVector[1] += 2
                               
        #limitating postiion in Z axis
        if self.translateVector[2] < self.Zceiling and self.translateVector[2] > self.Zfloor:
            self.updateCoords(None, None, True)
        else:
            if self.translateVector[2] > self.Zceiling:
                print("ceiling hit")
                self.angleY -= self.angleY * 2
                self.angleZ += np.pi
                self.translateVector[2] -= 0.2
            if self.translateVector[2] < self.Zfloor:
                print("floor hit")
                self.angleY += abs(self.angleY) * 2
                self.angleZ += np.pi
                self.translateVector[2] += 0.2
                   
    def updateCoords(self, X=False, Y =False, Z = False):
        """
        Paramaters
        ----------
        X : bool
            whether or not to update the position in the x axis
        Y : bool
            whether or not to update the position in the y axis        
        Z : bool
            whether or not to update the position in the z axis
        """
        # Spherical coordinates  
        if X == True:
            self.translateVector[0] += (self.delta) * np.cos(self.theta) * np.sin(self.phi) * -1 #X
        if Y == True:
            self.translateVector[1] += (self.delta) * np.cos(self.theta) * np.cos(self.phi) #Y
        if Z == True:
            self.translateVector[2] += (self.delta) * np.sin(self.theta) #Z
        
        
        





## time events

class timeEvents:
    """
    Class that represent the time passing in the scene
    
    Attributes
    ----------
    r1Rotation : float
        angle of rotation for the type 1 of rocks
    r2Rotation : float
        angle of rotation for the type 2 of rocks
    r1Speed : float
        angular speed of the type 1 of rocks
    r2Speed : float
        angular speed of the type 2 of rocks
    oscillation : float
        displacement of the airship from the actual position to emulate an oscillation
    dt : float
        delta time for the airship
    oscillationSpeed : float
        speed at which the airship oscillates
    oscillationA : float
        amplitude of oscillation of the airship
    ringOscillation : float
        displacement of the rings from their actual position to emulate an oscillation
    rDt : float
        rings delta time
    ringOscillationSpeed : float
        speed at which the rings oscillates
    ringA : float
        amplitude of oscillation of the rings
    """
    def __init__(self):
        self.r1Rotation = 0
        self.r2Rotation = 0
        self.r1Speed = 0.02
        self.r2Speed = 0.005
        
        self.oscillation = 0
        self.dt = 0
        self.oscillationSpeed = 0.04
        self.oscillationA = 0.1
        
        self.ringOscillation = 0
        self.rDt = 0
        self.ringOscillationSpeed = 0.06
        self.ringA = 0.1
        
        self.movingRockRotationSpeed = 0.2
        self.movingRockRotation = 0
        
        self.movingRockTr1 = 0
        self.movingRockTr2 = 0
        self.movingRockTr3 = 0 
        self.rock1X = np.random.randint(-30,-10)
        self.rock2X = np.random.randint(-10,10)
        self.rock3X = np.random.randint(10,30)
        
        self.planetRot = 0
        self.planetRotSpeed = 0.005
        
        self.sateliteRot = 0
        self.sateliteRotSpeed = 0.02
        


time = timeEvents()

def update(dt):
    """
    Updates all time events
    """
    time.r1Rotation += time.r1Speed
    time.r2Rotation += time.r2Speed
    
    time.dt += time.oscillationSpeed
    time.oscillation = time.oscillationA * np.sin(time.dt)
    
    time.rDt += time.ringOscillationSpeed
    time.ringOscillation = time.ringA * np.cos(time.rDt)
    
    time.movingRockTr1 += 0.1
    time.movingRockTr2 += 0.12
    time.movingRockTr3 += 0.15
    
    if int(time.movingRockTr1 % 65) == 0:
        time.rock1X = np.random.randint(-30,30)
    if int(time.movingRockTr2 % 65) == 0:
        time.rock2X = np.random.randint(-30,30)
    if int(time.movingRockTr3 % 65) == 0:
        time.rock3X = np.random.randint(-30,30)
        
    time.movingRockRotation -= time.movingRockRotationSpeed
    
    time.planetRot += time.planetRotSpeed
    
    time.sateliteRot += time.sateliteRotSpeed
        
    

    


schedule_interval(update, 0.01)
##

        
## scenegraph
#airship obj
airshipObj = gs.createGPUShape(objPipeline, read_OBJ2(ASSETS["airship_obj"]))
AOtex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
airshipTex = ASSETS["airship_text"]
airshipObj.texture = es.textureSimpleSetup(airshipTex, *AOtex_params)

#ring obj
ringObj = gs.createGPUShape(objPipeline, read_OBJ2(ASSETS["ring_obj"]))
ringtex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
ringTex = ASSETS["ring_tex"]
ringObj.texture = es.textureSimpleSetup(ringTex, *ringtex_params)
ringObjNode = sg.SceneGraphNode("ringobjnode")
ringObjNode.childs += [ringObj]

#shadow obj
ringShadow = gs.createGPUShape(objPipeline,read_OBJ2(ASSETS["ringShadow_obj"]))
sR_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
srTex = ASSETS["shadow_tex"]
ringShadow.texture = es.textureSimpleSetup(srTex, *sR_params)
ringNode = sg.SceneGraphNode("ringShadow_node")
ringNode.childs += [ringShadow]

#airship node
objNode = sg.SceneGraphNode("airshipNode")
objNode.transform = tr.matmul([tr.translate(0,0,3),tr.rotationX(np.pi / 2),tr.scale(0.3,0.3,0.3)])
objNode.childs += [airshipObj]

#escenary with texture
rockTex_TexCords = [1.0,1.0]
rockCube = gs.createGPUShape(texPipeline, bs.createCube(*rockTex_TexCords))
rockCube_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
rockTex = ASSETS["rock1_tex"]
rockCube.texture = sh.textureSimpleSetup(rockTex, *rockCube_params)

rockTex_TexCords2 = [1.0,1.0]
rockCube2 = gs.createGPUShape(texPipeline, bs.createCube(*rockTex_TexCords2))
rockCube_params2 = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
rockTex2 = ASSETS["rock2_tex"]
rockCube2.texture = sh.textureSimpleSetup(rockTex2, *rockCube_params2)

gpurockCube3 = gs.createGPUShape(texPipeline, bs.createCube(*[1.0,1.0]))
gpurockCube3.texture = sh.textureSimpleSetup(ASSETS["rock3_tex"], *rockCube_params2)               

rockCube3 = sg.SceneGraphNode("rockCubeModel")
rockCube3.transform = tr.scale(0.15,0.15,0.20)
rockCube3.childs += [gpurockCube3]

planetCoords = [1.0,1.0]
gpuPlanet = gs.createGPUShape(texPipeline, bs.createCube(*planetCoords))
planetParams = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
planetTex = ASSETS["planet_text"]
gpuPlanet.texture = sh.textureSimpleSetup(planetTex, *planetParams)

gpuPlanetNode = sg.SceneGraphNode("planetNode")
gpuPlanetNode.childs += [gpuPlanet]

sateliteCoords = [1.0,1.0]
gpuSatelite = gs.createGPUShape(texPipeline, bs.createCube(*sateliteCoords))
sateliteParams = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
sateliteTex = ASSETS["satelite_tex"]
gpuSatelite.texture = sh.textureSimpleSetup(sateliteTex, *sateliteParams)
          
gpuSateliteNode = sg.SceneGraphNode("gpuSateliteNode")
gpuSateliteNode.childs = [gpuSatelite]
     
#shadow for rocks
shadowCube = gs.createGPUShape(texPipeline, bs.createCube(*[1.0,1.0]))
shadowCube_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
shadowCubeTex = ASSETS["shadow_tex"]
shadowCube.texture = sh.textureSimpleSetup(shadowCubeTex, *shadowCube_params)

#background cube tex
bgCube_TexCoords = [40.0, 40.0]
bgCube = gs.createGPUShape(texPipeline, bs.createTextureQuad(*bgCube_TexCoords))
bgCube_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
bgCube_Tex = ASSETS["bg_tex"]
bgCube.texture = sh.textureSimpleSetup(bgCube_Tex, *bgCube_params)

#background cube node
bgNode = sg.SceneGraphNode("bgNode")
bgNode.transform = tr.matmul([tr.translate(0,0,-5),tr.scale(200,200,1)])
bgNode.childs += [bgCube]

#node that the camera follows
cameraPos = sg.SceneGraphNode("cameraPos")

#following airships
a1 = sg.SceneGraphNode("airship_1")
a1.childs += [objNode]

a2 = sg.SceneGraphNode("airship_2")
a2.childs += [objNode]

#airship movement node
airshipRotation = sg.SceneGraphNode("airshipRotation")
airshipRotation.childs += [objNode]
airshipRotation.childs += [cameraPos]

airshipTranslation = sg.SceneGraphNode("airshipTranslation")
airshipTranslation.childs += [airshipRotation]

airshipPos = sg.SceneGraphNode("airshipPosition")
airshipPos.childs += [airshipTranslation]

airship = sg.SceneGraphNode("airship")
airship.childs += [airshipPos]
airshipRotation.childs += [a1]
airshipRotation.childs += [a2]

#scenary
cubeShadowNode = sg.SceneGraphNode("cubeShadow")
cubeShadowNode.transform = tr.scale(1,1,0.5)
cubeShadowNode.childs += [shadowCube]

rockShadow1 = sg.SceneGraphNode("rockShadow1")
rockShadow1.childs += [cubeShadowNode]
rock1 = sg.SceneGraphNode("rock1")
rock1.childs += [rockCube]

rockShadow2 = sg.SceneGraphNode("rockShadow2")
rockShadow2.childs += [cubeShadowNode]
rock2 = sg.SceneGraphNode("rock2")
rock2.childs += [rockCube]

rockShadow3 = sg.SceneGraphNode("rockShadow3")
rockShadow3.childs += [cubeShadowNode]
rock3 = sg.SceneGraphNode("rock3")
rock3.childs += [rockCube]

rockShadow4 = sg.SceneGraphNode("rockShadow4")
rockShadow4.childs += [cubeShadowNode]
rock4 = sg.SceneGraphNode("rock4")
rock4.childs += [rockCube]

rockShadow5 = sg.SceneGraphNode("rockShadow5")
rockShadow5.childs += [cubeShadowNode]
rock5 = sg.SceneGraphNode("rock5")
rock5.childs += [rockCube]

rockShadow6 = sg.SceneGraphNode("rockShadow6")
rockShadow6.childs += [cubeShadowNode]
rock6 = sg.SceneGraphNode("rock6")
rock6.childs += [rockCube2]

rockShadow7 = sg.SceneGraphNode("rockShadow7")
rockShadow7.childs += [cubeShadowNode]
rock7 = sg.SceneGraphNode("rock7")
rock7.childs += [rockCube2]

rockShadow8 = sg.SceneGraphNode("rockShadow8")
rockShadow8.childs += [cubeShadowNode]
rock8 = sg.SceneGraphNode("rock8")
rock8.childs += [rockCube2]

rockShadow9 = sg.SceneGraphNode("rockShadow9")
rockShadow9.childs += [cubeShadowNode]
rock9 = sg.SceneGraphNode("rock9")
rock9.childs += [rockCube]

rockShadow10 = sg.SceneGraphNode("rockShadow10")
rockShadow10.childs += [cubeShadowNode]
rock10 = sg.SceneGraphNode("rock10")
rock10.childs += [rockCube]

movingRock1 = sg.SceneGraphNode("movingRock1")
movingRock1.childs += [rockCube3]

movingRock2 = sg.SceneGraphNode("movingRock2")
movingRock2.childs += [rockCube3]

movingRock3 = sg.SceneGraphNode("movingRock3")
movingRock3.childs += [rockCube3]


ring1 = sg.SceneGraphNode("ring1")
ring1.childs += [ringObjNode]
ringShadow1 = sg.SceneGraphNode("ringShadow1")
ringShadow1.childs += [ringNode]

ring2 = sg.SceneGraphNode("ring2")
ring2.childs += [ringObjNode]
ringShadow2 = sg.SceneGraphNode("ringShadow2")
ringShadow2.childs += [ringNode]

rings = sg.SceneGraphNode("rings")
rings.childs += [ring1]
rings.childs += [ringShadow1]
rings.childs += [ring2]
rings.childs += [ringShadow2]


sateliteShadow = sg.SceneGraphNode("sateliteShadow")
sateliteShadow.childs += [cubeShadowNode]

satelitePos = sg.SceneGraphNode("satelitePos")
satelitePos.childs = [gpuSateliteNode]


planetShadow = sg.SceneGraphNode("planetShadow")
planetShadow.childs += [cubeShadowNode]

planetPos = sg.SceneGraphNode("planetPos")
planetPos.childs += [gpuPlanetNode]
planetPos.childs += [satelitePos]
planetPos.childs += [sateliteShadow]



#scene root
sceneRoot = sg.SceneGraphNode("rootNode")
sceneRoot.childs += [airship]
sceneRoot.childs += [rings]


#background root
bgRoot = sg.SceneGraphNode("bgRootNode")
bgRoot.childs += [bgNode]
bgRoot.childs += [rock1]
bgRoot.childs += [rockShadow1]
bgRoot.childs += [rock2]
bgRoot.childs += [rockShadow2]
bgRoot.childs += [rock3]
bgRoot.childs += [rockShadow3]
bgRoot.childs += [rock4]
bgRoot.childs += [rockShadow4]
bgRoot.childs += [rock5]
bgRoot.childs += [rockShadow5]
bgRoot.childs += [rock6]
bgRoot.childs += [rockShadow6]
bgRoot.childs += [rock7]
bgRoot.childs += [rockShadow7]
bgRoot.childs += [rock8]
bgRoot.childs += [rockShadow8]
bgRoot.childs += [rock9]
bgRoot.childs += [rockShadow9]
bgRoot.childs += [rock10]
bgRoot.childs += [rockShadow10]
bgRoot.childs += [movingRock1]
bgRoot.childs += [movingRock2]
bgRoot.childs += [movingRock3]
bgRoot.childs += [planetPos]
bgRoot.childs += [planetShadow]

#shadow png
gpuShadow = gs.createGPUShape(objPipeline, read_OBJ2(ASSETS["shadow_obj"]))
shadowTex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
shadowTex = ASSETS["shadow_tex"]
gpuShadow.texture = sh.textureSimpleSetup(shadowTex, *shadowTex_params)

shadowObj = sg.SceneGraphNode("shadowObj")
shadowObj.transform = tr.matmul([tr.rotationX(np.pi / 2),tr.rotationY(0),tr.scale(0.4,0.4,0.4)])
shadowObj.childs += [gpuShadow]

shadowPos = sg.SceneGraphNode("shadowRot")
shadowPos.childs += [shadowObj]

shadow = sg.SceneGraphNode("shadow")
shadow.childs += [shadowPos]

airshipTranslation.childs += [shadow]

a1Shadow = sg.SceneGraphNode("shadow1")
a1Shadow.childs += [shadow]

a2Shadow = sg.SceneGraphNode("shadow2")
a2Shadow.childs += [shadow]

a1.childs += [a1Shadow]
a2.childs += [a2Shadow]


a0 = Airship()

glClearColor(0.3,0.3,0.3,1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(objPipeline.shaderProgram)
glUseProgram(texPipeline.shaderProgram)




@controller.event
def on_draw():
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    cameraFollow = sg.findPosition(cameraPos, "cameraPos")
    cameraFollow = np.array([cameraFollow[0][0],cameraFollow[1][0],cameraFollow[2][0]])
    camera.update(cameraFollow)

    
    view = tr.lookAt(
        camera.eye,
        camera.at,
        camera.up
    )
    
    glUniformMatrix4fv(glGetUniformLocation(objPipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    
    #airships movement
    a0.update()
    airshipRotation.transform = tr.matmul([tr.rotationZ(a0.angleZ), tr.rotationX(a0.angleY)])
    airshipTranslation.transform = tr.translate(a0.translateVector[0], a0.translateVector[1], a0.translateVector[2] + (time.oscillation))
    cameraPos.transform = tr.translate(a0.translateVector[0], a0.translateVector[1], a0.translateVector[2])
    shadow.transform = airshipRotation.transform
    a1Shadow.transform = a2Shadow.transform = tr.matmul([tr.rotationZ(-a0.angleZ)])
    
    
    a1.transform = tr.matmul([tr.translate(-1.2,-1.2,0.2)])
    a2.transform = tr.matmul([tr.translate(1.2,-1.2,0.2)])


    
    #scenary
    rock1.transform = tr.matmul([tr.translate(10,5,4),tr.scale(0.2,0.2,0.3), tr.rotationZ((np.pi * 5/6) + time.r1Rotation)])
    rockShadow1.transform = tr.matmul([tr.translate(10,5,0),tr.scale(0.2,0.2,0.01), tr.rotationZ((np.pi * 5/6) + time.r1Rotation)]) 
    rock2.transform = tr.matmul([tr.translate(20,15,5),tr.scale(0.25,0.25,0.35),tr.rotationZ((np.pi * 5/2) + time.r1Rotation)])
    rockShadow2.transform =tr.matmul([tr.translate(20,15,1),tr.scale(0.25,0.25,0.01),tr.rotationZ((np.pi * 5/2) + time.r1Rotation)])
    rock3.transform = tr.matmul([tr.translate(5,-9,6),tr.scale(0.25,0.25,0.35),tr.rotationZ((np.pi * 2/3) + time.r1Rotation)])
    rockShadow3.transform = tr.matmul([tr.translate(5,-9,2),tr.scale(0.25,0.25,0.01),tr.rotationZ((np.pi * 2/3) + time.r1Rotation)])
    rock4.transform = tr.matmul([tr.translate(10,13,6),tr.scale(0.3,0.3,0.4), tr.rotationZ((np.pi * 7/5) + time.r1Rotation)])
    rockShadow4.transform = tr.matmul([tr.translate(10,13,2),tr.scale(0.3,0.3,0.01), tr.rotationZ((np.pi * 7/5) + time.r1Rotation)])
    rock5.transform = tr.matmul([tr.translate(-10,12,6),tr.scale(0.2,0.2,0.3), tr.rotationZ((np.pi * 3 / 5) + time.r1Rotation)])
    rockShadow5.transform = tr.matmul([tr.translate(-10,12,2),tr.scale(0.2,0.2,0.01), tr.rotationZ((np.pi * 3 / 5) + time.r1Rotation)])
    rock6.transform = tr.matmul([tr.translate(-2,12,5),tr.scale(0.5,0.5,0.65), tr.rotationZ((np.pi * 1 / 5) + time.r2Rotation)])
    rockShadow6.transform = tr.matmul([tr.translate(-2,12,1),tr.scale(0.5,0.5,0.01), tr.rotationZ((np.pi * 1 / 5) + time.r2Rotation)])
    rock7.transform = tr.matmul([tr.translate(5,-7,5),tr.scale(0.6,0.6,0.75), tr.rotationZ((np.pi * 9 / 5) + time.r2Rotation)])
    rockShadow7.transform = tr.matmul([tr.translate(5,-7,1),tr.scale(0.6,0.6,0.01), tr.rotationZ((np.pi * 9 / 5) + time.r2Rotation)])
    rock8.transform = tr.matmul([tr.translate(20,-7,5),tr.scale(0.6,0.6,0.75), tr.rotationZ((np.pi * 9 / 5) + time.r2Rotation)])
    rockShadow8.transform = tr.matmul([tr.translate(20,-7,1),tr.scale(0.6,0.6,0.01), tr.rotationZ((np.pi * 9 / 5) + time.r2Rotation)])
    rock9.transform = tr.matmul([tr.translate(5,-18,5),tr.scale(0.4,0.4,0.55), tr.rotationZ((np.pi * 9 / 5) + time.r2Rotation)])
    rockShadow9.transform = tr.matmul([tr.translate(5,-18,1),tr.scale(0.4,0.4,0.01), tr.rotationZ((np.pi * 9 / 5) + time.r2Rotation)])
    rock10.transform = tr.matmul([tr.translate(-20,-7,5),tr.scale(0.3,0.3,0.35), tr.rotationZ((np.pi * 9 / 5) + time.r2Rotation)])
    rockShadow10.transform = tr.matmul([tr.translate(-20,-7,1),tr.scale(0.3,0.3,0.01), tr.rotationZ((np.pi * 9 / 5) + time.r2Rotation)])
    
    ring1.transform = tr.matmul([tr.translate(10,17, 5), tr.rotationX(np.pi / 2),tr.scale(0.6,0.7,0.4),tr.translate(0,time.ringOscillation,0)])
    ringShadow1.transform = tr.matmul([tr.translate(10,17,1),tr.rotationX(np.pi / 2),tr.scale(0.6,0.7,0.4),tr.translate(0,time.ringOscillation,0)])
    ring2.transform = tr.matmul([tr.translate(12,-22, 4), tr.rotationX(np.pi / 2),tr.rotationY(np.pi / 2),tr.scale(0.6,0.7,0.4),tr.translate(0,time.ringOscillation,0)])
    ringShadow2.transform = tr.matmul([tr.translate(12,-22,0),tr.rotationX(np.pi / 2),tr.rotationY(np.pi / 2),tr.scale(0.6,0.7,0.4),tr.translate(0,time.ringOscillation,0)])

    movingRock1.transform = tr.matmul([tr.translate(time.rock1X,-35 + (time.movingRockTr1 % 65),0),tr.rotationX(time.movingRockRotation)])
    movingRock2.transform = tr.matmul([tr.translate(time.rock2X,-35 + (time.movingRockTr2 % 65),0),tr.rotationX(time.movingRockRotation)])
    movingRock3.transform = tr.matmul([tr.translate(time.rock3X,-35 + (time.movingRockTr3 % 65),0),tr.rotationX(time.movingRockRotation)])

    planetPos.transform = tr.matmul([tr.translate(-18,-20,2),tr.rotationZ(time.planetRot),tr.scale(1,1,1.5)])
    satelitePos.transform = tr.matmul([tr.translate(2,0,0),tr.rotationZ(time.sateliteRot),tr.scale(0.2,0.2,0.2)])
    sateliteShadow.transform = tr.matmul([tr.translate(2,0,-3),tr.rotationZ(time.sateliteRot),tr.scale(0.2,0.2,0.001)])
    planetShadow.transform = tr.matmul([tr.translate(-18,-20,-1),tr.rotationZ(time.planetRot),tr.scale(1,1,0.001)])
    
    sg.drawSceneGraphNode(bgRoot, texPipeline, "model")
    sg.drawSceneGraphNode(sceneRoot, objPipeline, "model")

    


def update(dt, controller):
    controller.total_time += dt    

if __name__ == "__main__":
    schedule(update, controller)
    run()
    