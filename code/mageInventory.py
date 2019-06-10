# Chronicles of Darkness Mage Inventory Sheet UI created for use in conjunction with Dicecord.
#   Copyright (C) 2017  Roy Healy

import sip
import math
import stats
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import basicUI
import mageUI

class InventorySheet(QWidget):
    """
    Inventory Sheet
    """

    def __init__(self, character, stats_sheet):
        super().__init__()
        self.character = character
        self.stats_sheet = stats_sheet
        self.initUI()

    def initUI(self):
        # active spells
        self.aspells = basicUI.Hover_Label_Col("ACTIVE SPELLS", self.character, 'active spells')
        # Attainments
        self.attainments = basicUI.Hover_Label_Col("ATTAINMENTS", self.character, 'attainments')
        # Dedicated magical tool
        self.magtool = basicUI.Hover_Label_Col("MAGICAL TOOLS", self.character, 'magtool')
        # Praxes
        self.praxes = Praxes(self.character)

        # Physical description
        self.description = basicUI.Description(self.character)
        # Rotes
        self.rotes = Rotes(self.character)
        # Nimbus
        self.nimbus = basicUI.TextBoxEntry(self.character, 'nimbus')
        # Enchanted Items
        self.enchitems = Ench_Items(self.character, self.stats_sheet.mana)
        # Combat
        self.weapons = basicUI.Weapons(self.character)

        box = QHBoxLayout()
        self.setLayout(box)

        # left side
        lcol = QVBoxLayout()
        lcol.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        lcol.addWidget(self.aspells)
        lcol.addWidget(self.attainments)
        lcol.addWidget(self.magtool)
        lcol.addWidget(self.praxes)
        box.addLayout(lcol)

        # right side
        rcol = QVBoxLayout()
        rcol.setAlignment(Qt.AlignTop)
        rcol.addWidget(self.description)
        rcol.setAlignment(self.description, Qt.AlignHCenter | Qt.AlignTop)
        rcol.addWidget(self.rotes)
        rcol.addWidget(self.nimbus)
        rcol.setAlignment(self.nimbus, Qt.AlignHCenter | Qt.AlignTop)
        rcol.addWidget(self.enchitems)
        rcol.addWidget(self.weapons)
        box.addLayout(rcol)

    def edit_toggle(self):
        self.praxes.edit_toggle()
        self.attainments.edit_toggle()
        self.magtool.edit_toggle()
        self.rotes.edit_toggle()
        self.enchitems.edit_toggle()
        self.nimbus.edit_toggle()


