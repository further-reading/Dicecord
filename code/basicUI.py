# Basic UI elements shared over Dicecord sheet and inventory UI objects.
#    Copyright (C) 2017  Roy Healy


import sip, stats
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Character_Info(QWidget):
    def __init__(self, character, labels):
        super().__init__()
        self.character = character
        self.labels = labels
        self.initUI()

    def initUI(self):

        grid = QGridLayout()
        self.setLayout(grid)

        col = 0
        self.headers = {}
        for section in self.labels:
            row = 0
            for name in section:
                self.headers[name] = Label_Entry_Combo(self.character, name)
                grid.addWidget(self.headers[name], row, col)
                row += 1
            col += 1

    def edit_toggle(self):
        for name in self.headers:
            self.headers[name].edit_toggle()

class Label_Entry_Combo(QWidget):
    def __init__(self, character, name):
        super().__init__()
        self.setStyleSheet("QLabel { font: 10pt}")
        self.character = character
        self.name = name
        self.initUI()

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

        self.content.setReadOnly(not self.character.edit_mode)

    def save_changes(self):
        new = self.content.text()
        # if numeric userID, add <@ and > around it so discord will parse properly
        if self.name == 'user id' and new.isdigit():
            new = '<@' + new + '>'

        self.character.stats[self.name] = new
        self.content.setReadOnly(True)

    def edit_toggle(self):
        # set read only status
        self.content.setReadOnly(not self.character.edit_mode)

        if not self.character.edit_mode:
            # if edit mode turned off, apply changes
            self.save_changes()

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

        mental_group = stats.SKILL_TYPE['mental']
        physical_group = stats.SKILL_TYPE['physical']
        social_group = stats.SKILL_TYPE['social']

        self.mental = Stat_Col(mental_group, self.character, type="skill")
        self.physical = Stat_Col(physical_group, self.character, type="skill")
        self.social = Stat_Col(social_group, self.character, type="skill")

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setContentsMargins(0, 0, 0, 0)

        grid.addWidget(overall_label, 0, 0)
        grid.addWidget(mental_label, 1, 0)
        grid.addWidget(self.mental, 2, 0)
        grid.addWidget(physical_label, 3, 0)
        grid.addWidget(self.physical, 4, 0)
        grid.addWidget(social_label, 5, 0)
        grid.addWidget(self.social, 6, 0)

class Stat_Col(QWidget):
    def __init__(self, stats, character, type=""):
        '''
        Makes a column of dots.
        Takes list of Tuples in the form (title, current, max) and the associated character object.
        '''
        # Can rewrite to take list of keys instead.
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
                # check if stat is on character - distinguishes dark era and modern era
                if stat in self.character.stats:
                    if self.character.splat == 'mage':
                        # if mage, draw rote skill box
                        rotes = self.character.stats['rote skills']
                        rote_button = (Square(stat, self.character, filled= stat in rotes))
                        rote_button.clicked.connect(rote_button.change_Image)
                        grid.addWidget(rote_button,row,0)
                else:
                    continue
                
            grid.addWidget(Stat(self.character, stat, type = self.type),row,1)
            row += 1
        

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
        self.box.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.box)

        stats = self.character.stats['merits']
        self.merits = {}

        self.label = QLabel('===MERITS===')
        self.box.addWidget(self.label)
        self.box.setAlignment(Qt.AlignTop)
        self.box.setAlignment(self.label, Qt.AlignHCenter)

        self.delete_buttons = QButtonGroup()
        # the buttonClickedSlot method will take the ID of the clicked delete button as an argument
        self.delete_buttons.buttonClicked[int].connect(self.edit_entry)

        self.row = 1
        for stat in stats:
            # There can be a variable number of merits, so must be drawn with a loop.
            # starts at 1 since the label takes the 0 spot.
            merit = Stat(self.character, stat, type="merit")
            # a self.merits dict is made to help with deltion method
            self.merits[self.row] = merit
            # delete buttons are added to a button group with their row as an ID
            self.delete_buttons.addButton(merit.label, self.row)

            self.box.addWidget(self.merits[self.row])

            self.row += 1

        # Add the "add new" button for adding new merits
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

    def edit_entry(self, index=None):
        '''
        Edit the widget contents.
        Used for updating a current entry, deleting a current entry or adding a new one.
        '''

        if not self.character.edit_mode:
            # Actions only possible in edit mode
            return

        if not index:
            current_title = None
            # add new item if no index given
            label, tooltip, ok = Label_Tooltip_Dialog.get_input(wintitle="Add Merit")

        else:
            # edit current item
            current = self.merits[index]
            current_title = current.label.text().title()
            current_tooltip = current.label.toolTip()
            label, tooltip, ok = Label_Tooltip_Dialog.get_input(title=current_title, tooltip=current_tooltip,
                                                                        edit=True, wintitle="Change Merit")

        if not ok:
            # cancel pressed
            return

        if not current_title and label.lower() in self.character.stats['merits']:
            # add new but title already in use
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Merit with this name already exists.")
            msg.setInformativeText("Please use unique name.")
            msg.setWindowTitle("Duplicate Name")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

        elif not current_title:
            # Only adds new if entry by that name does not exist yet
            # add entry on character object
            new = label.lower()
            self.character.stats["merit details"][new] = tooltip
            self.character.stats["merits"][new] = 0

            # creates entry
            merit = Stat(self.character, new, type="merit")
            self.merits[self.row] = merit
            self.delete_buttons.addButton(merit.label, self.row)

            # remove the add new button
            self.box.removeWidget(self.new_button)

            # add the new Stat widget and delete button
            self.box.addWidget(merit)

            # add 1 to self.row
            self.row += 1

            # add the new button back to end
            self.box.addWidget(self.new_button)


        elif "####DELETE####" in label:
            # delete chosen
            # remove stat widget
            self.box.removeWidget(self.merits[index])
            sip.delete(self.merits[index])

            # remove associated data
            del self.character.stats["merits"][current_title.lower()]
            del self.character.stats["merit details"][current_title.lower()]
            del self.merits[index]

        else:
            # Update tooltip of existing entry
            current.label.setToolTip(tooltip)
            self.character.stats["merit details"][current_title.lower()] = tooltip
            if tooltip == '':
                # update cursor if blank now
                current.label.setCursor(QCursor(Qt.ArrowCursor))
            else:
                current.label.setCursor(QCursor(Qt.WhatsThisCursor))


