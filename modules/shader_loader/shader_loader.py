# Version:	1.0
# Author:	Vincent Diener - diener@teco.edu

from modules.shader.shader import Shader

class ShaderLoader:
	# Return vert+frag shader compiled from files.
	def __init__(self, vert_path, frag_path):
		# Load shaders from file.
		vert_str = self.readShader(vert_path)
		frag_str = self.readShader(frag_path)
		
		# Compile shaders.
		self.shader = self.makeShader(vert_str, frag_str)

	# Read file and return contents.
	def readShader(self, path):
		shader_f = open(path, 'r')
		return shader_f.read()
	
	# Compile shaders.
	def makeShader(self, vertex_str, frag_str):
		return Shader([vertex_str], [frag_str])