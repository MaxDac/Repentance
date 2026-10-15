# GodotInk

An [ink](https://github.com/inkle/ink) integration for [Godot Engine 4](https://github.com/godotengine/godot).  

If you use and like this project, please consider buying me a coffee.  
[![ko-fi](https://img.shields.io/badge/support_me_on_ko--fi-ff5e5b?style=for-the-badge&logo=kofi&logoColor=f5f5f5)](https://ko-fi.com/E1E53SKZF)

## Usage

You'll find a quick-start guide, and the general documentation on the project's
[wiki](https://github.com/paulloz/godot-ink/wiki).

### Installation

The following instructions assume that you have a working Godot and .NET installation. If not, please refer to the
official [engine documentation](https://docs.godotengine.org/).

1. [Download](https://github.com/paulloz/godot-ink/releases/latest) and extract the code at the root of your project.
   You should see a new `addons/GodotInk/` folder in your project's directory.

1. Add the following line in your `.csproj` file (before the closing `</Project>` tag).
   ```xml
   <Import Project="addons\GodotInk\GodotInk.props" />
   ```
   If you don't have a `.csproj` file, click the **Create C# Solution** button in the editor's
   **Project/Tools** menu.

1. Build your project once.

1. Enable **GodotInk** in your project settings.

## Local resource reset integration

This project's integration implements Godot's `_ResetState()` hook. Call the inherited
`ResetState()` entry point to restart an initialized Ink story; Godot-initiated resource resets
do the same, including calls through a `Resource` reference or native `reset_state`.
Resetting an uninitialized resource (including importer/editor placeholders) is a safe no-op.
An initialized reset retains compiled content, external bindings, observers, and signal connections.

## License

*GodotInk* is released under MIT license (see the [LICENSE](/LICENSE) file for more information).
