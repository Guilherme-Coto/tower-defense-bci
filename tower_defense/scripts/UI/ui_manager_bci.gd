extends "res://scripts/UI/UIManager.gd"

## ui_manager_bci.gd
## Interface limpa e normal para o modo BCI.
## Mantém o ecrã normal do jogo (os 4 botões de elemento em baixo e os corações)
## e alterna os botões conforme os comandos BCI chegam ou pelas teclas 1, 2, 3, 4.

func _ready() -> void:
	super._ready()

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

func take_hearth() -> void:
	super.take_hearth()
	if current_hearth_index < 0:
		# Torre destruída: pequena pausa e regressa ao menu
		await get_tree().create_timer(1.5).timeout
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
