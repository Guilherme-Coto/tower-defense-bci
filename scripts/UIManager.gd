extends MarginContainer

const label_prefab = preload("res://scenes/lbl_text_log.tscn") 

@onready var tower = get_tree().get_first_node_in_group("tower")
@onready var lbl_element = $VBox_element/lbl_element
@onready var log_container = $PanelContainer/LogScrollBar/VBCLogs
@onready var log_scrollbar = $PanelContainer/LogScrollBar

func _ready() -> void:
	add_text_to_log("Sistema de Log/UI iniciado")

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("log"):
		log_scrollbar.visible = not log_scrollbar.visible
		
func on_button_power_clicket(element : Weak_System.ELEMENT):
	if element == Weak_System.ELEMENT.Fire:
		lbl_element.text = "Fogo"
		add_text_to_log("O jogador selecionou Fogo")
	elif element == Weak_System.ELEMENT.Water:
		lbl_element.text = "Água"
		add_text_to_log("O jogador selecionou Água")
	elif element == Weak_System.ELEMENT.Wind:
		lbl_element.text = "Vento"
		add_text_to_log("O jogador selecionou Vento")
	elif element == Weak_System.ELEMENT.Earth:
		lbl_element.text = "Terra"
		add_text_to_log("O jogador selecionouTerra")

	tower.change_element(element)

func _on_btn_fire_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Fire)

func _on_btn_water_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Water)

func _on_btn_wind_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Wind)

func _on_btn_earth_pressed() -> void:
	on_button_power_clicket(Weak_System.ELEMENT.Earth)

func add_text_to_log(text):
	#espera que seja carregado
	if log_container == null:
		await get_tree().process_frame
		
	var new_label = label_prefab.instantiate()
	new_label.text = format_text(text);
	log_container.add_child(new_label) 
	#vai seguindo o texto	
	log_scrollbar.scroll_vertical = log_container.size.y
	
func format_text(text):
	var hour = Time.get_time_string_from_system()
	return "[" + hour + "] " + text