class Praxes(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignTop)

        overall_label = QLabel()
        overall_label.setText('==PRAXES==')
        overall_label.setStyleSheet("QLabel {font: 13pt;}")
        self.grid.addWidget(overall_label, 0, 0, 1, 3)
        self.grid.setAlignment(overall_label, Qt.AlignHCenter)

        overall_name = QLabel("Name")
        overall_name.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_arcanum = QLabel("Arcanum")
        overall_arcanum.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_pool = QLabel("Pool")
        overall_pool.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")

        self.grid.addWidget(overall_name, 1, 0)
        self.grid.setAlignment(overall_name, Qt.AlignHCenter)
        self.grid.addWidget(overall_arcanum, 1, 1)
        self.grid.setAlignment(overall_arcanum, Qt.AlignHCenter)
        self.grid.addWidget(overall_pool, 1, 2)
        self.grid.setAlignment(overall_pool, Qt.AlignHCenter)

        self.praxes = {}
        self.row = 2
        self.edit_buttons = QButtonGroup()
        self.edit_buttons.buttonClicked[int].connect(self.edit_entry)

        # self.character.stats['praxes'][name] = {'tooltip':'','arcanum':''}

        for name in self.character.stats['praxes']:
            self.praxes[self.row] = {'name': name}
            details = self.character.stats['praxes'][name]
            try:
                tooltip = details['tooltip']
            except KeyError:
                tooltip = details['tooltip'] = ''
            arcanum = details['arcanum']

            # item name
            button = QPushButton(name.title())
            button.setToolTip(tooltip)
            button.setStyleSheet("QPushButton {font: 10pt; border: none}")
            button.setCursor(QCursor(Qt.WhatsThisCursor))
            self.praxes[self.row]['button'] = button
            self.edit_buttons.addButton(button, self.row)

            # arcanum
            arcanum_label = QLabel(arcanum.title() + " (" + str(self.character.stats[arcanum]) + ")")
            arcanum_label.setStyleSheet("QLabel {font: 10pt}")
            self.praxes[self.row]['arcanum'] = arcanum_label

            # pool
            pool = self.calculate_pool(arcanum)
            pool_label = QLabel(pool)
            pool_label.setStyleSheet("QLabel {font: 10pt}")
            self.praxes[self.row]['pool'] = pool_label

            self.grid.addWidget(button, self.row, 0)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(arcanum_label, self.row, 1)
            self.grid.setAlignment(arcanum_label, Qt.AlignHCenter)
            self.grid.addWidget(pool_label, self.row, 2)
            self.grid.setAlignment(pool_label, Qt.AlignHCenter)
            self.row += 1

    def edit_toggle(self):
        if self.character.edit_mode:
            # add the new button to end
            self.new_button = QPushButton("Add New")
            self.new_button.setMaximumWidth(60)
            self.new_button.clicked.connect(self.edit_entry)
            self.grid.addWidget(self.new_button, self.row, 0)

        else:
            # remove new button
            self.grid.removeWidget(self.new_button)
            sip.delete(self.new_button)

            # update widget
            self.update_items()

    def calculate_pool(self, arcanum):
        return str(self.character.stats[arcanum] + self.character.stats['gnosis'])

    def update_items(self):
        for index in self.praxes:
            name = self.praxes[index]['name']
            details = self.character.stats['praxes'][name]
            arcanum = details['arcanum']
            arcanum_label = self.praxes[index]['arcanum']
            new_arcanum = arcanum.title() + " (" + str(self.character.stats[arcanum]) + ")"
            arcanum_label.setText(new_arcanum)

            pool_label = self.praxes[index]['pool']
            pool = str(self.character.stats[arcanum] + self.character.stats['gnosis'])
            pool_label.setText(pool)

    def edit_entry(self, index=None):
        if not self.character.edit_mode:
            # View only
            current = self.praxes[index]
            current_name = current['name']
            current_details = self.character.stats['praxes'][current_name]

            current_tooltip = current_details['tooltip']
            current_arcanum = current_details['arcanum']
            basicUI.ViewDialogue("Praxis",
                                 name=current_name,
                                 arcanum=current_arcanum.title(),
                                 details=current_tooltip)
            return

        if not index:
            current_name = None
            # add new item if no index given
            name, tooltip, arcanum, ok = Praxis_Dialog.get_praxis("Add Praxis")

        else:
            # edit current item
            current = self.praxes[index]
            current_name = current['name']
            current_details = self.character.stats['praxes'][current_name]

            current_tooltip = current_details['tooltip']
            current_arcanum = current_details['arcanum']

            name, tooltip, arcanum, ok = Praxis_Dialog.get_praxis("Change Praxis", current_name, current_tooltip,
                                                                  current_arcanum, edit=True)

        if not ok:
            # cancel pressed
            return

        if not current_name and name in self.character.stats['praxes']:
            # add new but title already in use
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Item with this name already exists.")
            msg.setInformativeText("Please use unique name.")
            msg.setWindowTitle("Duplicate Name")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

        elif not current_name:
            # Only adds new if entry by that name does not exist yet
            # add entry on character object
            self.character.stats['praxes'][name] = {'tooltip': tooltip, 'arcanum': arcanum}

            # create entry
            self.praxes[self.row] = {'name' : name}

            # item name
            button = QPushButton(name.title())
            button.setToolTip(tooltip)
            button.setStyleSheet("QPushButton {font: 10pt; border: none}")
            button.setCursor(QCursor(Qt.WhatsThisCursor))
            self.praxes[self.row]['button'] = button
            self.edit_buttons.addButton(button, self.row)

            # arcanum
            arcanum_label = QLabel(arcanum.title() + " (" + str(self.character.stats[arcanum]) + ")")
            arcanum_label.setStyleSheet("QLabel {font: 10pt}")
            self.praxes[self.row]['arcanum'] = arcanum_label

            # pool
            pool = self.calculate_pool(arcanum)
            pool_label = QLabel(pool)
            pool_label.setStyleSheet("QLabel {font: 10pt}")
            self.praxes[self.row]['pool'] = pool_label

            # remove the add new button
            self.grid.removeWidget(self.new_button)

            # add the new widgets
            self.grid.addWidget(button, self.row, 0)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(arcanum_label, self.row, 1)
            self.grid.setAlignment(arcanum_label, Qt.AlignHCenter)
            self.grid.addWidget(pool_label, self.row, 2)
            self.grid.setAlignment(pool_label, Qt.AlignHCenter)

            # add 1 to self.row
            self.row += 1

            # add the new button back to end
            self.grid.addWidget(self.new_button, self.row, 0)


        elif "####delete####" in name:
            # delete chosen
            # remove stat widget
            for key in self.praxes[index]:
                if key != 'name':
                    widget = self.praxes[index][key]
                    self.grid.removeWidget(widget)
                    sip.delete(widget)

            # remove associated data
            del self.character.stats["praxes"][current_name.lower()]
            del self.praxes[index]

        else:
            # Update character object
            self.character.stats["praxes"][name] = {'tooltip': tooltip, 'arcanum': arcanum}

            # Update tooltip
            self.praxes[index]['button'].setToolTip(tooltip)

            # Update arcanum
            self.praxes[index]['arcanum'].setText(arcanum.title() + " (" + str(self.character.stats[arcanum]) + ")")

            # Update pool
            pool = self.calculate_pool(arcanum)
            self.praxes[index]['pool'].setText(pool)


