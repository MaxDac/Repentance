extends SceneTree

func _initialize() -> void:
	if Engine.get_version_info().major != 4 or not ClassDB.class_exists("CSharpScript"):
		printerr("Repentance requires Godot 4 .NET/Mono; this executable has no compatible C# support.")
		quit(1)
	else:
		print("REPENTANCE GODOT OK")
		quit(0)