class Derivitives(QWidget):
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
        self.grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)

        self.devgrid = QGridLayout()
        self.devgrid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.devgrid.setSpacing(5)
        self.devgrid.setContentsMargins(0, 0, 0, 0)

        overall_base = QLabel("Base")
        overall_mod = QLabel("Modifier")
        overall_total = QLabel("Total")

        self.devgrid.addWidget(overall_base, 0, 1)
        self.devgrid.addWidget(overall_mod, 0, 2)
        self.devgrid.addWidget(overall_total, 0, 3)

        self.derived_stats = {}

        # size
        size_label = QLabel("Size: ")
        size_label.setToolTip("Regular humans are size 5")
        size_label.setCursor(QCursor(Qt.WhatsThisCursor))
        size_label.setContentsMargins(0, 0, 0, 0)
        size_rating = Num_with_Line(str(self.character.stats['size']))

        size_mod = QSpinBox()
        size_mod.setMinimum(-100)
        size_mod.setValue(self.character.stats['size mod'])
        size_mod.setMaximumSize(QSize(35, 20))

        size_total_num = self.character.stats['size'] + self.character.stats['size mod']
        size_total = Num_with_Line(str(size_total_num))

        self.derived_stats['size'] = (size_rating, size_mod, size_total)
        size_mod.valueChanged.connect(lambda: self.update_deriv('size'))

        self.devgrid.addWidget(size_label, 1, 0)
        self.devgrid.addWidget(size_rating, 1, 1)
        self.devgrid.addWidget(size_mod, 1, 2)
        self.devgrid.addWidget(size_total, 1, 3)

        # speed
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

        self.devgrid.addWidget(speed_label, 2, 0)
        self.devgrid.addWidget(speed_rating, 2, 1)
        self.devgrid.addWidget(speed_mod, 2, 2)
        self.devgrid.addWidget(speed_total, 2, 3)

        # defense
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

        self.devgrid.addWidget(defense_label, 3, 0)
        self.devgrid.addWidget(defense_rating, 3, 1)
        self.devgrid.addWidget(defense_mod, 3, 2)
        self.devgrid.addWidget(defense_total, 3, 3)

        # Int modifier
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

        self.devgrid.addWidget(initiative_label, 4, 0)
        self.devgrid.addWidget(initiative_rating, 4, 1)
        self.devgrid.addWidget(initiative_mod, 4, 2)
        self.devgrid.addWidget(initiative_total, 4, 3)

        # group up
        self.grid.addLayout(self.devgrid, 0, 0, 1, 2)

        space = QLabel(" ")
        self.grid.addWidget(space, 5, 0)

        # Armor
        armor_label = QLabel("Armor: ")
        self.armor_entry = QSpinBox()
        self.armor_entry.setMaximumSize(QSize(35, 20))
        self.armor_entry.valueChanged.connect(lambda: self.update_others("armor", self.armor_entry.value()))

        self.grid.addWidget(armor_label, 6, 0)
        self.grid.addWidget(self.armor_entry, 6, 1, alignment=Qt.AlignLeft)

        # Beats
        beat_label = QLabel("Beats: ")
        beatbox = QHBoxLayout()
        beats = {}
        # add button group for beat changes
        for i in range(1, 6):
            if i <= self.character.stats["beats"]:
                beats[i] = Square("beats", self.character, filled=True)
                beatbox.addWidget(beats[i])

            else:
                beats[i] = Square("beats", self.character, filled=False)
                beatbox.addWidget(beats[i])

        self.grid.addWidget(beat_label, 7, 0)
        self.grid.addLayout(beatbox, 7, 1)

        self.beat_group = Squares_Group("beats", 5, beats, self.character)
        for pos in beats:
            self.beat_group.addButton(beats[pos], pos)

        # add a click handler for the entire group
        self.beat_group.buttonClicked[int].connect(self.beat_group.buttonClickedSlot)

        # XP
        self.xp_label = QLabel("XP: ")
        self.xp_entry = QSpinBox()
        self.xp_entry.setMaximumSize(QSize(35, 20))
        self.xp_entry.setValue(self.character.stats['xp'])
        self.xp_entry.valueChanged.connect(lambda: self.update_others("xp", self.xp_entry.value()))

        self.grid.addWidget(self.xp_label, 8, 0)
        self.grid.addWidget(self.xp_entry, 8, 1, alignment=Qt.AlignLeft)


        # mage only section
        if self.character.splat == 'mage':
            # Arcane Beats
            arcbeat_label = QLabel("Arcane Beats: ")
            arcbeatbox = QHBoxLayout()
            arcbeats = {}
            # add button group for beat changes
            for i in range(1, 6):
                if i <= self.character.stats["arcane beats"]:
                    arcbeats[i] = Square("arcane beats", self.character, filled=True)
                    arcbeatbox.addWidget(arcbeats[i])

                else:
                    arcbeats[i] = Square("arcane beats", self.character, filled=False)
                    arcbeatbox.addWidget(arcbeats[i])

            self.grid.addWidget(arcbeat_label, 9, 0)
            self.grid.addLayout(arcbeatbox, 9, 1)

            self.arcbeat_group = Squares_Group("arcane beats", 5, arcbeats, self.character)
            for pos in arcbeats:
                self.arcbeat_group.addButton(arcbeats[pos], pos)

            # add a click handler for the entire group
            self.arcbeat_group.buttonClicked[int].connect(self.arcbeat_group.buttonClickedSlot)

            # Arcane XP
            self.axp_label = QLabel("Arcane XP: ")
            self.axp_entry = QSpinBox()
            self.axp_entry.setMaximumSize(QSize(35, 20))
            self.axp_entry.setValue(self.character.stats['arcane xp'])
            self.axp_entry.valueChanged.connect(lambda: self.update_others("arcane xp", self.axp_entry.value()))

            self.grid.addWidget(self.axp_label, 10, 0)
            self.grid.addWidget(self.axp_entry, 10, 1, alignment=Qt.AlignLeft)

    def update_deriv(self, stat):
        # update labels and ratings for a derived stat
        stats = self.derived_stats[stat]
        rating = stats[0]
        mod = stats[1]
        total = stats[2]
        rating.change_text(str(self.character.stats[stat]))
        self.character.stats[stat + ' mod'] = mod.value()
        total_num = self.character.stats[stat] + self.character.stats[stat + ' mod']
        total.change_text(str(total_num))

    def update_others(self, stat, value):
        # update xps and armor
        self.character.stats[stat] = value

    def update_all(self):
        for stat in self.derived_stats:
            self.update_deriv(stat)


