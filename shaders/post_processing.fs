// Version:	1.0
// Author:	Vincent Diener - diener@teco.edu

#version 110

uniform sampler2D tex0;

// Time (passed frames).
uniform int time;

// Width and height of input texture.
// In this case, it's the width and height of the color buffer.
uniform int tex_width;
uniform int tex_height;

// The size of the texture we get passed in might be rounded up th the
// nearest power of two, so before sampling it we need to make sure we
// transform the coordinates with the correct ratio. 
uniform float ratio_x;
uniform float ratio_y;

void pp_funct_0(vec2 uv) {
	// Calculate inverse of color. Set alpha to 1.
    vec4 color = texture2D(tex0, uv);		
    gl_FragColor = vec4(vec3(1.0) - color.rgb, 1.0);
} 

void pp_funct_1(vec2 uv) {
	// Alter x coordinate using the y coordinate and time to create wave effect.
	uv.x += sin(uv.y * 4.0*2.0*3.14159 + float(time) / 10.0) / 85.0;
	uv.y += sin(uv.x * 4.0*2.0*3.14159 + float(time) / 10.0) / 85.0;
    vec4 color = texture2D(tex0, uv);
	
	// Uncomment for a really trippy color effect.
	//color.r += sin((float(time + 12) + uv.x * 10.9 * uv.y * 91.9) / 40.0) / 4.0;	
	//color.g += cos((float(time + 55) + uv.x * 24.9 * uv.y * 10.9) / 32.0) / 3.0;	
	//color.b += cos((float(time + 23) + uv.x * 77.9 * uv.y * 13.9) / 88.0) / 2.0;	
    gl_FragColor = vec4(color.rgb, 1.0);
} 

void main()
{
	// Transform coordinates.
	vec2 uv = gl_TexCoord[0].st * vec2(ratio_x, ratio_y);
	pp_funct_1(uv);
}