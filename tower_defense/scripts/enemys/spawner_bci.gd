extends Node3D

## spawner_bci.gd
## Dedicated interactive spawner for Real-Time BCI Gameplay.
##
## Unlike calibration scenes (where the game automatically presses buttons),
## in this mode the tower is controlled EXCLUSIVELY by decoded brain rhythms
## via UDP on port 4242 (or manual player input).
##
## Spawns enemies wave by wave, announces target rhythms to imagine,
## and transmits high-precision markers over UDP on port 9000 to the Python pipeline.

const enemy_fire = preload("res://scenes/enemies/enemy_fire.tscn")
const enemy_water = preload("res://scenes/enemies/enemy_water.tscn")
const enemy_wind = preload("res://scenes/enemies/enemy_wind.tscn")
const enemy_electricity = preload("res://scenes/enemies/enemy_electricity.tscn")

const ENEMIES = [enemy_fire, enemy_water, enemy_wind, enemy_electricity]
const ELEMENT_NAMES = ["Fogo", "Água", "Vento", "Eletricidade"]
const RHYTHM_HINTS = [
	{"name": "Für Elise", "band": "Alpha (8-12 Hz)"},
	{"name": "Prelude in C Major", "band": "Theta (4-8 Hz)"},
	{"name": "The Four Seasons", "band": "Beta (13-30 Hz)"},
	{"name": "Waltz of the Flowers", "band": "Gamma (30-45 Hz)"}
]

@onready var UIManager = get_tree().get_first_node_in_group("UIManager")
@onready var spawner: Path3D = $"../EnemyPath"
@onready var bci = get_tree().get_first_node_in_group("BCI")

@export var waves: int = 5
@export var rest_duration: float = 2.5
@export var spawn_sequence: Array[int] = [0, 1, 2, 3] # Fire, Water, Wind, Electricity

var total_waves: int = 5
var current_wave: int = 1
var sequence_idx: int = 0
var active_enemy: Node3D = null
var defeated_count: int = 0
var is_game_over: bool = false

func _ready() -> void:
	if Engine.has_singleton("GameSettings") or get_node_or_null("/root/GameSettings"):
		var gs = get_node_or_null("/root/GameSettings")
		if gs:
			waves = gs.get_waves()
			
	total_waves = max(1, waves)
	current_wave = 1
	sequence_idx = 0
	defeated_count = 0
	
	print("[SpawnerBCI] Modo BCI Gameplay iniciado com %d ondas." % total_waves)
	_start_intro_and_first_wave()

func _start_intro_and_first_wave() -> void:
	if UIManager and UIManager.has_method("update_wave_info"):
		UIManager.update_wave_info(current_wave, total_waves)
		
	if UIManager and UIManager.has_method("show_instruction"):
		UIManager.show_instruction("Modo BCI: Prepara a mente!")
		
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("BCI_Gameplay_Started", 0.0)
		
	await get_tree().create_timer(2.0).timeout
	_spawn_next_enemy()

func get_counter_element(enemy_element: int) -> int:
	# Weakness mapping:
	# 0 (Fire) -> Counter is 1 (Water)
	# 1 (Water) -> Counter is 3 (Electricity)
	# 2 (Wind) -> Counter is 0 (Fire)
	# 3 (Electricity) -> Counter is 2 (Wind)
	match enemy_element:
		0: return 1 # Fire -> Water
		1: return 3 # Water -> Electricity
		2: return 0 # Wind -> Fire
		3: return 2 # Electricity -> Wind
		_: return 0

func _spawn_next_enemy() -> void:
	if is_game_over:
		return
		
	# Check if current wave completed
	if sequence_idx >= spawn_sequence.size():
		current_wave += 1
		sequence_idx = 0
		
		if current_wave > total_waves:
			_trigger_victory()
			return
		else:
			if UIManager and UIManager.has_method("show_instruction"):
				UIManager.show_instruction("Onda %d Concluída! Prepara-te..." % (current_wave - 1))
			if bci and bci.has_method("send_bci_marker"):
				bci.send_bci_marker("Wave_Completed_%d" % (current_wave - 1), 0.0)
			await get_tree().create_timer(3.0).timeout
			if is_game_over:
				return
				
	if UIManager and UIManager.has_method("update_wave_info"):
		UIManager.update_wave_info(current_wave, total_waves)
		
	var enemy_elem: int = spawn_sequence[sequence_idx]
	var counter_elem: int = get_counter_element(enemy_elem)
	var enemy_name: String = ELEMENT_NAMES[enemy_elem]
	var counter_name: String = ELEMENT_NAMES[counter_elem]
	var hint = RHYTHM_HINTS[counter_elem]
	
	# Send BCI markers to Python pipeline over UDP port 9000
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("Trial_Start_Enemy_" + enemy_name, 0.0)
		bci.send_bci_marker("Target_Imagine_" + counter_name, 0.0)
		
	# Update UI with tactical BCI briefing
	if UIManager and UIManager.has_method("set_target_briefing"):
		UIManager.set_target_briefing(enemy_elem, counter_elem)
	elif UIManager and UIManager.has_method("show_instruction"):
		UIManager.show_instruction("Inimigo: %s | Pensa no ritmo: %s (%s)" % [
			enemy_name.to_upper(),
			counter_name.to_upper(),
			hint["band"]
		])
		
	if UIManager and UIManager.has_method("change_next_element"):
		UIManager.change_next_element("Alvo: %s (Fraqueza: %s)" % [enemy_name, counter_name])
		
	# Instantiate enemy along the path
	var enemy_scene = ENEMIES[enemy_elem]
	var new_enemy = enemy_scene.instantiate()
	spawner.add_child(new_enemy)
	active_enemy = new_enemy
	
	sequence_idx += 1
	print("[SpawnerBCI] Spawned %s enemy. Target Counter: %s (%s)" % [
		enemy_name, counter_name, hint["name"]
	])

## Called by enemy.gd when an enemy is defeated or destroyed
func spawn_enemy(_force: bool = false, _specific_elem: int = -1) -> void:
	if is_game_over:
		return
		
	defeated_count += 1
	active_enemy = null
	
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("Enemy_Defeated", 0.0)
		bci.send_bci_marker("Rest_Start", 0.0)
		
	if UIManager and UIManager.has_method("show_instruction"):
		UIManager.show_instruction("Inimigo Derrotado! Descansa a mente...")
		
	if UIManager and UIManager.has_method("on_enemy_defeated"):
		UIManager.on_enemy_defeated()
		
	await get_tree().create_timer(rest_duration).timeout
	
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("Rest_End", 0.0)
		
	if not is_game_over:
		_spawn_next_enemy()

func kill_active_enemy() -> void:
	if active_enemy and is_instance_valid(active_enemy):
		if active_enemy.has_method("end"):
			active_enemy.end()

func _trigger_victory() -> void:
	print("[SpawnerBCI] VITÓRIA! Todas as ondas concluídas com sucesso.")
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("Game_Won_Victory", 0.0)
		
	if UIManager and UIManager.has_method("trigger_victory"):
		UIManager.trigger_victory(defeated_count, total_waves)
	elif UIManager and UIManager.has_method("show_instruction"):
		UIManager.show_instruction("VITÓRIA! Completaste todas as ondas com sucesso!")

func notify_game_over() -> void:
	is_game_over = true
	print("[SpawnerBCI] Game Over registrado.")
	if bci and bci.has_method("send_bci_marker"):
		bci.send_bci_marker("Game_Over_Defeat", 0.0)