class Willpower(QWidget):
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
        box.setContentsMargins(0, 0, 0, 0)

        label = QLabel('Willpower')
        label.setAlignment(Qt.AlignCenter)
        box.addWidget(label)

        self.setLayout(box)
        grid = QGridLayout()
        grid.setSpacing(5)
        grid.setContentsMargins(0, 0, 0, 0)
        squares = {}
        self.dots = {}
        col = 0

        for x in range(1, 11):
            if x <= self.current:
                self.dots[x] = Dot(filled=True)
            else:
                self.dots[x] = Dot(filled=False)
            if x <= self.filled:
                squares[x] = Square("willpower", self.character, filled=True)
            else:
                squares[x] = Square("willpower", self.character)
            grid.addWidget(self.dots[x], 0, x)
            grid.addWidget(squares[x], 1, x)

        self.willpower_group = Squares_Group("willpower filled", 10, squares, self.character)
        for pos in squares:
            self.willpower_group.addButton(squares[pos], pos)

        # add a click handler for the entire group
        self.willpower_group.buttonClicked[int].connect(self.willpower_group.buttonClickedSlot)

        box.addLayout(grid)

    def update_willpower(self):
        self.current = self.character.stats['willpower']

        for x in range(1, 11):
            if x <= self.current:
                self.dots[x].filled = True
                self.dots[x].select_Image()
            else:
                self.dots[x].filled = False
                self.dots[x].select_Image()


