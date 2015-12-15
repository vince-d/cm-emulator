# Version:	1.0
# Author:	Vincent Diener - diener@teco.edu

import pyglet
import math
import bluetooth
import os

from pyglet.gl import *
from pyglet.window import *
from pyglet.window import key as key
from random import randint
from threading import Thread
from ctypes import *

from modules.shader.shader import Shader
from modules.shader_loader.shader_loader import ShaderLoader
from modules.gl_helper.gl_helper import GLHelper
from modules.bt_helper.bt_helper import BTHelper

# ----------------------------------------------- #
# Constants                                       #
# ----------------------------------------------- #

# OpenGL context size at window creation.
# X and Y should be the same to avoid artifacts.
OPENGL_SIZE_X = 900
OPENGL_SIZE_Y = 900

# Window location on screen.
WIN_LOC_X = 50
WIN_LOC_Y = 50

# Frames per second. If you experience lag, lower this value.
OPENGL_FPS = 60

# FPS for the LED matrix.
# The actual hardware in the real Connection Machine supports about 10 FPS, 
# so make sure your app still looks good with that.
BLUETOOTH_FPS = 30

# The background color (RGB, 0-255).
BG_COLOR = (201, 198, 198)

# Use post processing shader.
# Since this naive implementation reads the color buffer on every frame,
# it may cause heavy lag. Try to lower OPENGL_FPS in that case.
# The current shader ("shaders/post_processing.fs") just takes the
# color buffer of the final rendered image and inverts the colors.
# Feel free to add some cool effects.
USE_POST_PROCESSING = False

#-------------------------------------------------#
# Window and helper setup                         #
#-------------------------------------------------#

# Create window. Uncomment config for 4x Anti-Aliasing.
# config = pyglet.gl.Config(sample_buffers=1, samples=4)
# window = pyglet.window.Window(OPENGL_SIZE_X, OPENGL_SIZE_Y, resizable=True, visible=True, caption="Connection Machine Emulator", config=config)

window = pyglet.window.Window(OPENGL_SIZE_X, OPENGL_SIZE_Y, resizable=True, visible=True, caption="Connection Machine Emulator")


# Set window position.
window.set_location(WIN_LOC_X, WIN_LOC_Y)

# Set minimum size.
window.set_minimum_size(50, 50)

# Create GL helper.
gl = GLHelper(OPENGL_SIZE_X, OPENGL_SIZE_Y)

# Create BT helper to take care of the Bluetooth connection.
# This is also used to store the matrix of red-values and do logging.
# Red values are stored as array of size 576 (24x24 red values), ranging from 0.0 to 1.0.
bt = BTHelper([0.0 for x in range(576)], BLUETOOTH_FPS, window)

#-------------------------------------------------#
# Draw loop and user input                        #
#-------------------------------------------------#

# ESCAPE keypress needs seperate treatment:
# For some reason the event doesn't register in draw loop.
# Also check for I, 1 and 2 key press because we don't want to poll those.
@window.event
def on_key_press(symbol, modifiers):
    global show_instructions
    global instruction_timer
    global lighting
    global floor
    global USE_POST_PROCESSING

    # Quit on ESC press.
    if symbol == pyglet.window.key.ESCAPE:
        os._exit(0)

    # I, 1 and 2 keypresses toggle the respective booleans.
    if symbol == pyglet.window.key.I:
        show_instructions = not show_instructions

    if symbol == pyglet.window.key._1:
        lighting = not lighting

    if symbol == pyglet.window.key._2:
        floor = not floor

    # Toggle PP.
    if symbol == pyglet.window.key.P:
        USE_POST_PROCESSING = not USE_POST_PROCESSING

    pass


# Poll keys (W, A, S, D)
# This gets called from the draw loop.
def handleUserInput():
    global keys
    global yPos
    global zPos

    # Move the camera.
    glMatrixMode(GL_PROJECTION)

    # Camers is at distance 20 from center.
    toCenter = zPos - 20

    # Move to center, rotate, move back out.
    if keys[key.D]:
        glTranslatef(0.0, 0.0, toCenter)
        glRotatef(4, 0, -1, 0)
        glTranslatef(0.0, 0.0, -toCenter)

    if keys[key.A]:
        glTranslatef(0.0, 0.0, toCenter)
        glRotatef(4, 0, 1, 0)
        glTranslatef(0.0, 0.0, -toCenter)

    # Move up and down.
    if keys[key.W]:
        if (yPos < 40):
            glTranslatef(0.0, -0.2, 0.0)
            yPos += 1

    if keys[key.S]:
        if (yPos > 0):
            glTranslatef(0.0, 0.2, 0.0)
            yPos -= 1

    # Done with camera movement.
    glMatrixMode(GL_MODELVIEW)

    # If space is pressed, reset the view.
    if keys[key.SPACE]:
        # Actual number is ignored by on_resize as it reads the viewport size.
        on_resize(512, 512)


