import random
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from player import Character
from stats import *
import sip

class Sheet(QWidget):
    '''
    Overall character sheet object
    '''
    def __init__(self, character):
        super().__init__()
        self.setStyleSheet("QPushButton:pressed { background-color: white }" )
        self.character = character
        self.character.edit_mode = False
        self.initUI()
        self.show()

    def initUI(self):
        #each section constructed as dedicated object
        self.char_info = Character_Info(self.character)

        #attributes
        self.attributes_label = QLabel("=====ATTRIBUTES=====")
        self.attributes_label.setStyleSheet("QLabel { font: 13pt }" )
        self.attributes_label.setAlignment(Qt.AlignCenter)
        self.attribute_mental_group = ATTRIBUTE_TYPE['mental']
        self.attribute_physical_group = ATTRIBUTE_TYPE['physical']
        self.attribute_social_group = ATTRIBUTE_TYPE['social']

        self.attribute_mental = Stat_Col(self.attribute_mental_group, self.character)
        self.attribute_physical = Stat_Col(self.attribute_physical_group, self.character)
        self.attribute_social =  Stat_Col(self.attribute_social_group, self.character)

        #others
        self.skills = Skills(self.character)
        self.arcana = Arcana(self.character)
        self.merits = Merits(self.character)
        self.mana = Mana(self.character)
        self.derivitives = Derivitives(self.character)

        #Health
        self.health = Health(self.character)
        #Willpower
        self.willpower = Willpower(self.character)

        #Gnosis
        gnosis = Stat(self.character, 'gnosis', maximum = 10, small=False)
        gnosis.setMaximumSize(gnosis.sizeHint())
        
        #Wisdom
        wisdom = Stat(self.character, 'wisdom', maximum = 10, small=False)

        #button to turn on edit mode
        self.edit_button = QPushButton("Edit")
        self.edit_button.setCheckable(True)
        self.edit_button.clicked.connect(self.edit_toggle)

        #test button - prints stats out to console
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.test)

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setAlignment(Qt.AlignTop)

        
        #top
        grid.addWidget(self.edit_button, 0,0)
        grid.addWidget(self.test_button, 0,1)
        grid.addWidget(self.char_info,1,0,1,3)
        grid.addWidget(self.attributes_label,2,0,1,3)

        #left side
        grid.addWidget(self.attribute_mental,3,0)
        grid.addWidget(self.skills,4,0,3,1)

        #middle
        grid.addWidget(self.attribute_physical, 3,1)
        grid.addWidget(self.arcana, 4,1)
        grid.addWidget(self.merits, 5,1)
        grid.addWidget(self.derivitives, 6,1)
        grid.setAlignment(self.derivitives, Qt.AlignBottom)
        
        #right
        last_col = QVBoxLayout()
        last_col.addWidget(self.attribute_social)
        last_col.addWidget(self.health)
        last_col.addWidget(self.willpower)
        last_col.setAlignment(self.willpower, Qt.AlignHCenter)
        last_col.addWidget(gnosis)
        last_col.setAlignment(gnosis, Qt.AlignHCenter)
        last_col.addWidget(wisdom)
        last_col.setAlignment(wisdom, Qt.AlignHCenter)
        last_col.addWidget(self.mana)
        last_col.setAlignment(self.mana, Qt.AlignHCenter)

        grid.addLayout(last_col,3,2,4,1)
        grid.setAlignment(last_col, Qt.AlignTop)
        

    def edit_toggle(self):
        #changed edit mode to the Checked status of the edit toggle
        self.character.edit_mode = self.edit_button.isChecked()
        if self.character.edit_mode:
            self.char_info.check_edit_mode()
        else:
            self.char_info.save_changes()
            self.character.update_derivitives()
            self.derivitives.update_all()
            self.willpower.update()
            self.health.update_max()
            #max mana/health update

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
        self.setStyleSheet("QLabel { font: 10pt}")
        self.character = character
        self.name = name
        self.initUI()
        self.check_edit_mode()

    def initUI(self):
        label = QLabel(self.name.title() + ":")
        label.setMinimumWidth(50)
        self.content = QLineEdit()
        self.content.setMaximumWidth(100)
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
        self.setStyleSheet("QLabel { font: 13pt}")
        self.character = character
        self.initUI()

    def initUI(self):
        label = QLabel("=====ATTRIBUTES=====")
        label.setAlignment(Qt.AlignCenter)
        mental_group = ATTRIBUTE_TYPE['mental']
        physical_group = ATTRIBUTE_TYPE['physical']
        social_group = ATTRIBUTE_TYPE['social']

        self.mental = Stat_Col(mental_group, self.character)
        self.physical = Stat_Col(physical_group, self.character)
        self.social =  Stat_Col(social_group, self.character)

        grid = QGridLayout()
        self.setLayout(grid)
        
        grid.addWidget(label, 0, 0, 1, 3) 
        grid.addWidget(self.mental,1,0)
        grid.addWidget(self.physical,1,1)
        grid.addWidget(self.social,1,2)

