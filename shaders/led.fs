// Version:	1.0
// Author:	Vincent Diener - diener@teco.edu

#version 110

uniform sampler2D tex0;
uniform int time;

// Red value.
varying vec4 red;

void main() {

	// Get texture coordinate.
	vec2 c = gl_TexCoord[0].xy;
 
	// Get pixel.
	vec4 color = texture2D(tex0, c).rgba;
	
	// Get red value.
	color.r = red.r;
	color.g = 0.0;
	color.b = 0.0;

	// Write fragment.
	gl_FragColor = color;
}