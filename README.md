# SensMatch
![sensmatch](https://user-images.githubusercontent.com/108157655/182255471-fc8158a2-a2f9-49ec-99bc-04a011be4483.png)

A Python based tool for matching your mouse sensitivity between 3D games on Linux. Probably only works on systems using X11 display server protocol as it uses the Xlib extension XTEST for simulating mouse events. If you run Wayland, please give it a go with XWayland.

Heavily inspired by [Kovaak's Sensitivity Matcher](https://github.com/KovaaK/SensitivityMatcher/). I could not get it to work in Linux so I set out to make a viable alternative as I have enjoyed using it under Windows.

## Installation

### Manual
Using your base Python installation or favourite virtual enviroment:
```shell
# Setup
git clone https://github.com/grindzohr/SensMatch.git
cd SensMatch
python3 -m pip install -r requirements.txt

# Run
python3 sensmatch.py
```

### PyInstaller package
A bundled package is available under [releases](https://github.com/grindzohr/SensMatch/releases). It's rather large as it contains a full Python enviroment and dependencies. The upside is that you don't need to have any knowledge of Python or even have it installed to use the tool.
```shell
# Make it executable
sudo chmod +x sensematch-0.1.0-beta

#Run
./sensematch-0.1.0-beta
```

## Usage
Run the tool, then:

1. Select the game/engine you want to convert the sensitivity from.
2. Input your sensitivity value from this game/engine.
3. If the game/engine you are converting to exists in the preset list, then select it now. The correct sensitivity value will be automatically calculated and displayed in the 'Sens' field. Great, you are done. If not, proceed to the next step.
4. Aim at specific point in your new game and press `Alt+.`, this will trigger a mouse event equivalent to a 360 degree rotation in the game/engine you are converting from.
5. Depending on if you are under- or overshooting your target, adjust the the mouse sensitivity in your new game until `Alt+.` performs a perfect (or close enough) 360 degree rotation.

### Configuration (optional)
SensMatch will look for a JSON configuration file in the following location:

`~/.config/sensmatch/config.json`

See **example_config.json** for syntax.

## TODO
* Despair when I realize how broken the tool is.
* Create an in app tutorial.
* Create tooltips for all the parameters.
* Enable input of 'Spin' settings.
* Add more common presets people might want.
* Add support for custom 'spin' hotkey in config file.
* Add support for user defined presets.
* Make a proper icon.