class Health(QWidget):
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
        box.setContentsMargins(0, 0, 0, 0)

        label = QLabel('Health')
        label.setAlignment(Qt.AlignCenter)
        box.addWidget(label)

        self.setLayout(box)
        grid = QGridLayout()
        grid.setSpacing(5)
        grid.setContentsMargins(0, 0, 0, 0)
        squares = {}
        self.dots = {}
        col = 0

        health = self.character.stats['health']

        for x in range(1, 13):
            if x <= health[0]:
                # health[0] is max jealth
                self.dots[x] = Dot(filled=True)
            else:
                self.dots[x] = Dot(filled=False)
            squares[x] = Square("health", self.character, index=x)
            grid.addWidget(self.dots[x], 0, x)
            grid.addWidget(squares[x], 1, x)

        # this will add buttons to button group and fill them appropiately
        self.health_group = Health_Group(squares, self.character)

        # add a click handler for the entire group
        self.health_group.buttonClicked[int].connect(self.health_group.change)

        box.addLayout(grid)

    def update_max(self):
        max_health = self.character.stats['health'][0]

        for x in range(1, 13):
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
            # add buttons to group
            self.addButton(buttons[pos], pos)
            buttons[pos].group = self
            buttons[pos].setContextMenuPolicy(Qt.CustomContextMenu)
            buttons[pos].customContextMenuRequested.connect(buttons[pos].reduce)

        # loop to initialise squares
        # counts from 0 to value starting with agg damage
        pos = 1
        for point in range(0, health[3]):
            buttons[pos].filled = 3
            buttons[pos].select_Image()
            pos += 1

        for point in range(0, health[2]):
            buttons[pos].filled = 2
            buttons[pos].select_Image()
            pos += 1

        for point in range(0, health[1]):
            buttons[pos].filled = 1
            buttons[pos].select_Image()
            pos += 1

    def change(self, index, reduce=False):
        # change everything
        if not reduce:
            self.buttons[index].change_Image()
        for button in range(1, index):
            current = self.buttons[button].filled
            if current < self.buttons[index].filled:
                self.buttons[button].filled = self.buttons[index].filled
                self.buttons[button].select_Image()

        for button in range(index + 1, 13):
            current = self.buttons[button].filled
            if current > self.buttons[index].filled:
                self.buttons[button].filled = self.buttons[index].filled
                self.buttons[button].select_Image()

        # record changes
        # unfilled will add to 0th position
        health = [0, 0, 0, 0]

        for button in range(1, 13):
            rating = self.buttons[button].filled
            health[rating] += 1

        # change values for all but 0th position
        self.character.stats['health'][1:] = health[1:]

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
        if small:
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

        if self.type == "skill":
            self.tooltip = ""
            # label is a button to add specialties
            self.label = QPushButton(self.name.title())
            self.label.setStyleSheet("QPushButton {border:none; font-size: 10pt; text-align: left}")
            self.label.clicked.connect(self.add_specialty)
            if self.name in self.character.stats['skill specialties']:
                self.tooltip = self.character.stats['skill specialties'][self.name]

                # skill specialty present - cursor and label font changed
                self.label.setCursor(QCursor(Qt.WhatsThisCursor))
                self.label.setToolTip(self.tooltip)
                self.label.setStyleSheet("QPushButton {border:none; font-size: 10pt; font: bold; text-align: left}")

        elif self.type == 'merit':
            # like skill but click connection not set here
            # click will allow for removing items so will be handled by a buttongroup in merit object
            self.tooltip = ""
            self.label = QPushButton(self.name.title())
            self.label.setStyleSheet("QPushButton {border:none; font-size: 10pt; text-align: left}")
            if len(self.name.title()) <= len("Investigation"):
                # at minimum this will be as big as the longest default stat name
                # If bigger then the UI will stretch to accomadate
                self.label.setMinimumWidth(105)
            self.tooltip = self.character.stats['merit details'][self.name]
            if self.tooltip != '':
                # if tooltip isn't blank, cursor and tolltip change added
                self.label.setCursor(QCursor(Qt.WhatsThisCursor))
                self.label.setToolTip(self.tooltip)
        

        else:
            self.label = QLabel(self.name.title())

        
        box.addWidget(self.label)

        # it will initilaise with the dots filled accoridng to character.stats['name']
        # Each dot is an abstract button widget
        for x in range(1,self.maximum+1):
            if x <= self.current:
                dots[x] = Dot(filled=True)
            else:
                dots[x] = Dot(filled=False)
            box.addWidget(dots[x])

        # a button group is created that will be used for changing dot rating
        # mght be possible to reorganise code to avoid second loop
        self.dot_group = Dots_Group(self.name, dots, self.character, maximum = self.maximum, type = self.type)
        for pos in dots:
            self.dot_group.addButton(dots[pos],pos)

        # add a click handler for the entire group
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
        # will one day use a proper CSS to set this
        
        box.addWidget(self.label)

        # it will initilaise with the dots filled accoridng to character.stats['name']
        # Each dot is an abstract button widget
        for x in range(1,self.maximum+1):
            if x <= self.current:
                dots[x] = Dot(filled=True)
            else:
                dots[x] = Dot(filled=False)
            dotbox.addWidget(dots[x])

        box.addLayout(dotbox)

        # a button group is created that will be used for changing dot rating
        # mght be possible to reorganise code to avoid second loop
        self.dot_group = Dots_Group(self.name, dots, self.character, maximum = self.maximum)
        for pos in dots:
            self.dot_group.addButton(dots[pos],pos)

        # add a click handler for the entire group
        self.dot_group.buttonClicked[int].connect(self.dot_group.buttonClickedSlot)

    def add_specialty(self):
        '''
        Method to add or remove a skill specialty
        '''
        if not self.character.edit_mode:
            return
        
        label, tooltip, ok = Label_Tooltip_Dialog.get_input(wintitle = "Add Specialty/Notes", title="spec# # ", tooltip=self.tooltip)
		
        if ok:
            self.character.stats['skill specialties'][self.name] = tooltip
            self.tooltip = tooltip
            if tooltip:
                self.label.setCursor(QCursor(Qt.WhatsThisCursor))
                self.label.setToolTip(tooltip)
                self.label.setStyleSheet("QPushButton {border:none; font-size: 10pt; font: bold; text-align: left}")
            else:
                # if new tooltip is blank
                self.label.setCursor(QCursor(Qt.WhatsThisCursor))
                self.label.setToolTip(tooltip)
                self.label.setStyleSheet("QPushButton {border:none; font-size: 10pt; text-align: left}")

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
            # nothing happens when not in edit mode
            return
        
        if self.last_click == index:
            # if a dotis clicked a second time in a row it unfills it
            index -= 1
        
        for x in range(1,self.maximum + 1):
            # currently has maximum hard coded
            # will need to replace with user entered maximum
            if x <= index:
                self.dots[x].filled = True
                self.dots[x].select_Image()
            elif x > index:
                self.dots[x].filled = False
                self.dots[x].select_Image()

        # associated stat is updated along with any derivitives
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
    def __init__(self, filled=False):
        super().__init__()
        self.filled = filled
        self.type = type
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.select_Image()

    def paintEvent(self, event):
        # paints the dot
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def select_Image(self):
        '''
        Checks if dot is currently filled and draws appropiate image.
        '''
        filled = r"images\filled.png"
        unfilled = r"images\unfilled.png"

        
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
        # paints the square
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
        if self.character.edit_mode and self.stat in stats.SKILLS:
            # changes rote skills if edit mode
            self.filled = not self.filled
            if self.filled:
                self.character.stats['rote skills'].add(self.stat)
            else:
                self.character.stats['rote skills'].remove(self.stat)
                
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
            # if a box is clicked twice in a row it unfills it
            index -= 1
            
        for x in range(1, self.stat_max):
            if x <= index:
                self.squares[x].filled = True
                self.squares[x].select_Image()
            elif x > index:
                self.squares[x].filled = False
                self.squares[x].select_Image()

        # associated stat is updated 
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

