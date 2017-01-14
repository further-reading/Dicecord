#Dicecord: Dice Roller and Character Sheet Viewer for use in conjucntion with Discord Chat Channels
#Copyright (C) 2017  Roy Healy
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#version 1.2 -> PyQT UI revamp


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from character import Character
import http.client, string, random, time, sys

VERSION = "1.2"

class Main(QMainWindow):
    #Main window
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        self.setWindowTitle('Dicecord')
        self.setWindowIcon(QIcon('D10.ico'))
        
        #file menu
        menubar = self.menuBar()
        file_Menu = menubar.addMenu('&File')
        ##last roll
        last_roll_action = QAction('Show Last Roll', self)
        last_roll_action.setShortcut('Ctrl+H')
        last_roll_action.triggered.connect(self.last_roll_display)
        file_Menu.addAction(last_roll_action)
        ##exit
        exit_Action = QAction('&Exit', self)
        exit_Action.setShortcut('Ctrl+Q')
        exit_Action.triggered.connect(self.close)
        file_Menu.addAction(exit_Action)
        
        #import menu
        import_Menu = menubar.addMenu('&Import')
        ##import
        import_Action = QAction('View/Change User Details', self)
        import_Action.setShortcut('Ctrl+N')
        import_Action.triggered.connect(self.import_show)
        import_Menu.addAction(import_Action)

        #help menu
        help_Menu = menubar.addMenu('&Help')
        ##about
        about_Action = QAction('About', self)
        help_Menu.addAction(about_Action)

        #add status bar and change its style sheet
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("QStatusBar{border-top: 1px outset grey;}")
        #set permanent message
        #This is needed as otherwise hovering over menu overwrites statusbar contents
        self.message = QLabel("Please import user details to begin.")
        self.statusbar.addWidget(self.message)

        #set the central widget as the Dice_Roller widget
        self.setCentralWidget(Dice_Roller())
        self.show()

    def last_roll_display(self):
        '''
        method to display last roll in a pop up window
        '''

        #get last roll
        last_roll = char.get_last_roll()

        #check if empty
        if last_roll == []:
            ##only status bar updated if empty
            self.status_update("No previous rolls")

        else:
            #open Last_Roll_Display widget in its own window
            self.dialog = Last_Roll_Display()
            self.dialog.show()

    def import_show(self):
        '''
        method to open details import window
        '''
        self.dialog = Details_Import()
        self.dialog.show()

    def status_update(self, message):
        '''
        method to update status bar message
        called by other widgets
        '''
        self.statusbar.removeWidget(self.message)
        self.message = QLabel(message)
        self.statusbar.addWidget(self.message)
        app.processEvents()


class Details_Import(QMainWindow):
    '''
    Details Import window
    '''
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Details')
        self.setWindowIcon(QIcon('D10.ico'))
        
        self.setCentralWidget(Import_Widget())
        

class Import_Widget(QWidget):
    '''
    Widget for importing details
    Will be repalced when moving to full character import/creation
    '''
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        '''
        UI is form layout asking for webhook URL and user ID
        '''
        form = QFormLayout()
        self.setLayout(form)
        webhook_label = QLabel("Webhook URL")
        self.webhook_field = QLineEdit()
        if char.webhook != '':
            #if not empty add current contents
            self.webhook_field.insert(char.webhook)
        

        userID_label = QLabel("User ID")
        self.userID_field = QLineEdit()
        if char.ID != '':
            #if not empty adds current contents
            #IDs are saved in form <@xxx> to allow for @mentions when mesaging
            #this window will only accept the xxx part so the other characters are stripped
            self.userID_field.insert(char.ID[2:-1])

        save_button = QPushButton("Submit")
        #I find that the default UI style is very subtle when button is pushed
        ##Updating to white to make it more obvious
        save_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        save_button.clicked.connect(self.save_setup)

        #add content to UI
        form.addRow(webhook_label, self.webhook_field)
        form.addRow(userID_label, self.userID_field)
        form.addRow(QLabel(), save_button)

    def save_setup(self):
        '''
        Function to saves setup and close window
        '''     
        global char
        #will update a global character variable
        
        webhook = self.webhook_field.text()

        #adds to userID to allow for @mentions in discord channels
        userID = "<@" + self.userID_field.text() + ">"

        #make the new character object
        char = Character(ID = userID, webhook = webhook)

        #close
        #currently closes by calling the main window object directly
        #might be a more universale way to do this?
        dr.dialog.close()

        #update main window status
        #as before it uses the name of the main window object directly, but that may not be avoidable since it's a new window
        dr.status_update("User details imported.")