class Praxis_Dialog(QDialog):
    '''
    Dialog for entering/changing labels with tooltips
    '''

    def __init__(self, wintitle, name='', tooltip='', arcanum='', edit=False):
        super().__init__()
        self.setWindowTitle(wintitle)
        self.name = name
        self.tooltip = tooltip
        self.edit = edit
        self.arcanum = arcanum

        self.initUI()
        # self.setMaximumSize(20, 20)

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.name_label = QLabel("Name:")
        self.name_entry = QLineEdit()
        self.name_entry.insert(self.name.title())

        self.arcanum_label = QLabel("Primary Arcanum:")
        self.arcanum_entry = QComboBox()
        for arcanum in mageUI.ARCANA:
            self.arcanum_entry.addItem(arcanum.title())

        if self.arcanum:
            self.arcanum_entry.setCurrentText(self.arcanum)

        self.tooltip_label = QLabel("Tooltip:")
        self.tooltip_entry = QTextEdit()
        self.tooltip_entry.setText(self.tooltip)

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
        self.grid.addWidget(self.name_entry, 0, 1)

        self.grid.addWidget(self.arcanum_label, 1, 0)
        self.grid.addWidget(self.arcanum_entry, 1, 1)

        self.grid.addWidget(self.tooltip_label, 5, 0)
        self.grid.setAlignment(self.tooltip_label, Qt.AlignTop)
        self.grid.addWidget(self.tooltip_entry, 5, 1)
        self.grid.addWidget(buttonBox, 6, 1)

    def del_item(self):
        '''
        Handler for delete item action.
        Sends an accept signal but adds a delete flag to output
        '''

        self.name_entry.insert("####delete####")
        self.accept()

    def get_praxis(wintitle, name='', tooltip='', arcanum='', edit=False):
        '''
        Used to open a dialog window to enter details of label.
        '''
        dialog = Praxis_Dialog(wintitle, name, tooltip, arcanum, edit)
        result = dialog.exec_()
        out_name = dialog.name_entry.text().lower()
        out_tooltip = dialog.tooltip_entry.toPlainText()
        out_arcanum = dialog.arcanum_entry.currentText().lower()
        return (out_name, out_tooltip, out_arcanum, result == QDialog.Accepted)


