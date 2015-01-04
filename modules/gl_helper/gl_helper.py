# Version:	1.0
# Author:	Vincent Diener - diener@teco.edu

import numpy
import pyglet

from pyglet.gl import *
from pyglet.window import *
from ctypes import *

# Helper class for creating the Connection Machine geometry
# and other things related to OpenGL.
class GLHelper:
	# Initialize.
	def __init__(self, width, height):
		# Gets set to false after the first draw call.
		self.firstDrawCall = True
		
		# List of all coordinates (x, y, z) of all LED-vertices.
		self.vertices = list()

		# List of all texture coordinates (u, v) of all LED-vertices.
		self.texCoords = list()
		
		# Vertex list returned by Batch.add(...).
		# This list can be used to change the vertex attributes.
		self.vlist = list()
		
		# The red values in a format we can pass to the shader.
		self.values = list()
		
		# Width and height of the OpenGL viewport.
		# Gets updated when the window is resized.
		self.gl_x = width
		self.gl_y = height
		
	# Create array of GLfloats from regular float array.
	def vec(self, *args):
		return (GLfloat * len(args))(*args)
		
	# Returns a cube, stretched along the x, y and z axis.
	# For (1, 1, 1), this returns a regular cube. 
	def getDeformedCube(self, x, y, z):
		cube = [[[0,0,0] for a in xrange(4)] for b in xrange(6)]
		
		x /= 2.0
		y /= 2.0
		z /= 2.0

		cube[0][0] = [  1.0 * x,  1.0 * y, -1.0 * z]
		cube[0][1] = [ -1.0 * x,  1.0 * y, -1.0 * z]
		cube[0][2] = [ -1.0 * x,  1.0 * y,  1.0 * z]
		cube[0][3] = [  1.0 * x,  1.0 * y,  1.0 * z]

		cube[1][0] = [  1.0 * x, -1.0 * y, -1.0 * z]
		cube[1][1] = [ -1.0 * x, -1.0 * y, -1.0 * z]
		cube[1][3] = [  1.0 * x, -1.0 * y,  1.0 * z]
		cube[1][2] = [ -1.0 * x, -1.0 * y,  1.0 * z]

		cube[2][0] = [  1.0 * x,  1.0 * y,  1.0 * z]
		cube[2][1] = [ -1.0 * x,  1.0 * y,  1.0 * z]
		cube[2][2] = [ -1.0 * x, -1.0 * y,  1.0 * z]
		cube[2][3] = [  1.0 * x, -1.0 * y,  1.0 * z]

		cube[3][0] = [  1.0 * x, -1.0 * y, -1.0 * z]
		cube[3][1] = [ -1.0 * x, -1.0 * y, -1.0 * z]
		cube[3][2] = [ -1.0 * x,  1.0 * y, -1.0 * z]
		cube[3][3] = [  1.0 * x,  1.0 * y, -1.0 * z]

		cube[4][0] = [ -1.0 * x,  1.0 * y,  1.0 * z]
		cube[4][1] = [ -1.0 * x,  1.0 * y, -1.0 * z]
		cube[4][2] = [ -1.0 * x, -1.0 * y, -1.0 * z]
		cube[4][3] = [ -1.0 * x, -1.0 * y,  1.0 * z]

		cube[5][0] = [  1.0 * x,  1.0 * y,  1.0 * z]
		cube[5][1] = [  1.0 * x,  1.0 * y, -1.0 * z]
		cube[5][2] = [  1.0 * x, -1.0 * y, -1.0 * z]
		cube[5][3] = [  1.0 * x, -1.0 * y,  1.0 * z]

		return cube

	# Prepares a texture so it can by used by OpenGL.
	# If enableAlpha is True, the texture may contain transparency.
	def prepareTex(self, fileName, enableAlpha):
		image = pyglet.image.load(fileName)
		texture = image.get_texture()
		glEnable(texture.target)
		glBindTexture(texture.target, texture.id)

		# Check if alpha is enabled for texture.
		if (enableAlpha):
			# If so, read RGBA.
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, (image.width), (image.height), 0, GL_RGBA, GL_UNSIGNED_BYTE, image.get_image_data().get_data('RGBA', image.width * 4))
		else :
			# If not, read RGB.
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, (image.width), (image.height), 0, GL_RGB, GL_UNSIGNED_BYTE, image.get_image_data().get_data('RGB', image.width * 3))

		return texture
		
	# Draw all faces of a given cube to a given batch at the given position.
	def drawAllFaces(self, batchToUse, cube, transX, transY, transZ):
		# Top face
		self.cubeFace(batchToUse, cube[0], transX, transY, transZ)

		# Bottom face
		self.cubeFace(batchToUse, cube[1], transX, transY, transZ)

		# Front face
		self.cubeFace(batchToUse, cube[2], transX, transY, transZ)

		# Back face
		self.cubeFace(batchToUse, cube[3], transX, transY, transZ)

		# Left face
		self.cubeFace(batchToUse, cube[4], transX, transY, transZ)

		# Right face
		self.cubeFace(batchToUse, cube[5], transX, transY, transZ)
	
	# Draw a ground quad to the given batch at the given position.
	def drawGround(self, batchToUse, x, y, z, d):
		groundsize = 4.66
		batchToUse.add(	4,
						GL_QUADS,
						None,
						('v3f', (groundsize * d+x, 0+y, -groundsize * d+z, groundsize * d+x,
								 0+y, groundsize * d+z, -groundsize * d+x, 0+y,
								 groundsize * d+z, -groundsize * d+x, 0+y, -groundsize * d+z)),
						('t2f', (0,0, 1.0,0, 1.0,1.0, 0,1.0)))

	# Draw one cube face of the given cube to the given batch at the given position.
	def cubeFace(self, batchToUse, cube, x, y, z):

		v1Minusv2 = [cube[0][0] - cube[1][0], cube[0][1] - cube[1][1], cube[0][2] - cube[1][2]]
		v1Minusv3 = [cube[0][0] - cube[2][0], cube[0][1] - cube[2][1], cube[0][2] - cube[2][2]]
		crPro = numpy.cross(v1Minusv2, v1Minusv3)

		batchToUse.add(	4,
					GL_QUADS,
					None,
					('v3f', (cube[0][0]+x, cube[0][1]+y, cube[0][2]+z, cube[1][0]+x, cube[1][1]+y, cube[1][2]+z, cube[2][0]+x, cube[2][1]+y, cube[2][2]+z, cube[3][0]+x, cube[3][1]+y, cube[3][2]+z)),
					('t2f', (0,0, 1.0,0, 1.0,1.0, 0,1.0)),
					('n3f', (crPro[0], crPro[1], crPro[2], crPro[0], crPro[1], crPro[2], crPro[0], crPro[1], crPro[2], crPro[0], crPro[1], crPro[2])))

	# Draw a flat screen overlay of given size and position to the given batch.
	# z value is used for ordering between overlays.
	def drawOverlay(self, batchToUse, x, y, zOrder, width, height):
		y = self.gl_y - y - height
		batchToUse.add	(4, GL_QUADS, None,
						('v3f', (x, y, zOrder, x + width, y, zOrder, x + width, y + height, zOrder, x, y + height, zOrder)),
						('t2f', (0,0,1,0,1,1,0,1)))
						
	# Update the 576 LEDs at the front of the Connection Machine.
	def drawAllLeds(self, batchToUse, matrix, d):
		# Common offsets for LEDs.
		base = -1.65 * d
		m = 0.113 * d

		# LED counter.
		counter = 0
		
		# Create a list of all vertices and their coordinates, but only on
		# the first draw call. After that, we can just change their parameters
		# to update them, without having to call Batch.add(...) again.
		if (self.firstDrawCall):
			# Loop over all LED quads.
			for x in range (0,24) :
				# X offset.
				xOff = base + m * x	
				if (x >= 12) :
					xOff += d * 0.6
				
				for y in range (0,24) :
					# Y offset.
					yOff = base + m * y
					if (y >= 12) :
						yOff += d * 0.6
					
					# Fill vertex and coordinate list.
					self.vertices.extend((0+xOff, 0+yOff, 1.85 * d,
										 m+xOff, 0+yOff, 1.85 * d,
										 m+xOff, m+yOff, 1.85 * d,
										 0+xOff, m+yOff, 1.85 * d))
										 
					self.texCoords.extend((0,0,1,0,1,1,0,1))
										 
	
		# Get current LED red values and bring them into a format that we can
		# pass to the shader.
		self.values = []
		for x in range (0, 576):
			red = matrix[x]
			self.values.extend([red for x in xrange(16)])
			
		# On the first draw call, add all vertices to the draw batch.
		# Any subsequent draw calls can just modify that batch.
		if (self.firstDrawCall):	
			# Add LED to batch.
			self.vlist = batchToUse.add(4 * 576, GL_QUADS, None,
										('v3f/static', self.vertices),
										('t2f/static', self.texCoords),
										('c4f/stream', self.values))
		else:
			self.vlist.colors = list(self.values)
			
		# First draw call is over.
		self.firstDrawCall = False							