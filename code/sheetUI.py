import random
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from player import Character
from stats import *
import sip

DOT_SIZE = 12

class Sheet(QWidget):
    '''
    Overall character sheet object
    '''
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.character.edit_mode = False
        self.initUI()
        self.show()

    def initUI(self):
        #each section constructed as dedicated object
        self.char_info = Character_Info(self.character)
        attributes = Attributes(self.character)
        skills = Skills(self.character)
        arcana = Arcana(self.character)
        merits = Merits(self.character)

        #button to turn on edit mode
        self.edit_button = QPushButton("Edit")
        self.edit_button.setCheckable(True)
        self.edit_button.clicked.connect(self.edit_toggle)
        self.edit_button.setStyleSheet("QPushButton:pressed { background-color: white }" )

        #test button - prints stats out to console
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.test)

        grid = QGridLayout()
        self.setLayout(grid)

        
        grid.addWidget(self.edit_button, 0, 0)
        grid.addWidget(self.test_button, 0, 1)
        grid.addWidget(self.char_info, 1, 0, 1, 3)
        grid.addWidget(attributes, 2, 0, 1, 3) 
        grid.addWidget(skills,3,0,3,1)
        grid.addWidget(arcana,3,1)
        grid.addWidget(merits,4,1)

    def edit_toggle(self):
        #changed edit mode to the Checked status of the edit toggle
        self.character.edit_mode = self.edit_button.isChecked()
        if self.character.edit_mode:
            self.char_info.check_edit_mode()
        else:
            self.char_info.save_changes()

    def test(self):
        #test functions to ensure that chnages are saved
        print(self.character.stats)
            

class Character_Info(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):

        grid = QGridLayout()
        self.setLayout(grid)
        
        col = 0
        self.headers = {}
        for section in HEADERS:
            row = 0
            for name in section:
                self.headers[name] = Label_Entry_Combo(self.character, name)
                grid.addWidget(self.headers[name],row,col)
                row += 1
            col += 1

    def check_edit_mode(self):
        for name in self.headers:
            self.headers[name].check_edit_mode()

    def save_changes(self):
        for name in self.headers:
            self.headers[name].save_changes()
            

class Label_Entry_Combo(QWidget):
    def __init__(self, character, name):
        super().__init__()
        self.character = character
        self.name = name
        self.initUI()
        self.check_edit_mode()

    def initUI(self):
        label = QLabel(self.name.title() + ":")
        label.setMinimumWidth(70)
        label.setStyleSheet("QLabel { font: 10pt}")
        self.content = QLineEdit()
        self.content. setMaximumWidth(100)
        self.content.insert(self.character.stats[self.name])
        
        box = QHBoxLayout()
        self.setLayout(box)
        box.setSpacing(5)
        box.setContentsMargins(0,0,0,0)

        box.addWidget(label)
        box.addWidget(self.content)

    def save_changes(self):
        self.character.stats[self.name] = self.content.text()
        self.content.setReadOnly(True)

    def check_edit_mode(self):
        self.content.setReadOnly(not self.character.edit_mode)

        
        

class Attributes (QWidget):
    '''
    Attributes are a 3 span column
    Split between mental, physical, social
    3 rows each
    '''
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):
        label = QLabel("=====ATTRIBUTES=====")
        label.setAlignment(Qt.AlignCenter)
        mental_group = self.get_points('mental')
        physical_group = self.get_points('physical')
        social_group = self.get_points('social')

        self.mental = Stat_Col(mental_group, self.character)
        self.physical = Stat_Col(physical_group, self.character)
        self.social =  Stat_Col(social_group, self.character)

        grid = QGridLayout()
        self.setLayout(grid)
        
        grid.addWidget(label, 0, 0, 1, 3) 
        grid.addWidget(self.mental,1,0)
        grid.addWidget(self.physical,1,1)
        grid.addWidget(self.social,1,2)
        
    def get_points(self, category):
        '''
        Get the ratings for attributes in designated category.
        A global variable lists the stats in each category.
        Stats are stored as a dict in the character object, each stat name is a key.
        Returns a 2 element list of stat's name and its current rating.
        '''
        #Note: can remove this method and rewrite Stat_Col to take list of keys
        output = []
        for stat in ATTRIBUTE_TYPE[category]:
            output += [[stat, self.character.stats[stat]]]
        return output

