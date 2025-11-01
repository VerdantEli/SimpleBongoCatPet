from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QPixmap, QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, Qt
from configparser import ConfigParser
import subprocess, shutil, random, keyboard, sys, os, win32gui, win32api, win32con

class config():
    configPath= os.path.expanduser("~\\.config\\bongocat\\config.ini")
    configFolder = os.path.expanduser("~\\.config\\bongocat")

    DEFAULTS = {
        'catSettings': {
            'cat_scale': '0.16',
            'cat_xpos': '1300',
            'cat_ypos': '0',
        }, 'catTapping' : {
            'cat_rng': 'off',
            'rng_switch' : '50'
        }
    }

    def writeConfig():
        os.makedirs(config.configFolder, exist_ok=True)
        catConfig = ConfigParser()

        if os.path.exists(config.configPath):
            catConfig.read(config.configPath)

        for section, options in config.DEFAULTS.items():
            if not catConfig.has_section(section):
                catConfig.add_section(section)
            for key, value in options.items():
                if not catConfig.has_option(section, key):
                    catConfig.set(section, key, value)

        with open(config.configPath, 'w') as configfile:
            catConfig.write(configfile)

    def readConfig():
        if not os.path.exists(config.configPath):
            config.writeConfig()

        catConfig = ConfigParser()
        catConfig.read(config.configPath)
        
        for section, options in config.DEFAULTS.items():
            if not catConfig.has_section(section):
                config.writeConfig()
                catConfig.read(config.configPath)
            for key, value in options.items():
                if not catConfig.has_option(section, key):
                    config.writeConfig()
                    catConfig.read(config.configPath)

        catScale = float(catConfig.get('catSettings', 'cat_scale'))
        catXpos = catConfig.getint('catSettings', 'cat_xpos')
        catYpos = catConfig.getint('catSettings', 'cat_ypos')
        catRNG = catConfig.get('catTapping', 'cat_rng')
        rngSwitch = catConfig.getint('catTapping', 'rng_switch')
    
        catConfigValues = {
            'catScale' : catScale,
            'catXpos' : catXpos,
            'catYpos' : catYpos,
            'catRNG' : catRNG,
            'rngSwitch' : rngSwitch
        }

        return catConfigValues

class bongoAssets():
    def assetsInstall():
        targetAssets= os.path.expanduser("~\\.config\\bongocat\\BongoCatAssets")
        sourceAssets= os.path.join(os.path.dirname(sys.argv[0]), "assets")
        os.makedirs(targetAssets, exist_ok=True)

        for assets in os.listdir(sourceAssets):
            if assets.lower().endswith('.png'):
                source = os.path.join(sourceAssets, assets)
                target = os.path.join(targetAssets, assets)
                if not os.path.exists(target):
                    shutil.copy(source, target)

class keyListener(QObject):
    keyPress = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        keyboard.on_press(self.onPress, suppress= False)

    def onPress(self, event):
        self.keyPress.emit(event.name)

class fullscreenDetector():
    def fullscreenCheck(self):
        try:
            self.foreWindow = win32gui.GetForegroundWindow()
            if not self.foreWindow == 0:
                return False
            try:
                self.resWindow = win32gui.GetWindowRect(self.foreWindow)
            except win32gui.error:
                return False

            style = win32gui.GetWindowLong(self.foreWindow, win32con.GWL_STYLE)
            isOverlapped = (style & win32con.WS_OVERLAPPEDWINDOW) == win32con.WS_OVERLAPPEDWINDOW

            self.screenWidth = win32api.GetSystemMetrics(0)
            self.screenHeight = win32api.GetSystemMetrics(1)

            fullScreen = abs(self.resWindow[0]) <= 2 and abs(self.resWindow[1]) <= 2 and abs(self.resWindow[2]-self.screenWidth) <= 2 and abs(self.resWindow[3] - self.screenHeight) <= 2

            if fullScreen and not isOverlapped:
                return True
            return False
        except Exception:
            return False

