import os
import sys
import json
from time import sleep, time

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QGroupBox, QCheckBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt, QLocale

from pynput import keyboard
from Xlib import X, display
from Xlib.ext import xtest

from presets import yawPresets


baseDir = os.path.dirname(__file__)
configDir = os.path.join(os.path.expanduser('~'), '.config', 'sensmatch')


class SensMatchUi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SensMatch')
        self.setWindowIcon(QIcon(os.path.join(baseDir, 'icons', 'icon.ico')))
        self.centralWidgetLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self._centralWidget.setLayout(self.centralWidgetLayout)
        self.setCentralWidget(self._centralWidget)

        self._createPresets()
        self._buildCentralWidget()

        # can't fuck up the layout if you can't resize it...
        self.setFixedSize(self.sizeHint())

    def _createPresets(self):
        presetsLayout = QFormLayout()
        self.presetsComboBox = QComboBox()
        self.presetsComboBox.addItems(yawPresets.keys())
        self.presetsComboBox.addItem('Custom')
        
        presetsLayout.addRow('Yaw presets: ', self.presetsComboBox)
        self.centralWidgetLayout.addLayout(presetsLayout)

    def _createGameFields(self):    
        doubleValidator = QDoubleValidator(0, 99, 14)
        doubleValidator.setLocale(QLocale.c())
        doubleValidator.setNotation(QDoubleValidator.StandardNotation)
        
        gameGroupBoxLayout = QVBoxLayout()
        self._gameGroupBox = QGroupBox('Game settings')
        self._gameGroupBox.setLayout(gameGroupBoxLayout)
        
        self.gameFields = {}
        fieldNames = ['sens', 'yaw','increment']
        fieldLabels = ['x', '=', 'Sens', '  Yaw (deg)', '   Increment'] # jank
        fieldsLayout = QHBoxLayout()
        labelsLayout = QHBoxLayout()
        
        for fieldName in fieldNames:
            self.gameFields[fieldName] = QLineEdit()
            self.gameFields[fieldName].setValidator(doubleValidator)
            fieldsLayout.addWidget(self.gameFields[fieldName])
            if len(fieldLabels) > len(fieldNames):
                fieldsLayout.addWidget(QLabel(fieldLabels.pop(0)))
        self.gameFields['increment'].setEnabled(False)
        
        for label in fieldLabels:
            labelsLayout.addWidget(QLabel(label))

        gameGroupBoxLayout.addLayout(fieldsLayout)
        gameGroupBoxLayout.addLayout(labelsLayout)

    def _createSpinFields(self):
        self._spinGroupBox = QGroupBox('Spin settings')
        self.spinFields = {}
        fieldNames = ['counts', 'move', 'freq']
        fieldLabels = ['Counts: ', 'Move: ', 'Freq: ']
        fieldsLayout = QFormLayout()

        for fieldName in fieldNames:
            self.spinFields[fieldName] = QLineEdit()
            self.spinFields[fieldName].setEnabled(False)
            fieldsLayout.addRow(fieldLabels.pop(0), self.spinFields[fieldName])

        self._spinGroupBox.setLayout(fieldsLayout)

    def _createPhysFields(self):
        self._physGroupBox = QGroupBox('Physical settings')
        self.physFields = {}
        fieldNames = ['cpi', 'cm']
        fieldLabels = ['CPI: ', 'cm/360°:']
        fieldsLayout = QFormLayout()

        for fieldName in fieldNames:
            self.physFields[fieldName] = QLineEdit()
            fieldsLayout.addRow(fieldLabels.pop(0), self.physFields[fieldName])
        self.physFields['cpi'].setValidator(QIntValidator(0, 99999))
        self.physFields['cm'].setEnabled(False)

        self._physGroupBox.setLayout(fieldsLayout)

    def _buildCentralWidget(self):
        self._createGameFields()
        self._createSpinFields()
        self._createPhysFields()

        spinPhysLayout = QHBoxLayout()
        spinPhysLayout.addWidget(self._spinGroupBox)
        spinPhysLayout.addWidget(self._physGroupBox)

        self.centralWidgetLayout.addWidget(self._gameGroupBox)
        self.centralWidgetLayout.addLayout(spinPhysLayout)