class Skills(QWidget):
    def __init__(self, character):
        '''
        Skills are a 3 span column.
        Each section contains physcial, social or mental skills.
        Labels indicate unlearned skill penalties.
        '''
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):
        overall_label = QLabel("===SKILLS===")
        overall_label.setAlignment(Qt.AlignCenter)
        mental_label = QLabel("MENTAL (-3)")
        mental_label.setAlignment(Qt.AlignCenter)
        physical_label = QLabel("PHYSICAL (-1)")
        physical_label.setAlignment(Qt.AlignCenter)
        social_label = QLabel("SOCIAL (-1)")
        social_label.setAlignment(Qt.AlignCenter)

        mental_group = self.get_points('mental')
        physical_group = self.get_points('physical')
        social_group = self.get_points('social')

        self.mental = Stat_Col(mental_group, self.character)
        self.physical = Stat_Col(physical_group, self.character)
        self.social =  Stat_Col(social_group, self.character)
                                 

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setContentsMargins(0,0,0,0)

        grid.addWidget(overall_label, 0, 0) 
        grid.addWidget(mental_label, 1, 0)
        grid.addWidget(self.mental, 2, 0)
        grid.addWidget(physical_label, 3, 0)
        grid.addWidget(self.physical, 4, 0)
        grid.addWidget(social_label, 5, 0)
        grid.addWidget(self.social, 6, 0)

    def get_points(self, category):
        '''
        Get the ratings for skills in designated category.
        A global variable lists the stats in each category.
        Stats are stored as a dict in the character object, each stat name is a key.
        Returns a 2 element list of stat's name and its current rating.
        '''
        #Note: can remove this method and rewrite Stat_Col to take list of keys
        output = []
        for stat in SKILL_TYPE[category]:
            output += [[stat, self.character.stats[stat]]]
        return output

class Arcana(QWidget):
    def __init__(self, character):
        '''
        Skills are a 3 span column.
        Each section contains physcial, social or mental skills.
        Labels indicate unlearned skill penalties.
        '''
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):
        box = QVBoxLayout()
        box.setSpacing(0)
        box.setContentsMargins(0,0,0,0)
        self.setLayout(box)
        
        overall_label = QLabel("===ARCANA===")
        overall_label.setAlignment(Qt.AlignCenter)

        arcana_group = self.get_points()

        self.arcana = Stat_Col(arcana_group, self.character)

        box.addWidget(overall_label) 
        box.addWidget(self.arcana)

    def get_points(self):
        '''
        Get the ratings for skills in designated category.
        A global variable lists the stats in each category.
        Stats are stored as a dict in the character object, each stat name is a key.
        Returns a 2 element list of stat's name and its current rating.
        '''
        #Note: can remove this method and rewrite Stat_Col to take list of keys
        output = []
        for stat in ARCANA:
            output += [[stat, self.character.stats[stat]]]
        return output

class Merits(QWidget):
    '''
    Object for holding merits.
    Handles addition and removal of merits along with rating update. 
    '''
    def __init__(self, character):
        super().__init__()
        self.character = character
        #Merits are a dict within the character.stats dict.
        self.stats = character.stats['merits']
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.merits = {}

        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)
        
        self.label = QLabel('===MERITS===')
        self.grid.addWidget(self.label, 0, 0, 1, 2)
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setAlignment(self.label, Qt.AlignHCenter)
        
        self.delete_buttons = QButtonGroup()
        #the buttonClickedSlot method will take the ID of the clicked delete button as an argument
        self.delete_buttons.buttonClicked[int].connect(self.buttonClickedSlot)

        self.row = 1
        for stat in self.stats:
            #There can be a variable number of merits, so must be drawn with a loop.
            #starts at 1 since the lable takes the 0 spot.
            merit = Stat(self.character, stat, self.stats[stat])
            delete_button = QPushButton("x")
            delete_button.setMaximumWidth(15)
            delete_button.setMaximumHeight(17)
            #a self.merits dict is made to help with deltion method
            #includes the Stats object, the deletion button and stat name
            self.merits[self.row] = [merit, delete_button, stat]
            #delete buttons are added to a button group with their row as an ID
            self.delete_buttons.addButton(delete_button,self.row)
            
            self.grid.addWidget(self.merits[self.row][0] ,self.row,0)
            self.grid.addWidget(self.merits[self.row][1] ,self.row,1)
            
            self.row += 1
        #Add the "add new" button for adding new merits
        self.new_button = QPushButton("Add New")
        self.new_button.setMaximumWidth(60)
        self.grid.addWidget(self.new_button, self.row, 0)
        self.new_button.clicked.connect(self.add_new)
        #for some reason alignment goes nuts without this line
        self.grid.setAlignment(self.new_button, Qt.AlignTop)


    def buttonClickedSlot(self,index):
        '''
        Removes row holding the clicked button.
        '''
        if not self.character.edit_mode:
            #check is edit mode
            #in future version edit mode toggle will disable button
            return
        
        #remove stat widget
        self.grid.removeWidget(self.merits[index][0])
        sip.delete(self.merits[index][0])
        self.merits[index][0] = None

        #remove deletion button
        self.grid.removeWidget(self.merits[index][1])
        sip.delete(self.merits[index][1])
        self.merits[index][1] = None

        #remove associated data
        del self.character.stats['merits'][self.merits[index][2]]
        del self.merits[index]

        #I toyed with adding code to reorder the IDs to make upfor the missing one but it is quite difficult
        #No need to even do it though sicne new items will always add to end anyway
            

    def add_new(self):
        '''
        Add new merit to list
        '''
        if not self.character.edit_mode:
            #check is edit mode
            #in future version edit mode toggle will disable button
            return

        #Ask for name of merit
        text, ok = QInputDialog.getText(self, 'Add Merit', 
            'Enter merit name:')
        
        if ok and str(text).lower() not in self.character.stats['merits']:
            #it won't add a second merit of the same name
            new = str(text)
            #adds merit to character object
            self.character.stats['merits'][new.lower()] = 0

            #creates new Stat widget to display merit
            merit = Stat(self.character, new.title(), 0)
            #adds a delete button for it too
            delete_button = QPushButton("x")
            delete_button.setMaximumWidth(15)
            delete_button.setMaximumHeight(17)
            self.delete_buttons.addButton(delete_button,self.row)
            #adds it to tge self.merits dict with current value of self.row as the key
            self.merits[self.row] = [merit, delete_button, new]

            #remove the add new button
            self.grid.removeWidget(self.new_button)

            #add the new Stat widget and delete button
            self.grid.addWidget(self.merits[self.row][0] ,self.row,0)
            self.grid.addWidget(self.merits[self.row][1] ,self.row,1)

            #add 1 to self.row
            self.row += 1

            #add the new button back to end
            self.grid.addWidget(self.new_button, self.row,0)

