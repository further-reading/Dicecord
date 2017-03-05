# Basic UI elements shared over Dicecord sheet and inventory UI objects.
#    Copyright (C) 2017  Roy Healy


import sip, stats
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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
                    rotes = self.character.stats['rote skills']
                    rote_button = (Square(stat, self.character, filled= stat in rotes))
                    rote_button.clicked.connect(rote_button.change_Image)
                    grid.addWidget(rote_button,row,0)
                else:
                    continue
                
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
        

        elif "# # # # DELETE# # # # " in label:
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
        
        self.title_entry.insert("# # # # DELETE# # # # ")
        self.accept()

    def get_input(wintitle, title = '', tooltip = '', edit = False):
        '''
        Used to open a dialog window to enter details of label.
        '''
        dialog = Label_Tooltip_Dialog(title, tooltip, edit, wintitle)
        result = dialog.exec_()
        return (dialog.title_entry.text(), dialog.tooltip_entry.toPlainText(), result == QDialog.Accepted)
