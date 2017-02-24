#Dicecord: Dice Roller and Character Sheet Viewer for use in conjucntion with Discord Chat Channels
#Copyright (C) 2017  Roy Healy
#
#version 1.0


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QTabWidget
from PyQt5.QtWidgets import QMainWindow, qApp, QTextEdit, QLabel, QGridLayout, QFileDialog
from PyQt5.QtWidgets import QAction, QCheckBox, QRadioButton, QSpinBox, QFormLayout
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QCoreApplication, QSize
from player import Character
import sheetUI, inventoryUI
import http.client, string, random, time, sys, copy

VERSION = "v1.0"

class Sheet(QTabWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.statsheet = sheetUI.StatsSheet(character)
        self.inventory = inventoryUI.InventorySheet(character, self.statsheet)
        self.notes = QTextEdit()
        font = QFont()
        font.setPointSize(12)
        self.notes.setFont(font)
        self.notes.setText(character.notes)
        self.notes.textChanged.connect(self.update_notes)
        
        self.addTab(self.statsheet,"Stats")
        self.addTab(self.inventory,"Inventory")
        self.addTab(self.notes,"Notes")

    def edit_toggle(self, toggle):
        self.character.edit_mode = toggle
        self.statsheet.edit_toggle()
        self.inventory.edit_toggle()

    def update_notes(self):
        self.character.notes = self.notes.toPlainText()

class Main(QMainWindow):
    '''
    Main window for displaying character sheet
    '''
    def __init__(self, character):
        super().__init__()
        self.character = character
        #save original as a copy to detect changes on quit
        self.old_character = copy.deepcopy(character)
        self.path = None
        self.initUI()
        self.show()
        
        
    def initUI(self):
        
        self.setWindowTitle('Dicecord')
        self.setWindowIcon(QIcon(r'images\D10.ico'))
        self.sheet = Sheet(self.character)
        self.setCentralWidget(self.sheet)

        #toolbar
        self.toolbar = self.addToolBar("Actions")
        ##roller
        roller_Action = QAction(QIcon(r'images\D10.ico'), 'Edit', self)
        roller_Action.setShortcut('Ctrl+R')
        roller_Action.triggered.connect(self.open_roller)
        self.toolbar.addAction(roller_Action)

        ##edit mode
        self.edit_Action = QAction(QIcon(r'images\edit.ico'), 'Edit', self)
        self.edit_Action.triggered.connect(self.edit_mode)
        self.edit_Action.setCheckable(True)
        self.toolbar.addAction(self.edit_Action)

        #file menu
        menubar = self.menuBar()
        file_Menu = menubar.addMenu('&File')
        ##Open
        open_Action = QAction('&Open', self)
        open_Action.setShortcut('Ctrl+O')
        file_Menu.addAction(open_Action)
        open_Action.triggered.connect(self.import_character)
        ##Save
        save_Action = QAction('&Save', self)
        save_Action.setShortcut('Ctrl+S')
        file_Menu.addAction(save_Action)
        save_Action.triggered.connect(self.save)
        ##Save As
        save_as_Action = QAction('&Save As', self)
        save_as_Action.setShortcut('Ctrl+Shift+S')
        file_Menu.addAction(save_as_Action)
        save_as_Action.triggered.connect(lambda: self.save(save_as = True))
        ##Exit
        exit_Action = QAction('&Exit', self)
        exit_Action.setShortcut('Ctrl+Q')
        exit_Action.triggered.connect(self.close)
        file_Menu.addAction(exit_Action)

        #help menu
        help_Menu = menubar.addMenu('&Help')
        ##about
        about_Action = QAction('About', self)
        about_Action.triggered.connect(self.about_display)
        help_Menu.addAction(about_Action)

    def edit_mode(self):
        if self.edit_Action.isChecked():
            #edit mode turned on, save current copy of character
            self.old_character = copy.deepcopy(self.character)
            
        #toggle edit mode on sheet
        self.sheet.edit_toggle(self.edit_Action.isChecked())

        
        if not self.edit_Action.isChecked():
            #edit mode turned off
            #check for changes
            if self.character.stats != self.old_character.stats:
                if self.path:
                    #bring up save/discard choice dialog
                    self.ask_save()
                else:
                    #no path yet, bring up save filedialog immediately
                    self.save(save_as = True)
                
            
    def ask_save(self):
        message = QMessageBox()
        message.setWindowTitle("Save Changes")
        message.setIcon(QMessageBox.Question)
        message.setText("Do you want to save changes?")
        message.setInformativeText("Press 'reset' to undo all changes.")
        message.addButton("Save As", QMessageBox.RejectRole)
        message.addButton("Save", QMessageBox.NoRole)
        
        if self.old_character:
            message.addButton("Reset", QMessageBox.ApplyRole)
            
        message.exec_()
        clicked = message.clickedButton().text()
        
        if clicked == 'Save':
            self.save()
            
        elif clicked == 'Save As':
            self.save(save_as = True)

        elif clicked == 'Reset':
            self.sheet = sheetUI.Sheet(self.character)
            self.setCentralWidget(self.sheet)

    def save(self, save_as = False):
        name = self.character.stats['shadow name']
        if name == '':
            name = 'character'

        path = "characters/" + name

        if self.path == None or save_as:
            #open filedialog to get path
            fname = QFileDialog.getSaveFileName(self, 'Save file', path, "XML Files (*.xml)")
            if fname[0] == '':
                #nothing chosen, end function
                return
            
            self.path = fname[0]

        self.character.save_xml(self.path)
        #set as old_character copy for detecting further changes on quit
        self.old_character = copy.deepcopy(self.character)

    def import_character(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', "characters/", "XML Files (*.xml)")
        
        if fname[0] == '':
            return

        self.path = fname[0]

        self.character = Character.from_xml(self.path)
        #set as old_character copy for detecting further changes on quit
        self.old_character = copy.deepcopy(self.character)

        #redraw UI with new character object
        self.sheet = Sheet(self.character)
        self.setCentralWidget(self.sheet)

    def open_roller(self):
        self.dialog = New_Window(Roller(self.character), "Roller")
        self.dialog.show()

    def about_display(self):
        file = open(r'LICENSE\ABOUT.txt', 'r')
        content = file.read()
        file.close()
        box = QLabel(content)
        self.dialog = New_Window(box, "Dicecord " + VERSION)
        self.dialog.show()

    def closeEvent(self, event):
        if self.character.stats != self.old_character.stats or self.character.notes != self.old_character.notes:
            #unsaved changes
            message = QMessageBox()
            message.setWindowTitle("Save Changes")
            message.setIcon(QMessageBox.Question)
            message.setText("Do you want to save changes before exiting?")
            message.addButton("Save", QMessageBox.AcceptRole)
            message.addButton("Save As", QMessageBox.RejectRole)
            message.addButton("No", QMessageBox.ApplyRole)
            message.addButton("Cancel", QMessageBox.HelpRole)
        
            
            message.exec_()
            clicked = message.clickedButton().text()

            if clicked == "Save":
                self.save()
                
            elif clicked == "Save As":
                self.save(save_as=True)

            elif clicked == "Cancel":               
                event.ignore()
                return

            event.accept()
    

class Roller(QMainWindow):
    '''
    Dice Roller
    '''
    
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()
        
        
    def initUI(self):
        
        self.setWindowTitle('Dicecord')
        self.setWindowIcon(QIcon(r'images\D10.ico'))
        

        #add status bar and change its style sheet
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("QStatusBar{border-top: 1px outset grey;}")
        #set permanent message
        #This is needed as otherwise hovering over menu overwrites statusbar contents
        self.message = QLabel()
        self.statusbar.addWidget(self.message)
        
        if self.character.stats['webhook'] == '' or self.character.stats['user id'] == '':
            #add message if now ebhook or user id present
            self.status_update("Please add user details to sheet.")

        #set the central widget as the Dice_Roller widget
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
        self.dialog = New_Window(box, "Dicecord " + VERSION)
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


class Last_Roll_Display(QWidget):
    '''
    Opens window to display last roll details
    '''
    
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()
        
    def initUI(self):
        #It's just a QTextEdit with the details inside
        #Using QTextEdit to allow for copy/paste
        #To do: look into making a dialogue and having a "add to clipboard button"
        text = "Your previous roll: \n"
        rolls = self.character.get_last_roll()

        for roll in rolls:
            #Replaces character ID with "You"
            text += "\n" + roll.replace(self.character.stats['user id'], "You")
        

        grid = QGridLayout()
        self.setLayout(grid)
        
        content = QLabel(text)
        grid.addWidget(content,0 ,0, 1, 2)
        content.setStyleSheet("QLabel { font: 12pt; border: 3px inset palette(dark); border-radius: 3px; background-color: white; color: #545454;}" )
        clipboard = QApplication.clipboard()
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(lambda: clipboard.setText(text))
        copy_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        grid.addWidget(copy_button,1 ,1)
        

class Dice_Roller(QWidget):
    '''
    widget for dice rolls
    '''
    def __init__(self, parent, character):
        '''
        Initialises with rote and quiet mode to false, dice to 0 and again to 10
        '''
        super().__init__()
        self.initUI()
        self.parent = parent
        self.character = character
        self.rote = False
        self.quiet = False
        self.again = 10
        self.dice = 0
        
    def initUI(self):
        '''
        UI for dice roller
        '''
        
        grid = QGridLayout()
        self.setLayout(grid)
        #inner grid for the dice roll selecter + its label
        innergrid = QGridLayout()

        #dice_pool_selecter
        #inner grid for the dice roll selecter + its label
        innergrid = QGridLayout()

        #Spinner for selecting pool number
        self.num = QSpinBox()
        self.num.setMaximumSize(QSize(35, 20))
        innergrid.addWidget(self.num, 0,0)

        #label for spinner
        label = QLabel()
        label.setText("Enter Dice Pool")
        innergrid.addWidget(label, 0,1)

        #add inner grid to normal grid
        grid.addLayout(innergrid,0 ,0)

        #Show Last Roll button
        last_roll_display_button = QPushButton("Show Last Roll")
        last_roll_display_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        last_roll_display_button.clicked.connect(self.last_roll_display)
        grid.addWidget(last_roll_display_button, 2,2)
        
        #roll button
        roll_button = QPushButton("Roll Dice Pool")
        roll_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        roll_button.clicked.connect(self.roll_handler)
        grid.addWidget(roll_button, 0,2)

        #chance roll button
        chance_button = QPushButton("Roll Chance Die")
        chance_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        chance_button.clicked.connect(self.chance_handler)
        grid.addWidget(chance_button, 1,2)

        #rote check
        self.rote_sel = QCheckBox()
        self.rote_sel.setText("Rote")
        grid.addWidget(self.rote_sel, 1,0)

        #quiet check
        self.quiet_sel = QCheckBox()
        self.quiet_sel.setText("Quiet Mode")
        grid.addWidget(self.quiet_sel, 2,0)

        #again buttons
        #10 is selected on initiation
        #Might look into making this an explicit button group instead
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
        
        #dict showing value for each button
        agains = {'10 Again' : 10,
                  '9 Again' : 9,
                  '8 Again' : 8}

        #uses text of pushed button as key, sets value of self.again
        self.again = agains[button.text()]
                
    def roll_handler(self):
        '''
        handler for when roll button pushed
        '''
        #Check if details entered yet
        if self.character.stats['webhook'] == "" or self.character.stats['user id'] == "":
            #Tell user something is missing and then stop
            self.parent.status_update("User Details Missing.")
            return

        self.parent.status_update("Rolling dice.")

        #reads UI elements to get other values
        dice = self.num.value()
        if dice == 0:
            self.parent.status_update("Please select at least 1 die.")
            return

        #Qt checkboxes are tri-state, return 2 if checked.
        rote = self.rote_sel.checkState() == 2
        quiet = self.quiet_sel.checkState() == 2

        #call roll_set method on character object
        #this returns a list of strings of each die result follwoed by total successes
        #if quiet mode selected, returns a single element list stating roll summary
        messages = self.character.roll_set(dice, rote, self.again, quiet)

        #quiet mode, only send first message to channel, which will be a summary
        if quiet:
            self.send(messages[0], self.character.stats['webhook'])

        else:
            for message in messages:
                self.send(message, self.character.stats['webhook'])
                time.sleep(1)

        #Updates status with final element in list, which will be total successes
        self.parent.status_update(messages[-1].replace(" for " + self.character.stats['user id'],""))
        

    def chance_handler(self):
        '''
        Handler for chance roll button.
        '''

        self.parent.status_update("Rolling chance die.")

        #Check if details entered yet
        if self.character.stats['webhook'] == "" or self.character.stats['user id'] == "":
            #Tell user something is missing
            self.parent.status_update("User Details Missing.")
            return

        #use roll_chance method for character object
        #returns a list of strings, first states die value and second states its result 
        messages = char.roll_chance()

        for message in messages:
            self.send(message, char.stats['webhook'])
            time.sleep(1)

        #Prints final result to client console
        self.parent.status_update(messages[-1].replace(self.character.stats['user id'],"You"))

    def last_roll_display(self):
        '''
        method to display last roll in a pop up window
        '''

        #get last roll
        last_roll = self.character.get_last_roll()

        #check if empty
        if last_roll == []:
            ##only status bar updated if empty
            self.parent.status_update("No previous rolls")

        else:
            #open Last_Roll_Display widget in its own window
            self.dialog = New_Window(Last_Roll_Display(self.character), "Last Roll")
            self.dialog.show()

    def send(self, message, webhook):
        '''
        Sends message to webhook
        '''

        #create connection
        #If expanding to other services further changes will be required here
        conn = http.client.HTTPSConnection("discordapp.com")
        
        #input sanitation: the seperator for each element is replaced by a space if found in message
        sep = "--11BOUND11"
        message = message.replace(sep, " ")

        #This payload will make a Discord webhook send message to its associated channel
        #If expanding to other services further changes may be required here
        payload = sep + "\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + message + "\r\n" + sep + "--"

        #headers for the connection
        #If expanding to other services further changes may be required here
        headers = {
        'content-type': "multipart/form-data; boundary=" + sep[2:],
        'cache-control': "no-cache",
        }
        
        #sends a POST command to the webhook with the payload and headers defined above
        conn.request("POST", webhook, payload, headers)
        
        #get response
        res = conn.getresponse()
        
        #warning messages
        text = res.read()
        text = text.decode("utf-8")
        
        #first check if there was a warning message
        #For discord, the data will be blank unless error occures sending webhook
        #Usually a rate limit hit
        #For expansion to other services this may need to be updated
        
        if text != "":
            if "rate limited" in text:
                #confirms that is is a rate limit on Discord
                #Discord will helpfully tell the user how long they need to wait until the next retry 
                index1 = text.find('"retry_after"')
                chop = text[index1+13:]
                wait = ''
                for character in chop:
                    #find the wait time requested
                    #given in miliseconds usually
                    if character in '0123456789':
                        wait += character
                    if character == '\n':
                        break
                
                #wait will given in miliseconds, convert to seconds and add 0.5 just in case
                wait = int(wait)/1000 + 0.5
                
                #update status, should always have at least 3 significant digits
                self.parent.status_update("Rate limit hit. Will try again in " + str(wait)[:4] + " seconds.")

                #try again after wait
                time.sleep(wait)
                send(message, webhook)
                
            if "400 Bad Request" in text:
                #Likely bad bad URL
                #look into making a pop up dialogue instead
                self.parent.status_update("400 Bad Request - Double check URL.")
                return

            else:
                #Unexpected problem - Result printed to client console
                #goes as a temp message so it won't be overwritten by success message
                #user can still find results in last roll display
                #might look into making this a pop up dialogue instead
                index1 = text.find('"message"')
                index2 = text.find('\n', index1)
                chop = text[index1:index2]
                self.parent.statusBar.showMessage(chop)
                return
            #end of if statement for warning message

            #now include some rate limit protection
            remaining = int(res.getheader('X-RateLimit-Remaining'))
            reset = int(res.getheader('X-RateLimit-Reset')) - int(time.time())

            #reset should be the number of seconds until rate limit refreshed
            #In my experience it will reset faster than this
            #For now, it will add delays to messages if remaining message count is less than or equal to 2

            if remaining <= 2:
                self.parent.status_update("Rate Limit approaching. Next message delay is 2 seconds.")
                #already a 1 second delay between messages, so extra secound added here
                time.sleep(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #initialise with a blank character object
    #when import added will skip this and instead ask for input or offer character creation at startup
    char = Character()
    dr = Main(char)
    sys.exit(app.exec_())
