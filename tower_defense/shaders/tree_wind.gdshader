shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform sampler2D texture_albedo : source_color, filter_linear_mipmap, repeat_enable;
uniform vec4 color_tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float alpha_scissor_threshold : hint_range(0.0, 1.0) = 0.5;

uniform float wind_speed : hint_range(0.1, 5.0) = 1.4;
uniform float wind_strength : hint_range(0.0, 0.1) = 0.008;
uniform float leaf_flutter_strength : hint_range(0.0, 0.05) = 0.004;
uniform float leaf_flutter_speed : hint_range(0.1, 10.0) = 3.0;
uniform vec2 wind_direction = vec2(1.0, 0.4);

void vertex() {
	vec3 world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 norm_wind_dir = normalize(wind_direction);
	
	// Leaves Y range is 2.0 to 5.1 in local mesh space
	float height_factor = clamp((VERTEX.y - 2.0) / 3.12, 0.0, 1.0);
	float canopy_sway = 0.4 + 0.6 * height_factor;
	
	// Gentle wave
	float wave_phase = dot(world_pos.xz, norm_wind_dir) * 0.25 + TIME * wind_speed;
	float main_sway = sin(wave_phase) * wind_strength * canopy_sway;
	
	// Subtle flutter in the leaves
	float flutter = sin(TIME * leaf_flutter_speed + dot(VERTEX, vec3(12.9898, 78.233, 45.164))) * leaf_flutter_strength;
	
	float total_x = main_sway * norm_wind_dir.x + flutter;
	float total_z = main_sway * norm_wind_dir.y + flutter;
	
	VERTEX.x += total_x;
	VERTEX.z += total_z;
	VERTEX.y -= abs(main_sway) * 0.1;
}

void fragment() {
	vec4 tex_color = texture(texture_albedo, UV) * color_tint;
	ALBEDO = tex_color.rgb;
	ALPHA = tex_color.a;
	ALPHA_SCISSOR_THRESHOLD = alpha_scissor_threshold;
	ROUGHNESS = 0.85;
	SPECULAR = 0.15;
}