class Ench_Items(QWidget):
    def __init__(self, character, mana_widget):
        super().__init__()
        self.character = character
        self.mana_widget = mana_widget
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignTop)

        overall_label = QLabel()
        overall_label.setText('==Enchanted Items==')
        overall_label.setStyleSheet("QLabel {font: 13pt;}")
        self.grid.addWidget(overall_label, 0, 0, 1, 3)
        self.grid.setAlignment(overall_label, Qt.AlignHCenter)

        overall_type = QLabel("Type")
        overall_type.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_name = QLabel("Name")
        overall_name.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_pool = QLabel("Pool")
        overall_pool.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")

        self.grid.addWidget(overall_type, 1, 0)
        self.grid.setAlignment(overall_type, Qt.AlignHCenter)
        self.grid.addWidget(overall_name, 1, 1)
        self.grid.setAlignment(overall_name, Qt.AlignHCenter)
        self.grid.addWidget(overall_pool, 1, 2)
        self.grid.setAlignment(overall_pool, Qt.AlignHCenter)

        self.items = {}
        self.row = 2
        self.edit_buttons = QButtonGroup()
        self.edit_buttons.buttonClicked[int].connect(self.edit_entry)

        # self.character.stats['ench item'][name] = {'type':, 'tooltip':, 'rating':, 'mana':}
        # imbued mana = 1 + optional extra
        # artifact mana = rating*2
        # imbued pool = rating + player Gnosis
        # artifact pool = rating + 0.5*rating (rounded up)

        for name in self.character.stats['ench items']:
            self.items[self.row] = []
            item_details = self.character.stats['ench items'][name]
            item_type = item_details['type']
            tooltip = item_details['tooltip']

            # item type
            item_label = QLabel(item_type.title())
            item_label.setStyleSheet("QLabel {font: 10pt}")
            self.items[self.row].append(item_label)

            # item name
            button = QPushButton(name.title())
            button.setToolTip(tooltip)
            button.setStyleSheet("QPushButton {font: 10pt; border: none}")
            button.setCursor(QCursor(Qt.WhatsThisCursor))
            self.items[self.row].append(button)
            self.edit_buttons.addButton(button, self.row)

            # pool
            pool, pool_tooltip = self.calculate_pool(item_details)
            pool_label = QLabel(pool)
            pool_label.setToolTip(pool_tooltip)
            pool_label.setCursor(QCursor(Qt.WhatsThisCursor))
            pool_label.setStyleSheet("QLabel {font: 10pt}")
            self.items[self.row].append(pool_label)

            self.grid.addWidget(item_label, self.row, 0)
            self.grid.setAlignment(item_label, Qt.AlignHCenter)
            self.grid.addWidget(button, self.row, 1)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(pool_label, self.row, 2)
            self.grid.setAlignment(pool_label, Qt.AlignHCenter)
            self.row += 1

    def edit_toggle(self):
        if self.character.edit_mode:
            # add the new button to end
            self.new_button = QPushButton("Add New")
            self.new_button.clicked.connect(self.edit_entry)
            self.grid.addWidget(self.new_button, self.row, 0)

        else:
            # remove new button
            self.grid.removeWidget(self.new_button)
            sip.delete(self.new_button)

            # apply changes
            self.update_items()

    def calculate_pool(self, item_details):
        item_type = item_details['type']
        rating = int(item_details['rating']) #imported as str

        if item_type == "imbued":
            # imbued pool = rating + player Gnosis
            return (str(rating + self.character.stats['gnosis']),
                    "Item Rating(" + str(rating) + ") + Character Gnosis(" + str(self.character.stats['gnosis']) + ")")
        else:
            # artifact pool = rating + 0.5*rating (rounded up)
            # players can optionally use their own stats, but will only show the item's stats
            return (str(math.ceil(rating * 1.5)),
                    "Item Rating(" + str(rating) + ") + Item Gnosis(" + str(math.ceil(rating / 2)) + ")")

    def update_items(self):
        for index in self.items:
            widgets = self.items[index]
            item_name = widgets[1].text().lower()
            item_details = self.character.stats['ench items'][item_name]
            new_pool, new_tooltip = self.calculate_pool(item_details)
            widgets[2].setText(new_pool)
            widgets[2].setToolTip(new_tooltip)

    def edit_entry(self, index=None):
        if not self.character.edit_mode:
            # View only
            current = self.items[index]
            current_name = current[1].text().lower()
            current_details = self.character.stats['ench items'][current_name]

            current_type = current_details['type']
            current_tooltip = current_details['tooltip']
            basicUI.ViewDialogue("Enchanted Item",
                                 name=current_name,
                                 type=current_type.title(),
                                 details=current_tooltip)
            return

        if not index:
            current_name = None
            # add new item if no index given
            item_type, name, tooltip, rating, mana, ok = EnchItem_Dialog.get_input("Add Item")

        else:
            # edit current item
            current = self.items[index]
            current_name = current[1].text().lower()
            current_details = self.character.stats['ench items'][current_name]

            current_type = current_details['type']
            current_tooltip = current_details['tooltip']
            current_rating = int(current_details['rating']) # imported as str
            current_mana = int(current_details['mana']) # imported as str

            item_type, name, tooltip, rating, mana, ok = EnchItem_Dialog.get_input("Change Item", current_type,
                                                                                   current_name, current_tooltip,
                                                                                   current_rating, current_mana,
                                                                                   edit=True)

        if not ok:
            # cancel pressed
            return

        if not current_name and name in self.character.stats['ench items']:
            # add new but title already in use
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Item with this name already exists.")
            msg.setInformativeText("Please use unique name.")
            msg.setWindowTitle("Duplicate Name")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

        elif not current_name:
            # Only adds new if entry by that name does not exist yet
            # add entry on character object
            self.character.stats['ench items'][name] = {'type': item_type,
                                                        'tooltip': tooltip,
                                                        'rating': rating,
                                                        'mana': mana,
                                                        'mana spent':0}

            # create entry
            self.items[self.row] = []

            # item type
            item_label = QLabel(item_type.title())
            item_label.setStyleSheet("QLabel {font: 10pt}")
            self.items[self.row].append(item_label)

            # item name
            button = QPushButton(name.title())
            button.setToolTip(tooltip)
            button.setStyleSheet("QPushButton {font: 10pt; border: none}")
            button.setCursor(QCursor(Qt.WhatsThisCursor))
            self.items[self.row].append(button)
            self.edit_buttons.addButton(button, self.row)

            # pool
            pool, pool_tooltip = self.calculate_pool(self.character.stats['ench items'][name])
            pool_label = QLabel(pool)
            pool_label.setToolTip(pool_tooltip)
            pool_label.setCursor(QCursor(Qt.WhatsThisCursor))
            pool_label.setStyleSheet("QLabel {font: 10pt}")
            self.items[self.row].append(pool_label)

            # remove the add new button
            self.grid.removeWidget(self.new_button)

            # add the new widgets
            self.grid.addWidget(item_label, self.row, 0)
            self.grid.setAlignment(item_label, Qt.AlignHCenter)
            self.grid.addWidget(button, self.row, 1)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(pool_label, self.row, 2)
            self.grid.setAlignment(pool_label, Qt.AlignHCenter)

            # add 1 to self.row
            self.row += 1

            # add the new button back to end
            self.grid.addWidget(self.new_button, self.row, 0)


        elif "####delete####" in name:
            # delete chosen
            # remove stat widget
            for widget in self.items[index]:
                self.grid.removeWidget(widget)
                sip.delete(widget)

            # remove associated data
            del self.character.stats["ench items"][current_name.lower()]
            del self.items[index]

        else:
            # Update character object
            self.character.stats['ench items'][name] = {'type': item_type,
                                                        'tooltip': tooltip,
                                                        'rating': rating,
                                                        'mana': mana,
                                                        'mana spent':0}

            # Update type
            self.items[index][0].setText(item_type.title())

            # Update tooltip
            self.items[index][1].setToolTip(tooltip)

            # update pool
            pool, pool_tooltip = self.calculate_pool(self.character.stats['ench items'][name])
            current[2].setText(pool)
            current[2].setToolTip(pool_tooltip)

        # update mana widget
        self.mana_widget.update_ench_items()


