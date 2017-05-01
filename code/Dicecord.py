# Dicecord: Dice Roller and Character Sheet Viewer for use in conjucntion with Discord Chat Channels
# Copyright (C) 2017  Roy Healy
# 
# version 1.1


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import http.client, time, sys, copy, random
import urllib.error
import urllib.request
from player import Character
import stats
import mageUI, mageInventory
import vampireUI, vampireInventory


VERSION = "1.1"


class Intro(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()
        self.setFixedSize(500, 200)

    def initUI(self):
        QFontDatabase.addApplicationFont(r"font\Magra-Regular.ttf")
        buttonstyle = """QPushButton {font-family: \"Magra\";
                                        font-size: 13pt;
                                        color: white;
                                        background-color: #7289da;
                                        border-style: inset;
                                        border-width: 2px; border-color: white;}"""

        import_button = QPushButton("Import Character", self)
        import_button.clicked.connect(self.import_character)
        import_button.setStyleSheet(buttonstyle)
        import_button.resize(140, 70)
        import_button.move(355, 115)
        import_button.setCursor(QCursor(Qt.PointingHandCursor))

        new_button = QPushButton("New Character", self)
        new_button.clicked.connect(self.new_character)
        new_button.setStyleSheet(buttonstyle)
        new_button.resize(140, 70)
        new_button.move(180.5, 115)
        new_button.setCursor(QCursor(Qt.PointingHandCursor))

        updates_button = QPushButton("Check for Updates", self)
        updates_button.setStyleSheet(buttonstyle)
        updates_button.clicked.connect(self.parent.update_client)
        updates_button.resize(140, 70)
        updates_button.move(5, 115)
        updates_button.setCursor(QCursor(Qt.PointingHandCursor))

        self.setGeometry(300, 300, 500, 200)

    def import_character(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', "characters/", "XML Files (*.xml)")

        if fname[0] == '':
            return

        path = fname[0]
        character = Character.from_xml(path)
        self.parent.mainUI(character, path)

    def new_character(self):

        splat, computer, drive, firearms, ok = New_Character_Dialog.set_UI(self)
        if ok:
            character = Character(splat = splat)
            
            # remove modern defaults
            del character.stats['computer']
            del character.stats['firearms']
            del character.stats['drive']

            # add replacements
            character.stats[computer] = 0
            character.stats[drive] = 0
            character.stats[firearms] = 0
            
            self.parent.mainUI(character, path=None)
            self.parent.edit_Action.setChecked(True) # set checked
            self.parent.edit_mode()


class New_Character_Dialog(QDialog):
    '''
    Dialog for creating new character
    '''
    def __init__(self):
        super().__init__()
        self.splat = 'mage'
        self.initUI()
        self.setMaximumSize(20,20)

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.setWindowTitle('New Character')
        self.setWindowIcon((QIcon(r'images\D10.ico')))

        splat_label = QLabel("==Character Type==")
        splat_label.setStyleSheet("QLabel { font: 13pt}")
        self.grid.addWidget(splat_label, 0, 0, 1, 3)
        self.grid.setAlignment(splat_label, Qt.AlignHCenter)

        # radio button set
        splatbox = QHBoxLayout()
        mage = QRadioButton()
        mage.setText("Mage")
        mage.setChecked(True)
        mage.toggled.connect(lambda: self.changesplat("mage"))
        splatbox.addWidget(mage)

        vamp = QRadioButton()
        vamp.setText("Vampire")
        vamp.toggled.connect(lambda: self.changesplat("vampire"))
        splatbox.addWidget(vamp)

        self.grid.addLayout(splatbox, 1, 0, 1, 3)

        # dark era skill settings
        era_label = QLabel("==Dark Era Skills==")
        era_label.setStyleSheet("QLabel { font: 13pt}")
        self.grid.addWidget(era_label, 2, 0, 1, 3)
        self.grid.setAlignment(era_label, Qt.AlignHCenter)

        computer_min = QLabel("Computer")
        computer_max = QLabel("Enigmas")

        self.comp_slider = QSlider(Qt.Horizontal)
        self.comp_slider.setMinimum(0)
        self.comp_slider.setMaximum(1)
        self.comp_slider.setTickInterval(1)
        self.comp_slider.setSliderPosition(0)

        self.grid.addWidget(computer_min, 3, 0)
        self.grid.addWidget(self.comp_slider, 3, 1)
        self.grid.addWidget(computer_max, 3, 2)

        drive_min = QLabel("Drive")
        drive_max = QLabel("Ride")

        self.ride_slider = QSlider(Qt.Horizontal)
        self.ride_slider.setMinimum(0)
        self.ride_slider.setMaximum(1)
        self.ride_slider.setTickInterval(1)
        self.ride_slider.setSliderPosition(0)

        self.grid.addWidget(drive_min, 4, 0)
        self.grid.addWidget(self.ride_slider, 4, 1)
        self.grid.addWidget(drive_max, 4, 2)

        firearms_min = QLabel("Firearms")
        firearms_max = QLabel("Archery")

        self.fire_slider = QSlider(Qt.Horizontal)
        self.fire_slider.setMinimum(0)
        self.fire_slider.setMaximum(1)
        self.fire_slider.setTickInterval(1)
        self.fire_slider.setSliderPosition(0)

        self.grid.addWidget(firearms_min, 5, 0)
        self.grid.addWidget(self.fire_slider, 5, 1)
        self.grid.addWidget(firearms_max, 5, 2)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel, Qt.Horizontal, self)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.grid.addWidget(buttonBox, 6, 1, 1, 2)

    def changesplat(self, splat):
        self.splat = splat

    def set_UI(self):
        '''
        Used to open a dialog window to enter details of label.
        '''
        dialog = New_Character_Dialog()
        result = dialog.exec_()
        out_splat = dialog.splat
        if dialog.comp_slider.sliderPosition() == 0:
            out_computer = "computer"
        else:
            out_computer = 'enigmas'

        if dialog.ride_slider.sliderPosition() == 0:
            out_drive = "drive"
        else:
            out_drive = 'ride'

        if dialog.fire_slider.sliderPosition() == 0:
            out_firearms = "firearms"
        else:
            out_firearms = 'archery'

        return (out_splat, out_computer, out_drive, out_firearms, result == QDialog.Accepted)



class Main(QMainWindow):
    '''
    Main window for displaying character sheet
    '''
    def __init__(self):
        super().__init__()
        self.character = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Dicecord')
        self.setWindowIcon(QIcon(r'images\D10.ico'))
        self.setCentralWidget(Intro(self))
        self.setFixedSize(500, 200)

        image = QImage(r"images\splash.png")
        palette = QPalette()
        palette.setBrush(10, QBrush(image))

        self.setPalette(palette)

    def mainUI(self, character, path):
        palette = QPalette()
        self.setPalette(palette)
        self.move(100, 100)
        self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
        self.setMinimumSize(0, 0)
        self.character = character
        # save original as a copy to detect changes on quit
        self.old_character = copy.deepcopy(character)
        self.path = path

        self.sheet = Sheet(self.character)
        self.setCentralWidget(self.sheet)

        # toolbar
        self.toolbar = self.addToolBar("Actions")
        # # roller
        roller_Action = QAction(QIcon(r'images\D10.ico'), 'Edit', self)
        roller_Action.setShortcut('Ctrl+R')
        roller_Action.triggered.connect(self.open_roller)
        self.toolbar.addAction(roller_Action)

        # # edit mode
        self.edit_Action = QAction(QIcon(r'images\edit.ico'), 'Edit', self)
        self.edit_Action.triggered.connect(self.edit_mode)
        self.edit_Action.setCheckable(True)
        self.toolbar.addAction(self.edit_Action)

        # file menu
        menubar = self.menuBar()
        file_Menu = menubar.addMenu('&File')
        # # New
        new_action = QAction('&New Character', self)
        new_action.setShortcut('Ctrl+N')
        file_Menu.addAction(new_action)
        new_action.triggered.connect(self.new_character)
        # # Open
        open_Action = QAction('&Open Character', self)
        open_Action.setShortcut('Ctrl+O')
        file_Menu.addAction(open_Action)
        open_Action.triggered.connect(self.import_character)
        # # Save
        save_Action = QAction('&Save Character', self)
        save_Action.setShortcut('Ctrl+S')
        file_Menu.addAction(save_Action)
        save_Action.triggered.connect(self.save)
        # # Save As
        save_as_Action = QAction('&Save Character As', self)
        save_as_Action.setShortcut('Ctrl+Shift+S')
        file_Menu.addAction(save_as_Action)
        save_as_Action.triggered.connect(lambda: self.save(save_as = True))
        # # Exit
        exit_Action = QAction('&Exit', self)
        exit_Action.setShortcut('Ctrl+Q')
        exit_Action.triggered.connect(self.close)
        file_Menu.addAction(exit_Action)

        # options menu
        options_Menu = menubar.addMenu('&Options')
        # # Bot Personality
        personality_action = QAction('&Personality Settings', self)
        personality_action.triggered.connect(self.personality)
        options_Menu.addAction(personality_action)

        # help menu
        help_Menu = menubar.addMenu('&Help')
        # # ReadMe Link
        readme_action = QAction('Instructions', self)
        readme_action.triggered.connect(self.link)
        help_Menu.addAction(readme_action)

        # # about
        about_Action = QAction('About', self)
        about_Action.triggered.connect(self.about_display)
        help_Menu.addAction(about_Action)

        # # Check for updates
        update_action = QAction('Check for updates', self)
        update_action.triggered.connect(self.update_client)
        help_Menu.addAction(update_action)

    def new_character(self):

        splat, computer, drive, firearms, ok = New_Character_Dialog.set_UI(self)

        if ok:
            if splat == 'mage':
                dots = stats.STATS.copy()
                
            # remove modern defaults
            del dots['computer']
            del dots['firearms']
            del dots['drive']

            # add replacements
            dots[computer] = 0
            dots[drive] = 0
            dots[firearms] = 0

            self.character = Character(dots)
            self.sheet = Sheet(self.character)
            self.setCentralWidget(self.sheet)
            self.edit_Action.setChecked(True) # set checked
            self.edit_mode()

    def update_client(self):
        req = urllib.request.Request("http://further-reading.net/dicecord%20version.txt")
        try: response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setIcon(QMessageBox.Critical)
            message.setWindowIcon(QIcon(r'images\D10.ico'))
            message.setText("Unable to connect to server.")
            message.setInformativeText("Error Code: " + e.code)
            message.addButton("Okay", QMessageBox.AcceptRole)
            message.exec_()
            return
        except urllib.error.URLError:
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setWindowIcon(QIcon(r'images\D10.ico'))
            message.setIcon(QMessageBox.Critical)
            message.setText("Unable to connect to server.")
            message.setInformativeText("Please try again later.")
            message.addButton("Okay", QMessageBox.AcceptRole)
            message.exec_()
            return

        version = response.read()
        version = str(version)[1:].replace("'", "")
        if version == VERSION:
            message = QMessageBox()
            message.setWindowIcon(QIcon(r'images\D10.ico'))
            message.setWindowTitle("Up to Date")
            message.setIcon(QMessageBox.Information)
            message.setText("You are using the latest version.")
            message.addButton("Okay", QMessageBox.AcceptRole)
            message.exec_()

        else:
            message = QMessageBox()
            message.setWindowTitle("Update available")
            message.setWindowIcon(QIcon(r'images\D10.ico'))
            message.setIcon(QMessageBox.Warning)
            message.setText("Do you want to update to version " + version + "?")
            message.addButton("Yes", QMessageBox.AcceptRole)
            message.addButton("No", QMessageBox.AcceptRole)
            message.exec_()

            clicked = message.clickedButton().text()

            if clicked == 'Yes':
                message = "This will open a link in your browser and close the client. Do you want to continue?"
                reply = QMessageBox.warning(self, 'Open Link',
                                            message, QMessageBox.Yes, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    QDesktopServices.openUrl(QUrl('http://further-reading.net/dicecord/'))
                    self.close()

    def link(self):
        message = "This will open a link in your browser. Do you want to continue?"
        reply = QMessageBox.warning(self, 'Open Link',
                                          message, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl('https://github.com/further-reading/Dicecord'))

    def personality(self):
        self.dialog = New_Window(Personality(self.character, parent = self), "Personality Settings")
        self.dialog.show()


    def edit_mode(self):
        if self.edit_Action.isChecked():
            # edit mode turned on, save current copy of character
            self.old_character = copy.deepcopy(self.character)
            
        # toggle edit mode on sheet
        self.sheet.edit_toggle(self.edit_Action.isChecked())

        
        if not self.edit_Action.isChecked():
            # edit mode turned off
            # check for changes
            if self.character.stats != self.old_character.stats:
                if self.path:
                    # bring up save/discard choice dialog
                    self.ask_save()
                else:
                    # no path yet
                    self.ask_save(new = True)
                
            
    def ask_save(self, new = False):
        message = QMessageBox()
        message.setWindowTitle("Save Changes")
        message.setWindowIcon(QIcon(r'images\D10.ico'))
        message.setIcon(QMessageBox.Question)
        message.setText("Do you want to export changes?")
        if not new:
            message.setInformativeText("Press 'reset' to undo all changes.")
            message.addButton("Save", QMessageBox.AcceptRole)
            message.addButton("Save As", QMessageBox.RejectRole)
            message.addButton("Reset", QMessageBox.RejectRole)
        else:
            message.addButton("Yes", QMessageBox.AcceptRole)
        message.addButton("No", QMessageBox.RejectRole)
            
        message.exec_()
        clicked = message.clickedButton().text()
        
        if clicked == 'Save':
            self.save()
            
        elif clicked == 'Save As' or clicked == "Yes":
            self.save(save_as = True)

        elif clicked == 'Reset':
            self.character = self.old_character
            self.sheet = Sheet(self.character)
            self.setCentralWidget(self.sheet)

    def save(self, save_as = False):

        if self.character.splat == 'mage':
            name = self.character.stats['shadow name']
        else:
            name = self.character.stats['name']

            
        if name == '':
            name = 'character'

        path = "characters/" + name

        if self.path == None or save_as:
            # open filedialog to get path
            fname = QFileDialog.getSaveFileName(self, 'Save file', path, "XML Files (*.xml)")
            if fname[0] == '':
                # nothing chosen, end function
                return
            
            self.path = fname[0]

        self.character.save_xml(self.path)
        # set as old_character copy for detecting further changes on quit
        self.old_character = copy.deepcopy(self.character)

    def import_character(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', "characters/", "XML Files (*.xml)")
        
        if fname[0] == '':
            return

        self.path = fname[0]

        self.character = Character.from_xml(self.path)
        # set as old_character copy for detecting further changes on quit
        self.old_character = copy.deepcopy(self.character)

        # redraw UI with new character object
        self.sheet = Sheet(self.character)
        self.setCentralWidget(self.sheet)

    def open_roller(self):
        self.dialog = Roller(self.character)
        self.dialog.show()

    def about_display(self):
        file = open(r'LICENSE\ABOUT.txt', 'r')
        content = file.read()
        file.close()
        box = QLabel(content)
        self.dialog = New_Window(box, "Dicecord v" + VERSION)
        self.dialog.show()

    def closeEvent(self, event):

        if self.character == None:
            # if no character close
            event.accept()
            return

        # check changes
        stat_changed = self.character.stats != self.old_character.stats
        note_changed = self.character.notes != self.old_character.notes
        goodMessages_changed = self.character.goodMessages != self.old_character.goodMessages
        badMessages_changed = self.character.badMessages != self.old_character.badMessages
        goodRates_changed = self.character.goodRate != self.old_character.goodRate
        badRates_changed = self.character.badRate != self.old_character.badRate
            
        if stat_changed or note_changed or goodMessages_changed or badMessages_changed or goodRates_changed or badRates_changed:
            # unsaved changes
            message = QMessageBox()
            message.setWindowTitle("Save Changes")
            message.setWindowIcon(QIcon(r'images\D10.ico'))
            message.setIcon(QMessageBox.Question)
            message.setText("Do you want to save changes before exiting?")
            message.addButton("Yes", QMessageBox.AcceptRole)
            message.addButton("No", QMessageBox.ApplyRole)
            message.addButton("Cancel", QMessageBox.HelpRole)
        
            
            message.exec_()
            clicked = message.clickedButton().text()

            if clicked == "Yes":
                self.save(save_as=True)

            elif clicked == "Cancel":               
                event.ignore()
                return

            event.accept()


class Sheet(QTabWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        if self.character.splat == 'mage':
            self.statsheet = mageUI.StatsSheet(character)
            self.inventory = mageInventory.InventorySheet(character, self.statsheet)
        elif self.character.splat == 'vampire':
            self.statsheet = vampireUI.StatsSheet(character)
            self.inventory = vampireInventory.InventorySheet(character)
        self.notes = QTextEdit()
        font = QFont()
        font.setPointSize(12)
        self.notes.setFont(font)
        self.notes.setText(character.notes)
        self.notes.textChanged.connect(self.update_notes)

        self.addTab(self.statsheet, "Stats")
        self.addTab(self.inventory, "Inventory")
        self.addTab(self.notes, "Notes")

    def edit_toggle(self, toggle):
        self.character.edit_mode = toggle
        self.statsheet.edit_toggle()
        self.inventory.edit_toggle()

    def update_notes(self):
        self.character.notes = self.notes.toPlainText()
    
class Personality(QWidget):
    def __init__(self, character, parent):
        super().__init__()
        self.character = character
        self.parent = parent
        self.initUI()

    def initUI(self):

        grid = QGridLayout()
        self.setLayout(grid)

        # Rates
        box = QVBoxLayout()

        good_rate_label = QLabel("Positive Messaging Rate")
        good_rate_label.setStyleSheet("QLabel {font: bold;}")

        good_box = QHBoxLayout()

        good_min = QLabel("Never")
        good_max = QLabel("Always")

        self.good_slider = QSlider(Qt.Horizontal)
        self.good_slider.setMinimum(0)
        self.good_slider.setMaximum(100)
        self.good_slider.setTickInterval(1)
        self.good_slider.setSliderPosition(self.character.goodRate)
        self.good_slider.setStatusTip("Chance for a 5+ success roll to send an additional message")

        good_box.addWidget(good_min)
        good_box.addWidget(self.good_slider)
        good_box.addWidget(good_max)

        bad_rate_label = QLabel("Negative Messaging Rate")
        bad_rate_label.setStyleSheet("QLabel {font: bold;}")

        bad_box = QHBoxLayout()

        bad_min = QLabel("Never")
        bad_max = QLabel("Always")

        self.bad_slider = QSlider(Qt.Horizontal)
        self.bad_slider.setMinimum(0)
        self.bad_slider.setMaximum(100)
        self.bad_slider.setSliderPosition(self.character.badRate)
        self.bad_slider.setStatusTip("Chance for 0 success roll to send an additional message")

        bad_box.addWidget(bad_min)
        bad_box.addWidget(self.bad_slider)
        bad_box.addWidget(bad_max)

        box.addWidget(good_rate_label)
        box.setAlignment(good_rate_label, Qt.AlignHCenter)
        box.addLayout(good_box)
        box.addWidget(bad_rate_label)
        box.setAlignment(bad_rate_label, Qt.AlignHCenter)
        box.addLayout(bad_box)

        # Messaging

        good_label = QLabel("Positive Messages")
        self.good_text = QTextEdit()
        self.good_text.setStatusTip("One line per message.")
        good_content = ''
        for message in self.character.goodMessages:
            good_content += message + '\n'
            self.good_text.setText(good_content)

        bad_label = QLabel("Negative Messages")
        self.bad_text = QTextEdit()
        self.bad_text.setStatusTip("One line per message.")
        bad_content = ''
        for message in self.character.badMessages:
            bad_content += message + '\n'
        self.bad_text.setText(bad_content)

        save_button = QPushButton("Save And Close")
        save_button.clicked.connect(self.save_settings)

        grid.addLayout(box, 0, 0, 1, 2)
        grid.addWidget(good_label, 1, 0)
        grid.addWidget(bad_label, 1, 1)
        grid.addWidget(self.good_text, 2, 0)
        grid.addWidget(self.bad_text, 2, 1)
        grid.addWidget(save_button, 3, 1)


    def save_settings(self):
        # set rate
        self.character.goodRate = self.good_slider.sliderPosition()
        self.character.badRate = self.bad_slider.sliderPosition()

        # set good messages
        goodMessages = self.good_text.toPlainText()
        goodMessages = goodMessages.split("\n")
        for message in goodMessages:
            message = message.replace("\n", "")
        goodMessages = [i for i in goodMessages if i != '']

        # set bad messages
        badMessages = self.bad_text.toPlainText()
        badMessages = badMessages.split("\n")
        for message in badMessages:
            message = message.replace("\n", "")
        badMessages = [i for i in badMessages if i != '']

        # update character object
        self.character.goodMessages = goodMessages
        self.character.badMessages = badMessages

        # ask save
        self.parent.ask_save()

        self.parent.dialog.close()


class Roller(QMainWindow):
    '''
    Dice Roller
    '''
    
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()
        
        
    def initUI(self):
        
        self.setWindowTitle('Roll Dice')
        self.setWindowIcon(QIcon(r'images\D10.ico'))
        

        # add status bar and change its style sheet
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("QStatusBar{border-top: 1px outset grey;}")
        # set permanent message
        # This is needed as otherwise hovering over menu overwrites statusbar contents
        self.message = QLabel()
        self.statusbar.addWidget(self.message)
        
        if self.character.stats['webhook'] == '' or self.character.stats['user id'] == '':
            # add message if now ebhook or user id present
            self.status_update("Please add user details to sheet.")

        # set the central widget as the Dice_Roller widget
        self.setCentralWidget(Dice_Roller(self, self.character))

    def status_update(self, message):
        '''
        method to update status bar message
        called by other widgets
        '''
        self.statusbar.removeWidget(self.message)
        self.message = QLabel(message)
        self.statusbar.addWidget(self.message)
        app.processEvents()

    def about_display(self):
        file = open(r'LICENSE\ABOUT.txt', 'r')
        content = file.read()
        file.close()
        box = QLabel(content)
        self.dialog = New_Window(box, "Dicecord v" + VERSION)
        self.dialog.show()

class New_Window(QMainWindow):
    '''
    Opens a new window with specific widget and title
    '''
    def __init__(self, cent_widget, title):
        super().__init__()
        self.cent_widget = cent_widget
        self.title = title
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(r'images\D10.ico'))       
        self.setCentralWidget(self.cent_widget)
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("QStatusBar{border-top: 1px outset grey;}")


class Last_Roll_Display(QWidget):
    '''
    Opens window to display last roll details
    '''
    
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()
        
    def initUI(self):
        # It's just a QTextEdit with the details inside
        # Using QTextEdit to allow for copy/paste
        text = "Your previous roll: \n"
        rolls = self.character.get_last_roll()

        for roll in rolls:
            # Replaces character ID with "You"
            text += "\n" + roll.replace(self.character.stats['user id'], "You")
        

        grid = QGridLayout()
        self.setLayout(grid)
        
        content = QLabel(text)
        grid.addWidget(content, 0, 0, 1, 2)
        content.setStyleSheet("""QLabel {background-color: white;
                                        border-style: inset;
                                        border-width: 2px; border-color: #C0C0C0;}""" )
        clipboard = QApplication.clipboard()
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(lambda: clipboard.setText(text))
        copy_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        grid.addWidget(copy_button, 1, 1)
        

class Dice_Roller(QWidget):
    '''
    widget for dice rolls
    '''
    def __init__(self, parent, character):
        '''
        Initialises with rote and quiet mode to True, dice to 0 and again to 10
        '''
        super().__init__()
        self.initUI()
        self.parent = parent
        self.character = character
        self.again = 10
        self.dice = 0
        
    def initUI(self):
        '''
        UI for dice roller
        '''
        
        grid = QGridLayout()
        self.setLayout(grid)

        # dice pool selector
        # inner grid for the dice roll selector + its label
        innergrid = QGridLayout()

        # Spinner for selecting pool number
        self.num = QSpinBox()
        self.num.setMaximumSize(QSize(35, 20))
        innergrid.addWidget(self.num, 0, 0)

        # label for spinner
        label = QLabel()
        label.setText("Enter Dice Pool")
        innergrid.addWidget(label, 0, 1)

        # add inner grid to normal grid
        grid.addLayout(innergrid, 0, 0)

        # Show Last Roll button
        last_roll_display_button = QPushButton("Show Last Roll")
        last_roll_display_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        last_roll_display_button.clicked.connect(self.last_roll_display)
        grid.addWidget(last_roll_display_button, 2,2)
        
        # roll button
        roll_button = QPushButton("Roll Dice Pool")
        roll_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        roll_button.clicked.connect(self.roll_handler)
        grid.addWidget(roll_button, 0, 2)

        # chance roll button
        chance_button = QPushButton("Roll Chance Die")
        chance_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        chance_button.clicked.connect(self.chance_handler)
        grid.addWidget(chance_button, 1, 2)

        # rote check
        self.rote_sel = QCheckBox()
        self.rote_sel.setText("Rote")
        grid.addWidget(self.rote_sel, 1, 0)

        # quiet check
        self.multiline_sel = QCheckBox()
        self.multiline_sel.setText("Multiline")
        grid.addWidget(self.multiline_sel, 2, 0)

        # again buttons
        # 10 is selected on initiation
        # Might look into making this an explicit button group instead
        again10 = QRadioButton()
        again10.setText("10 Again")
        again10.setChecked(True)
        again10.toggled.connect(lambda: self.change_again(again10))
        grid.addWidget(again10, 0, 1)
        
        again9 = QRadioButton()
        again9.setText("9 Again")
        again9.toggled.connect(lambda: self.change_again(again9))
        grid.addWidget(again9, 1, 1)
        
        again8 = QRadioButton()
        again8.setText("8 Again")
        again8.toggled.connect(lambda: self.change_again(again8))
        grid.addWidget(again8, 2, 1)

    def change_again(self, button):
        '''
        Method that runs whenever an again radio button is clicked
        '''
        
        # dict showing value for each button
        agains = {'10 Again' : 10,
                  '9 Again' : 9,
                  '8 Again' : 8}

        # uses text of pushed button as key, sets value of self.again
        self.again = agains[button.text()]
                
    def roll_handler(self):
        '''
        handler for when roll button pushed
        '''
        # Check if details entered yet
        if self.character.stats['webhook'] == "" or self.character.stats['user id'] == "":
            # Tell user something is missing and then stop
            self.parent.status_update("User Details Missing.")
            return

        self.parent.status_update("Rolling dice.")

        # reads UI elements to get other values
        dice = self.num.value()
        if dice == 0:
            self.parent.status_update("Please select at least 1 die.")
            return

        # Qt checkboxes are tri-state, return 2 if checked.
        rote = self.rote_sel.checkState() == 2
        quiet = self.multiline_sel.checkState() != 2

        # call roll_set method on character object
        # this returns a list of strings of each die result follwoed by total successes
        # if quiet mode selected, returns a single element list stating roll summary
        messages = self.character.roll_set(dice, rote, self.again, quiet)

        # quiet mode, only send first message to channel, which will be a summary
        if quiet:
            self.send(messages[0], self.character.stats['webhook'])
            time.sleep(1)

        else:
            for message in messages:
                self.send(message, self.character.stats['webhook'])
                time.sleep(1)

        # Final element in list will be total successes
        # Check if it warrants a special message
        self.personality_message(messages[-1])

        # Update the roller window status bar with final successes
        self.parent.status_update(messages[-1].replace(" for " + self.character.stats['user id'],""))
        
    def personality_message(self,message):
        '''
        Takes the final message from the roll, determines if a positive/negative message should be sent.
        :param message: string
        :return: None
        '''
        index = -1
        value = ''

        # Use loop to get the digits from message
        while True:
            if message[index].isdigit():
                value = message[index] + value
                index -= 1
            else:
                break

        value = int(value)

        if value == 0 and random.randrange(1,100) <= self.character.badRate:
            self.bot_message("bad")
        elif value >= 5 and random.randrange(1,100) <= self.character.goodRate:
            self.bot_message("good")

    def bot_message(self, messagetype):
        '''
        Randomly sends a positive/negative message with very good or very bad rolls
        :param type: "good" or "bad"
        :return: none
        '''

        if messagetype == 'good':
                out = random.choice(self.character.goodMessages)
        else:
                out = random.choice(self.character.badMessages)

        out = out.replace("[userID]", self.character.stats['user id'])
        self.send(out, self.character.stats['webhook'])

    def chance_handler(self):
        '''
        Handler for chance roll button.
        '''

        self.parent.status_update("Rolling chance die.")

        # Check if details entered yet
        if self.character.stats['webhook'] == "" or self.character.stats['user id'] == "":
            # Tell user something is missing
            self.parent.status_update("User Details Missing.")
            return

        # use roll_chance method for character object
        # returns a list of strings, first states die value and second states its result 
        messages = self.character.roll_chance()

        for message in messages:
            self.send(message, self.character.stats['webhook'])
            time.sleep(1)

        # Prints final result to client console
        self.parent.status_update(messages[-1].replace(self.character.stats['user id'],"You"))

    def last_roll_display(self):
        '''
        method to display last roll in a pop up window
        '''

        # get last roll
        last_roll = self.character.get_last_roll()

        # check if empty
        if not last_roll:
            # # only status bar updated if empty
            self.parent.status_update("No previous rolls")

        else:
            # open Last_Roll_Display widget in its own window
            self.dialog = New_Window(Last_Roll_Display(self.character), "Last Roll")
            self.dialog.show()

    def send(self, message, webhook):
        '''
        Sends message to webhook
        '''

        # create connection
        # If expanding to other services further changes will be required here
        conn = http.client.HTTPSConnection("discordapp.com")
        
        # input sanitation: the seperator for each element is replaced by a space if found in message
        sep = "--11BOUND11"
        message = message.replace(sep, " ")

        # This payload will make a Discord webhook send message to its associated channel
        # If expanding to other services further changes may be required here
        payload = sep + "\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + message + "\r\n" + sep + "--"

        # headers for the connection
        # If expanding to other services further changes may be required here
        headers = {
                    'content-type': "multipart/form-data; boundary=" + sep[2:],
                    'cache-control': "no-cache",
                    }
        
        # sends a POST command to the webhook with the payload and headers defined above
        conn.request("POST", webhook, payload, headers)
        
        # get response
        res = conn.getresponse()
        
        # warning messages
        text = res.read()
        text = text.decode("utf-8")
        
        # first check if there was a warning message
        # For discord, the data will be blank unless error occures sending webhook
        # Usually a rate limit hit
        # For expansion to other services this may need to be updated
        
        if text != "":
            if "rate limited" in text:
                # confirms that is is a rate limit on Discord
                # Discord will helpfully tell the user how long they need to wait until the next retry 
                index1 = text.find('"retry_after"')
                chop = text[index1+13:]
                wait = ''
                for character in chop:
                    # find the wait time requested
                    # given in miliseconds usually
                    if character in '0123456789':
                        wait += character
                    if character == '\n':
                        break
                
                # wait will given in miliseconds, convert to seconds and add 0.5 just in case
                wait = int(wait)/1000 + 0.5
                
                # update status, should always have at least 3 significant digits
                self.parent.status_update("Rate limit hit. Will try again in " + str(wait)[:4] + " seconds.")

                # try again after wait
                time.sleep(wait)
                self.send(message, webhook)
                
            if "400 Bad Request" in text:
                # Likely bad bad URL
                # look into making a pop up dialogue instead
                self.parent.status_update("400 Bad Request - Double check URL.")
                return

            elif text != "":
                # Unexpected problem - Result printed to client console
                # goes as a temp message so it won't be overwritten by success message
                # user can still find results in last roll display
                # might look into making this a pop up dialogue instead
                index1 = text.find('"message"')
                index2 = text.find('\n', index1)
                chop = text[index1:index2]
                self.parent.statusBar.showMessage(chop)
                return
            # end of if statement for warning message

            # now include some rate limit protection
            remaining = int(res.getheader('X-RateLimit-Remaining'))
            # reset = int(res.getheader('X-RateLimit-Reset')) - int(time.time())

            # reset should be the number of seconds until rate limit refreshed
            # In my experience it will reset faster than this
            # For now, it will add delays to messages if remaining message count is less than or equal to 2

            if remaining <= 2:
                self.parent.status_update("Rate Limit approaching. Next message delay is 2 seconds.")
                # already a 1 second delay between messages, so extra secound added here
                time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dr = Main()
    dr.show()
    sys.exit(app.exec_())
