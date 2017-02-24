#Chronicles of Darkness Character Sheet for use in conjunction with Dicecord.
#   Copyright (C) 2017  Roy Healy

import math
import sys, sip
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from player import Character
from stats import *
import basicUI

class StatsSheet(QWidget):
    '''
    Overall character sheet object
    '''
    def __init__(self, character):
        super().__init__()
        self.setStyleSheet("QPushButton:pressed { background-color: white }" )
        self.character = character
        self.character.update_derivitives()
        self.character.edit_mode = False
        self.initUI()

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

        self.attribute_mental = basicUI.Stat_Col(self.attribute_mental_group, self.character)
        self.attribute_physical = basicUI.Stat_Col(self.attribute_physical_group, self.character)
        self.attribute_social =  basicUI.Stat_Col(self.attribute_social_group, self.character)

        #skills
        self.skills = Skills(self.character)

        #arcana
        self.arcana = Arcana(self.character)

        #merits
        self.merits = Merits(self.character)

        #mana
        self.mana = Mana(self.character)

        #advantages
        self.derivitives = Derivitives(self.character)

        #Health
        self.health = Health(self.character)
        
        #Willpower
        self.willpower = Willpower(self.character)

        #Gnosis
        gnosis = basicUI.Stat(self.character, 'gnosis', maximum = 10, small=False)
        gnosis.setMaximumSize(gnosis.sizeHint())
        
        #Wisdom
        wisdom = basicUI.Stat(self.character, 'wisdom', maximum = 10, small=False)

        #Conditions
        self.conditions = basicUI.Hover_Label_Col("CONDITIONS", self.character, 'conditions')

        #Aspirations
        self.aspirations = basicUI.Hover_Label_Col("ASPIRATIONS", self.character, 'aspirations')
        
        #Obsessions
        self.obsessions = basicUI.Hover_Label_Col("OBSESSIONS", self.character, 'obsessions')

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setAlignment(Qt.AlignTop)

        
        #top
        grid.addWidget(self.char_info,1,0,1,3)
        grid.addWidget(self.attributes_label,2,0,1,3)

        #left side
        grid.addWidget(self.attribute_mental,3,0)
        grid.addWidget(self.skills,4,0,3,1)
        grid.setAlignment(self.skills, Qt.AlignTop)

        #middle
        grid.addWidget(self.attribute_physical, 3,1)
        grid.addWidget(self.arcana, 4,1)
        grid.addWidget(self.merits, 5,1)
        grid.setAlignment(self.merits, Qt.AlignHCenter)
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
        last_col.addWidget(self.conditions)
        last_col.setAlignment(self.conditions, Qt.AlignHCenter)
        last_col.addWidget(self.aspirations)
        last_col.setAlignment(self.aspirations, Qt.AlignHCenter)
        last_col.addWidget(self.obsessions)
        last_col.setAlignment(self.obsessions, Qt.AlignHCenter)

        grid.addLayout(last_col,3,2,4,1)
        grid.setAlignment(last_col, Qt.AlignTop)
        
        

    def edit_toggle(self):
        #toggle edit mode on relevant stats
        self.merits.edit_toggle()
        self.obsessions.edit_toggle()
        self.aspirations.edit_toggle()
        self.char_info.edit_toggle()
        
        if not self.character.edit_mode:
            #apply changes
            self.character.update_derivitives()
            self.derivitives.update_all()
            self.willpower.update()
            self.health.update_max()
            self.mana.update_mana()

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
                self.headers[name] = basicUI.Label_Entry_Combo(self.character, name)
                grid.addWidget(self.headers[name],row,col)
                row += 1
            col += 1

    def edit_toggle(self):
        for name in self.headers:
            self.headers[name].edit_toggle()

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

        self.mental = basicUI.Stat_Col(mental_group, self.character, type = "skill")
        self.physical = basicUI.Stat_Col(physical_group, self.character, type = "skill")
        self.social =  basicUI.Stat_Col(social_group, self.character, type = "skill")
                                 

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
        Arcana dots.
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

        self.arcana = basicUI.Stat_Col(ARCANA, self.character)

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
        self.initUI()

    def initUI(self):
        self.box = QVBoxLayout()
        self.box.setSpacing(0)
        self.box.setContentsMargins(0,0,0,0)
        self.setLayout(self.box)

        stats = self.character.stats['merits']
        self.merits = {}
        
        self.label = QLabel('===MERITS===')
        self.box.addWidget(self.label)
        self.box.setAlignment(Qt.AlignTop)
        self.box.setAlignment(self.label, Qt.AlignHCenter)
        
        self.delete_buttons = QButtonGroup()
        #the buttonClickedSlot method will take the ID of the clicked delete button as an argument
        self.delete_buttons.buttonClicked[int].connect(self.edit_entry)

        self.row = 1
        for stat in stats:
            #There can be a variable number of merits, so must be drawn with a loop.
            #starts at 1 since the label takes the 0 spot.
            merit = basicUI.Stat(self.character, stat, type="merit")
            #a self.merits dict is made to help with deltion method
            self.merits[self.row] = merit
            #delete buttons are added to a button group with their row as an ID
            self.delete_buttons.addButton(merit.label,self.row)
            
            self.box.addWidget(self.merits[self.row])
            
            self.row += 1
        
        #Add the "add new" button for adding new merits
        if self.character.edit_mode:
            self.edit_toggle()

    def edit_toggle(self):
        if self.character.edit_mode:
            self.new_button = QPushButton("Add New")
            self.new_button.setMaximumWidth(60)
            self.new_button.clicked.connect(self.edit_entry)
            self.box.addWidget(self.new_button)

        else:
            self.box.removeWidget(self.new_button)
            sip.delete(self.new_button)
            

    def edit_entry(self,index=None):
        '''
        Edit the widget contents.
        Used for updating a current entry, deleting a current entry or adding a new one.
        '''

        if not self.character.edit_mode:
            #Actions only possible in edit mode
            return
        
        if not index:
            current_title = None
            #add new item if no index given
            label, tooltip, ok = basicUI.Label_Tooltip_Dialog.get_input(wintitle = "Add Merit")

        else:
            #edit current item
            current = self.merits[index]
            current_title = current.label.text().title()
            current_tooltip = current.label.toolTip()
            label, tooltip, ok = basicUI.Label_Tooltip_Dialog.get_input(title = current_title, tooltip = current_tooltip, edit = True, wintitle = "Change Merit")
        
        if not ok:
            #cancel pressed
            return

        if not current_title and label.lower() in self.character.stats['merits']:
            #add new but title already in use
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Merit with this name already exists.")
            msg.setInformativeText("Please use unique name.")
            msg.setWindowTitle("Duplicate Name")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

        elif not current_title:
            #Only adds new if entry by that name does not exist yet
            #add entry on character object
            new = label.lower()
            self.character.stats["merit details"][new] = tooltip
            self.character.stats["merits"][new] = 0

            #creates entry
            merit = basicUI.Stat(self.character, new, type="merit")
            self.merits[self.row] = merit
            self.delete_buttons.addButton(merit.label,self.row)

            #remove the add new button
            self.box.removeWidget(self.new_button)

            #add the new Stat widget and delete button
            self.box.addWidget(merit)

            #add 1 to self.row
            self.row += 1

            #add the new button back to end
            self.box.addWidget(self.new_button)
        

        elif "####DELETE####" in label:
            #delete chosen
            #remove stat widget
            self.box.removeWidget(self.merits[index])
            sip.delete(self.merits[index])

            #remove associated data
            del self.character.stats["merits"][current_title.lower()]
            del self.character.stats["merit details"][current_title.lower()]
            del self.merits[index]
            
        else:
            #Update tooltip of existing entry
            current.label.setToolTip(tooltip)
            self.character.stats["merit details"][current_title.lower()] = tooltip
            if tooltip == '':
                #update cursor if blank now
                current.label.setCursor(QCursor(Qt.ArrowCursor))
            else:
                current.label.setCursor(QCursor(Qt.WhatsThisCursor))

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
        size_rating = basicUI.Num_with_Line(str(self.character.stats['size']))
        
        size_mod = QSpinBox()
        size_mod.setMinimum(-100)
        size_mod.setValue(self.character.stats['size mod'])
        size_mod.setMaximumSize(QSize(35, 20))

        size_total_num = self.character.stats['size'] + self.character.stats['size mod']
        size_total = basicUI.Num_with_Line(str(size_total_num))

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
        speed_rating = basicUI.Num_with_Line(str(self.character.stats['speed']))
        
        speed_mod = QSpinBox()
        speed_mod.setMinimum(-100)
        speed_mod.setValue(self.character.stats['speed mod'])
        speed_mod.setMaximumSize(QSize(35, 20))

        speed_total_num = self.character.stats['speed'] + self.character.stats['speed mod']
        speed_total = basicUI.Num_with_Line(str(speed_total_num))

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
        defense_rating = basicUI.Num_with_Line(str(self.character.stats['defense']))
        
        defense_mod = QSpinBox()
        defense_mod.setMinimum(-100)
        defense_mod.setValue(self.character.stats['defense mod'])
        defense_mod.setMaximumSize(QSize(35, 20))

        defense_total_num = self.character.stats['defense'] + self.character.stats['defense mod']
        defense_total = basicUI.Num_with_Line(str(defense_total_num))

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
        initiative_rating = basicUI.Num_with_Line(str(self.character.stats['initiative']))
        
        initiative_mod = QSpinBox()
        initiative_mod.setMinimum(-100)
        initiative_mod.setValue(self.character.stats['initiative mod'])
        initiative_mod.setMaximumSize(QSize(35, 20))

        initiative_total_num = self.character.stats['initiative'] + self.character.stats['initiative mod']
        initiative_total = basicUI.Num_with_Line(str(initiative_total_num))

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
                beats[i] = basicUI.Square("beats", self.character, filled=True)
                beatbox.addWidget(beats[i])
                
            else:
                beats[i] = basicUI.Square("beats", self.character, filled=False)
                beatbox.addWidget(beats[i])

        self.grid.addWidget(beat_label,7,0)
        self.grid.addLayout(beatbox,7,1)

        self.beat_group = basicUI.Squares_Group("beats", 5, beats, self.character)
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
                arcbeats[i] = basicUI.Square("arcane beats", self.character, filled=True)
                arcbeatbox.addWidget(arcbeats[i])
                
            else:
                arcbeats[i] = basicUI.Square("arcane beats", self.character, filled=False)
                arcbeatbox.addWidget(arcbeats[i])

        self.grid.addWidget(arcbeat_label,9,0)
        self.grid.addLayout(arcbeatbox,9,1)

        self.arcbeat_group = basicUI.Squares_Group("arcane beats", 5, arcbeats, self.character)
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
                self.dots[x] = basicUI.Dot(filled=True)
            else:
                self.dots[x] = basicUI.Dot(filled=False)
            if x <= self.filled:
                squares[x] = basicUI.Square("willpower", self.character, filled=True)
            else:
                squares[x] = basicUI.Square("willpower", self.character)
            grid.addWidget(self.dots[x],0,x)
            grid.addWidget(squares[x],1,x)


        self.willpower_group = basicUI.Squares_Group("willpower filled", 10, squares, self.character)
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
                self.dots[x] = basicUI.Dot(filled=True)
            else:
                self.dots[x] = basicUI.Dot(filled=False)
            squares[x] = basicUI.Square("health", self.character, index=x)
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
        #unfilled will add to 0th position
        health = [0, 0, 0, 0]

        for button in range(1,13):
            rating = self.buttons[button].filled
            health[rating] += 1

        #change values for all but 0th position
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
        self.overall_label = QLabel("===MANA===")
        self.overall_label.setStyleSheet("QLabel { font: 13pt}")
        self.source_label = QLabel("Source")
        self.source_label.setStyleSheet("QLabel {text-decoration: underline; font: 10pt}")
        self.spent_label = QLabel("Spent")
        self.spent_label.setStyleSheet("QLabel {text-decoration: underline; font: 10pt}")
        self.current_label = QLabel("Current")
        self.current_label.setStyleSheet("QLabel {text-decoration: underline; font: 10pt}")

        self.grid.addWidget(self.overall_label, 0, 0, 1, 3)
        self.grid.setAlignment(self.overall_label, Qt.AlignHCenter)
        self.grid.addWidget(self.source_label, 1, 0)
        self.grid.setAlignment(self.source_label, Qt.AlignRight)
        self.grid.addWidget(self.spent_label, 1, 1)
        self.grid.addWidget(self.current_label, 1, 2)

        ##Base
        #base label
        self.base_label = QLabel("Base : ")
        
        #base spent
        self.spent = QSpinBox()
        self.spent.setValue(self.character.stats['mana spent'])
        self.spent.setMaximumSize(QSize(35, 20))
        self.spent.setMaximum(self.character.stats['mana'])
        self.spent.valueChanged.connect(self.update_mana)

        
        #base current
        current_num = self.character.stats['mana'] - self.character.stats['mana spent']
        self.current = basicUI.Num_with_Line(str(current_num) + "/" + str(self.character.stats['mana']))

        self.grid.addWidget(self.base_label, 2, 0)
        self.grid.setAlignment(self.base_label, Qt.AlignRight)
        self.grid.addWidget(self.spent, 2, 1)
        self.grid.addWidget(self.current, 2, 2)

        #enchanted items
        self.ench_items = {}
        self.update_ench_items()

    def update_ench_items(self):
        keys = list(self.ench_items.keys())
        for item in keys:
            widgets = self.ench_items[item]
            name = widgets[0]
            #remove all from UI,remove from dict and delete
            for widget in widgets[1:]:
                self.grid.removeWidget(widget)
                sip.delete(widget)

            #remove associated data
            del self.ench_items[item]
            

        self.row = 3
        #add back in
        for item in self.character.stats['ench items']:
            self.ench_items[self.row] = [item]
            total_mana = self.character.stats['ench items'][item][3]
            spent_mana = self.character.stats['ench items'][item][4]
            item_type = self.character.stats['ench items'][item][0]

            #label
            label = QLabel(item.title() + "(" + item_type.title() + ") :")
            self.ench_items[self.row].append(label)

            #spent
            spent = QSpinBox()
            spent.setValue(spent_mana)
            spent.setMaximumSize(QSize(35, 20))
            spent.setMaximum(total_mana)
            spent.valueChanged.connect(self.update_mana)
            self.ench_items[self.row].append(spent)

            #current
            current_num = total_mana - spent_mana
            current = basicUI.Num_with_Line(str(current_num) + "/" + str(total_mana))
            self.ench_items[self.row].append(current)

            #add to grid
            self.grid.addWidget(label, self.row, 0)
            self.grid.setAlignment(label, Qt.AlignRight)
            self.grid.addWidget(spent, self.row, 1)
            self.grid.addWidget(current, self.row, 2)
            self.row += 1

        

    def update_mana(self):
        #base change
        self.character.stats['mana spent'] = self.spent.value()
        self.spent.setMaximum(self.character.stats['mana'])
        
        current_num = self.character.stats['mana'] - self.character.stats['mana spent']
        self.current.change_text(str(current_num) + "/" + str(self.character.stats['mana']))

        #rest changed
        for item in self.ench_items:
            name = self.ench_items[item][0]
            spent_widget = self.ench_items[item][2]
            current_widget = self.ench_items[item][3]

            #update character object
            self.character.stats['ench items'][name][4] = spent_widget.value()

            #update current display
            current_num = self.character.stats['ench items'][name][3] - spent_widget.value()
            current_widget.change_text(str(current_num) + "/" + str(self.character.stats['ench items'][name][3]))
