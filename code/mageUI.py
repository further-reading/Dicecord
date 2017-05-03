# Chronicles of Darkness Mage Inventory Sheet UI created for use in conjunction with Dicecord.
#   Copyright (C) 2017  Roy Healy

import stats
import sip
import basicUI
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from xml.dom import minidom
from xml.etree.ElementTree import Element
from xml.etree import ElementTree as etree

# mage powers

ARCANA = ['death',
          'fate',
          'forces',
          'life',
          'matter',
          'mind',
          'prime',
          'spirit',
          'space',
          'time']

# Mage sheet headers

HEADERS = [['shadow name', 'user id', 'webhook'],
           ['concept','virtue','vice'],
           ['path', 'order', 'legacy']]

# make default mage
DEFAULT = {}
for stat in stats.STATS.copy():
    DEFAULT[stat] = stats.STATS[stat]
for arcana in ARCANA:
    DEFAULT[arcana] = 0
for skill in stats.SKILLS:
    DEFAULT[skill] = 0
for attribute in stats.ATTRIBUTES:
    DEFAULT[attribute] = 1
for col in HEADERS:
    for header in col:
        DEFAULT[header] = ''

DEFAULT['gnosis'] = 1
DEFAULT['wisdom'] = 7
DEFAULT['mana spent'] = 0
DEFAULT['rote skills'] = set([])
DEFAULT['obsessions'] = {}
DEFAULT['rotes'] = {}
DEFAULT['nimbus'] = ''
DEFAULT['magtool'] = {}
DEFAULT['praxes'] = {}
DEFAULT['attainments'] = {}
DEFAULT['active spells'] = {}
DEFAULT['ench items'] = {}
DEFAULT['arcane beats'] = 0
DEFAULT['arcane xp'] = 0

# remove dark era stats
del DEFAULT['enigmas']
del DEFAULT['ride']
del DEFAULT['archery']

# default messaging
goodMessages = ["The Lie cannot withstand your will, [userID]!",
                    "Reality is yours to command, [userID]!",
                    "You should take the beat, [userID].",
                    "Aren't I a good bot, [userID]?",
                    "[userID] is a conduit to the supernal!",
                    "Did you hack me, [userID]?",
                    "[userID], if you were still a sleeper the majesty of this action would have awoken you!"]
badMessages = ["[userID]'s nimbus looks like a wet dishrag.",
                   "The lie constricts your potential, [userID].",
                   "Don't blame your bad luck on me, [userID]! I'm just a random number generator.",
                   "That was just a practice roll, right [userID]?",
                   "[userID] rolls like a diary farmer.",
                   "Ask for a dramatic failure [userID], you know you want to!",
                   "[userID], I hope that wasn't an important roll ...",
                   "[userID]'s watchtower called out to the wrong soul."]

# mana update
def update_mana(character):
    if character.stats['gnosis'] < 5:
        character.stats['mana'] = 9 + character.stats['gnosis']
    elif character.stats['gnosis'] <= 8:
        character.stats['mana'] = 15 + 5 * (character.stats['gnosis'] - 5)
    elif character.stats['gnosis'] == 9:
        character.stats['mana'] = 50
    else:
        character.stats['mana'] = 75

