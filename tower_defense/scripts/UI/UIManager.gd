extends CanvasLayer

const label_prefab = preload("res://scenes/lbl_text_log.tscn") 

@onready var tower = get_tree().get_first_node_in_group("tower")
@onready var logger = get_tree().get_first_node_in_group("logger")

@onready var lbl_element = $UI/VBox_element/lbl_element
@onready var log_container = $UI/PanelContainer/LogScrollBar/VBCLogs
@onready var log_scrollbar = $UI/PanelContainer/LogScrollBar
@onready var box_blink = $UI/VBoxBlinkContainer/BoxBlink

#botões
@onready var btn_fire = $UI/VBoxContainer/HBoxContainer/btn_fire
@onready var btn_water = $UI/VBoxContainer/HBoxContainer/btn_water
@onready var btn_wind = $UI/VBoxContainer/HBoxContainer/btn_wind
@onready var btn_electricity = $UI/VBoxContainer/HBoxContainer/btn_electricity

@onready var pause_menu = $PauseMenu

#corações
@onready var hearts = $UI/HealthBarContainer.get_children()

#texturas dos corações
var hearth_full = preload("res://assets/ui/Heart_Full.png")
var hearth_damage = preload("res://assets/ui/Heart_Empty.png")

#texturas dos botões
var fire_disable = preload("res://assets/icons/fire-zone.png")
var fire_enable = preload("res://assets/icons/fire_active.png")
var water_disable = preload("res://assets/icons/water-recycling.png")
var water_enable = preload("res://assets/icons/water_active.png")
var wind_disable = preload("res://assets/icons/wind-hole.png")
var wind_enable = preload("res://assets/icons/wind_active.png")
var electricity_disable = preload("res://assets/icons/electric.png")
var electricity_enable = preload("res://assets/icons/electric_active.png")

var current_hearth_index = 4

var blink_times = {
	"fire" : 0.2,
	"water" : 0.250,
	"earth" : 0.333,
	"wind" : 0.500
}

var box_blink_time = 0.250

#diferentes timers
var timer_fire : Timer
var timer_water : Timer
var timer_earth : Timer
var timer_wind : Timer

var timer_box_blink : Timer

var buttons_blink = false
var box_isblinking = false


var timers_list : Array[Timer] = []
var actual_index : int = 0
var timer_alter : Timer


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS # Permite que este nó continue ativo para despausar
	
	add_text_to_log("Sistema de Log/UI iniciado")
	
	#dá set aos timers
	#timer botão de fogo
	timer_fire = Timer.new()
	timer_fire.wait_time = blink_times["fire"]
	timer_fire.timeout.connect(_on_timer_fire_timeout)
	#timer botão de água
	timer_water = Timer.new()
	timer_water.wait_time = blink_times["water"]
	timer_water.timeout.connect(_on_timer_water_timeout)
	#timer botão de vento
	timer_wind = Timer.new()
	timer_wind.wait_time = blink_times["wind"]
	timer_wind.timeout.connect(_on_timer_wind_timeout)
	#timer botão de terra
	timer_earth = Timer.new()
	timer_earth.wait_time = blink_times["earth"]
	timer_earth.timeout.connect(_on_timer_earth_timeout)
	
	#adiciona os timers à cena
	add_child(timer_fire)
	add_child(timer_water)
	add_child(timer_wind)
	add_child(timer_earth)
	
	#coloca os timers na lista
	timers_list = [timer_fire, timer_water, timer_wind, timer_earth]
	
	#inicializa o timer que altera de 3 em 3 segundos
	timer_alter = Timer.new()
	timer_alter.wait_time = 3.0
	timer_alter.timeout.connect(_on_timer_alter_timeout)
	add_child(timer_alter)

	#configura o timer do quadrado
	timer_box_blink = Timer.new()
	timer_box_blink.wait_time = box_blink_time
	timer_box_blink.timeout.connect(_on_timer_box_blink_timeout)
	add_child(timer_box_blink)
	
	active_a_button(Weak_System.ELEMENT.Fire, false)
	

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("log"):
		log_scrollbar.visible = not log_scrollbar.visible
	
	if event.is_action_pressed("blink_buttons"):
		if buttons_blink:
			timer_alter.stop()
			timers_list[actual_index].stop()
			
			#ativa os botões
			btn_fire_enable()
			btn_water_enable()
			btn_wind_enable()
			btn_electricity_enable()
			
			buttons_blink = false
		else:
			#renicia o ciclo
			actual_index = 0
			timer_alter.start()
			timers_list[actual_index].start()

			buttons_blink = true
	elif event.is_action_pressed("box_blink"):
		if box_isblinking:
			logger.write_log("Box stop to blink")
			desactive_box_blink()
		else:
			logger.write_log("Box start to blink")
			active_box_blink()
	
	if event.is_action_pressed("pause"):	
		logger.write_log("Game paused")
		toggle_pause()

func active_box_blink():
	logger.write_log("Box start blinking")
	timer_box_blink.start()
	box_isblinking = true

func desactive_box_blink():
	logger.write_log("Box stop blinking")
	timer_box_blink.stop()
	box_isblinking = false
	
func _on_timer_alter_timeout() -> void:
	timers_list[actual_index].stop()
	_check_btn_active(actual_index)

	actual_index = (actual_index + 1) % timers_list.size()
	
	timers_list[actual_index].start()