class Hover_Label_Col(QWidget):
    def __init__(self, title, character, stat_name):
        super().__init__()
        self.title = "===" + title + "==="
        self.character = character
        self.stat_name = stat_name
        self.initUI()

    def initUI(self):
        self.box = QVBoxLayout()
        self.box.setSpacing(0)
        self.box.setContentsMargins(0,0,0,0)
        self.setLayout(self.box)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("QLabel { font: 13pt }" )
        self.box.addWidget(title_label)
        self.box.setAlignment(Qt.AlignTop)
        self.box.setAlignment(title_label, Qt.AlignHCenter)

        self.content = {}

        self.edit_buttons = QButtonGroup()
        self.edit_buttons.buttonClicked[int].connect(self.edit_entry)

        self.row = 1
        for stat in self.character.stats[self.stat_name]:
            button = QPushButton(stat.title())
            button.setCursor(QCursor(Qt.WhatsThisCursor))
            button.setToolTip(self.character.stats[self.stat_name][stat])
            button.setStyleSheet("QPushButton {border:none; font: 10pt}")

            self.content[self.row] = button
            self.edit_buttons.addButton(button,self.row)

            self.box.addWidget(button)

            self.row += 1

        
        if self.stat_name in ("conditions", "active spells"):
            # other types only edited in edit mode
            # new button not added unless edit mode toggled
            self.new_button = QPushButton("Add New")
            self.new_button.setMaximumWidth(60)
            self.box.addWidget(self.new_button)
            self.new_button.clicked.connect(self.edit_entry)

    def edit_entry(self,index=None):
        '''
        Edit the widget contents.
        Used for updating a current entry, deleting a current entry or adding a new one.
        '''

        if self.stat_name not in ("conditions", "active spells"):
            if not self.character.edit_mode:
                # other stats can only be changed in edit mode
                return

        if not index:
            current_title = None
            # add new item if no index given
            label, tooltip, ok = Label_Tooltip_Dialog.get_input(wintitle = "Add Item")

        else:
            # edit current item
            current = self.content[index]
            current_title = current.text().title()
            current_tooltip = current.toolTip()
            label, tooltip, ok = Label_Tooltip_Dialog.get_input(title = current_title, tooltip = current_tooltip, edit = True, wintitle = "Change Item")
        
        if not ok:
            return

        if not current_title and label.lower() in self.character.stats[self.stat_name]:
            # add new where title already in use
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText(self.stat_name.title()[:-1] + " with this name already exists.")
            msg.setInformativeText("Please use unique name.")
            msg.setWindowTitle("Duplicate Name")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

        elif not current_title:
            # Only adds new if entry by that name does not exist yet
            # add entry on character object
            new = label.lower()
            self.character.stats[self.stat_name][new] = tooltip

            # creates new button
            button = QPushButton(new.title())
            button.setCursor(QCursor(Qt.WhatsThisCursor))
            button.setToolTip(self.character.stats[self.stat_name][new])
            button.setStyleSheet("QPushButton {border:none; font: 10pt}")

            self.content[self.row] = button
            self.edit_buttons.addButton(button,self.row)

            # remove the add new button
            self.box.removeWidget(self.new_button)

            # add the new Stat widget and delete button
            self.box.addWidget(button)

            # add 1 to self.row
            self.row += 1

            # add the new button back to end
            self.box.addWidget(self.new_button)
        

        elif "####DELETE####" in label:
            # delete chosen
            # remove stat widget
            self.box.removeWidget(self.content[index])
            sip.delete(self.content[index])

            # remove associated data
            del self.character.stats[self.stat_name][current_title.lower()]
            del self.content[index]
            
        else:
            # Update tooltip of existing entry
            self.character.stats[self.stat_name][current.text()] = tooltip
            current.setToolTip(tooltip)

    def edit_toggle(self):
        # used to add edit button
        if self.character.edit_mode:
            # add the new button to end
            self.new_button = QPushButton("Add New")
            self.new_button.setMaximumWidth(60)
            self.new_button.clicked.connect(self.edit_entry)
            self.box.addWidget(self.new_button)

        else:
            # remove new button
            self.box.removeWidget(self.new_button)
            sip.delete(self.new_button)