class EnchItem_Dialog(QDialog):
    '''
    Dialog for entering/changing labels with tooltips
    '''

    def __init__(self, wintitle, item_type='artifact', name='', tooltip='', rating=0, mana=0, edit=False):
        super().__init__()
        self.setWindowTitle(wintitle)
        self.type = item_type
        self.name = name
        self.tooltip = tooltip
        self.rating = rating
        if item_type == 'imbued':
            self.mana_mod_amt = mana - 1
        else:
            self.mana_mod_amt = 0
        self.edit = edit

        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.details = QLabel()

        self.type_label = QLabel("Type:")
        self.type_entry = QComboBox()
        self.type_entry.addItem("Artifact")
        self.type_entry.addItem("Imbued")
        if self.type:
            self.type_entry.setCurrentText(self.type.title())

        self.type_entry.currentIndexChanged.connect(self.mana_change)

        self.name_label = QLabel("Name:")
        self.name_entry = QLineEdit()
        self.name_entry.insert(self.name.title())

        self.rating_label = QLabel("Arcanum Rating:")
        self.rating_entry = QSpinBox()
        self.rating_entry.setMaximumWidth(30)
        self.rating_entry.setValue(self.rating)
        self.rating_entry.valueChanged.connect(self.mana_change)

        self.mana_label = QLabel("Mana (Base + Mod = Total):")
        self.mana_base = QLabel()
        self.mana_mod = QSpinBox()
        self.mana_mod.setValue(self.mana_mod_amt)
        self.mana_mod.valueChanged.connect(self.mana_change)
        self.mana_total = QLabel()
        self.mana_change()

        self.tooltip_label = QLabel("Tooltip:")
        self.tooltip_entry = QTextEdit()
        self.tooltip_entry.setText(self.tooltip)

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

        self.grid.addWidget(self.type_label, 1, 0)
        self.grid.addWidget(self.type_entry, 1, 1, 1, 3)

        self.grid.addWidget(self.rating_label, 2, 0)
        self.grid.addWidget(self.rating_entry, 2, 1, 1, 3)

        self.grid.addWidget(self.mana_label, 3, 0)
        self.grid.addWidget(self.mana_base, 3, 1)
        self.grid.setAlignment(self.mana_base, Qt.AlignCenter)
        self.grid.addWidget(self.mana_mod, 3, 2)
        self.grid.setAlignment(self.mana_mod, Qt.AlignCenter)
        self.grid.addWidget(self.mana_total, 3, 3)
        self.grid.setAlignment(self.mana_total, Qt.AlignCenter)

        self.grid.addWidget(self.details, 4, 1, 1, 3)

        self.grid.addWidget(self.tooltip_label, 5, 0)
        self.grid.setAlignment(self.tooltip_label, Qt.AlignTop)
        self.grid.addWidget(self.tooltip_entry, 5, 1, 1, 3)
        self.grid.addWidget(buttonBox, 6, 1, 1, 3)

    def mana_change(self):
        self.type = self.type_entry.currentText().lower()
        self.rating = self.rating_entry.value()

        if self.type == "artifact":
            self.details.setText("Base Mana is twice Arcanum Rating.")
            self.mana_base.setText(str(self.rating * 2))
            self.mana_mod.setValue(0)
            self.mana_mod.setEnabled(False)

        else:
            self.details.setText("Base Mana is 1, but can upgrade.")
            self.mana_base.setText("1")
            self.mana_mod.setEnabled(True)

        self.mana_total.setText(str(int(self.mana_base.text()) + self.mana_mod.value()))

    def del_item(self):
        '''
        Handler for delete item action.
        Sends an accept signal but adds a delete flag to output
        '''

        self.name_entry.insert("a####delete####")
        self.accept()

    def get_input(wintitle, item_type='artifact', name='', tooltip='', rating=0, mana=0, edit=False):
        '''
        Used to open a dialog window to enter details of label.
        '''
        dialog = EnchItem_Dialog(wintitle, item_type, name, tooltip, rating, mana, edit)
        result = dialog.exec_()
        out_type = dialog.type_entry.currentText().lower()
        out_name = dialog.name_entry.text().lower()
        out_tooltip = dialog.tooltip_entry.toPlainText()
        out_rating = dialog.rating_entry.value()
        out_mana = int(dialog.mana_total.text())
        return (out_type, out_name, out_tooltip, out_rating, out_mana, result == QDialog.Accepted)


