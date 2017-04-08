# Chronicles of Darkness Mage Inventory Sheet UI created for use in conjunction with Dicecord.
#   Copyright (C) 2017  Roy Healy

import stats
import basicUI
import player
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
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
DEFAULT['humanity'] = {'rating': 7}
DEFAULT['vitae spent'] = 0
DEFAULT['banes'] = {}
DEFAULT['disciplines'] = {}
DEFAULT['languages'] = {}
DEFAULT['history'] = ""
DEFAULT['other traits'] = {}
DEFAULT['description'] = ''
DEFAULT['age'] = ''
DEFAULT['apparant age'] = ''
DEFAULT['sex'] = ''
DEFAULT['race'] = ''
DEFAULT['hair'] = ''
DEFAULT['eyes'] = ''
DEFAULT['height'] = ''
DEFAULT['weight'] = ''
DEFAULT['rites or miracles'] = {}
DEFAULT['equipment'] = {}

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
    if character.stats['blood'] == 0:
        character.stats['vitae'] = character.stats['stamina']
    elif character.stats['blood'] < 5:
        character.stats['vitae'] = 9 + character.stats['blood']
    elif character.stats['blood'] <= 8:
        character.stats['vitae'] = 15 + 5 * (character.stats['blood'] - 5)
    elif character.stats['blood'] == 9:
        character.stats['vitae'] = 50
    else:
        character.stats['vitae'] = 75

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
        self.disciplines = basicUI.StatWithTooltip(self.character, 'disciplines')

        # merits
        self.merits = basicUI.StatWithTooltip(self.character, 'merits')

        # advantages
        self.derivitives = basicUI.Derivitives(self.character)

        # Health
        self.health = basicUI.Health(self.character)

        # Willpower
        self.willpower = basicUI.Willpower(self.character)

        # Blood
        self.blood = basicUI.Stat(self.character, 'blood', maximum=10, small=False)
        self.blood.setMaximumSize(self.blood.sizeHint())

        # Vitae
        self.vitae = Vitae(self.character)

        # Humanity
        humanitylabel = QLabel('===HUMANITY===')
        humanitylabel.setStyleSheet("QLabel { font: 13pt}")
        self.humanity = Humanity(self.character)

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
        grid.addWidget(self.skills, 4, 0, 5, 1)
        grid.setAlignment(self.skills, Qt.AlignTop)

        # middle
        grid.addWidget(self.attribute_physical, 3, 1)
        grid.addWidget(self.disciplines, 4, 1)
        grid.addWidget(self.merits, 5, 1)
        grid.setAlignment(self.merits, Qt.AlignHCenter)
        grid.addWidget(self.aspirations, 6, 1)
        grid.addWidget(self.banes, 7, 1)
        grid.addWidget(self.derivitives, 8, 1)

        # right
        grid.addWidget(self.attribute_social, 3, 2)

        last_col = QVBoxLayout()
        last_col.addWidget(self.health)
        last_col.addWidget(self.willpower)
        last_col.setAlignment(self.willpower, Qt.AlignHCenter)
        last_col.addWidget(self.blood)
        last_col.setAlignment(self.blood, Qt.AlignHCenter)
        last_col.addWidget(self.vitae)
        last_col.setAlignment(self.vitae, Qt.AlignHCenter)
        last_col.addWidget(humanitylabel)
        last_col.setAlignment(humanitylabel, Qt.AlignHCenter)
        last_col.addWidget(self.humanity)
        last_col.setAlignment(self.humanity, Qt.AlignHCenter)

        grid.addLayout(last_col, 4, 2, 5, 1)
        grid.setAlignment(last_col, Qt.AlignTop)

        # edit button for testing
        # remove for dicecord merge
        editbutton = QPushButton("Edit")
        editbutton.clicked.connect(self.edit_toggle)
        grid.addWidget(editbutton, 0, 0)

    def edit_toggle(self):
        # toggle edit mode on relevant stats
        # remove first line when merging with dicecord
        self.character.edit_mode = not self.character.edit_mode
        self.merits.edit_toggle()
        self.disciplines.edit_toggle()
        self.banes.edit_toggle()
        self.aspirations.edit_toggle()
        self.char_info.edit_toggle()

        if not self.character.edit_mode:
            # apply changes
            self.character.update_derivitives()
            self.derivitives.update_all()
            self.willpower.update()
            self.health.update_max()

