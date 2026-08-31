shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

uniform vec4 color_base : source_color = vec4(0.08, 0.38, 0.06, 1.0);
uniform vec4 color_tip : source_color = vec4(0.28, 0.62, 0.12, 1.0);
uniform float wind_speed : hint_range(0.1, 5.0) = 1.6;
uniform float wind_strength : hint_range(0.0, 1.0) = 0.22;
uniform float wind_turbulence : hint_range(0.0, 2.0) = 0.6;
uniform vec2 wind_direction = vec2(1.0, 0.4);
uniform float grass_height : hint_range(0.1, 5.0) = 1.0;

varying float height_factor;

void vertex() {
	height_factor = clamp(VERTEX.y / grass_height, 0.0, 1.0);
	float sway_curve = pow(height_factor, 1.5);
	
	vec3 world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 norm_wind_dir = normalize(wind_direction);
	
	float wave_phase = dot(world_pos.xz, norm_wind_dir) * 0.5 + TIME * wind_speed;
	float main_wave = sin(wave_phase);
	float gust_wave = sin(wave_phase * 2.3 + world_pos.x * 0.8) * wind_turbulence;
	
	float total_sway = (main_wave + gust_wave * 0.4) * wind_strength * sway_curve;
	
	VERTEX.x += norm_wind_dir.x * total_sway;
	VERTEX.z += norm_wind_dir.y * total_sway;
	VERTEX.y -= abs(total_sway) * 0.25;
}

void fragment() {
	vec3 col = mix(color_base.rgb, color_tip.rgb, height_factor);
	ALBEDO = col;
	ROUGHNESS = 0.8;
	SPECULAR = 0.15;
	BACKLIGHT = color_tip.rgb * 0.3;
}
