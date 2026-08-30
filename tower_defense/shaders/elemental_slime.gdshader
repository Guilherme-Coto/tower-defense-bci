shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform vec4 core_color : source_color = vec4(1.0, 0.3, 0.05, 1.0);
uniform vec4 rim_color : source_color = vec4(1.0, 0.8, 0.2, 1.0);
uniform float emission_energy : hint_range(0.0, 10.0) = 2.5;
uniform float pulse_speed : hint_range(0.1, 10.0) = 3.0;
uniform float wobble_amount : hint_range(0.0, 0.5) = 0.08;
uniform float wobble_speed : hint_range(0.1, 10.0) = 4.0;
uniform float fresnel_power : hint_range(0.5, 6.0) = 2.5;
uniform float roughness : hint_range(0.0, 1.0) = 0.2;
uniform float metallic : hint_range(0.0, 1.0) = 0.1;
uniform float alpha_transparency : hint_range(0.0, 1.0) = 0.95;
uniform bool is_hit = false;

void vertex() {
	// Bouncy organic wobble / pulse
	float wobble = sin(TIME * wobble_speed + VERTEX.y * 5.0) * wobble_amount;
	float wobble_x = cos(TIME * (wobble_speed * 0.8) + VERTEX.z * 4.0) * (wobble_amount * 0.7);
	
	VERTEX += NORMAL * (wobble + wobble_x);
	
	// Slight squish and stretch idle breathing
	float breath = sin(TIME * pulse_speed) * 0.04;
	VERTEX.y *= (1.0 + breath);
	VERTEX.xz *= (1.0 - breath * 0.5);
}

void fragment() {
	if (is_hit) {
		// Hit flash effect
		ALBEDO = vec3(1.0, 1.0, 1.0);
		EMISSION = vec3(2.5, 2.5, 2.5);
		ALPHA = 1.0;
	} else {
		// Fresnel glow calculation
		float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), fresnel_power);
		
		// Pulsing emission
		float pulse = 0.85 + 0.15 * sin(TIME * pulse_speed);
		
		vec3 base_col = mix(core_color.rgb, rim_color.rgb, fresnel);
		ALBEDO = base_col;
		
		// Glowing edges with HDR emission for glow/bloom
		EMISSION = rim_color.rgb * fresnel * emission_energy * pulse + core_color.rgb * 0.35;
		
		ROUGHNESS = roughness;
		METALLIC = metallic;
		ALPHA = mix(alpha_transparency, 1.0, fresnel * 0.5);
	}
}