class Rotes(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignTop)

        overall_label = QLabel()
        overall_label.setText('==ROTES==')
        overall_label.setStyleSheet("QLabel {font: 13pt;}")
        self.grid.addWidget(overall_label, 0, 0, 1, 4)
        self.grid.setAlignment(overall_label, Qt.AlignHCenter)

        overall_name = QLabel("Name")
        overall_name.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_arcanum = QLabel("Arcanum")
        overall_arcanum.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_skill = QLabel("Skill")
        overall_skill.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")
        overall_pool = QLabel("Pool")
        overall_pool.setStyleSheet("QLabel {text-decoration: underline; font: 11pt}")

        self.grid.addWidget(overall_name, 1, 0)
        self.grid.setAlignment(overall_name, Qt.AlignHCenter)
        self.grid.addWidget(overall_arcanum, 1, 1)
        self.grid.setAlignment(overall_arcanum, Qt.AlignHCenter)
        self.grid.addWidget(overall_skill, 1, 2)
        self.grid.setAlignment(overall_skill, Qt.AlignHCenter)
        self.grid.addWidget(overall_pool, 1, 3)
        self.grid.setAlignment(overall_pool, Qt.AlignHCenter)

        self.rotes = {}
        self.row = 2
        self.edit_buttons = QButtonGroup()
        self.edit_buttons.buttonClicked[int].connect(self.edit_entry)

        for rote in self.character.stats['rotes']:
            self.rotes[self.row] = []
            rote_details = self.character.stats['rotes'][rote]
            try:
                tooltip = rote_details['tooltip']
            except KeyError:
                tooltip = rote_details['tooltip'] = ''
            arcanum = rote_details['arcanum']
            skill = rote_details['skill']

            # spellname
            button = QPushButton(rote.title())
            button.setToolTip(tooltip)
            button.setStyleSheet("QPushButton {font: 10pt; border: none}")
            button.setCursor(QCursor(Qt.WhatsThisCursor))
            self.rotes[self.row].append(button)
            self.edit_buttons.addButton(button, self.row)

            # primary arcanum
            arcanum_label = QLabel(arcanum.title() + " (" + str(self.character.stats[arcanum]) + ")")
            arcanum_label.setStyleSheet("QLabel {font: 10pt}")
            self.rotes[self.row].append(arcanum_label)

            # rote skill
            skill_label = QLabel(skill.title() + " (" + str(self.character.stats[skill]) + ")")
            # check for rote skill
            if skill in self.character.stats['rote skills']:
                skill_label.setStyleSheet("QLabel {font: bold; font-size: 10pt}")
            else:
                skill_label.setStyleSheet("QLabel {font-size: 10pt}")

            self.rotes[self.row].append(skill_label)

            # pool
            pool = self.calculate_pool(rote)
            pool_label = QLabel(str(pool))
            pool_label.setStyleSheet("QLabel {font: 10pt}")
            self.rotes[self.row].append(pool_label)

            self.grid.addWidget(button, self.row, 0)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(arcanum_label, self.row, 1)
            self.grid.setAlignment(arcanum_label, Qt.AlignHCenter)
            self.grid.addWidget(skill_label, self.row, 2)
            self.grid.setAlignment(skill_label, Qt.AlignHCenter)
            self.grid.addWidget(pool_label, self.row, 3)
            self.grid.setAlignment(pool_label, Qt.AlignHCenter)
            self.row += 1

    def edit_toggle(self):
        if self.character.edit_mode:
            # add the new button to end
            self.new_button = QPushButton("Add New")
            self.new_button.setMaximumWidth(60)
            self.new_button.clicked.connect(self.edit_entry)
            self.grid.addWidget(self.new_button, self.row, 0)

        else:
            # remove new button
            self.grid.removeWidget(self.new_button)
            sip.delete(self.new_button)

            # apply changes
            self.update_items()

    def calculate_pool(self, rote_name):
        rote = self.character.stats['rotes'][rote_name]
        arcanum = rote['arcanum']
        skill = rote['skill']

        pool = self.character.stats[skill] + self.character.stats['gnosis'] + self.character.stats[arcanum]
        if skill in self.character.stats['rote skills']:
            pool += 1

        return pool

    def update_items(self):
        for index in self.rotes:
            current = self.rotes[index]
            rote = current[0].text().lower()
            arcanum = self.character.stats['rotes'][rote]['arcanum']
            skill = self.character.stats['rotes'][rote]['skill']

            current[1].setText(arcanum.title() + " (" + str(self.character.stats[arcanum]) + ")")
            current[2].setText(skill.title() + " (" + str(self.character.stats[skill]) + ")")

            # change skill formatting
            if skill in self.character.stats['rote skills']:
                current[2].setStyleSheet("QLabel {font: bold; font-size: 10pt}")
            else:
                current[2].setStyleSheet("QLabel {font-size: 10pt}")

            # update pool
            pool = self.calculate_pool(rote)
            current[3].setText(str(pool))

    def edit_entry(self, index=None):
        if not self.character.edit_mode:
            # View only
            current = self.rotes[index]
            current_title = current[0].text()
            current_tooltip = current[0].toolTip()

            # The labels are edited, so skill and arcanum taken from character's rote entry
            current_arcanum = self.character.stats['rotes'][current_title.lower()]['arcanum']
            current_skill = self.character.stats['rotes'][current_title.lower()]['skill']
            basicUI.ViewDialogue("Rote",
                                 name = current_title,
                                 arcanum = current_arcanum.title(),
                                 skill = current_skill.title(),
                                 details = current_tooltip)
            return

        if not index:
            current_title = None
            # add new item if no index given
            rote, tooltip, skill, arcanum, ok = Rote_Dialog.get_input("Add Rote")

        else:
            # edit current item
            current = self.rotes[index]
            current_title = current[0].text()
            current_tooltip = current[0].toolTip()

            # The labels are edited, so skill and arcanum taken from character's rote entry
            current_arcanum = self.character.stats['rotes'][current_title.lower()]['arcanum']
            current_skill = self.character.stats['rotes'][current_title.lower()]['skill']

            rote, tooltip, skill, arcanum, ok = Rote_Dialog.get_input("Change Rote", title=current_title,
                                                                      tooltip=current_tooltip, skill=current_skill,
                                                                      arcanum=current_arcanum, edit=True)

        if not ok:
            # cancel pressed
            return

        if not current_title and rote in self.character.stats['rotes']:
            # add new but title already in use
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("Rote with this name already exists.")
            msg.setInformativeText("Please use unique name.")
            msg.setWindowTitle("Duplicate Name")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

        elif not current_title:
            # Only adds new if entry by that name does not exist yet
            # add entry on character object
            self.character.stats["rotes"][rote] = {'tooltip': tooltip,
                                                   'arcanum': arcanum,
                                                   'skill': skill}

            # create entry
            self.rotes[self.row] = []
            # spellname
            button = QPushButton(rote.title())
            button.setToolTip(tooltip)
            button.setStyleSheet("QPushButton {font: 10pt; border: none}")
            button.setCursor(QCursor(Qt.WhatsThisCursor))
            self.rotes[self.row].append(button)
            self.edit_buttons.addButton(button, self.row)

            # primary arcanum
            arcanum_label = QLabel(arcanum.title() + " (" + str(self.character.stats[arcanum]) + ")")
            arcanum_label.setStyleSheet("QLabel {font: 10pt}")
            self.rotes[self.row].append(arcanum_label)

            # rote skill
            skill_label = QLabel(skill.title() + " (" + str(self.character.stats[skill]) + ")")
            # check for rote skill
            if skill in self.character.stats['rote skills']:
                skill_label.setStyleSheet("QLabel {font: bold; font-size: 10pt}")
            else:
                skill_label.setStyleSheet("QLabel {font-size: 10pt}")

            self.rotes[self.row].append(skill_label)

            # pool
            pool = self.calculate_pool(rote)
            pool_label = QLabel(str(pool))
            pool_label.setStyleSheet("QLabel {font: 10pt}")
            self.rotes[self.row].append(pool_label)

            self.grid.addWidget(button, self.row, 0)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(arcanum_label, self.row, 1)
            self.grid.setAlignment(arcanum_label, Qt.AlignHCenter)
            self.grid.addWidget(skill_label, self.row, 2)
            self.grid.setAlignment(skill_label, Qt.AlignHCenter)
            self.grid.addWidget(pool_label, self.row, 3)
            self.grid.setAlignment(pool_label, Qt.AlignHCenter)

            # remove the add new button
            self.grid.removeWidget(self.new_button)

            # add the new widgets
            self.grid.addWidget(button, self.row, 0)
            self.grid.setAlignment(button, Qt.AlignHCenter)
            self.grid.addWidget(arcanum_label, self.row, 1)
            self.grid.setAlignment(arcanum_label, Qt.AlignHCenter)
            self.grid.addWidget(skill_label, self.row, 2)
            self.grid.setAlignment(skill_label, Qt.AlignHCenter)
            self.grid.addWidget(pool_label, self.row, 3)
            self.grid.setAlignment(pool_label, Qt.AlignHCenter)

            # add 1 to self.row
            self.row += 1

            # add the new button back to end
            self.grid.addWidget(self.new_button, self.row, 0)


        elif "####delete####" in rote:
            # delete chosen
            # remove stat widget
            for widget in self.rotes[index]:
                self.grid.removeWidget(widget)
                sip.delete(widget)

            # remove associated data
            del self.character.stats["rotes"][current_title.lower()]
            del self.rotes[index]

        else:
            # Update character object
            self.character.stats["rotes"][rote] = {'tooltip': tooltip,
                                                   'arcanum': arcanum,
                                                   'skill': skill}

            # Update existing entry
            current[0].setToolTip(tooltip)
            current[1].setText(arcanum.title() + " (" + str(self.character.stats[arcanum]) + ")")
            current[2].setText(skill.title() + " (" + str(self.character.stats[skill]) + ")")

            # change skill formatting
            if skill in self.character.stats['rote skills']:
                current[2].setStyleSheet("QLabel {font: bold; font-size: 10pt}")
            else:
                current[2].setStyleSheet("QLabel {font-size: 10pt}")

            # update pool
            pool = self.calculate_pool(rote)
            current[3].setText(str(pool))


