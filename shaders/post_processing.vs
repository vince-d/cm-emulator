// Version:	1.0
// Author:	Vincent Diener - diener@teco.edu

#version 110

varying vec3 N;
varying vec3 V;
	
void main() {
	// Transform the vertex position.
	gl_Position = ftransform();
	
	// Pass through the texture coordinate.
	gl_TexCoord[0] = gl_MultiTexCoord0;
}