# Gets called every time the window is resized or space is pressed.
@window.event
def on_resize(w, h):
    global yPos
    global zPos
    global gl

    # Get actual size of the GL viewport.
    (gl.gl_x, gl.gl_y) = window.get_size()

    # Set lighting parameters.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, gl.vec(-12, -0, -4, 0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, gl.vec(5.0, 0.8, 0.8))
    glLightfv(GL_LIGHT0, GL_AMBIENT, gl.vec(0.23, 0.23, 0.23))

    # Set perspective/position parameters.
    yPos = 8
    zPos = 6
    zNear = 0.01
    zFar = 1000.0
    fieldOfView = 45.0
    size = zNear * math.tan(math.radians(fieldOfView) / 2.0)

    # Create viewport.
    glViewport(0, 0, gl.gl_x, gl.gl_y)

    # Set up perspective (projection matrix).
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Prevent division by zero.
    w_divided_h = gl.gl_x / float(gl.gl_y)
    glFrustum(-size, size, -size / w_divided_h, size / w_divided_h, zNear, zFar)

    # Put model in correct position.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.2, -14.0)

    return pyglet.event.EVENT_HANDLED


# Gets called for every frame.
@window.event
def on_draw():
    global bt
    global gl
    global window
    global time
    global lighting
    global floor
    global instruction_timer
    global show_instructions

    # Progress time.
    time += 1

    # This creates the fade effect for the instructions.
    if (show_instructions and instruction_timer > 0):
        instruction_timer -= 3

    if (not show_instructions and instruction_timer < 50):
        instruction_timer += 3

    # Clear buffer.
    window.invalid = True
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Check if any keys are pressed.
    handleUserInput()

    # Draw detailed floor?
    if (floor):
        # If so, draw flashing red ring effect at the bottom.
        # Time is passed in to create the effect.
        shader_ground.shader.bind()
        shader_ground.shader.uniformi(b'time', time)
        glBindTexture(texture_effect_red.target, texture_effect_red.id)
        batch_effect_red.draw()
        shader_ground.shader.unbind()

    # Draw Connection Machine and floor with or without lighting.
    # Time is 0, so drawing is fully opaque.
    shader_body.shader.bind()
    shader_body.shader.uniformi(b'do_light', lighting)
    shader_body.shader.uniformi(b'time', 0)

    # Connection Machine center cube and stand.
    glBindTexture(texture_metal_0.target, texture_metal_0.id)
    batch_metal_0.draw()

    # Connection Machine, 8 main cubes.
    glBindTexture(texture_metal_1.target, texture_metal_1.id)
    batch_metal_1.draw()

    # Draw detailed floor?
    if (floor):
        # If so, draw detailed texture (multiple times).
        glBindTexture(texture_detailed_ground.target, texture_detailed_ground.id)
        batch_detailed_ground.draw()
    else:
        # If not, draw simple texture once.
        glBindTexture(texture_simple_ground.target, texture_simple_ground.id)
        batch_simple_ground.draw()

    shader_body.shader.unbind()

    # Draw front LEDs.
    shader_leds.shader.bind()

    # For each frame, pass in the red values for the 576 LEDs.
    loc = glGetUniformLocation(shader_leds.shader.handle, b"pixel")
    glUniform1fv(loc, 576, (c_float * 576)(*bt.matrix))
    glBindTexture(texture_led.target, texture_led.id)

    batch_led.draw()
    shader_leds.shader.unbind()

    # Draw the overlays (logo, instructions, fade in).
    shader_body.shader.bind()

    # Disable lighting for these draw calls.
    shader_body.shader.uniformi(b'do_light', False)

    # Set up correct perspective (orthogonal projection).
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, OPENGL_SIZE_X, 0, OPENGL_SIZE_Y, -1, 1)

    # Draw instructions.
    # Time is set to the instruction_timer to create the fade effect.
    shader_body.shader.uniformi(b'time', instruction_timer)
    glBindTexture(texture_instructions.target, texture_instructions.id)
    batch_instructions.draw()

    # Draw logo. Time is 0, so it is drawn fully opaque.
    shader_body.shader.uniformi(b'time', 0)
    glBindTexture(texture_logo.target, texture_logo.id)
    batch_logo.draw()

    # Draw fade-in-from-black overlay.
    # Normal time is passed in, so it becomes transparent in 50 frames.
    shader_body.shader.uniformi(b'time', time)
    glBindTexture(texture_fade.target, texture_fade.id)
    batch_fade.draw()

    shader_body.shader.unbind()

    # Post processing shader
    if (USE_POST_PROCESSING):
        global texture_pp
        global color_buffer

        shader_pp.shader.bind()

        # Create texture in the size of the OpenGL viewport.
        # The size might be rounded up to the nearest power of two. This means that if we blit the
        # color buffer into the texture in the next step, it might have a "frame".
        texture_pp = pyglet.image.Texture.create_for_size(GL_TEXTURE_2D, gl.gl_x, gl.gl_y, GL_RGBA)
        color_buffer = pyglet.image.get_buffer_manager().get_color_buffer()

        # To get rid of that frame in the shader, we calculate the ratio between the actual buffer
        # and our texture. By passing this ratio to the shader, it can sample the texture at the
        # correct coordinates.
        pixel_ratio_x = color_buffer.width / float(texture_pp.width)
        pixel_ratio_y = color_buffer.height / float(texture_pp.height)

        # Write color buffer to texture.
        texture_pp.blit_into(color_buffer, 0, 0, 0)

        glBindTexture(texture_pp.target, texture_pp.id)

        # Pass uniforms to post processing shader.
        shader_pp.shader.uniformf(b'ratio_x', pixel_ratio_x)
        shader_pp.shader.uniformf(b'ratio_y', pixel_ratio_y)
        shader_pp.shader.uniformi(b'tex_width', gl.gl_x)
        shader_pp.shader.uniformi(b'tex_height', gl.gl_y)
        shader_pp.shader.uniformi(b'time', time)

        # Draw and unbind.
        batch_fullscreen.draw()
        shader_pp.shader.unbind()

    # Load old perspective.
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