class Skills(QWidget):
    def __init__(self, character):
        '''
        Skills are a 3 span column.
        Each section contains physcial, social or mental skills.
        Labels indicate unlearned skill penalties.
        '''
        super().__init__()
        self.character = character
        self.setStyleSheet("QLabel { font: 10pt}")
        self.initUI()

    def initUI(self):
        overall_label = QLabel("===SKILLS===")
        overall_label.setStyleSheet("QLabel { font: 13pt}")
        overall_label.setAlignment(Qt.AlignCenter)
        mental_label = QLabel("MENTAL (-3)")
        mental_label.setAlignment(Qt.AlignCenter)
        physical_label = QLabel("PHYSICAL (-1)")
        physical_label.setAlignment(Qt.AlignCenter)
        social_label = QLabel("SOCIAL (-1)")
        social_label.setAlignment(Qt.AlignCenter)

        mental_group = SKILL_TYPE['mental']
        physical_group = SKILL_TYPE['physical']
        social_group = SKILL_TYPE['social']

        self.mental = Stat_Col(mental_group, self.character, type = 'skill')
        self.physical = Stat_Col(physical_group, self.character, type = 'skill')
        self.social =  Stat_Col(social_group, self.character, type = 'skill')
                                 

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

class Arcana(QWidget):
    def __init__(self, character):
        '''
        Skills are a 3 span column.
        Each section contains physcial, social or mental skills.
        Labels indicate unlearned skill penalties.
        '''
        super().__init__()
        self.setStyleSheet("QLabel { font: 13pt}")
        self.character = character
        self.initUI()

    def initUI(self):
        box = QVBoxLayout()
        box.setSpacing(0)
        box.setContentsMargins(0,0,0,0)
        self.setLayout(box)
        
        overall_label = QLabel("===ARCANA===")
        overall_label.setAlignment(Qt.AlignCenter)

        self.arcana = Stat_Col(ARCANA, self.character)

        box.setAlignment(Qt.AlignTop)
        box.addWidget(overall_label)
        box.addWidget(self.arcana)

class Merits(QWidget):
    '''
    Object for holding merits.
    Handles addition and removal of merits along with rating update. 
    '''
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.setStyleSheet("QLabel { font: 13pt}")
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
        self.grid.addWidget(self.label, 0, 0, 1, 3)
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setAlignment(self.label, Qt.AlignHCenter)
        
        self.delete_buttons = QButtonGroup()
        #the buttonClickedSlot method will take the ID of the clicked delete button as an argument
        self.delete_buttons.buttonClicked[int].connect(self.buttonClickedSlot)

        self.row = 1
        for stat in self.stats:
            #There can be a variable number of merits, so must be drawn with a loop.
            #starts at 1 since the lable takes the 0 spot.
            merit = Stat(self.character, stat, type="merit")
            delete_button = QPushButton("x")
            delete_button.setMaximumWidth(15)
            delete_button.setMaximumHeight(17)
            #a self.merits dict is made to help with deltion method
            #includes the Stats object, the deletion button and stat name
            self.merits[self.row] = [merit, delete_button, stat]
            #delete buttons are added to a button group with their row as an ID
            self.delete_buttons.addButton(delete_button,self.row)
            
            self.grid.addWidget(self.merits[self.row][1] ,self.row,0)
            self.grid.addWidget(self.merits[self.row][0] ,self.row,1,1,2)
            
            self.row += 1
        #Add the "add new" button for adding new merits
        self.new_button = QPushButton("Add New")
        self.new_button.setMaximumWidth(60)
        self.grid.addWidget(self.new_button, self.row, 0,1,3)
        self.new_button.clicked.connect(self.add_new)


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
            

    def add_new(self):
        '''
        Add new merit to list
        '''
        if not self.character.edit_mode:
            #check is edit mode
            #in future version edit mode toggle will disable button
            return

        #Ask for name of merit
        text, ok = QInputDialog.getText(self, 'Add Merit', 'Enter merit name:')
        
        if ok and str(text).lower() not in self.character.stats['merits']:
            #it won't add a second merit of the same name
            new = str(text).lower()
            #adds merit to character object
            self.character.stats['merits'][new] = 1

            #creates new Stat widget to display merit
            merit = Stat(self.character, new, type = "merit")
            #adds a delete button for it too
            delete_button = QPushButton("x")
            delete_button.setMaximumWidth(15)
            delete_button.setMaximumHeight(17)
            self.delete_buttons.addButton(delete_button,self.row)
            #adds it to the self.merits dict with current value of self.row as the key
            self.merits[self.row] = [merit, delete_button, new]

            #remove the add new button
            self.grid.removeWidget(self.new_button)

            #add the new Stat widget and delete button
            self.grid.addWidget(self.merits[self.row][1] ,self.row,0)
            self.grid.addWidget(self.merits[self.row][0] ,self.row,1,1,2)

            #add 1 to self.row
            self.row += 1

            #add the new button back to end
            self.grid.addWidget(self.new_button, self.row,0,1,3)

