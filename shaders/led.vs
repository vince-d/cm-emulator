// Version:	1.0
// Author:	Vincent Diener - diener@teco.edu

#version 110

varying vec4 red;
	
void main() {
    // Transform the vertex position.
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	
    // Pass through the texture coordinate.
    gl_TexCoord[0] = gl_MultiTexCoord0;
	gl_TexCoord[1] = gl_MultiTexCoord1;
	
	// Red value is passed in through gl_Color attribute.
	red = gl_Color;
}