class Label_Tooltip_Dialog (QDialog):
    '''
    Dialog for entering/changing labels with tooltips
    '''
    def __init__(self, title = '', tooltip = '', edit = False, wintitle = "Tooltip"):
        super().__init__()
        self.setWindowTitle(wintitle)
        self.title = title
        self.tooltip = tooltip
        self.edit = edit
        self.initUI()
        self.setMaximumSize(20,20)

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.title_label = QLabel("Label:")
        self.title_entry = QLineEdit()
        self.title_entry.insert(self.title)

        self.tooltip_label = QLabel("Tooltip:")
        self.tooltip_entry = QTextEdit()
        self.tooltip_entry.setText(self.tooltip)

        if self.edit:
            # add delete button and disable label box if editing
            self.title_entry.setDisabled(self.edit)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel|QDialogButtonBox.Discard, Qt.Horizontal, self)
            buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.del_item)
            buttonBox.button(QDialogButtonBox.Discard).setText("Delete")
        else:
            # adding new or specialty edit - only okay and cancel button
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel, Qt.Horizontal, self)


        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        if self.title != "spec# # ":
            # don't add these if skill specialty edit
            self.grid.addWidget(self.title_label, 0,0)
            self.grid.addWidget(self.title_entry, 0,1)
        
        self.grid.addWidget(self.tooltip_label, 1,0)
        self.grid.setAlignment(self.tooltip_label, Qt.AlignTop)
        self.grid.addWidget(self.tooltip_entry, 1,1)
        self.grid.addWidget(buttonBox, 2,1)

    def del_item(self):
        '''
        Handler for delete item action.
        Sends an accept signal but adds a delete flag to output
        '''
        
        self.title_entry.insert("####DELETE####")
        self.accept()

    def get_input(wintitle, title = '', tooltip = '', edit = False):
        '''
        Used to open a dialog window to enter details of label.
        '''
        dialog = Label_Tooltip_Dialog(title, tooltip, edit, wintitle)
        result = dialog.exec_()
        return (dialog.title_entry.text(), dialog.tooltip_entry.toPlainText(), result == QDialog.Accepted)