# mage sheet UI
class StatsSheet(QWidget):
    '''
    Overall character sheet object
    '''

    def __init__(self, character):
        super().__init__()
        self.setStyleSheet("QPushButton:pressed { background-color: white }")
        self.character = character
        self.character.update_derivitives()
        self.character.edit_mode = False
        self.initUI()

    def initUI(self):
        # each section constructed as dedicated object
        self.char_info = basicUI.Character_Info(self.character, HEADERS)

        # attributes
        # attributes aren't part of basicUI to ensure proper sorting
        self.attributes_label = QLabel("=====ATTRIBUTES=====")
        self.attributes_label.setStyleSheet("QLabel { font: 13pt }")
        self.attributes_label.setAlignment(Qt.AlignCenter)
        self.attribute_mental_group = stats.ATTRIBUTE_TYPE['mental']
        self.attribute_physical_group = stats.ATTRIBUTE_TYPE['physical']
        self.attribute_social_group = stats.ATTRIBUTE_TYPE['social']

        self.attribute_mental = basicUI.Stat_Col(self.attribute_mental_group, self.character)
        self.attribute_physical = basicUI.Stat_Col(self.attribute_physical_group, self.character)
        self.attribute_social = basicUI.Stat_Col(self.attribute_social_group, self.character)

        # skills
        self.skills = basicUI.Skills(self.character)

        # arcana
        self.arcana = Arcana(self.character)

        # merits
        self.merits = basicUI.StatWithTooltip(self.character, 'merits')

        # mana
        self.mana = Mana(self.character)

        # advantages
        self.derivitives = basicUI.Derivitives(self.character)

        # Health
        self.health = basicUI.Health(self.character)

        # Willpower
        self.willpower = basicUI.Willpower(self.character)

        # Gnosis
        gnosis = basicUI.Stat(self.character, 'gnosis', maximum=10, small=False)
        gnosis.setMaximumSize(gnosis.sizeHint())

        # Wisdom
        wisdom = basicUI.Stat(self.character, 'wisdom', maximum=10, small=False)

        # Conditions
        self.conditions = basicUI.Hover_Label_Col("CONDITIONS", self.character, 'conditions')

        # Aspirations
        self.aspirations = basicUI.Hover_Label_Col("ASPIRATIONS", self.character, 'aspirations')

        # Obsessions
        self.obsessions = basicUI.Hover_Label_Col("OBSESSIONS", self.character, 'obsessions')

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setAlignment(Qt.AlignTop)

        # top
        grid.addWidget(self.char_info, 1, 0, 1, 3)
        grid.addWidget(self.attributes_label, 2, 0, 1, 3)

        # left side
        grid.addWidget(self.attribute_mental, 3, 0)
        grid.addWidget(self.skills, 4, 0, 3, 1)
        grid.setAlignment(self.skills, Qt.AlignTop)

        # middle
        grid.addWidget(self.attribute_physical, 3, 1)
        grid.addWidget(self.arcana, 4, 1)
        grid.addWidget(self.merits, 5, 1)
        grid.setAlignment(self.merits, Qt.AlignHCenter)
        grid.addWidget(self.derivitives, 6, 1)
        grid.setAlignment(self.derivitives, Qt.AlignBottom)

        # right
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

        grid.addLayout(last_col, 3, 2, 4, 1)
        grid.setAlignment(last_col, Qt.AlignTop)

    def edit_toggle(self):
        # toggle edit mode on relevant stats
        self.merits.edit_toggle()
        self.obsessions.edit_toggle()
        self.aspirations.edit_toggle()
        self.char_info.edit_toggle()

        if not self.character.edit_mode:
            # apply changes
            self.character.update_derivitives()
            self.derivitives.update_all()
            self.willpower.update_willpower()
            self.health.update_max()
            self.mana.update_mana()


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
        box.setContentsMargins(0, 0, 0, 0)
        self.setLayout(box)

        overall_label = QLabel("===ARCANA===")
        overall_label.setAlignment(Qt.AlignCenter)

        self.arcana = basicUI.Stat_Col(ARCANA, self.character)

        box.setAlignment(Qt.AlignTop)
        box.addWidget(overall_label)
        box.addWidget(self.arcana)