class Derivitives (QWidget):
    def __init__(self, character):
        '''
        Makes a column of dots.
        Takes list of Tuples in the form (title, current, max) and the associated character object.
        '''
        super().__init__()
        self.setStyleSheet("QLabel { font: 10pt}")
        self.character = character
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)

        self.devgrid = QGridLayout()
        self.devgrid.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.devgrid.setSpacing(5)
        self.devgrid.setContentsMargins(0,0,0,0)

        overall_base = QLabel("Base")
        overall_mod = QLabel("Modifier")
        overall_total = QLabel("Total")

        self.devgrid.addWidget(overall_base,0,1)
        self.devgrid.addWidget(overall_mod,0,2)
        self.devgrid.addWidget(overall_total,0,3)

        self.derived_stats = {}

        #size
        size_label = QLabel("Size: ")
        size_label.setToolTip("Regular humans are size 5")
        size_label.setCursor(QCursor(Qt.WhatsThisCursor))
        size_label.setContentsMargins(0,0,0,0)
        size_rating = Num_with_Line(str(self.character.stats['size']))
        
        size_mod = QSpinBox()
        size_mod.setMinimum(-100)
        size_mod.setValue(self.character.stats['size mod'])
        size_mod.setMaximumSize(QSize(35, 20))

        size_total_num = self.character.stats['size'] + self.character.stats['size mod']
        size_total = Num_with_Line(str(size_total_num))

        self.derived_stats['size'] = (size_rating, size_mod, size_total)
        size_mod.valueChanged.connect(lambda: self.update_deriv('size'))
        
        self.devgrid.addWidget(size_label,1,0)
        self.devgrid.addWidget(size_rating,1,1)
        self.devgrid.addWidget(size_mod,1,2)
        self.devgrid.addWidget(size_total,1,3)
        
        #speed
        speed_label = QLabel("Speed: ")
        speed_label.setToolTip("Dexterity + Strength + 5")
        speed_label.setCursor(QCursor(Qt.WhatsThisCursor))
        speed_rating = Num_with_Line(str(self.character.stats['speed']))
        
        speed_mod = QSpinBox()
        speed_mod.setMinimum(-100)
        speed_mod.setValue(self.character.stats['speed mod'])
        speed_mod.setMaximumSize(QSize(35, 20))

        speed_total_num = self.character.stats['speed'] + self.character.stats['speed mod']
        speed_total = Num_with_Line(str(speed_total_num))

        self.derived_stats['speed'] = (speed_rating, speed_mod, speed_total)
        speed_mod.valueChanged.connect(lambda: self.update_deriv('speed'))

        self.devgrid.addWidget(speed_label,2,0)
        self.devgrid.addWidget(speed_rating,2,1)
        self.devgrid.addWidget(speed_mod,2,2)
        self.devgrid.addWidget(speed_total,2,3)
        
        #defense
        defense_label = QLabel("Defense: ")
        defense_label.setToolTip("Lower of Dexterity or Wits")
        defense_label.setCursor(QCursor(Qt.WhatsThisCursor))
        defense_rating = Num_with_Line(str(self.character.stats['defense']))
        
        defense_mod = QSpinBox()
        defense_mod.setMinimum(-100)
        defense_mod.setValue(self.character.stats['defense mod'])
        defense_mod.setMaximumSize(QSize(35, 20))

        defense_total_num = self.character.stats['defense'] + self.character.stats['defense mod']
        defense_total = Num_with_Line(str(defense_total_num))

        self.derived_stats['defense'] = (defense_rating, defense_mod, defense_total)
        defense_mod.valueChanged.connect(lambda: self.update_deriv('defense'))

        self.devgrid.addWidget(defense_label,3,0)
        self.devgrid.addWidget(defense_rating,3,1)
        self.devgrid.addWidget(defense_mod,3,2)
        self.devgrid.addWidget(defense_total,3,3)
        
        #Int modifier
        initiative_label = QLabel("Initiative: ")
        initiative_label.setToolTip("Dexterity + Composure")
        initiative_label.setCursor(QCursor(Qt.WhatsThisCursor))
        initiative_rating = Num_with_Line(str(self.character.stats['initiative']))
        
        initiative_mod = QSpinBox()
        initiative_mod.setMinimum(-100)
        initiative_mod.setValue(self.character.stats['initiative mod'])
        initiative_mod.setMaximumSize(QSize(35, 20))

        initiative_total_num = self.character.stats['initiative'] + self.character.stats['initiative mod']
        initiative_total = Num_with_Line(str(initiative_total_num))

        self.derived_stats['initiative'] = (initiative_rating, initiative_mod, initiative_total)
        initiative_mod.valueChanged.connect(lambda: self.update_deriv('initiative'))

        self.devgrid.addWidget(initiative_label,4,0)
        self.devgrid.addWidget(initiative_rating,4,1)
        self.devgrid.addWidget(initiative_mod,4,2)
        self.devgrid.addWidget(initiative_total,4,3)

        #group up
        self.grid.addLayout(self.devgrid,0,0,1,2)

        space = QLabel(" ")
        self.grid.addWidget(space,5,0)
        
        #Armor
        armor_label = QLabel("Armor: ")
        self.armor_entry = QSpinBox()
        self.armor_entry.setMaximumSize(QSize(35, 20))
        self.armor_entry.valueChanged.connect(lambda: self.update_others("armor", self.armor_entry.value()))
        
        self.grid.addWidget(armor_label,6,0)
        self.grid.addWidget(self.armor_entry,6,1, alignment=Qt.AlignLeft)
        
        #Beats
        beat_label = QLabel("Beats: ")
        beatbox = QHBoxLayout()
        beats = {}
        #add button group for beat changes
        for i in range(1,6):
            if i <= self.character.stats["beats"]:
                beats[i] = Square("beats", self.character, filled=True)
                beatbox.addWidget(beats[i])
                
            else:
                beats[i] = Square("beats", self.character, filled=False)
                beatbox.addWidget(beats[i])

        self.grid.addWidget(beat_label,7,0)
        self.grid.addLayout(beatbox,7,1)

        self.beat_group = Squares_Group("beats", 5, beats, self.character)
        for pos in beats:
            self.beat_group.addButton(beats[pos],pos)

        #add a click handler for the entire group
        self.beat_group.buttonClicked[int].connect(self.beat_group.buttonClickedSlot)
        
        #XP
        self.xp_label = QLabel("XP: ")
        self.xp_entry = QSpinBox()
        self.xp_entry.setMaximumSize(QSize(35, 20))
        self.xp_entry.setValue(self.character.stats['xp'])
        self.xp_entry.valueChanged.connect(lambda: self.update_others("xp", self.xp_entry.value()))
        
        self.grid.addWidget(self.xp_label,8,0)
        self.grid.addWidget(self.xp_entry,8,1, alignment=Qt.AlignLeft)
        
        #Arcane Beats
        arcbeat_label = QLabel("Arcane Beats: ")
        arcbeatbox = QHBoxLayout()
        arcbeats = {}
        #add button group for beat changes
        for i in range(1,6):
            if i <= self.character.stats["arcane beats"]:
                arcbeats[i] = Square("arcane beats", self.character, filled=True)
                arcbeatbox.addWidget(arcbeats[i])
                
            else:
                arcbeats[i] = Square("arcane beats", self.character, filled=False)
                arcbeatbox.addWidget(arcbeats[i])

        self.grid.addWidget(arcbeat_label,9,0)
        self.grid.addLayout(arcbeatbox,9,1)

        self.arcbeat_group = Squares_Group("arcane beats", 5, arcbeats, self.character)
        for pos in arcbeats:
            self.arcbeat_group.addButton(arcbeats[pos],pos)

        #add a click handler for the entire group
        self.arcbeat_group.buttonClicked[int].connect(self.arcbeat_group.buttonClickedSlot)
        
        #Arcane XP
        self.axp_label = QLabel("Arcane XP: ")
        self.axp_entry = QSpinBox()
        self.axp_entry.setMaximumSize(QSize(35, 20))
        self.axp_entry.setValue(self.character.stats['arcane xp'])
        self.axp_entry.valueChanged.connect(lambda: self.update_others("arcane xp", self.axp_entry.value()))
        
        self.grid.addWidget(self.axp_label,10,0)
        self.grid.addWidget(self.axp_entry,10,1, alignment=Qt.AlignLeft)
    
    def update_deriv (self, stat):
        #update labels and ratings for a derived stat
        stats = self.derived_stats[stat]
        rating = stats[0]
        mod = stats[1]
        total = stats[2]
        rating.change_text(str(self.character.stats[stat]))
        self.character.stats[stat + ' mod'] = mod.value()
        total_num = self.character.stats[stat] + self.character.stats[stat + ' mod']
        total.change_text(str(total_num))

    def update_others(self, stat, value):
        #update xps and armor
        self.character.stats[stat] = value

    def update_all(self):
        for stat in self.derived_stats:
            self.update_deriv(stat)

