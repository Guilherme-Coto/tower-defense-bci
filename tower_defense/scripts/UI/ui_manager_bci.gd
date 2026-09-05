extends "res://scripts/UI/UIManager.gd"

## ui_manager_bci.gd
## Enhanced UI Manager specifically designed for Interactive BCI Gameplay.
## Displays:
##   - Real-time Enemy & Counter-Rhythm briefing
##   - Tower Effectiveness status (2x Damage / Ineffective)
##   - Live BCI UDP command pulse indicator
##   - Victory & Game Over screens
##   - Keyboard hotkeys (1, 2, 3, 4) for manual control fallback

const ELEM_NAMES = ["FOGO", "ÁGUA", "VENTO", "ELETRICIDADE"]
const ELEM_COLORS = [
	Color(1.0, 0.35, 0.1), # Fire: Orange-Red
	Color(0.2, 0.7, 1.0),  # Water: Blue
	Color(0.3, 0.9, 0.4),  # Wind: Green
	Color(1.0, 0.9, 0.2)   # Electricity: Yellow
]

const RHYTHMS = [
	{"song": "Für Elise", "band": "Alpha (8-12 Hz)"},
	{"song": "Prelude in C Major", "band": "Theta (4-8 Hz)"},
	{"song": "The Four Seasons", "band": "Beta (13-30 Hz)"},
	{"song": "Waltz of the Flowers", "band": "Gamma (30-45 Hz)"}
]

var cur_enemy_elem: int = -1
var cur_counter_elem: int = -1
var bci_switches_total: int = 0

# UI Overlay references
var bci_hud_panel: PanelContainer
var lbl_bci_enemy: Label
var lbl_bci_rhythm: Label
var lbl_bci_status: Label
var lbl_bci_pulse: Label

var end_panel: PanelContainer
var lbl_end_title: Label
var lbl_end_msg: Label
var btn_end_restart: Button
var btn_end_menu: Button

func _ready() -> void:
	super._ready()
	_create_bci_hud()
	_create_end_overlays()
	
	# Listen for BCI signals from BciReceiver singleton if present
	if Engine.has_singleton("BciReceiver") or get_node_or_null("/root/BciReceiver"):
		var bci_rx = get_node_or_null("/root/BciReceiver")
		if bci_rx and not bci_rx.bci_power_received.is_connected(_on_bci_power_signal):
			bci_rx.bci_power_received.connect(_on_bci_power_signal)

func _create_bci_hud() -> void:
	bci_hud_panel = PanelContainer.new()
	bci_hud_panel.name = "BciHudPanel"
	
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.06, 0.08, 0.12, 0.88)
	style.border_width_bottom = 2
	style.border_width_left = 2
	style.border_width_right = 2
	style.border_width_top = 2
	style.border_color = Color(0.25, 0.5, 0.8, 0.7)
	style.corner_radius_bottom_left = 8
	style.corner_radius_bottom_right = 8
	style.corner_radius_top_left = 8
	style.corner_radius_top_right = 8
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	bci_hud_panel.add_theme_stylebox_override("panel", style)
	
	bci_hud_panel.set_anchors_preset(Control.PRESET_CENTER_TOP)
	bci_hud_panel.position = Vector2(0, 16)
	bci_hud_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 4)
	vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	
	lbl_bci_enemy = Label.new()
	lbl_bci_enemy.text = "Inimigo: A aguardar spawn..."
	lbl_bci_enemy.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_bci_enemy.add_theme_font_size_override("font_size", 18)
	lbl_bci_enemy.add_theme_color_override("font_color", Color(1.0, 1.0, 1.0))
	vbox.add_child(lbl_bci_enemy)
	
	lbl_bci_rhythm = Label.new()
	lbl_bci_rhythm.text = "Sugestão BCI: Foca-te no ritmo mental correspondente"
	lbl_bci_rhythm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_bci_rhythm.add_theme_font_size_override("font_size", 15)
	lbl_bci_rhythm.add_theme_color_override("font_color", Color(0.7, 0.85, 1.0))
	vbox.add_child(lbl_bci_rhythm)
	
	var hbox_status = HBoxContainer.new()
	hbox_status.alignment = BoxContainer.ALIGNMENT_CENTER
	hbox_status.add_theme_constant_override("separation", 20)
	
	lbl_bci_status = Label.new()
	lbl_bci_status.text = "Torre: FOGO [NORMAL]"
	lbl_bci_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_bci_status.add_theme_font_size_override("font_size", 14)
	hbox_status.add_child(lbl_bci_status)
	
	lbl_bci_pulse = Label.new()
	lbl_bci_pulse.text = "BCI UDP: 127.0.0.1:4242 pronto"
	lbl_bci_pulse.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_bci_pulse.add_theme_font_size_override("font_size", 13)
	lbl_bci_pulse.add_theme_color_override("font_color", Color(0.6, 0.9, 0.6))
	hbox_status.add_child(lbl_bci_pulse)
	
	vbox.add_child(hbox_status)
	bci_hud_panel.add_child(vbox)
	
	$UI.add_child(bci_hud_panel)
	
	# Reposition top center
	await get_tree().process_frame
	if bci_hud_panel and is_instance_valid(bci_hud_panel):
		bci_hud_panel.set_anchors_preset(Control.PRESET_CENTER_TOP)

