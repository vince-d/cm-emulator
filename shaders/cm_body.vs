// Version:	1.0
// Author:	Vincent Diener - diener@teco.edu

#version 110

varying vec3 N;
varying vec3 V;
	
void main() {
	// Transform the vertex position.
	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	
	// Pass transformed vertex position and normal to fragment shader.
	V = vec3(gl_ModelViewMatrix * gl_Vertex);
	N = normalize(gl_NormalMatrix * gl_Normal);
	
	// Pass through the texture coordinate.
	gl_TexCoord[0] = gl_MultiTexCoord0;
}