class Rote_Dialog(QDialog):
    '''
    Dialog for entering/changing labels with tooltips
    '''

    def __init__(self, wintitle, title='', tooltip='', skill='', arcanum='', edit=False):
        super().__init__()
        self.setWindowTitle(wintitle)
        self.title = title
        self.tooltip = tooltip
        self.skill = skill
        self.arcanum = arcanum
        self.edit = edit

        self.initUI()
        # self.setMaximumSize(20,20)

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.title_label = QLabel("Name:")
        self.title_entry = QLineEdit()
        self.title_entry.insert(self.title)

        self.tooltip_label = QLabel("Tooltip:")
        self.tooltip_entry = QTextEdit()
        self.tooltip_entry.setText(self.tooltip)

        self.arcanum_label = QLabel("Primary Arcanum:")
        self.arcanum_entry = QComboBox()
        for arcanum in sorted(mageUI.ARCANA):
            self.arcanum_entry.addItem(arcanum.title())

        if self.arcanum:
            self.arcanum_entry.setCurrentText(self.arcanum.title())

        self.skill_label = QLabel("Skill:")
        self.skill_entry = QComboBox()
        for skill in sorted(stats.SKILLS):
            self.skill_entry.addItem(skill.title())

        if self.skill:
            self.skill_entry.setCurrentText(self.skill.title())

        if self.edit:
            # add delete button and disable title box if editing
            self.title_entry.setDisabled(self.edit)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Discard,
                                         Qt.Horizontal, self)
            buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.del_item)
            buttonBox.button(QDialogButtonBox.Discard).setText("Delete")

        else:
            # adding new or viewing - only okay and cancel button
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.grid.addWidget(self.title_label, 0, 0)
        self.grid.addWidget(self.title_entry, 0, 1)

        self.grid.addWidget(self.arcanum_label, 1, 0)
        self.grid.addWidget(self.arcanum_entry, 1, 1)

        self.grid.addWidget(self.skill_label, 2, 0)
        self.grid.addWidget(self.skill_entry, 2, 1)

        self.grid.addWidget(self.tooltip_label, 3, 0)
        self.grid.setAlignment(self.tooltip_label, Qt.AlignTop)
        self.grid.addWidget(self.tooltip_entry, 3, 1)
        self.grid.addWidget(buttonBox, 4, 1)

    def del_item(self):
        '''
        Handler for delete item action.
        Sends an accept signal but adds a delete flag to output
        '''

        self.title_entry.insert("####delete####")
        self.accept()

    def get_input(wintitle, title='', tooltip='', skill='', arcanum='', edit=False):
        '''
        Used to open a dialog window to enter details of label.
        '''
        dialog = Rote_Dialog(wintitle, title, tooltip, skill, arcanum, edit)
        result = dialog.exec_()
        return (
        dialog.title_entry.text().lower(), dialog.tooltip_entry.toPlainText(), dialog.skill_entry.currentText().lower(),
        dialog.arcanum_entry.currentText().lower(), result == QDialog.Accepted)