class Stat_Col(QWidget):
    def __init__(self, stats, character):
        '''
        Makes a column of dots.
        Takes list of Tuples in the form (title, current, max) and the associated character object.
        '''
        #Can rewrite to take list of keys instead.
        super().__init__()
        self.stats = stats
        self.character = character
        self.initUI()

    def initUI(self):
        box = QVBoxLayout()
        box.setSpacing(0)
        box.setContentsMargins(0,0,0,0)
        self.setLayout(box)
        
        for stat in self.stats:
            box.addWidget(Stat(self.character, stat[0], stat[1]))

class Stat(QWidget):
    '''
    Object for showing dots in the form "name ooooo".
    '''
    
    def __init__(self, character, name, current, maximum = 5):
        super().__init__()
        self.current = current
        self.maximum = maximum
        self.name = name
        self.character = character
        self.initUI()

    def initUI(self):
        dots = {}
        box = QHBoxLayout()
        self.setLayout(box)
        box.setSpacing(5)
        box.setContentsMargins(0,0,0,0)
        
        self.label = QLabel(self.name.title())
        #will one day use a proper CSS to set this
        self.label.setStyleSheet("QLabel { font: 10pt}")
        self.label.setMinimumWidth(70)
        box.addWidget(self.label)
        col = 1

        #it will initilaise with the dots filled accoridng to character.stats['name']
        #Each dot is an abstract button widget
        for x in range(1,self.maximum+1):
            if x <= self.current:
                dots[x] = Dot(filled=True)
            else:
                dots[x] = Dot(filled=False)
            box.addWidget(dots[x])
            col += 1

        #a button group is created that will be used for changing dot rating
        #mght be possible to reorganise code to avoid second loop
        self.dot_group = Dots_Group(self.name, dots, self.character)
        for pos in dots:
            self.dot_group.addButton(dots[pos],pos)

        #add a click handler for the entire group
        self.dot_group.buttonClicked[int].connect(self.dot_group.buttonClickedSlot)

class Dots_Group(QButtonGroup):
    '''
    A QButton group that handles what happens when dots are clicked.
    '''
    def __init__(self, stat_name, dots, character):
        super().__init__()
        self.dots = dots
        self.stat_name = stat_name
        self.character = character
        
    def buttonClickedSlot(self,index):
        '''
        Index will be the dot clicked, counting up from 1.
        This will fill all dots up to and including index, and empty anything bigger than index.
        The associated stat in the character object will also be updated.
        '''
        if not self.character.edit_mode:
            #nothing happens when not in edit mode
            return
        for x in range(1,6):
            #currently has maximum hard coded
            #will need to replace with user entered maximum
            if x <= index:
                self.dots[x].filled = True
                self.dots[x].select_Image()
            elif x > index:
                self.dots[x].filled = False
                self.dots[x].select_Image()

        #associated stat is updated along with any derivitives 
        self.character.stats[self.stat_name] = index
        self.character.update_derivitives()

class Dot(QAbstractButton):
    '''
    Object for the dot.
    Sets the images for the dot and image changing method
    '''
    def __init__(self, filled=False):
        super().__init__()
        self.filled = filled
        self.select_Image()
        #dot is set to not get any bigger or smaller than default size
        self.setMaximumSize(DOT_SIZE, DOT_SIZE)
        self.setMinimumSize(DOT_SIZE, DOT_SIZE)

    def paintEvent(self, event):
        #paints the dot
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        #must check if i even need this
        return QSize(1, 1)

    def select_Image(self):
        '''
        Checks if dot is currently filled and draws appropiate image.
        '''
        if self.filled:
            self.pixmap = QPixmap(r"images\filled.png")
            #without self.update() the draw event is delayed until the mouse moves off clicked dot
            self.update()
        else:
            self.pixmap = QPixmap(r"images\unfilled.png")
            self.update()

if __name__ == '__main__':
    #code to open UI for testing
    app = QApplication(sys.argv)
    char = Character()
    char.stats['merits'] = {"resources" : 1, "mentor" : 3}
    test = Sheet(char)
    test.show()
    sys.exit(app.exec_())