# Triggers the draw loop.
def schedule_update(t):
    pass


# Randomize matrix of red values.
# Only do this when there is no active BT connection.
def schedule_randomize(t):
    global bt

    if (bt.running == False):
        for x in range(0, 576):
            rnd = randint(0, 1)
            bt.matrix[x] = rnd


# LEDs are updated at 15 FPS.
def schedule_leds(t, d):
    global batch_led
    global bt
    gl.drawAllLeds(batch_led, bt.matrix, d)

#-------------------------------------------------#
# Application and OpenGL setup                    #
#-------------------------------------------------#

# Add key handler to process user input.
keys = key.KeyStateHandler()
window.push_handlers(keys)

# Time (passed frames)
time = 0

# Show instructions or hide them?
show_instructions = True

# Enable lighting?
lighting = True

# Render detailed floor?
floor = False

# Timer for instruction fade.
instruction_timer = 0

# Height of camera.
# Locked within a certain interval.
yPos = 0

# Distance of camera from Connection Machine.
# Locked within a certain interval.
zPos = 0

# Load textures. Enable transparency for some.
texture_led = gl.prepareTex("textures/led.png", True)
texture_metal_0 = gl.prepareTex("textures/metal_0.jpg", False)
texture_metal_1 = gl.prepareTex("textures/metal_1.jpeg", False)
texture_simple_ground = gl.prepareTex("textures/ground_0.png", True)
texture_detailed_ground = gl.prepareTex("textures/ground_1.png", True)
texture_effect_red = gl.prepareTex("textures/effect_red.png", True)
texture_fade = gl.prepareTex("textures/fade.png", True)
texture_logo = gl.prepareTex("textures/logo.png", True)
texture_instructions = gl.prepareTex("textures/instructions.png", True)

# Create texture for post processing shader.
texture_pp = pyglet.image.Texture.create_for_size(GL_TEXTURE_2D, OPENGL_SIZE_X, OPENGL_SIZE_Y, GL_RGBA)
color_buffer = pyglet.image.get_buffer_manager().get_color_buffer()

# Create draw batches.
batch_led = pyglet.graphics.Batch()
batch_metal_0 = pyglet.graphics.Batch()
batch_metal_1 = pyglet.graphics.Batch()
batch_simple_ground = pyglet.graphics.Batch()
batch_detailed_ground = pyglet.graphics.Batch()
batch_effect_red = pyglet.graphics.Batch()
batch_fade = pyglet.graphics.Batch()
batch_logo = pyglet.graphics.Batch()
batch_instructions = pyglet.graphics.Batch()
batch_fullscreen = pyglet.graphics.Batch()