func _check_btn_active(indice: int) -> void:
	match indice:
		0: btn_fire_enable()
		1: btn_water_enable()
		2: btn_wind_enable()
		3: btn_electricity_enable()

func _on_timer_fire_timeout():
	if btn_fire.disabled: #mostra o botão
		btn_fire_enable()
	else: #esconde o botão
		btn_fire_disable()

func _on_timer_water_timeout():
	if btn_water.disabled: #mostra o botão
		btn_water_enable()
	else: #esconde o botão
		btn_water_disable()
	
func _on_timer_wind_timeout():
	if btn_wind.disabled: #mostra o botão
		btn_wind_enable()
	else: #esconde o botão
		btn_wind_disable()

func _on_timer_earth_timeout():
	if btn_electricity.disabled: #mostra o botão
		btn_electricity_enable()
	else: #esconde o botão
		btn_electricity_disable() 

#função para o timer piscar
func _on_timer_box_blink_timeout():
	box_blink.visible = not box_blink.visible

#funções de ativação e desativação dos botões
func btn_fire_enable():
	btn_fire.modulate.a = 1.0  
	btn_fire.disabled = false	

func btn_fire_disable():
	btn_fire.modulate.a = 0.0 
	btn_fire.disabled = true
	
func btn_water_enable():
	btn_water.modulate.a = 1.0  
	btn_water.disabled = false

func btn_water_disable():
	btn_water.modulate.a = 0.0 
	btn_water.disabled = true
	
func btn_wind_enable():
	btn_wind.modulate.a = 1.0  
	btn_wind.disabled = false

func btn_wind_disable():
	btn_wind.modulate.a = 0.0 
	btn_wind.disabled = true

func btn_electricity_enable():
	btn_electricity.modulate.a = 1.0  
	btn_electricity.disabled = false

func btn_electricity_disable():
	btn_electricity.modulate.a = 0.0 
	btn_electricity.disabled = true

#função de clique em um botão de elemento
func on_button_power_clicket(element : Weak_System.ELEMENT, send_log: bool = true):
	if send_log:
		if element == Weak_System.ELEMENT.Fire:
			add_text_to_log("O jogador selecionou Fogo")
			logger.write_log("FIRE selected")
		elif element == Weak_System.ELEMENT.Water:
			add_text_to_log("O jogador selecionou Água")
			logger.write_log("WATER selected")
		elif element == Weak_System.ELEMENT.Wind:
			add_text_to_log("O jogador selecionou Vento")
			logger.write_log("WIND selected")
		elif element == Weak_System.ELEMENT.Electricity:
			add_text_to_log("O jogador selecionou Eletricidade")
			logger.write_log("ELECTRICITY selected")
		
	if tower: tower.change_element(element)

func _on_btn_fire_pressed() -> void:
	active_a_button(Weak_System.ELEMENT.Fire)

func _on_btn_water_pressed() -> void:
	active_a_button(Weak_System.ELEMENT.Water)

func _on_btn_wind_pressed() -> void:
	active_a_button(Weak_System.ELEMENT.Wind)

func _on_btn_electricity_pressed() -> void:
	active_a_button(Weak_System.ELEMENT.Electricity)

func active_a_button(element: Weak_System.ELEMENT, send_log: bool = true):
	_set_button_texture(btn_fire, fire_disable)
	_set_button_texture(btn_water, water_disable)
	_set_button_texture(btn_wind, wind_disable)
	_set_button_texture(btn_electricity, electricity_disable)
	
	match element:
		Weak_System.ELEMENT.Fire:
			_set_button_texture(btn_fire, fire_enable)
		Weak_System.ELEMENT.Water:
			_set_button_texture(btn_water, water_enable)
		Weak_System.ELEMENT.Wind:
			_set_button_texture(btn_wind, wind_enable)
		Weak_System.ELEMENT.Electricity:
			_set_button_texture(btn_electricity, electricity_enable)
			
	on_button_power_clicket(element, send_log)


func _set_button_texture(btn: Control, tex: Texture2D) -> void:
	if btn is TextureButton:
		btn.texture_normal = tex
	elif btn is Button:
		btn.icon = tex
	
func add_text_to_log(text):
	#espera que seja carregado
	if log_container == null:
		await get_tree().process_frame
		
	var new_label = label_prefab.instantiate()
	new_label.text = format_text(text);
	log_container.add_child(new_label) 
	#vai seguindo o texto	
	await get_tree().process_frame
	log_scrollbar.scroll_vertical = int(log_container.size.y)
	
func format_text(text):
	var hour = Time.get_time_string_from_system()
	return "[" + hour + "] " + text

func change_next_element(text):
	lbl_element.text = text

func _on_btn_quit_pressed() -> void:
	get_tree().paused = false 
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_btn_resume_pressed() -> void:
	logger.write_log("Game unpaused")
	toggle_pause()

func toggle_pause() -> void:
	#inverte o estado
	get_tree().paused = !get_tree().paused
	pause_menu.visible = get_tree().paused

func take_hearth() -> void:
	if current_hearth_index < 0:
		print("Morreu")
	else:
		hearts[current_hearth_index].texture = hearth_damage
		current_hearth_index-=1

func heal() -> void:
	if current_hearth_index < 4:
		current_hearth_index += 1
		hearts[current_hearth_index].texture = hearth_full
		add_text_to_log("O Feiticeiro curou o jogador!")
		logger.write_log("Player healed by Wizard")
