# Chronicles of Darkness Mage Inventory Sheet UI created for use in conjunction with Dicecord.
#   Copyright (C) 2017  Roy Healy

import stats
import basicUI
import player
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from xml.dom import minidom
from xml.etree.ElementTree import Element
from xml.etree import ElementTree as etree
import sys

# Vampire sheet headers

HEADERS = [['name', 'user id', 'webhook'],
           ['mask','dirge','concept'],
           ['clan', 'bloodline', 'covenant']]

# make default vampire
DEFAULT = {}
for stat in stats.STATS.copy():
    DEFAULT[stat] = stats.STATS[stat]
for skill in stats.SKILLS:
    DEFAULT[skill] = 0
for attribute in stats.ATTRIBUTES:
    DEFAULT[attribute] = 0
for col in HEADERS:
    for header in col:
        DEFAULT[header] = ''

DEFAULT['blood'] = 1
DEFAULT['humanity'] = 7
DEFAULT['vitae spent'] = 0
DEFAULT['banes'] = {}

# remove dark era stats
del DEFAULT['enigmas']
del DEFAULT['ride']
del DEFAULT['archery']

# default messaging
goodMessages = ["You should take the beat, [userID].",
                "Aren't I a good bot, [userID]?",
                "Did you hack me, [userID]?"]
badMessages = ["Don't blame your bad luck on me, [userID]! I'm just a random number generator.",
               "That was just a practice roll, right [userID]?",
               "[userID] rolls like a diary farmer.",
               "Ask for a dramatic failure [userID], you know you want to!",
               "[userID], I hope that wasn't an important roll ...",
               "[userID] puts the suck in bloodsucker!"]

# vitae update
def update_vitae(character):
    pass

# vampire sheet UI
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

        # disciplines

        # merits
        self.merits = basicUI.Merits(self.character)

        # advantages
        self.derivitives = basicUI.Derivitives(self.character)

        # Health
        self.health = basicUI.Health(self.character)

        # Willpower
        self.willpower = basicUI.Willpower(self.character)

        # Blood
        self.blood = basicUI.Stat(self.character, 'blood', maximum=10, small=False)
        self.blood.setMaximumSize(self.blood.sizeHint())

        # Humanity

        # Aspirations
        self.aspirations = basicUI.Hover_Label_Col("ASPIRATIONS", self.character, 'aspirations')

        # Banes
        self.banes = basicUI.Hover_Label_Col("BANES", self.character, 'banes')

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setAlignment(Qt.AlignTop)

        # top
        grid.addWidget(self.char_info, 1, 0, 1, 3)
        grid.addWidget(self.attributes_label, 2, 0, 1, 3)

        # left side
        grid.addWidget(self.attribute_mental, 3, 0)
        grid.addWidget(self.skills, 4, 0, 4, 1)
        grid.setAlignment(self.skills, Qt.AlignTop)

        # middle
        grid.addWidget(self.attribute_physical, 3, 1)
        #grid.addWidget(self.arcana, 4, 1)
        grid.addWidget(self.merits, 5, 1)
        grid.setAlignment(self.merits, Qt.AlignHCenter)
        grid.addWidget(self.aspirations, 6, 1)
        grid.addWidget(self.banes, 7, 1)

        # right
        last_col = QVBoxLayout()
        last_col.addWidget(self.attribute_social)
        last_col.addWidget(self.health)
        last_col.addWidget(self.willpower)
        last_col.setAlignment(self.willpower, Qt.AlignHCenter)
        last_col.addWidget(self.blood)
        last_col.setAlignment(self.blood, Qt.AlignHCenter)
        #last_col.addWidget(wisdom)
        #last_col.setAlignment(wisdom, Qt.AlignHCenter)
        #last_col.addWidget(self.mana)
        #last_col.setAlignment(self.mana, Qt.AlignHCenter)
        last_col.addWidget(self.derivitives)

        grid.addLayout(last_col, 3, 2, 4, 1)
        grid.setAlignment(last_col, Qt.AlignTop)

    def edit_toggle(self):
        # toggle edit mode on relevant stats
        self.merits.edit_toggle()
        self.banes.edit_toggle()
        self.aspirations.edit_toggle()
        self.char_info.edit_toggle()

        if not self.character.edit_mode:
            # apply changes
            self.character.update_derivitives()
            self.derivitives.update_all()
            self.willpower.update()
            self.health.update_max()