class Humanity(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):
        self.form = QFormLayout()
        self.setLayout(self.form)
        self.form.setSpacing(5)
        self.form.setContentsMargins(0, 0, 0, 0)

        self.widgets = {}
        self.dots = QButtonGroup()
        self.dots.buttonClicked[int].connect(self.edit_dots)

        self.derangements = QButtonGroup()
        self.derangements.buttonClicked[int].connect(self.edit_Derangement)
        
        for i in range(10, 0, -1):
          self.widgets[i] = {}

          # add numeric label
          self.widgets[i]['ratinglabel'] = QLabel(str(i))
          self.widgets[i]['ratinglabel'].setStyleSheet("QLabel { font: 12pt}")

          # add dot
          fillcheck = i <= self.character.stats['humanity']['rating']
          self.widgets[i]['dot'] = basicUI.Dot(filled = fillcheck)
          self.dots.addButton(self.widgets[i]['dot'],i)

          # add Derangement
          self.widgets[i]['label'] = basicUI.Lined_Button("")
          self.widgets[i]['label'].setCursor(QCursor(Qt.PointingHandCursor))
          
          self.derangements.addButton(self.widgets[i]['label'].button,i)

          # check for Derangement details
          if i in self.character.stats['humanity']:
              title = self.character.stats['humanity'][i]['title']
              tooltip = self.character.stats['humanity'][i]['tooltip']
              # recheck
              self.widgets[i]['label'].change_text(title)
              self.widgets[i]['label'].button.setToolTip(tooltip)

          # add to layout
          self.widgets[i]['boxdot'] = QHBoxLayout()
          self.widgets[i]['boxdot'].addWidget(self.widgets[i]['dot'])
          self.widgets[i]['boxdot'].addWidget(self.widgets[i]['label'])
          self.form.addRow(self.widgets[i]['ratinglabel'], self.widgets[i]['boxdot'])

    def edit_dots(self, value):

        # only runs on edit mode
        if not self.character.edit_mode:
            return
        
        self.character.stats['humanity']['rating'] = value
        for row in self.widgets:
            if row <= value:
                self.widgets[row]['dot'].filled = True
                
            else:
                self.widgets[row]['dot'].filled = False
                
            self.widgets[row]['dot'].select_Image()

    def edit_Derangement(self, index):
        # only runs on edit mode
        if not self.character.edit_mode:
            return
        
        # open dialog to enter text/tooltip
        current = self.widgets[index]['label']
        current_title = current.text
        current_tooltip = current.tooltip
        title, tooltip, ok = basicUI.Label_Tooltip_Dialog.get_input(title = current_title, tooltip = current_tooltip, edit = False, wintitle = "Edit Derangement")
        
        # change button text
        if not ok:
            return

        # update character object
        if title == '':
            # remove label and tooltip
            current.change_text()
            # remove associated data
            
            del self.character.stats['humanity'][index]
        
        else:
            # Update tooltip and label of existing entry
            new = {'title': title.title(), 'tooltip':tooltip}
            self.character.stats['humanity'][index] = new
            current.change_text(title.title(), tooltip)
        

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
        self.spent_label = QLabel("Spent")
        self.spent_label.setStyleSheet("QLabel {text-decoration: underline; font: 10pt}")
        self.current_label = QLabel("Current")
        self.current_label.setStyleSheet("QLabel {text-decoration: underline; font: 10pt}")

        self.grid.addWidget(self.overall_label, 0, 0, 1, 2)
        self.grid.setAlignment(self.overall_label, Qt.AlignHCenter)
        self.grid.addWidget(self.spent_label, 1, 0)
        self.grid.setAlignment(self.spent_label, Qt.AlignHCenter)
        self.grid.addWidget(self.current_label, 1, 1)
        self.grid.setAlignment(self.current_label, Qt.AlignHCenter)

        # base spent
        self.spent = QSpinBox()
        self.spent.setValue(self.character.stats['vitae spent'])
        self.spent.setMaximumSize(QSize(35, 20))
        self.spent.setMaximum(self.character.stats['vitae'])
        self.spent.valueChanged.connect(self.update_vitae)

        # base current
        current_num = self.character.stats['vitae'] - self.character.stats['vitae spent']
        self.current = basicUI.Num_with_Line(str(current_num) + "/" + str(self.character.stats['vitae']))

        self.grid.addWidget(self.spent, 2, 0)
        self.grid.setAlignment(self.spent, Qt.AlignHCenter)
        self.grid.addWidget(self.current, 2, 1)
        self.grid.setAlignment(self.current, Qt.AlignHCenter)

    def update_vitae(self):
        # base change
        self.character.stats['vitae spent'] = self.spent.value()
        self.spent.setMaximum(self.character.stats['vitae'])

        current_num = self.character.stats['vitae'] - self.character.stats['vitae spent']
        self.current.change_text(str(current_num) + "/" + str(self.character.stats['vitae']))

def save_xml(character, path):
    pass
    '''
    Save vampire as xml
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

        # stats with tooltips
        elif stat in ('merits', 'disciplines'):
            for content in character.stats[stat]:
                item = Element(stat)
                root.append(item)

                name = Element('name')
                item.append(name)
                name.text = content

                rating = Element('rating')
                item.append(rating)
                rating.text = str(character.stats[stat][content]['rating'])

                if 'tooltip' in character.stats[stat][content]:
                    tooltip = Element('tooltip')
                    item.append(tooltip)
                    tooltip.text = character.stats[stat][content]['tooltip']

        elif stat in ('skill specialties'):
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
    disciplines = dom.findall('disciplines')
    others = dom.findall('other')

    input_stats = {}
    input_stats['merits'] = {}
    input_stats['skill specialties'] = {}
    input_stats['health'] = [0, 0, 0, 0]
    input_stats['disciplines'] = {}
    input_stats['weapons'] = {}
    specials = ['conditions', 'aspirations', 'banes']

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

    for merit in merits:
        name = merit.find('name').text
        rating = merit.find('rating').text
        input_stats['merits'][name]['rating'] = int(rating)

        if merit.find('tooltip') != None:
            tooltip = merit.find('tooltip').text
            input_stats['merits'][name]['tooltip'] = tooltip

    for discipline in disciplines:
        name = discipline.find('name').text
        rating = discipline.find('rating').text
        input_stats['disciplines'][name]['rating'] = int(rating)

        if discipline.find('tooltip') != None:
            tooltip = discipline.find('tooltip').text
            input_stats['disciplines'][name]['tooltip'] = tooltip

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
