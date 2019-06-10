# Chronicles of Darkness Vampire Inventory Sheet UI created for use in conjunction with Dicecord.
#   Copyright (C) 2017  Roy Healy

import sip
import math
import stats
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import basicUI

import player
import sys

class InventorySheet(QWidget):
    '''
    Inventory Sheet
    '''

    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):
        # Other Traits
        self.others = basicUI.StatWithTooltip(self.character, 'other traits')

        # Rites/Miracles
        self.ritesmiracles = RitesMiracles(self.character)

        # Languages
        self.languages = basicUI.Hover_Label_Col("LANGUAGES", self.character, 'languages')

        # Conditions
        self.conditions = basicUI.Hover_Label_Col("CONDITIONS", self.character, 'conditions')

        # History
        self.history = basicUI.TextBoxEntry(self.character, 'history')

        # Description
        self.description = basicUI.Description(self.character)

        # Weapons
        self.weapons = basicUI.Weapons(self.character)

        # Equipment
        self.equipment = basicUI.Equipment(self.character)

        box = QHBoxLayout()
        self.setLayout(box)

        # left side
        lcol = QVBoxLayout()
        lcol.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        lcol.addWidget(self.others)
        lcol.addWidget(self.ritesmiracles)
        lcol.addWidget(self.languages)
        lcol.addWidget(self.conditions)
        box.addLayout(lcol)

        # right side
        rcol = QVBoxLayout()
        rcol.setAlignment(Qt.AlignTop)
        rcol.addWidget(self.history)
        rcol.setAlignment(self.history, Qt.AlignHCenter|Qt.AlignTop)
        rcol.addWidget(self.description)
        rcol.setAlignment(self.description, Qt.AlignHCenter|Qt.AlignTop)
        rcol.addWidget(self.weapons)
        rcol.addWidget(self.equipment)
        box.addLayout(rcol)

    def edit_toggle(self):
        self.others.edit_toggle()
        self.ritesmiracles.edit_toggle()
        self.languages.edit_toggle()
        self.description.edit_toggle()
        self.history.edit_toggle()

class RitesMiracles(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignTop|Qt.AlignHCenter)

        overall_label = QLabel()
        overall_label.setText('==RITES/MIRACLES==')
        overall_label.setStyleSheet("QLabel {font: 13pt;}")
        self.grid.addWidget(overall_label, 0, 0, 1, 2)
        self.grid.setAlignment(overall_label, Qt.AlignHCenter)

        overall_name = QLabel("Name")
        overall_name.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_level = QLabel("Level")
        overall_level.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")

        self.grid.addWidget(overall_name, 1, 0)
        self.grid.setAlignment(overall_name, Qt.AlignHCenter)
        self.grid.addWidget(overall_level, 1, 1)
        self.grid.setAlignment(overall_level, Qt.AlignHCenter)

        self.items = {}
        self.row = 2
        self.edit_buttons = QButtonGroup()
        self.edit_buttons.buttonClicked[int].connect(self.edit_entry)

        # self.character.stats['rites or miracles'][name] = {tooltip, level}

        for name in self.character.stats['rites or miracles']:
            self.items[self.row] = {'name': name}
            details = self.character.stats['rites or miracles'][name]
            level = details['level'] # may be str if read
            tooltip = details['tooltip']

            # entry name
            self.items[self.row]['button'] = QPushButton(name.title())
            self.items[self.row]['button'].setStyleSheet("QPushButton {font: 10pt; border: none}")
            self.items[self.row]['button'].setCursor(QCursor(Qt.PointingHandCursor))
            self.items[self.row]['button'].setToolTip(tooltip)
            self.edit_buttons.addButton(self.items[self.row]['button'], self.row)

            # level
            self.items[self.row]['level'] = QLabel(str(level))
            self.items[self.row]['level'].setStyleSheet("QLabel {font: 10pt}")

            self.grid.addWidget(self.items[self.row]['button'], self.row, 0)
            self.grid.setAlignment(self.items[self.row]['button'], Qt.AlignHCenter)
            self.grid.addWidget(self.items[self.row]['level'], self.row, 1)
            self.grid.setAlignment(self.items[self.row]['level'], Qt.AlignHCenter)
            self.row += 1

        #if edit mode, add the new button to end
        if self.character.edit_mode: 
            self.new_button = QPushButton("Add New")
            self.new_button.setMaximumWidth(60)
            self.new_button.clicked.connect(self.edit_entry)
            self.grid.addWidget(self.new_button, self.row, 0)

    def edit_toggle(self):
        if self.character.edit_mode:
            #add button if edit mode started
            self.new_button = QPushButton("Add New")
            self.new_button.setMaximumWidth(60)
            self.new_button.clicked.connect(self.edit_entry)
            self.grid.addWidget(self.new_button, self.row, 0)
        else:
            # remove button if edit mode ended
            self.grid.removeWidget(self.new_button)
            sip.delete(self.new_button)

    def edit_entry(self, index=None):
        # only works in edit mode
        if not self.character.edit_mode:
            return

        if not index:
            current_name = None
            # add new item if no index given
            name, tooltip, level, ok = RitesMiracles_Dialog.get_input("Add Rite/Miracle")

        else:
            # edit current item
            current = self.items[index]
            current_name = current['name']
            current_details = self.character.stats['rites or miracles'][current_name]

            current_tooltip = current_details['tooltip']
            current_level = current_details['level']

            name, tooltip, level, ok = RitesMiracles_Dialog.get_input(
                "Change Rite/Miracle",
                current_name,
                current_tooltip,
                current_level,
                edit=True)

        if not ok:
            # cancel pressed
            return

        if not current_name and name in self.character.stats['rites or miracles']:
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
            self.character.stats['rites or miracles'][name] = {'tooltip': tooltip, 'level': level}

            # create entry
            self.items[self.row] = {'name': name}

            # entry name
            self.items[self.row]['button'] = QPushButton(name.title())
            self.items[self.row]['button'].setStyleSheet("QPushButton {font: 10pt; border: none}")
            self.items[self.row]['button'].setCursor(QCursor(Qt.PointingHandCursor))
            self.items[self.row]['button'].setToolTip(tooltip)
            self.edit_buttons.addButton(self.items[self.row]['button'], self.row)

            # level
            self.items[self.row]['level'] = QLabel(str(level))
            self.items[self.row]['level'].setStyleSheet("QLabel {font: 10pt}")

            # remove the add new button
            self.grid.removeWidget(self.new_button)

            # add the new widgets
            self.grid.addWidget(self.items[self.row]['button'], self.row, 0)
            self.grid.setAlignment(self.items[self.row]['button'], Qt.AlignHCenter)
            self.grid.addWidget(self.items[self.row]['level'], self.row, 1)
            self.grid.setAlignment(self.items[self.row]['level'], Qt.AlignHCenter)

            # add 1 to self.row
            self.row += 1

            # add the new button back to end
            self.grid.addWidget(self.new_button, self.row, 0)

        elif "####delete####" in name:
            # delete chosen
            # remove stat widget
            for widget in [self.items[index]['button'],self.items[index]['level']]:
                self.grid.removeWidget(widget)
                sip.delete(widget)

            # remove associated data
            del self.character.stats["rites or miracles"][current_name.lower()]
            del self.items[index]

        else:
            # Update character object
            self.character.stats['rites or miracles'][name] = {'tooltip': tooltip, 'level': level}

            # Update tooltip
            self.items[index]['button'].setToolTip(tooltip)
            # Update level
            self.items[index]['level'].setText(str(level))
            