class Vitae(QWidget):
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
        self.overall_label = QLabel("===VITAE===")
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
        self.spent.setValue(self.character.stats['mana spent'])
        self.spent.setMaximumSize(QSize(35, 20))
        self.spent.setMaximum(self.character.stats['mana'])
        self.spent.valueChanged.connect(self.update_mana)

        # base current
        current_num = self.character.stats['mana'] - self.character.stats['mana spent']
        self.current = basicUI.Num_with_Line(str(current_num) + "/" + str(self.character.stats['mana']))

        self.grid.addWidget(self.base_label, 2, 0)
        self.grid.setAlignment(self.base_label, Qt.AlignRight)
        self.grid.addWidget(self.spent, 2, 1)
        self.grid.addWidget(self.current, 2, 2)

    def update_vitae(self):
        # base change
        self.character.stats['vitae spent'] = self.spent.value()
        self.spent.setMaximum(self.character.stats['vitae'])

        current_num = self.character.stats['vitae'] - self.character.stats['vitae spent']
        self.current.change_text(str(current_num) + "/" + str(self.character.stats['vitae']))

def save_xml(character, path):
    pass
    # CHANGE
    '''
    Save mage as xml
    :param character: Character object
    :param path: Path to save file
    :return: None
    '''
    root = Element('root')

    # notes
    if character.notes != '':
        item = Element('notes')
        root.append(item)

        content = Element('content')
        item.append(content)
        content.text = character.notes

    # splat
    item = Element('splat')
    root.append(item)
    item.text = character.splat

    for stat in character.stats:
        # skills
        if stat in stats.SKILLS:
            item = Element('skill')
            root.append(item)

            name = Element('name')
            item.append(name)
            name.text = stat

            rating = Element('rating')
            item.append(rating)
            rating.text = str(character.stats[stat])

            if stat in character.stats['skill specialties']:
                # record specialties
                tooltip = Element('tooltip')
                item.append(tooltip)
                tooltip.text = character.stats['skill specialties'][stat]

            if stat in character.stats['rote skills']:
                rote = Element('rote')
                item.append(rote)
                rote.text = "True"

        # merits
        elif stat == 'merits':
            for merit in character.stats['merits']:
                item = Element('merit')
                root.append(item)

                name = Element('name')
                item.append(name)
                name.text = merit

                rating = Element('rating')
                item.append(rating)
                rating.text = str(character.stats['merits'][merit])

                if merit in character.stats['merit details']:
                    tooltip = Element('tooltip')
                    item.append(tooltip)
                    tooltip.text = character.stats['merit details'][merit]

        elif stat in ('skill specialties', 'merit details', 'rote skills'):
            # skip these - added when associated merit/skill added
            pass

        # labels and tooltips
        elif stat in ('conditions', 'aspirations', 'obsessions', 'active spells', 'attainments', 'magtool'):
            if character.stats[stat] != {}:
                item = Element(stat)
                root.append(item)

                for entry in character.stats[stat]:
                    leaf = Element('entry')
                    name = Element('name')
                    leaf.append(name)
                    name.text = entry

                    if character.stats[stat][entry] != '':
                        tooltip = Element('tooltip')
                        leaf.append(tooltip)
                        tooltip.text = character.stats[stat][entry]

                    item.append(leaf)

        # any other stat but health, praxes, rote, weapons or enchanted items
        elif stat not in ('health', 'rotes', 'ench items', 'praxes', 'weapons'):
            item = Element('other')
            root.append(item)

            name = Element('name')
            item.append(name)
            name.text = stat

            rating = Element('rating')
            item.append(rating)

            # note, this can be strings or numbers
            rating.text = str(character.stats[stat])

        elif stat == 'weapons':
            if character.stats['weapons'] != {}:
                for weapon in character.stats['weapons']:
                    item = Element('weapon')
                    root.append(item)

                    name = Element('name')
                    item.append(name)
                    name.text = weapon

                    details = character.stats['weapons'][weapon]

                    for detail in details:
                        # loop over dict, skip blank entries
                        if details[detail] != '':
                            entry = Element(detail)
                            item.append(entry)
                            entry.text = str(details[detail])

        elif stat == 'praxes':
            if character.stats['praxes'] != {}:
                for praxis in character.stats['praxes']:
                    item = Element('praxis')
                    root.append(item)

                    name = Element('name')
                    item.append(name)
                    name.text = praxis.replace('’', "'")

                    if character.stats['praxes'][praxis]['tooltip'] != '':
                        tooltip = Element('tooltip')
                        item.append(tooltip)
                        tooltip.text = character.stats['praxes'][praxis]['tooltip']

                    arcanum = Element('arcanum')
                    item.append(arcanum)
                    arcanum.text = character.stats['praxes'][praxis]['arcanum']


        elif stat == 'rotes':
            for rote in character.stats['rotes']:
                item = Element('rote')
                root.append(item)
                content = character.stats['rotes'][rote]

                name = Element('name')
                item.append(name)
                name.text = rote.replace('’', "'")

                if content[0] != '':
                    tooltip = Element('tooltip')
                    item.append(tooltip)
                    tooltip.text = content[0]

                arcanum = Element('arcanum')
                item.append(arcanum)
                arcanum.text = content[1]

                skill = Element('skill')
                item.append(skill)
                skill.text = content[2]

        # health
        elif stat == 'health':
            health = character.stats['health']
            item = Element('health')
            root.append(item)

            bashing = Element('bashing')
            lethal = Element('lethal')
            agg = Element('agg')

            # max ignored since it is derived
            bashing.text = str(health[1])
            lethal.text = str(health[2])
            agg.text = str(health[3])

            item.append(bashing)
            item.append(lethal)
            item.append(agg)

        elif stat == 'ench items':
            for name in character.stats['ench items']:
                item = Element('enchitem')
                root.append(item)

                content = character.stats['ench items'][name]
                item_name = Element('name')
                item_type = Element('item_type')
                tooltip = Element('tooltip')
                rating = Element('rating')
                mana = Element('mana')
                mana_spent = Element('mana_spent')

                item_name.text = name
                item_type.text = content[0]
                tooltip.text = content[1]
                rating.text = str(content[2])
                mana.text = str(content[3])
                mana_spent.text = str(content[4])

                item.append(item_name)
                item.append(item_type)
                item.append(tooltip)
                item.append(rating)
                item.append(mana)
                item.append(mana_spent)

    # Personality
    for message in character.goodMessages:
        item = Element('goodmessage')
        root.append(item)

        mess = Element('message')
        item.append(mess)
        mess.text = message

    for message in character.badMessages:
        item = Element('badmessage')
        root.append(item)

        mess = Element('message')
        item.append(mess)
        mess.text = message

    item = Element('badrate')
    root.append(item)
    item.text = str(character.badRate)

    item = Element('goodrate')
    root.append(item)
    item.text = str(character.goodRate)

    # write file
    rough_string = etree.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    text = reparsed.toprettyxml(indent="  ")

    # used to remove ’ style apostrophes that cause crashes when reading the file
    text = text.replace('’', "'")

    f = open(path, 'w')
    f.write(text)
    f.close()

def from_xml(dom):
    pass
    # CHANGE
    '''
    Create a stats dicts from XML
    :param dom: Appropiate XML object
    :return: Stats dict
    '''

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
    input_stats['merit details'] = {}
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

        input_stats['ench items'][name] = [item_type, tooltip, int(rating), int(mana), int(mana_spent)]

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
        input_stats['merits'][name] = int(rating)

        if merit.find('tooltip') != None:
            tooltip = merit.find('tooltip').text
            input_stats['merit details'][name] = tooltip

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

        input_stats['rotes'][name] = [tooltip, arcanum, skill]

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

    return input_stats

if __name__ == '__main__':
    app = QApplication(sys.argv)
    char = player.Character(splat = 'vampire')
    test = StatsSheet(char)
    test.show()
    sys.exit(app.exec_())