class Weapons(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignTop)

        overall_label = QLabel()
        overall_label.setText('==WEAPONS==')
        overall_label.setStyleSheet("QLabel {font: 13pt;}")
        self.grid.addWidget(overall_label, 0, 0, 1, 7)
        self.grid.setAlignment(overall_label, Qt.AlignHCenter)

        # weapon/attack, damage, range, clip, init, str, size
        overall_name = QLabel("Weapon/Attack")
        overall_name.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_damage = QLabel("Damage")
        overall_damage.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_range = QLabel("Range")
        overall_range.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_clip = QLabel("Clip")
        overall_clip.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_init = QLabel("Init. mod")
        overall_init.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_str = QLabel("Str.")
        overall_str.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_size = QLabel("Size")
        overall_size.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")

        self.grid.addWidget(overall_name, 1, 0)
        self.grid.setAlignment(overall_name, Qt.AlignHCenter)
        self.grid.addWidget(overall_damage, 1, 1)
        self.grid.setAlignment(overall_damage, Qt.AlignHCenter)
        self.grid.addWidget(overall_range, 1, 2)
        self.grid.setAlignment(overall_range, Qt.AlignHCenter)
        self.grid.addWidget(overall_clip, 1, 3)
        self.grid.setAlignment(overall_clip, Qt.AlignHCenter)
        self.grid.addWidget(overall_init, 1, 4)
        self.grid.setAlignment(overall_init, Qt.AlignHCenter)
        self.grid.addWidget(overall_str, 1, 5)
        self.grid.setAlignment(overall_str, Qt.AlignHCenter)
        self.grid.addWidget(overall_size, 1, 6)
        self.grid.setAlignment(overall_size, Qt.AlignHCenter)

        self.weapons = {}
        self.row = 2
        self.edit_buttons = QButtonGroup()
        self.edit_buttons.buttonClicked[int].connect(self.edit_entry)

        # self.character.stats['weapons'][name] = {damage, range, clip, init, str, size}

        for name in self.character.stats['weapons']:
            self.weapons[self.row] = [name]
            details = self.character.stats['weapons'][name]
            damage = details['damage']
            weapon_range = details['range']
            clip = details['clip']
            init = details['init']
            strength = details['str']
            size = details['size']

            # weapon name
            button = QPushButton(name.title())
            button.setStyleSheet("QPushButton {font: 10pt; border: none}")
            button.setCursor(QCursor(Qt.PointingHandCursor))
            self.weapons[self.row].append(button)
            self.edit_buttons.addButton(button, self.row)

            # damage
            damage_label = QLabel(str(damage))
            damage_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(damage_label)

            # range
            range_label = QLabel(weapon_range)
            range_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(range_label)

            # clip
            if clip == 0:
                clip = "N/A"

            clip_label = QLabel(str(clip))
            clip_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(clip_label)

            # init
            init_label = QLabel(str(init))
            init_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(init_label)

            # str
            str_label = QLabel(str(strength))
            str_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(str_label)

            # size
            size_label = QLabel(str(size))
            size_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(size_label)

            self.grid.addWidget(button, self.row, 0)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(damage_label, self.row, 1)
            self.grid.setAlignment(damage_label, Qt.AlignHCenter)
            self.grid.addWidget(range_label, self.row, 2)
            self.grid.setAlignment(range_label, Qt.AlignHCenter)
            self.grid.addWidget(clip_label, self.row, 3)
            self.grid.setAlignment(clip_label, Qt.AlignHCenter)
            self.grid.addWidget(init_label, self.row, 4)
            self.grid.setAlignment(init_label, Qt.AlignHCenter)
            self.grid.addWidget(str_label, self.row, 5)
            self.grid.setAlignment(str_label, Qt.AlignHCenter)
            self.grid.addWidget(size_label, self.row, 6)
            self.grid.setAlignment(size_label, Qt.AlignHCenter)
            self.row += 1

        # add the new button to end
        self.new_button = QPushButton("Add New")
        self.new_button.setMaximumWidth(60)
        self.new_button.clicked.connect(self.edit_entry)
        self.grid.addWidget(self.new_button, self.row, 0)

    def edit_entry(self, index=None):

        if not index:
            current_name = None
            # add new item if no index given
            name, damage, weapon_range, clip, init, strength, size, ok = Weapons_Dialog.get_weapon("Add Weapon/Attack")

        else:
            # edit current item
            current = self.weapons[index]
            current_name = current[1].text().lower()
            current_details = self.character.stats['weapons'][current_name]

            current_damage = current_details['damage']
            current_range = current_details['range']
            current_clip = current_details['clip']
            current_init = current_details['init']
            current_strength = current_details['str']
            current_size = current_details['size']

            name, damage, weapon_range, clip, init, strength, size, ok = Weapons_Dialog.get_weapon(
                "Change Weapon/Attack",
                current_name,
                current_damage,
                current_range,
                current_clip,
                current_init,
                current_strength,
                current_size,
                edit=True)

        if not ok:
            # cancel pressed
            return

        if not current_name and name in self.character.stats['weapons']:
            # add new but title already in use
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Weapon with this name already exists.")
            msg.setInformativeText("Please use unique name.")
            msg.setWindowTitle("Duplicate Name")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

        elif not current_name:
            # Only adds new if entry by that name does not exist yet
            # add entry on character object
            self.character.stats['weapons'][name] = {'damage': damage, 'range': weapon_range, 'clip': clip,
                                                     'init': init, 'str': strength, 'size': size}

            # create entry
            self.weapons[self.row] = [name]

            # weapon name
            button = QPushButton(name.title())
            button.setStyleSheet("QPushButton {font: 10pt; border: none}")
            button.setCursor(QCursor(Qt.PointingHandCursor))
            self.weapons[self.row].append(button)
            self.edit_buttons.addButton(button, self.row)

            # damage
            damage_label = QLabel(str(damage))
            damage_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(damage_label)

            # range
            range_label = QLabel(weapon_range)
            range_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(range_label)

            # clip
            if clip == 0:
                clip = "N/A"

            clip_label = QLabel(str(clip))
            clip_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(clip_label)

            # init
            init_label = QLabel(str(init))
            init_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(init_label)

            # str
            str_label = QLabel(str(strength))
            str_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(str_label)

            # size
            size_label = QLabel(str(size))
            size_label.setStyleSheet("QLabel {font: 10pt}")
            self.weapons[self.row].append(size_label)

            # remove the add new button
            self.grid.removeWidget(self.new_button)

            # add the new widgets
            self.grid.addWidget(button, self.row, 0)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(damage_label, self.row, 1)
            self.grid.setAlignment(damage_label, Qt.AlignHCenter)
            self.grid.addWidget(range_label, self.row, 2)
            self.grid.setAlignment(range_label, Qt.AlignHCenter)
            self.grid.addWidget(clip_label, self.row, 3)
            self.grid.setAlignment(clip_label, Qt.AlignHCenter)
            self.grid.addWidget(init_label, self.row, 4)
            self.grid.setAlignment(init_label, Qt.AlignHCenter)
            self.grid.addWidget(str_label, self.row, 5)
            self.grid.setAlignment(str_label, Qt.AlignHCenter)
            self.grid.addWidget(size_label, self.row, 6)
            self.grid.setAlignment(size_label, Qt.AlignHCenter)

            # add 1 to self.row
            self.row += 1

            # add the new button back to end
            self.grid.addWidget(self.new_button, self.row, 0)


        elif "####delete####" in name:
            # delete chosen
            # remove stat widget
            for widget in self.weapons[index][1:]:
                self.grid.removeWidget(widget)
                sip.delete(widget)

            # remove associated data
            del self.character.stats["weapons"][current_name.lower()]
            del self.weapons[index]

        else:
            # Update character object
            self.character.stats['weapons'][name] = {'damage': damage, 'range': weapon_range, 'clip': clip,
                                                     'init': init, 'str': strength, 'size': size}

            # Update damage
            self.weapons[index][2].setText(str(damage))
            # Update range
            self.weapons[index][3].setText(str(weapon_range))
            # Update clip
            self.weapons[index][4].setText(str(clip))
            # Update init
            self.weapons[index][5].setText(str(init))
            # Update str
            self.weapons[index][6].setText(str(strength))
            # Update size
            self.weapons[index][7].setText(str(size))