class Willpower (QWidget):
    '''
    Willpower with dots and bozes like this:
            Willpower
          0  0  0  0  0
         [ ][ ][ ][ ][ ]
     '''
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.current = character.stats['willpower']
        self.filled = character.stats['willpower filled']
        self.setStyleSheet("QLabel { font: 13pt}")
        self.initUI()
        self.setMaximumSize(self.sizeHint())

    def initUI(self):
        box = QVBoxLayout()
        box.setSpacing(5)
        box.setContentsMargins(0,0,0,0)

        label = QLabel('Willpower')
        label.setAlignment(Qt.AlignCenter)
        box.addWidget(label)
        
        self.setLayout(box)
        grid = QGridLayout()
        grid.setSpacing(5)
        grid.setContentsMargins(0,0,0,0)
        squares = {}
        self.dots = {}
        col = 0

        for x in range(1,11):
            if x <= self.current:
                self.dots[x] = Dot(filled=True, type = "big")
            else:
                self.dots[x] = Dot(filled=False, type = "big")
            if x <= self.filled:
                squares[x] = Square("willpower", self.character, filled=True)
            else:
                squares[x] = Square("willpower", self.character)
            grid.addWidget(self.dots[x],0,x)
            grid.addWidget(squares[x],1,x)


        self.willpower_group = Squares_Group("willpower filled", 10, squares, self.character)
        for pos in squares:
            self.willpower_group.addButton(squares[pos],pos)

        #add a click handler for the entire group
        self.willpower_group.buttonClicked[int].connect(self.willpower_group.buttonClickedSlot)

        box.addLayout(grid)

    def update(self):
        self.current = self.character.stats['willpower']

        for x in range(1,11):
            if x <= self.current:
                self.dots[x].filled = True
                self.dots[x].select_Image()
            else:
                self.dots[x].filled = False
                self.dots[x].select_Image()