class App(QWidget):
    CONFIG = os.path.expanduser("~\\.config\\bongocat\\")
    pawDetected = pyqtSignal(int)


    def __init__(self):
        super().__init__()
        self.title = 'Bongo Cat'
        self.initUI()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.topOrNot)
        self.timer.start(250)
        self.pawTap = 0
        self.timer.timeout.connect(self.keyPressed)
        self.timer.start(10)

        self.pawDetected.connect(self.tapDrums)


    def initUI(self):
        self.catConfigData = config.readConfig()
        self.bongoCat()

        self.setWindowTitle(self.title)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(os.path.expanduser("~\\.config\\bongocat\\BongoCatAssets\\ralsei.png")))
        self.tray.setToolTip("Ralsei Pet")
        self.tray.setVisible(True)

        menu = QMenu(self)
        openFolder = QAction("Open Config Folder", self)
        openFolder.triggered.connect(App.openConfig)
        menu.addAction(openFolder)

        reloadConfig = QAction("Reload Cat", self)
        reloadConfig.triggered.connect(self.reloadCat)
        menu.addAction(reloadConfig)

        menu.addSeparator()

        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.quitCat)
        menu.addAction(exitAction)

        self.tray.setContextMenu(menu)
        self.tray.show()

        self.label = QLabel(self)
        self.label.setPixmap(self.catScaledUp)
        self.label.resize(self.scaleCatWidth, self.scaleCatHeight)
        self.resize(self.scaleCatWidth, self.scaleCatHeight)

        self.show()
        self.move(self.catConfigData['catXpos'], self.catConfigData['catYpos'])

    def bongoCat(self):
        self.upImagePath = os.path.expanduser("~\\.config\\bongocat\\BongoCatAssets\\bongo-cat-both-up.png")
        self.leftDownImagePath = os.path.expanduser("~\\.config\\bongocat\\BongoCatAssets\\bongo-cat-left-down.png")
        self.rightDownImagePath = os.path.expanduser("~\\.config\\bongocat\\BongoCatAssets\\bongo-cat-right-down.png")
        self.downImagePath = os.path.expanduser("~\\.config\\bongocat\\BongoCatAssets\\bongo-cat-both-down.png")

        self.pixmapUp = QPixmap(self.upImagePath)
        self.pixmapLeftDown = QPixmap(self.leftDownImagePath)
        self.pixmapRightDown = QPixmap(self.rightDownImagePath)
        self.pixmapDown = QPixmap(self.downImagePath)

        self.scaleCat = self.catConfigData['catScale']
        self.scaleCatWidth = int(self.pixmapUp.width()*self.scaleCat)
        self.scaleCatHeight = int(self.pixmapUp.height()*self.scaleCat)

        self.catScaledUp = self.pixmapUp.scaled(
            self.scaleCatWidth,
            self.scaleCatHeight,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.catScaledLeftDown = self.pixmapLeftDown.scaled(
            self.scaleCatWidth,
            self.scaleCatHeight,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.catScaledRightDown = self.pixmapRightDown.scaled(
            self.scaleCatWidth,
            self.scaleCatHeight,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.catScaledDown = self.pixmapDown.scaled(
            self.scaleCatWidth,
            self.scaleCatHeight,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def quitCat(self):
        self.tray.hide()
        self.timer.stop()
        self.close()
        QApplication.instance().quit()


    def reloadCat(self):
        self.catConfigData = config.readConfig()
        self.bongoCat()
        
        self.label.setPixmap(self.catScaledUp)
        self.label.resize(self.scaleCatWidth, self.scaleCatHeight)
        self.resize(self.scaleCatWidth, self.scaleCatHeight)
        self.move(self.catConfigData['catXpos'], self.catConfigData['catYpos'])

    def topOrNot(self):
        if fullscreenDetector().fullscreenCheck():
            if self.isVisible():
                self.hide()
        else:
            if not self.isVisible():
                self.show()
                2
    def openConfig():
        if sys.platform == "win32":
            subprocess.Popen(['explorer', App.CONFIG])

    def keyPressed(self):
        paw = 0

        leftSide = [1,2,3,4,5,6,16,17,18,19,20,30,31,32,33,34,30,31,41,44,45,46,47,48,59,60,61,62,63,64,91]
        rightSide = [7,8,9,10,11,12,13,21,22,23,24,25,26,27,35,36,37,38,39,43,49,50,51,52,53,65,66,67,68,72,75,77,80,87,88,]
        leftFuncSide = {'left ctrl','left alt','left shift',  'caps lock', 'tab', 'windows'}
        rightFuncSide = {'right shift', 'enter', 'backspace'}

        leftKeyboard = list(leftSide) + list(leftFuncSide)
        rightKeyboard = list(rightSide) + list(rightFuncSide)

        leftPaw = False
        rightPaw = False

        for lkey in leftKeyboard :
            if keyboard.is_pressed(lkey):
                leftPaw = True
                break  
        
        for rkey in rightKeyboard:
            if keyboard.is_pressed(rkey):
                rightPaw = True
                break
        
        if keyboard.is_pressed('space'):
            paw = 3
        elif leftPaw and rightPaw:
            paw = 3
        elif leftPaw:
            paw = 1
        elif rightPaw:
            paw = 2

        if paw != getattr(self, 'pawTap'):
            self.pawTap = paw
            self.pawDetected.emit(paw)

    def tapDrums(self, side):
        if self.catConfigData['catRNG'] == 'off':
            if side == 1:
                self.label.setPixmap(self.catScaledLeftDown)
            elif side == 2:
                self.label.setPixmap(self.catScaledRightDown)
            elif side == 3:
                self.label.setPixmap(self.catScaledDown)
            else:
                self.label.setPixmap(self.catScaledUp)
            
        
        else:
            self.random = random.randint(1, 100)
            if self.random < self.catConfigData['rngSwitch']:
                self.label.setPixmap(self.catScaledLeftDown)
            else:
                self.label.setPixmap(self.catScaledRightDown)
            QTimer.singleShot(250, lambda: self.label.setPixmap(self.catScaledUp))

if __name__ == '__main__':
    bongoAssets.assetsInstall()
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())