# Create shaders.
shader_body = ShaderLoader('shaders/cm_body.vs', 'shaders/cm_body.fs')
shader_leds = ShaderLoader('shaders/led.vs', 'shaders/led.fs')
shader_ground = ShaderLoader('shaders/ground.vs', 'shaders/ground.fs')
shader_pp = ShaderLoader('shaders/post_processing.vs', 'shaders/post_processing.fs')

# Set texture units for shaders.
shader_body.shader.bind()
shader_body.shader.uniformi(b'tex0', 0)
shader_body.shader.unbind()

shader_leds.shader.bind()
shader_leds.shader.uniformi(b'tex0', 0)
shader_leds.shader.unbind()

shader_ground.shader.bind()
shader_ground.shader.uniformi(b'tex0', 0)
shader_ground.shader.unbind()

shader_pp.shader.bind()
shader_pp.shader.uniformi(b'tex0', 0)
shader_pp.shader.unbind()


# Set buffer clear color.
glClearColor(BG_COLOR[0] / 255.0, BG_COLOR[1] / 255.0, BG_COLOR[2] / 255.0, 1.0)

# Enable alpha blending.
glEnable(GL_BLEND)
glBlendEquation(GL_FUNC_ADD)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Enable depth testing.
glEnable(GL_DEPTH_TEST)

# This d parameter determines the size of the Connection Machine.
# It is only evaluated once when creating the geometry.
d = 1.5

# Draw center cube
gl.drawAllFaces(batch_metal_0, gl.getDeformedCube(3.33 * d, 3.33 * d, 3.33 * d), 0, 0, 0)

# Draw stand
gl.drawAllFaces(batch_metal_0, gl.getDeformedCube(2.833 * d, 0.5 * d, 2.833 * d), 0, -1.9 * d, 0)

# Facing front (4)
normalCube = gl.getDeformedCube(1.666 * d, 1.666 * d, 1.666 * d)
gl.drawAllFaces(batch_metal_1, normalCube, d, d, d)
gl.drawAllFaces(batch_metal_1, normalCube, -d, d, d)
gl.drawAllFaces(batch_metal_1, normalCube, d, -d, d)
gl.drawAllFaces(batch_metal_1, normalCube, -d, -d, d)

# Facing back (4)
gl.drawAllFaces(batch_metal_1, normalCube, d, d, -d)
gl.drawAllFaces(batch_metal_1, normalCube, -d, d, -d)
gl.drawAllFaces(batch_metal_1, normalCube, d, -d, -d)
gl.drawAllFaces(batch_metal_1, normalCube, -d, -d, -d)

# Draw ground with shadow.
for x in range(0, 12):
    gl.drawGround(batch_detailed_ground, 0, -2.2 * d + x * 0.004, 0, d)

gl.drawGround(batch_effect_red, 0, -2.2 * d - 0.004, 0, d)

# Simple ground
gl.drawGround(batch_simple_ground, 0, -2.2 * d + 11.0 * 0.004, 0, d)

# Draw flat overlays					
gl.drawOverlay(batch_fullscreen, 0, 0, 0, OPENGL_SIZE_X, OPENGL_SIZE_Y)
gl.drawOverlay(batch_fade, 0, 0, -0.001, OPENGL_SIZE_X, OPENGL_SIZE_Y)
gl.drawOverlay(batch_logo, 10, 5, -0.002, OPENGL_SIZE_X / 4.5, OPENGL_SIZE_Y / 13.5)
gl.drawOverlay(batch_instructions, 0, 0, -0.003, OPENGL_SIZE_X, OPENGL_SIZE_Y)

# Draw at 40 FPS, update random pattern at 1 Hz.
pyglet.clock.schedule_interval(schedule_update, 1.0 / OPENGL_FPS)
pyglet.clock.schedule_interval(schedule_leds, 1.0 / BLUETOOTH_FPS, d)
pyglet.clock.schedule_interval(schedule_randomize, 1 / 1.0)

# Randomize once so a random pattern is shown from the start.
schedule_randomize(0)

# Start bluetooth reader thread.
thread_bluetooth = Thread(target=bt.btreader, args=(10, ))
thread_bluetooth.start()

# Uncomment to start TCP reader thread.
# Not currently included/supported.
# thread_tcp_net = Thread(target = tcpreader, args = (10, ))
# thread_tcp_net.start()

# Run application.
pyglet.app.run()