class Health (QWidget):
    '''
    Health with dots and boxes like this:
             Health
          0  0  0  0  0
         [ ][ ][ ][ ][ ]

    Boxes can go through all 4 stages
     '''
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.setStyleSheet("QLabel { font: 13pt}")
        self.initUI()

    def initUI(self):
        box = QVBoxLayout()
        box.setSpacing(5)
        box.setContentsMargins(0,0,0,0)

        label = QLabel('Health')
        label.setAlignment(Qt.AlignCenter)
        box.addWidget(label)
        
        self.setLayout(box)
        grid = QGridLayout()
        grid.setSpacing(5)
        grid.setContentsMargins(0,0,0,0)
        squares = {}
        self.dots = {}
        col = 0

        health = self.character.stats['health']
        

        for x in range(1,13):
            if x <= health[0]:
                #health[0] is max jealth
                self.dots[x] = Dot(filled=True, type = "big")
            else:
                self.dots[x] = Dot(filled=False, type = "big")
            squares[x] = Square("health", self.character, index=x)
            grid.addWidget(self.dots[x],0,x)
            grid.addWidget(squares[x],1,x)


        #this will add buttons to button group and fill them appropiately
        self.health_group = Health_Group(squares, self.character)

        #add a click handler for the entire group
        self.health_group.buttonClicked[int].connect(self.health_group.change)

        box.addLayout(grid)

    def update_max(self):
        max_health = self.character.stats['health'][0]

        for x in range(1,13):
            if x <= max_health:
                self.dots[x].filled = True
                self.dots[x].select_Image()
            else:
                self.dots[x].filled = False
                self.dots[x].select_Image()

