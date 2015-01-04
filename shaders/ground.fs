// Version:	1.0
// Author:	Vincent Diener - diener@teco.edu

#version 110

uniform sampler2D tex0;
uniform int time;

void main() {
	// Get texture coordinate.
	vec2 c = gl_TexCoord[0].xy;
 
	// Only get alpha value.
	vec4 color = vec4(0.0, 0.0, 0.0, texture2D(tex0, c).a);

	// Red flash effect.
	vec2 from_middle = vec2(0.5, 0.5) - c;
	color.r =  0.5 - ((length(from_middle)));
	color.r += pow(1.0 - distance(normalize(from_middle) * sin(mod(float(time), 140.0) / -30.0), from_middle), 20.0);
   
	// Write fragment.
	gl_FragColor = color;
}