extends Node

# Singleton de Configurações Globais do Jogo
# Gere parâmetros como o número de ondas (waves) selecionado para os níveis

const DEFAULT_WAVES: int = 5
const MIN_WAVES: int = 1
const MAX_WAVES: int = 100
const SAVE_PATH: String = "user://game_settings.cfg"

var waves: int = DEFAULT_WAVES

signal waves_changed(new_waves: int)

func _ready() -> void:
	load_settings()

func get_waves() -> int:
	return waves

func set_waves(value: int) -> void:
	var clamped_value = clampi(value, MIN_WAVES, MAX_WAVES)
	if waves != clamped_value:
		waves = clamped_value
		waves_changed.emit(waves)
		save_settings()

func increase_waves(amount: int = 1) -> void:
	set_waves(waves + amount)

func decrease_waves(amount: int = 1) -> void:
	set_waves(waves - amount)

func reset_to_defaults() -> void:
	waves = DEFAULT_WAVES
	waves_changed.emit(waves)
	save_settings()

func save_settings() -> void:
	var config = ConfigFile.new()
	config.set_value("gameplay", "waves", waves)
	config.save(SAVE_PATH)

func load_settings() -> void:
	var config = ConfigFile.new()
	var err = config.load(SAVE_PATH)
	if err == OK:
		waves = config.get_value("gameplay", "waves", DEFAULT_WAVES)
		waves = clampi(waves, MIN_WAVES, MAX_WAVES)