class SensMatchCtrl:
    def __init__(self, view, model):
        self._view = view
        self._model = model
        self._loadConfig()
        self._populateUI()
        self._setupMnK()
        self._connectSignals()

    def _loadConfig(self):
        self.config = {}
        try:
            with open(os.path.join(configDir, 'config.json'), 'r') as f:
                self.config = json.load(f)
            
            self._model.sens = self.config['defaults']['sens']
            self._model.yaw = self.config['defaults']['yaw']
            self._model.cpi = self.config['defaults']['cpi']
        
        except:
            pass

    def _saveConfig(self):
        pass

    def _populateUI(self):
        self._updatePreset()
        self._view.gameFields['sens'].setText(f'{self._model.sens:g}')
        self._view.gameFields['yaw'].setText(f'{self._model.yaw:g}')
        self._updateIncrement()
        self._updateCounts()
        self._view.spinFields['move'].setText(f'{self._model.move:g}')
        self._view.spinFields['freq'].setText(f'{self._model.freq:g}')
        self._view.physFields['cpi'].setText(f'{self._model.cpi:g}')
        self._updateCm()

    def _setupMnK(self):
        # using Xlib with XTEST to fake mouse inputs
        self._display = display.Display()

        # setup glbal hotkey
        listener = keyboard.GlobalHotKeys({'<alt>+.': self._mouseSpin})
        listener.start()
        
    def _updatePreset(self):
        presetKeys = list(yawPresets.keys())
        presetValues = list(yawPresets.values())
        if self._model.yaw in presetValues:
            presetValuePos = presetValues.index(self._model.yaw)
            presetKey = presetKeys[presetValuePos]
            self._view.presetsComboBox.setCurrentText(presetKey)
        else:
            self._view.presetsComboBox.setCurrentText('Custom')

    def _setSens(self):
        if self._view.gameFields['sens'].text() != '':
            self._model.sens = float(self._view.gameFields['sens'].text())

    def _updateSens(self):
        self._model.calcSens()
        self._view.gameFields['sens'].setText(f'{self._model.sens:g}')
    
    def _setYaw(self):
        if self._view.gameFields['yaw'].text() != '':
            self._model.yaw = float(self._view.gameFields['yaw'].text())
    
    def _updateYaw(self):
        if self._view.presetsComboBox.currentText() != 'Custom':
            self._model.yaw = yawPresets[self._view.presetsComboBox.currentText()]
            self._view.gameFields['yaw'].setText(f'{self._model.yaw:g}')

    def _updateIncrement(self):
        self._model.calcIncrement()
        self._view.gameFields['increment'].setText(f'{self._model.increment:g}')

    def _updateCounts(self):
        self._model.calcCounts()
        self._view.spinFields['counts'].setText(f'{self._model.counts:g}')

    def _setCPI(self):
        if self._view.physFields['cpi'].text() != '':
            self._model.cpi = float(self._view.physFields['cpi'].text())
    
    def _setCm(self):
        pass
    
    def _updateCm(self):
        self._model.calcCm()
        self._view.physFields['cm'].setText(f'{self._model.cm:g}')

    def _mouseSpin(self):
        remainingCounts = self._model.counts
        while remainingCounts > 0:
            if remainingCounts < self._model.move:
                residual = round(remainingCounts)
                xtest.fake_input(self._display, X.MotionNotify, 1, x=residual)
            else:
                xtest.fake_input(self._display, X.MotionNotify, 1, x=self._model.move)
            remainingCounts -= self._model.move
            
            self._display.flush()
            sleep(1/self._model.freq)

    def _connectSignals(self):
        # order matters...
        self._view.presetsComboBox.currentTextChanged.connect(lambda: self._updateYaw())
        self._view.gameFields['sens'].textEdited.connect(lambda: self._setSens())
        self._view.gameFields['sens'].textEdited.connect(lambda: self._updateIncrement())
        self._view.gameFields['yaw'].textEdited.connect(lambda: self._setYaw())
        self._view.gameFields['yaw'].textEdited.connect(lambda: self._updatePreset())
        self._view.gameFields['yaw'].textChanged.connect(lambda: self._updateSens())
        self._view.gameFields['increment'].textChanged.connect(lambda: self._updateCounts())
        self._view.gameFields['increment'].textChanged.connect(lambda: self._updateCm())
        self._view.physFields['cpi'].textEdited.connect(lambda: self._setCPI())
        self._view.physFields['cpi'].textEdited.connect(lambda: self._updateCm())


class SensMatchCalc():
    def __init__(self):
        self.sens = 1.8
        self.yaw = 0.022
        self.increment = 0
        self.counts = 0 # mouse counts to a 360 in game
        self.move = 480 # mouse counts per mouse event
        self.freq = 100 # frequency of mouse events
        self.cpi = 800
        self.cm = 0

    def calcSens(self):
        try:
            self.sens = self.increment/self.yaw
        except ZeroDivisionError:
            self.sens = 0
    
    def calcIncrement(self):
        self.increment = self.sens*self.yaw

    def calcCounts(self):
        try:
            self.counts = 360 / self.increment
        except ZeroDivisionError:
            self.counts = 0

    def calcCm(self):
        try:
            self.cm = self.counts/self.cpi * 2.54
        except ZeroDivisionError:
            self.cm = 0

def main():
    sensMatch = QApplication(sys.argv)

    view = SensMatchUi()
    view.show()

    model = SensMatchCalc()

    SensMatchCtrl(view=view, model=model)

    sys.exit(sensMatch.exec_())

if __name__ == '__main__':
    main()