func _create_end_overlays() -> void:
	end_panel = PanelContainer.new()
	end_panel.name = "EndPanel"
	end_panel.visible = false
	
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.04, 0.05, 0.08, 0.94)
	style.border_width_bottom = 3
	style.border_width_left = 3
	style.border_width_right = 3
	style.border_width_top = 3
	style.border_color = Color(0.3, 0.6, 0.9, 0.8)
	style.corner_radius_bottom_left = 12
	style.corner_radius_bottom_right = 12
	style.corner_radius_top_left = 12
	style.corner_radius_top_right = 12
	style.content_margin_left = 32
	style.content_margin_right = 32
	style.content_margin_top = 24
	style.content_margin_bottom = 24
	end_panel.add_theme_stylebox_override("panel", style)
	
	end_panel.set_anchors_preset(Control.PRESET_CENTER)
	
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 16)
	vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	
	lbl_end_title = Label.new()
	lbl_end_title.text = "FIM DE JOGO"
	lbl_end_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_end_title.add_theme_font_size_override("font_size", 32)
	vbox.add_child(lbl_end_title)
	
	lbl_end_msg = Label.new()
	lbl_end_msg.text = "Estatísticas do jogo"
	lbl_end_msg.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_end_msg.add_theme_font_size_override("font_size", 18)
	vbox.add_child(lbl_end_msg)
	
	var hbox_btns = HBoxContainer.new()
	hbox_btns.alignment = BoxContainer.ALIGNMENT_CENTER
	hbox_btns.add_theme_constant_override("separation", 24)
	
	btn_end_restart = Button.new()
	btn_end_restart.text = "Jogar Novamente"
	btn_end_restart.custom_minimum_size = Vector2(170, 48)
	btn_end_restart.pressed.connect(_on_btn_restart_pressed)
	hbox_btns.add_child(btn_end_restart)
	
	btn_end_menu = Button.new()
	btn_end_menu.text = "Menu Principal"
	btn_end_menu.custom_minimum_size = Vector2(170, 48)
	btn_end_menu.pressed.connect(_on_btn_quit_pressed)
	hbox_btns.add_child(btn_end_menu)
	
	vbox.add_child(hbox_btns)
	end_panel.add_child(vbox)
	$UI.add_child(end_panel)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1:
				active_a_button(Weak_System.ELEMENT.Fire)
			KEY_2:
				active_a_button(Weak_System.ELEMENT.Water)
			KEY_3:
				active_a_button(Weak_System.ELEMENT.Wind)
			KEY_4:
				active_a_button(Weak_System.ELEMENT.Electricity)

func set_target_briefing(enemy_elem: int, counter_elem: int) -> void:
	cur_enemy_elem = enemy_elem
	cur_counter_elem = counter_elem
	
	var e_name = ELEM_NAMES[enemy_elem]
	var c_name = ELEM_NAMES[counter_elem]
	var r_info = RHYTHMS[counter_elem]
	
	if lbl_bci_enemy:
		lbl_bci_enemy.text = "INIMIGO APROXIMANDO: %s" % e_name
		lbl_bci_enemy.add_theme_color_override("font_color", ELEM_COLORS[enemy_elem])
		
	if lbl_bci_rhythm:
		lbl_bci_rhythm.text = "Pensa no ritmo: %s  (%s - %s)" % [
			c_name,
			r_info["song"],
			r_info["band"]
		]
		
	update_effectiveness_display()

