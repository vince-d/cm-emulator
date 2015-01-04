// Version:	1.0
// Author:	Vincent Diener - diener@teco.edu

#version 110

uniform sampler2D tex0;
uniform int time;
uniform bool do_light;

varying vec3 N;
varying vec3 V;

void main() {
	// Calculate fade factor from time for 50 frame fade in.
	float fade = max(50.0 - float(time), 0.0) / 50.0;
   
	// Get texture coordinate.
	vec2 c = gl_TexCoord[0].xy;
 
	// Get current pixel.
	vec4 current = texture2D(tex0, c).rgba;
	
	// Add lighting?
	if (do_light) {
		vec3 L = normalize(gl_LightSource[0].position.xyz - V);   
	 
		// Calculate ambient light.  
		vec4 amb = gl_LightSource[0].ambient;    

		//calculate Diffuse Term:  
		vec4 diff = gl_LightSource[0].diffuse * max(dot(normalize(N), L), 0.0);
		diff = clamp(diff, 0.0, 1.0);     
		vec3 out_col = clamp((current * (amb + diff)).rgb, 0.0, 1.0);
		
		gl_FragColor = vec4(out_col.rgb, current.a * fade);
	} else {
		// If not, just use texture color.
		gl_FragColor = vec4(current.rgb, current.a * fade);
	}
}