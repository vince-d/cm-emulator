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

vec2 rOffset = vec2(0.005, 0.005);
vec2 gOffset = vec2(0.002, 0.002);
vec2 bOffset = vec2(0.003, 0.003);

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

// Chromatic aberration
void pp_funct_2(vec2 uv) {	
	float timeMult = (sin(float(time) / 30.0) + 1.0) / 2.0;

	vec2 toMiddle = uv - vec2(0.5 * ratio_x, 0.5 * ratio_y);
	float ml = pow(length(toMiddle), timeMult);
	vec2 uv2 = toMiddle * pow(1.005, timeMult * 4.0) + vec2(0.5 * ratio_x, 0.5 * ratio_y);
	vec2 uv3 = toMiddle * pow(0.995, timeMult * 2.0) + vec2(0.5 * ratio_x, 0.5 * ratio_y);
	vec2 uv4 = toMiddle * pow(1.006, timeMult * 3.0) + vec2(0.5 * ratio_x, 0.5 * ratio_y);

    vec4 rValue = texture2D(tex0, uv2);  
    vec4 gValue = texture2D(tex0, uv3);
    vec4 bValue = texture2D(tex0, uv4);  

	vec2 a = vec2(0.005, 0.01);
	vec2 b = vec2(0.00, 0.00);
	vec2 c = vec2(-0.005, 0.005);
	vec2 d = vec2(0.005, -0.005);
	
	rValue += texture2D(tex0, uv2 + uv2 * ml * a);
	rValue += texture2D(tex0, uv2 + uv2 * ml * b);
	rValue += texture2D(tex0, uv2 + uv2 * ml * c);
	rValue += texture2D(tex0, uv2 + uv2 * ml * d);
	
	gValue += texture2D(tex0, uv3 + uv3 * ml * a);
	gValue += texture2D(tex0, uv3 + uv3 * ml * b);
	gValue += texture2D(tex0, uv3 + uv3 * ml * c);
	gValue += texture2D(tex0, uv3 + uv3 * ml * d);
	
	bValue += texture2D(tex0, uv4 + uv4 * ml * a);
	bValue += texture2D(tex0, uv4 + uv4 * ml * b);
	bValue += texture2D(tex0, uv4 + uv4 * ml * c);
	bValue += texture2D(tex0, uv4 + uv4 * ml * d);
	
	gl_FragColor = vec4(rValue.r / 5.0, gValue.g / 5.0, bValue.b / 5.0, 1.0);

} 

// Zoom
void pp_funct_3(vec2 uv) {	
	vec2 distToMiddle = (uv - vec2(0.5 * ratio_x, 0.5 * ratio_y));
	
	float timeMult = (sin(float(time) / 49.0) + 1.0) * 45.4;
	distToMiddle *= timeMult;
	//float a = (distToMiddle) * 10.6;
    vec4 rValue = texture2D(tex0, uv - rOffset + distToMiddle);  
    vec4 gValue = texture2D(tex0, uv - gOffset + distToMiddle);
    vec4 bValue = texture2D(tex0, uv - bOffset + distToMiddle);  


	gl_FragColor = vec4(rValue.r, gValue.g, bValue.b, 1.0);

} 

void main()
{
	// Transform coordinates.
	vec2 uv = gl_TexCoord[0].st * vec2(ratio_x, ratio_y);
	pp_funct_1(uv);
}