class Weapons_Dialog(QDialog):
    '''
    Dialog for entering/changing labels with tooltips
    '''

    def __init__(self, wintitle, name='', damage=0, weapon_range='', clip=0, init=0, strength=0, size=1, edit=False):
        super().__init__()
        self.setWindowTitle(wintitle)
        self.name = name
        self.damage = damage
        self.range = weapon_range
        self.clip = clip
        self.init = init
        self.str = strength
        self.size = size
        self.edit = edit

        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.name_label = QLabel("Name:")
        self.name_entry = QLineEdit()
        self.name_entry.insert(self.name.title())

        self.damage_label = QLabel("Damage:")
        self.damage_entry = QSpinBox()
        self.damage_entry.setMaximumWidth(30)
        self.damage_entry.setValue(self.damage)

        self.range_label = QLabel("Ranges:")
        self.range_entry = QLineEdit()
        self.range_entry.setText(self.range)

        self.clip_label = QLabel("Clip:")
        self.clip_entry = QSpinBox()
        self.clip_entry.setMaximumWidth(30)
        self.clip_entry.setValue(self.clip)

        self.init_label = QLabel("Init. Mod:")
        self.init_entry = QSpinBox()
        self.init_entry.setMaximum(0)
        self.init_entry.setMinimum(-20)
        self.init_entry.setMaximumWidth(30)
        self.init_entry.setValue(self.init)

        self.str_label = QLabel("Str:")
        self.str_entry = QSpinBox()
        self.str_entry.setMaximumWidth(30)
        self.str_entry.setValue(self.str)

        self.size_label = QLabel("Size:")
        self.size_entry = QSpinBox()
        self.size_entry.setMaximumWidth(30)
        self.size_entry.setValue(self.size)

        if self.edit:
            # add delete button and disable name box if editing
            self.name_entry.setDisabled(self.edit)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Discard,
                                         Qt.Horizontal, self)
            buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.del_item)
            buttonBox.button(QDialogButtonBox.Discard).setText("Delete")
        else:
            # adding new - only okay and cancel button
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.grid.addWidget(self.name_label, 0, 0)
        self.grid.addWidget(self.name_entry, 0, 1, 1, 3)

        self.grid.addWidget(self.damage_label, 1, 0)
        self.grid.addWidget(self.damage_entry, 1, 1)

        self.grid.addWidget(self.range_label, 2, 0)
        self.grid.addWidget(self.range_entry, 2, 1, 1, 3)

        self.grid.addWidget(self.clip_label, 3, 0)
        self.grid.addWidget(self.clip_entry, 3, 1)

        self.grid.addWidget(self.init_label, 3, 2)
        self.grid.addWidget(self.init_entry, 3, 3)
        self.grid.setAlignment(self.init_label, Qt.AlignRight)

        self.grid.addWidget(self.str_label, 4, 0)
        self.grid.addWidget(self.str_entry, 4, 1)

        self.grid.addWidget(self.size_label, 4, 2)
        self.grid.addWidget(self.size_entry, 4, 3)
        self.grid.setAlignment(self.size_label, Qt.AlignRight)

        self.grid.addWidget(buttonBox, 5, 1, 1, 3)

    def del_item(self):
        '''
        Handler for delete item action.
        Sends an accept signal but adds a delete flag to output
        '''

        self.name_entry.insert("####delete####")
        self.accept()

    def get_weapon(wintitle, name='', damage=0, weapon_range='', clip=0, init=0, strength=0, size=1, edit=False):
        '''
        Used to open a dialog window to enter details of label.
        '''
        dialog = Weapons_Dialog(wintitle, name, damage, weapon_range, clip, init, strength, size, edit)
        result = dialog.exec_()
        out_name = dialog.name_entry.text().lower()
        out_damage = dialog.damage_entry.value()
        out_range = dialog.range_entry.text().lower()
        out_clip = dialog.clip_entry.value()
        out_init = dialog.init_entry.value()
        out_str = dialog.str_entry.value()
        out_size = dialog.size_entry.value()
        return (out_name, out_damage, out_range, out_clip, out_init, out_str, out_size, result == QDialog.Accepted)
