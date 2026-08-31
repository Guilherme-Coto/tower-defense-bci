shader_type spatial;
render_mode blend_add, cull_disabled, unshaded;

uniform vec4 core_color : source_color = vec4(1.0, 0.4, 0.05, 1.0);
uniform vec4 rim_color : source_color = vec4(1.0, 0.9, 0.2, 1.0);
uniform float emission_energy : hint_range(1.0, 15.0) = 4.0;
uniform float fresnel_power : hint_range(0.5, 5.0) = 2.0;

void fragment() {
	float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), fresnel_power);
	vec3 col = mix(core_color.rgb, rim_color.rgb, fresnel) * emission_energy;
	ALBEDO = col;
	ALPHA = mix(0.6, 1.0, fresnel);
}
