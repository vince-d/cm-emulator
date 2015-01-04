// Version:	1.0
// Author:	Vincent Diener - diener@teco.edu

#version 110
	
void main() {
    // Transform the vertex position.
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	
    // Pass through the texture coordinate.
    gl_TexCoord[0] = gl_MultiTexCoord0;
}