class Mana(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()
        self.setMaximumSize(self.sizeHint())

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
        self.grid.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # Overall
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
        # base label
        self.base_label = QLabel("Base : ")

        # base spent
        self.spent = QSpinBox()
        self.spent.setValue(int(self.character.stats['mana spent'])) # imported as str
        self.spent.setMaximumSize(QSize(35, 20))
        self.spent.setMaximum(int(self.character.stats['mana'])) # imported as str
        self.spent.valueChanged.connect(self.update_mana)

        # base current
        current_num = int(self.character.stats['mana']) - int(self.character.stats['mana spent']) # imported as str
        self.current = basicUI.Num_with_Line(str(current_num) + "/" + str(self.character.stats['mana']))

        self.grid.addWidget(self.base_label, 2, 0)
        self.grid.setAlignment(self.base_label, Qt.AlignRight)
        self.grid.addWidget(self.spent, 2, 1)
        self.grid.addWidget(self.current, 2, 2)

        # enchanted items
        self.ench_items = {}
        self.update_ench_items()

    def update_ench_items(self):
        keys = list(self.ench_items.keys())
        for item in keys:
            widgets = self.ench_items[item]
            name = widgets[0]
            # remove all from UI,remove from dict and delete
            for widget in widgets[1:]:
                self.grid.removeWidget(widget)
                sip.delete(widget)

            # remove associated data
            del self.ench_items[item]

        self.row = 3
        # add back in
        for item in self.character.stats['ench items']:
            self.ench_items[self.row] = [item]
            total_mana = int(self.character.stats['ench items'][item]['mana'])
            spent_mana = int(self.character.stats['ench items'][item]['mana spent'])
            item_type = self.character.stats['ench items'][item]['type']

            # label
            label = QLabel(item.title() + "(" + item_type.title() + ") :")
            self.ench_items[self.row].append(label)

            # spent
            spent = QSpinBox()
            spent.setValue(spent_mana)
            spent.setMaximumSize(QSize(35, 20))
            spent.setMaximum(total_mana)
            spent.valueChanged.connect(self.update_mana)
            self.ench_items[self.row].append(spent)

            # current
            current_num = total_mana - spent_mana
            current = basicUI.Num_with_Line(str(current_num) + "/" + str(total_mana))
            self.ench_items[self.row].append(current)

            # add to grid
            self.grid.addWidget(label, self.row, 0)
            self.grid.setAlignment(label, Qt.AlignRight)
            self.grid.addWidget(spent, self.row, 1)
            self.grid.addWidget(current, self.row, 2)
            self.row += 1

    def update_mana(self):
        # base change
        self.character.stats['mana spent'] = self.spent.value()
        self.spent.setMaximum(self.character.stats['mana'])

        current_num = self.character.stats['mana'] - self.character.stats['mana spent']
        self.current.change_text(str(current_num) + "/" + str(self.character.stats['mana']))

        # rest changed
        for item in self.ench_items:
            name = self.ench_items[item][0]
            spent_widget = self.ench_items[item][2]
            current_widget = self.ench_items[item][3]

            # update character object
            self.character.stats['ench items'][name]['mana spent'] = spent_widget.value()

            # update current display
            current_num = int(self.character.stats['ench items'][name]['mana']) - spent_widget.value() # imported as str
            current_widget.change_text(str(current_num) + "/" + str(self.character.stats['ench items'][name]['mana']))


def from_xml(cls, dom):
    '''
    Create a stats dicts from XML
    :param dom: Appropiate XML object
    :return: Stats dict
    '''

    notes = dom.find('notes')
    goodMessages = dom.findall('goodmessage')
    badMessages = dom.findall('badmessage')
    goodRate = dom.find('badrate')
    badRate = dom.find('goodrate')

    skills = dom.findall('skill')
    merits = dom.findall('merit')
    health = dom.find('health')
    weapons = dom.findall('weapon')
    praxes = dom.findall('praxis')
    rotes = dom.findall('rote')
    others = dom.findall('other')
    ench_items = dom.findall('enchitem')

    input_stats = {}
    input_stats['merits'] = {}
    input_stats['skill specialties'] = {}
    input_stats['rote skills'] = set([])
    input_stats['rotes'] = {}
    input_stats['health'] = [0, 0, 0, 0]
    input_stats['ench items'] = {}
    input_stats['praxes'] = {}
    input_stats['weapons'] = {}
    specials = ['conditions', 'aspirations', 'obsessions', 'active spells', 'attainments', 'magtool']

    for item in ench_items:
        name = item.find('name').text
        item_type = item.find('item_type').text

        if item.find('tooltip') != None:
            tooltip = item.find('tooltip').text
        else:
            tooltip = ''

        rating = item.find('rating').text
        mana = item.find('mana').text
        mana_spent = item.find('mana_spent').text

        input_stats['ench items'][name] = {'type': item_type,
                                           'tooltip': tooltip,
                                           'rating': int(rating),
                                           'mana': int(mana),
                                           'mana spent': int(mana_spent)}

    for weapon in weapons:
        name = weapon.find('name').text
        damage = weapon.find('damage').text
        if weapon.find('range') != None:
            weapon_range = weapon.find('range').text
        else:
            weapon_range = ''
        clip = weapon.find('clip').text
        init = weapon.find('init').text
        strength = weapon.find('str').text
        size = weapon.find('size').text

        input_stats['weapons'][name] = {'damage': int(damage),
                                        'range': weapon_range,
                                        'clip': int(clip),
                                        'init': int(init),
                                        'str': int(strength),
                                        'size': int(size)}

    for skill in skills:
        name = skill.find('name').text
        rating = skill.find('rating').text
        input_stats[name] = int(rating)

        if skill.find('tooltip') != None:
            tooltip = skill.find('tooltip').text
            input_stats['skill specialties'][name] = tooltip

        if skill.find('rote') != None:
            input_stats['rote skills'].add(name)

    for merit in merits:
        name = merit.find('name').text
        rating = merit.find('rating').text
        input_stats['merits'][name] = {'rating':int(rating), 'tooltip':''}

        if merit.find('tooltip') != None:
            tooltip = merit.find('tooltip').text
            input_stats['merits'][name]['tooltip'] = tooltip

    dam_type = 1
    for damage in ['bashing', 'lethal', 'agg']:
        amount = int(health.find(damage).text)
        input_stats['health'][dam_type] = amount
        dam_type += 1

    for entry in specials:
        input_stats[entry] = {}
        leaf = dom.find(entry)
        if leaf != None:
            items = leaf.findall('entry')
            for item in items:
                name = item.find('name').text
                if item.find('tooltip') != None:
                    tooltip = item.find('tooltip').text
                else:
                    tooltip = ''

                input_stats[entry][name] = tooltip

    for praxis in praxes:
        name = praxis.find('name').text
        arcanum = praxis.find('arcanum').text

        if praxis.find('tooltip') != None:
            tooltip = praxis.find('tooltip').text
        else:
            tooltip = ""

        input_stats['praxes'][name] = {'tooltip': tooltip, 'arcanum': arcanum}

    for rote in rotes:
        name = rote.find('name').text
        tooltip = rote.find('tooltip').text
        arcanum = rote.find('arcanum').text
        skill = rote.find('skill').text

        if tooltip == None:
            # happens when tooltip is blank
            tooltip = ''

        input_stats['rotes'][name] = {'tooltip': tooltip,
                                      'arcanum': arcanum,
                                      'skill': skill}

    for other in others:
        name = other.find('name').text
        rating = other.find('rating').text
        if rating == None:
            # happens only for blank string inputs
            input_stats[name] = ''
        elif rating.isdigit() and name != 'user id':
            # numbers, but not user id
            input_stats[name] = int(rating)
        else:
            # string input
            input_stats[name] = rating

    input_goodMessages = []
    input_badMessages = []

    if notes == None:
        input_notes = ''
    else:
        input_notes = notes.find('content').text

    if goodMessages:
        for message in goodMessages:
            mess = message.find('message').text
            input_goodMessages.append(mess)
    else:
        # this happens is xml is v1.00
        input_goodMessages = mageUI.goodMessages

    if badMessages:
        for message in badMessages:
            mess = message.find('message').text
            input_badMessages.append(mess)
    else:
        # this happens is xml is v1.00
        input_badMessages = mageUI.badMessages

    if goodRate != None:
        input_goodRate = int(goodRate.text)
    else:
        # this happens is xml is v1.00
        input_goodRate = 100

    if badRate != None:
        input_badRate = int(badRate.text)
    else:
        # this happens is xml is v1.00
        input_badRate = 50

    return cls(stats = input_stats,
               goodMessages = input_goodMessages,
               badMessages = input_badMessages,
               goodrate = input_goodRate,
               badrate = input_badRate,
               notes = input_notes,
               splat = 'mage')