class RitesMiracles_Dialog(QDialog):
    '''
    Dialog for entering/changing labels with tooltips
    '''

    def __init__(self, wintitle, name = '', tooltip = '', level = 0, edit=False):
        super().__init__()
        self.setWindowTitle(wintitle)
        self.name = name
        self.tooltip = tooltip
        self.level = int(level) # may be a str if read
        self.edit = edit

        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.name_label = QLabel("Name:")
        self.name_entry = QLineEdit()
        self.name_entry.insert(self.name.title())

        self.tooltip_label = QLabel("Tooltip:")
        self.tooltip_entry = QTextEdit()
        self.tooltip_entry.setText(self.tooltip)

        self.level_label = QLabel("Level:")
        self.level_entry = QSpinBox()
        self.level_entry.setMaximumWidth(30)
        self.level_entry.setValue(self.level)

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

        self.grid.addWidget(self.level_label, 1, 0)
        self.grid.addWidget(self.level_entry, 1, 1)

        self.grid.addWidget(self.tooltip_label, 2, 0)
        self.grid.setAlignment(self.tooltip_label, Qt.AlignTop)
        self.grid.addWidget(self.tooltip_entry, 2, 1, 1, 3)

        self.grid.addWidget(buttonBox, 3, 1, 1, 3)

    def del_item(self):
        '''
        Handler for delete item action.
        Sends an accept signal but adds a delete flag to output
        '''

        self.name_entry.insert("a####delete####")
        self.accept()

    def get_input(wintitle, name = '', tooltip = '', level = 0, edit=False):
        '''
        Used to open a dialog window to enter details of label.
        '''
        dialog = RitesMiracles_Dialog(wintitle, name, tooltip, level, edit)
        result = dialog.exec_()
        out_name = dialog.name_entry.text().lower()
        out_tooltip = dialog.tooltip_entry.toPlainText()
        out_level = dialog.level_entry.value()
        return (out_name, out_tooltip, out_level, result == QDialog.Accepted)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    char = player.Character(splat = 'vampire')
    char.edit_mode = False
    test = InventorySheet(char)
    test.show()
    sys.exit(app.exec_())