class Health_Group(QButtonGroup):
    def __init__(self, buttons, character):
        super().__init__()
        self.character = character
        self.buttons = buttons

        health = character.stats['health']
        
        for pos in buttons:
            #add buttons to group
            self.addButton(buttons[pos],pos)
            buttons[pos].group = self
            buttons[pos].setContextMenuPolicy(Qt.CustomContextMenu)
            buttons[pos].customContextMenuRequested.connect(buttons[pos].reduce)

        #loop to initialise squares
        #counts from 0 to value starting with agg damage
        pos = 1
        for point in range(0,health[3]):
            buttons[pos].filled = 3
            buttons[pos].select_Image()
            pos += 1

        for point in range(0,health[2]):
            buttons[pos].filled = 2
            buttons[pos].select_Image()
            pos += 1

        for point in range(0,health[1]):
            buttons[pos].filled = 1
            buttons[pos].select_Image()
            pos += 1

    def change(self,index, reduce=False):
        #change everything
        if not reduce:
            self.buttons[index].change_Image()
        for button in range(1,index):
            current = self.buttons[button].filled
            if current < self.buttons[index].filled:
                self.buttons[button].filled = self.buttons[index].filled
                self.buttons[button].select_Image()

        for button in range(index+1, 13):
            current = self.buttons[button].filled
            if current > self.buttons[index].filled:
                self.buttons[button].filled = self.buttons[index].filled
                self.buttons[button].select_Image()

        #record changes
        health = [0, 0, 0, 0]

        for button in range(1,13):
            rating = self.buttons[button].filled
            health[rating] += 1

        self.character.stats['health'][1:] = health[1:]