func _on_bci_power_signal(elem_id: int) -> void:
	notify_bci_switch(elem_id)

func notify_bci_switch(elem_id: int) -> void:
	bci_switches_total += 1
	var elem_name = ELEM_NAMES[elem_id]
	add_text_to_log("BCI decodificou: " + elem_name + " (power:%d)" % elem_id)
	
	if lbl_bci_pulse:
		lbl_bci_pulse.text = "Sinal BCI: %s (detectado!)" % elem_name
		lbl_bci_pulse.add_theme_color_override("font_color", ELEM_COLORS[elem_id])
		
		var tween = create_tween()
		tween.tween_property(lbl_bci_pulse, "modulate", Color(2.0, 2.0, 2.0, 1.0), 0.1)
		tween.tween_property(lbl_bci_pulse, "modulate", Color(1.0, 1.0, 1.0, 1.0), 0.4)
		
	update_effectiveness_display()

func active_a_button(element: Weak_System.ELEMENT, send_log: bool = true) -> void:
	super.active_a_button(element, send_log)
	update_effectiveness_display()

func update_effectiveness_display() -> void:
	if not tower or not lbl_bci_status:
		return
		
	var cur_elem = tower.current_element
	var elem_name = ELEM_NAMES[cur_elem]
	
	if cur_enemy_elem != -1:
		var mult = Weak_System.get_damage_mult(cur_elem, cur_enemy_elem)
		if mult >= 2.0:
			lbl_bci_status.text = "Torre: %s [EFICAZ! DANO 2X]" % elem_name
			lbl_bci_status.add_theme_color_override("font_color", Color(0.3, 1.0, 0.3))
		elif mult <= 0.0:
			lbl_bci_status.text = "Torre: %s [NULO! 0x DANO]" % elem_name
			lbl_bci_status.add_theme_color_override("font_color", Color(1.0, 0.2, 0.2))
		elif mult < 1.0:
			lbl_bci_status.text = "Torre: %s [FRACO 0.5x]" % elem_name
			lbl_bci_status.add_theme_color_override("font_color", Color(1.0, 0.6, 0.2))
		else:
			lbl_bci_status.text = "Torre: %s [NORMAL 1x]" % elem_name
			lbl_bci_status.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))
	else:
		lbl_bci_status.text = "Torre: %s" % elem_name
		lbl_bci_status.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))

func on_enemy_defeated() -> void:
	cur_enemy_elem = -1
	cur_counter_elem = -1
	if lbl_bci_enemy:
		lbl_bci_enemy.text = "Inimigo Derrotado! [Pausa]"
		lbl_bci_enemy.add_theme_color_override("font_color", Color(0.4, 1.0, 0.5))
	if lbl_bci_rhythm:
		lbl_bci_rhythm.text = "Descansa a mente antes da próxima vaga..."
	update_effectiveness_display()

func take_hearth() -> void:
	super.take_hearth()
	if current_hearth_index < 0:
		trigger_game_over()

func trigger_victory(defeated: int, waves_total: int) -> void:
	if end_panel:
		lbl_end_title.text = "VITÓRIA!"
		lbl_end_title.add_theme_color_override("font_color", Color(0.3, 1.0, 0.4))
		lbl_end_msg.text = "Parabéns! Completaste com sucesso todas as %d ondas!\nInimigos derrotados: %d\nComandos BCI executados: %d" % [
			waves_total, defeated, bci_switches_total
		]
		end_panel.visible = true

func trigger_game_over() -> void:
	var spawner = get_tree().get_first_node_in_group("spawner")
	if spawner and spawner.has_method("notify_game_over"):
		spawner.notify_game_over()
		
	if end_panel:
		lbl_end_title.text = "DERROTA"
		lbl_end_title.add_theme_color_override("font_color", Color(1.0, 0.25, 0.25))
		lbl_end_msg.text = "A torre foi destruída!\nTrocas de poder BCI efetuadas: %d" % bci_switches_total
		end_panel.visible = true

func _on_btn_restart_pressed() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()