class Last_Roll_Display(QMainWindow):
    '''
    Opens window to display last roll details
    '''
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        #It's just a QTextEdit with the details inside
        #Using QTextEdit to allow for copy/paste
        #To do: look into making a dialogue and having a "add to clipboard button"
        self.setWindowTitle('Last Roll')
        self.setWindowIcon(QIcon('D10.ico')) 

        text = QTextEdit()
        text.setText("Your previous roll is as follows:\n")
        self.setCentralWidget(text)
        
        rolls = char.get_last_roll()

        for roll in rolls:
            #Replaces character ID with "You"
            text.append(roll.replace(char.ID,"You"))
        

class Dice_Roller(QWidget):
    '''
    widget for dice rolls
    '''
    def __init__(self):
        '''
        Initialises with rote and quiet mode to false, dice to 0 and again to 10
        '''
        super().__init__()
        self.initUI()
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

        #labe; for spinner
        label = QLabel()
        label.setText("Enter Dice Pool")
        innergrid.addWidget(label, 0,1)

        #add inner grid to normal grid
        grid.addLayout(innergrid,0 ,0)
        
        #roll button
        roll_button = QPushButton("Roll Dice Pool")
        roll_button.setStyleSheet("QPushButton:pressed { background-color: white }" )
        roll_button.clicked.connect(self.roll_handler)
        grid.addWidget(roll_button, 2,2)

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
        again10.toggled.connect(lambda: self.change_again(again9))
        grid.addWidget(again9, 1, 1)
        
        again8 = QRadioButton()
        again8.setText("8 Again")
        again10.toggled.connect(lambda: self.change_again(again8))
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
        if char.webhook == "" or char.ID == "":
            #Tell user something is missing and then stop
            dr.status_update("User Details Missing.")
            return

        dr.status_update("Rolling dice.")

        #reads UI elements to get other values
        dice = self.num.value()
        if dice == 0:
            dr.status_update("Please select at least 1 die.")
            return

        #Qt checkboxes are tri-state, return 2 if checked.
        rote = self.rote_sel.checkState() == 2
        quiet = self.quiet_sel.checkState() == 2

        #call roll_set method on character object
        #this returns a list of strings of each die result follwoed by total successes
        #if quiet mode selected, returns a single element list stating total successes
        messages = char.roll_set(dice, rote, self.again, quiet)

        for message in messages:
            self.send(message, char.webhook)
            time.sleep(1)

        #Updates status with final element in list, which will be total successes
        dr.status_update(messages[-1].replace(" for " + char.ID,""))
        

    def chance_handler(self):
        '''
        Handler for chance roll button.
        '''

        dr.status_update("Rolling chance die.")

        #Check if details entered yet
        if char.webhook == "" or char.ID == "":
            #Tell user something is missing
            dr.status_update("User Details Missing.")
            return

        #use roll_chance method for character object
        #returns a list of strings, first states die value and second states its result 
        messages = char.roll_chance()

        for message in messages:
            self.send(message, char.webhook)
            time.sleep(1)

        #Prints final result to client console
        dr.status_update(messages[-1].replace(char.ID,"You"))

    def send(self, message, webhook):
        '''
        Sends message to webhook
        '''

        #create connection
        #If expanding to other services further changes will be required here
        conn = http.client.HTTPSConnection("discordapp.com")
        
        #input sanitation: the seperator for each element of payload is randomised and also replaced by a space if found in message
        sep = "--" + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
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
        try:
            conn.request("POST", webhook, payload, headers)
        except:
            #error here usually due to bad webhook
            dr.status_update("Error sending message. Double check webhook URL.")
            return
        
        #get response
        res = conn.getresponse()
        
        #warning messages
        text = res.read()
        text = text.decode("utf-8")
        
        #first check if there was a warning message
        #For discord, the data will be blank unless error occures sending webhook
        #Usually a rate limit approached
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
                dr.status_update("Rate limit hit. Will try again in " + str(wait)[:4] + " seconds.")

                #try again after wait
                time.sleep(wait)
                send(message, webhook)
                
            else:
                #Unexpected problem - Result printed to client console
                #goes as a temp message so it won't be overwritten by success message
                #user can still find results in last roll display
                index1 = text.find('"message"')
                index2 = text.find('\n', index1)
                chop = text[index1:index2]
                dr.statusBar.showMessage(chop)
            #end of if statement for warning message

            #now include some rate limit protection
            remaining = int(res.getheader('X-RateLimit-Remaining'))
            reset = int(res.getheader('X-RateLimit-Reset')) - int(time.time())

            #reset should be the number of seconds until rate limit refreshed
            #In my experience it will reset faster than this
            #For now, it will add delays to messages if remaining message count is less than or equal to 2

            if remaining <= 2:
                dr.status_update("Rate Limit approaching. Next message delay is 2 seconds.")
                #already a 1 second delay between messages, so extra secound added here
                time.sleep(1)
                


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #initialise with a blank character object
    #when import added will skip this and instead ask for input or offer character creation at startup
    char = Character()
    dr = Main()
    sys.exit(app.exec_())