class Mana(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()
        self.setMaximumSize(self.sizeHint())

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        #Overall
        self.overall_label = QLabel("Mana")
        self.overall_label.setStyleSheet("QLabel { font: 13pt}")

        #Spend
        self.spent_label = QLabel("Spent")
        self.spent_label.setStyleSheet("QLabel {text-decoration: underline; font: 10pt}")
        self.spent = QSpinBox()
        self.spent.setValue(self.character.stats['mana spent'])
        self.spent.setMaximumSize(QSize(35, 20))
        self.spent.setMaximum(self.character.stats['mana'] + self.character.stats['mana mod'])
        self.spent.valueChanged.connect(self.update_mana)

        
        #Current total
        self.current_label = QLabel("Current")
        self.current_label.setStyleSheet("QLabel {text-decoration: underline; font: 10pt}")
        current_num = self.character.stats['mana'] + self.character.stats['mana mod'] - self.character.stats['mana spent']
        self.current = Num_with_Line(str(current_num) + "/" + str(self.character.stats['mana']))

        self.grid.addWidget(self.overall_label, 0, 0, 1, 2)
        self.grid.setAlignment(self.overall_label, Qt.AlignHCenter)
        self.grid.addWidget(self.spent_label, 1, 0)
        self.grid.addWidget(self.current_label, 1, 1)
        self.grid.addWidget(self.spent, 2, 0)
        self.grid.addWidget(self.current, 2, 1)

    def update_mana(self):
        self.character.stats['mana spent'] = self.spent.value()
        self.spent.setMaximum(self.character.stats['mana'] + self.character.stats['mana mod'])
        
        current_num = self.character.stats['mana'] + self.character.stats['mana mod'] - self.character.stats['mana spent']
        self.current.change_text(str(current_num) + "/" + str(self.character.stats['mana']))

class Hover_Label_Col(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = "==" + title + "=="
        self.initUI()

    def initUI(self):
        box = QVBoxLayout()
        self.setLayout(box)
        box.setSpacing(5)
        box.setContentsMargins(0,0,0,0)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("Qlabel {font = 13pt}")

        

class Stat_Col(QWidget):
    def __init__(self, stats, character, type=""):
        '''
        Makes a column of dots.
        Takes list of Tuples in the form (title, current, max) and the associated character object.
        '''
        #Can rewrite to take list of keys instead.
        super().__init__()
        self.stats = stats
        self.character = character
        self.type = type
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)
        grid.setSpacing(0)
        grid.setContentsMargins(0,0,0,0)

        row = 0
            
        for stat in self.stats:
            if self.type == "skill":
                rotes = self.character.stats['rote skill']
                rote_button = (Square(stat, self.character, filled= stat in rotes))
                rote_button.clicked.connect(rote_button.change_Image)
                grid.addWidget(rote_button,row,0)
                
            grid.addWidget(Stat(self.character, stat, type = self.type),row,1)
            row += 1
        

class Stat(QWidget):
    '''
    Object for showing dots in the form "name ooooo" for small dots.
    In form "name\n OOOOO" for big dots
    '''
    
    def __init__(self, character, name, maximum = 5, small=True, type=""):
        super().__init__()
        self.maximum = maximum
        self.name = name
        self.character = character
        self.type = type
        if self.type == "merit":
            self.current = character.stats['merits'][name]
        else:
            self.current = character.stats[name]
        if type == "merit":
            self.setStyleSheet("QLabel { font: 8pt}")
            self.initSmallUI()
        elif small:
            self.setStyleSheet("QLabel { font: 10pt}")
            self.initSmallUI()
        else:
            self.setStyleSheet("QLabel { font: 13pt}")
            self.initBigUI()

    def initSmallUI(self):
        dots = {}
        box = QHBoxLayout()
        self.setLayout(box)
        box.setSpacing(5)
        box.setContentsMargins(0,0,0,0)
        
        self.label = QLabel(self.name.title())
        box.addWidget(self.label)

        #it will initilaise with the dots filled accoridng to character.stats['name']
        #Each dot is an abstract button widget
        for x in range(1,self.maximum+1):
            if x <= self.current:
                dots[x] = Dot(filled=True)
            else:
                dots[x] = Dot(filled=False)
            box.addWidget(dots[x])

        #a button group is created that will be used for changing dot rating
        #mght be possible to reorganise code to avoid second loop
        self.dot_group = Dots_Group(self.name, dots, self.character, maximum = self.maximum, type = self.type)
        for pos in dots:
            self.dot_group.addButton(dots[pos],pos)

        #add a click handler for the entire group
        self.dot_group.buttonClicked[int].connect(self.dot_group.buttonClickedSlot)

    def initBigUI(self):
        dots = {}
        box = QVBoxLayout()
        dotbox = QHBoxLayout()
        self.setLayout(box)
        box.setSpacing(5)
        box.setContentsMargins(0,0,0,0)
        
        self.label = QLabel(self.name.title())
        self.label.setAlignment(Qt.AlignCenter)
        #will one day use a proper CSS to set this
        
        box.addWidget(self.label)

        #it will initilaise with the dots filled accoridng to character.stats['name']
        #Each dot is an abstract button widget
        for x in range(1,self.maximum+1):
            if x <= self.current:
                dots[x] = Dot(filled=True, type = "big")
            else:
                dots[x] = Dot(filled=False, type = "big")
            dotbox.addWidget(dots[x])

        box.addLayout(dotbox)

        #a button group is created that will be used for changing dot rating
        #mght be possible to reorganise code to avoid second loop
        self.dot_group = Dots_Group(self.name, dots, self.character, maximum = self.maximum)
        for pos in dots:
            self.dot_group.addButton(dots[pos],pos)

        #add a click handler for the entire group
        self.dot_group.buttonClicked[int].connect(self.dot_group.buttonClickedSlot)
        

class Dots_Group(QButtonGroup):
    '''
    A QButton group that handles what happens when dots are clicked.
    '''
    def __init__(self, stat_name, dots, character, maximum=5, type=''):
        super().__init__()
        self.dots = dots
        self.stat_name = stat_name
        self.character = character
        self.maximum = maximum
        self.type = type
        self.last_click = 0
        
    def buttonClickedSlot(self,index):
        '''
        Index will be the dot clicked, counting up from 1.
        This will fill all dots up to and including index, and empty anything bigger than index.
        The associated stat in the character object will also be updated.
        '''
        if not self.character.edit_mode:
            #nothing happens when not in edit mode
            return
        
        if self.last_click == index:
            #if a dotis clicked a second time in a row it unfills it
            index -= 1
        
        for x in range(1,self.maximum + 1):
            #currently has maximum hard coded
            #will need to replace with user entered maximum
            if x <= index:
                self.dots[x].filled = True
                self.dots[x].select_Image()
            elif x > index:
                self.dots[x].filled = False
                self.dots[x].select_Image()

        #associated stat is updated along with any derivitives
        if self.type == 'merit':
            self.character.stats['merits'][self.stat_name] = index
        else:
            self.character.stats[self.stat_name] = index
        self.character.update_derivitives()
        self.last_click = index

class Dot(QAbstractButton):
    '''
    Object for the dot.
    Sets the images for the dot and image changing method
    '''
    def __init__(self, type="small", filled=False):
        super().__init__()
        self.filled = filled
        self.type = type
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.select_Image()

    def paintEvent(self, event):
        #paints the dot
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def select_Image(self):
        '''
        Checks if dot is currently filled and draws appropiate image.
        '''
        if self.type == "small":
            filled = r"images\filled.png"
            unfilled = r"images\unfilled.png"
        else:
            filled = r"images\big_filled.png"
            unfilled = r"images\big_unfilled.png"

        
        if self.filled:
            self.pixmap = QPixmap(filled)
    
        else:
            self.pixmap = QPixmap(unfilled)

        self.setMaximumSize(self.pixmap.size())
        self.setMinimumSize(self.pixmap.size())
        self.update()

class Square(QAbstractButton):
    '''
    Object for the square.
    Sets the images for the square and image changing method
    '''
    def __init__(self, stat, character, filled=0, index=None, group = None):
        super().__init__()
        self.filled = filled
        self.index = index
        self.stat = stat
        self.character = character
        self.group = None
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.squares = {0: r"images\square_unfilled.png",
                        1: r"images\square_one.png",
                        2: r"images\square_two.png",
                        3: r"images\square_full.png",
                        }
        self.select_Image()

    def paintEvent(self, event):
        #paints the square
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def select_Image(self):
        '''
        Draws appropiate square.
        '''
        self.pixmap = QPixmap(self.squares[self.filled])

        self.setMaximumSize(self.pixmap.size())
        self.setMinimumSize(self.pixmap.size())
        self.update()

    def change_Image(self):
        if self.character.edit_mode and self.stat in SKILLS:
            #changes rote skills if edit mode
            self.filled = not self.filled
            if self.filled:
                self.character.stats['rote skill'].add(self.stat)
            else:
                self.character.stats['rote skill'].remove(self.stat)
                
        elif self.stat == 'health':
            self.filled += 1
            if self.filled == 4:
                self.filled = 0

        self.select_Image()

    def reduce (self):
        self.filled -= 1
        if self.filled < 0:
            self.filled = 3
 
        self.select_Image()

        self.group.change(self.index, reduce = True)

class Squares_Group(QButtonGroup):
    '''
    A QButton group that handles what happens when squares are clicked.
    '''
    def __init__(self, stat_name, stat_max, squares, character):
        super().__init__()
        self.squares = squares
        self.stat_name = stat_name
        self.stat_max = stat_max + 1
        self.character = character
        self.last_click = 0
        
    def buttonClickedSlot(self,index):
        '''
        Index will be the square clicked, counting up from 1.
        This will fill all squares up to and including index, and empty anything bigger than index.
        The associated stat in the character object will also be updated.
        '''
        if self.last_click == index:
            #if a box is clicked twice in a row it unfills it
            index -= 1
            
        for x in range(1, self.stat_max):
            if x <= index:
                self.squares[x].filled = True
                self.squares[x].select_Image()
            elif x > index:
                self.squares[x].filled = False
                self.squares[x].select_Image()

        #associated stat is updated 
        self.character.stats[self.stat_name] = index
        self.last_click = index

class Num_with_Line(QWidget):
    '''
    A Label with a line under it.
    '''
    def __init__(self, text):
        super().__init__()
        self.text = " " + text + " "
        self.initUI()
        
        
    def initUI(self):      
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.setLayout(self.grid)
        
        self.rating = QLabel(self.text)
        self.rating.setStyleSheet("QLabel {text-decoration: underline}")
        self.rating.setAlignment(Qt.AlignCenter)
        
        self.grid.addWidget(self.rating,0,0)

    def change_text(self, new_text):
        self.text = " " + new_text + " "
        self.rating.setText(self.text)

if __name__ == '__main__':
    #code to open UI for testing
    app = QApplication(sys.argv)
    char = Character()
    char.stats['health'] = [1,1,1,1]
    char.stats['merits']['test'] = 3
    test = Sheet(char)
    #test = Derivitives(char)
    test.show()
    sys.exit(app.exec_())
