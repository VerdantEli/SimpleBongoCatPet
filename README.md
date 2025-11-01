# SimpleBongoCatPet
**Python Windows Bongo Cat Pet**

---

A Python Bongo Cat Pet that just sits in your desktop that reacts to your key presses. That's it.

Features:
- Bongo Cat can be changed to anything you want
- Cat taps depending on which side of the keyboard you press, or make it RNG (Your choice :P)
- Always on top but will hide when a fullscreen application is active
- Included a System Tray icon to reload the cat or to exit

The Cat can be customized from the `~\.config\bongocat` folder

You can change the image of the cat but do not change the name of the file. The application looks for these specific filenames:
- `bongo-cat-both-up.png`
- `bongo-cat-left-down.png`
- `bongo-cat-right-down.png` 
- `bongo-cat-both-down.png`

---

# Running the Program

Can only be runned with:
- Windows 10/11

### Option 1: Pre-built Executable (Recommended)
1. Download the latest release from the [Releases](https://github.com/VerdantEli/SimpleBongoCatPet/releases) 
2. Extract the ZIP file
3. Run `BongoCat.exe`

---

### Option 2: From Source
1. Install Python 3.7+ from [python.org](https://python.org) or use:
```
winget install 9NQ7512CXL7T
```

2. In order to run the pet, you would need these packages:
- PyQt
- PyWin32
- keyboard

 Install with:
```
pip install PyQt6 pywin32 keyboard
```

3. Clone the Repo 
```
git clone https://github.com/VerdantEli/SimpleBongoCatPet.git
```

4. Either open the file directly or use the terminal to execute it

```
cd SimpleBongoCatPet
python BongoCat.py
```

---

# Credits
- Ralsei Bongo Cat: @Mushroom-cookie-bears

