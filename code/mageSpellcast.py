from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from mageUI import ARCANA

PRACTICES = [('Compelling', 1),
             ('Knowing', 1),
             ('Unveiling', 1),
             ('Ruling', 2),
             ('Shielding', 2),
             ('Veiling', 2),
             ('Fraying', 3),
             ('Perfecting', 3),
             ('Weaving', 3),
             ('Patterning', 4),
             ('Unraveling', 4),
             ('Making', 5),
             ('Unmaking', 5)]
YANTRAS = [("Demense", 2),
           ("Enviornment", 1),
           ("Supernal Verge", 2),
           ("Concentration", 2),
           ("Mantra", 2),
           ("Runes", 2)]
DURATION = [[0,'1 Turn'],
            [-2,'2 Turns'],
            [-4,'3 Turns'],
            [-6,'5 Turns'],
            [-8,'10 Turns']]
ADV_DURATION = [[0,'One scene/hour'],
            [-2,'2 One Day'],
            [-4,'One Week'],
            [-6,'One Month'],
            [-8,'One Year'],
            [-10, 'Indefinite (+1 Reach and Mana)']]
SCALE = [[0,{"Subjects": {"Amount": 1, "Size": 5}, "Area": "Arm's Reach"}],
            [-2,{"Subjects": {"Amount": 2, "Size": 6}, "Area": "Small Room"}],
            [-4,{"Subjects": {"Amount": 4, "Size": 7}, "Area": "Large Room"}],
            [-6,{"Subjects": {"Amount": 8, "Size": 8}, "Area": "Several Rooms/Single Floor of a House"}],
            [-8,{"Subjects": {"Amount": 16, "Size": 9}, "Area": "Ballroom/small house"}]]
ADV_SCALE = [[0,{"Subjects": {"Amount": 5, "Size": 5}, "Area": "Large House/Building"}],
            [-2,{"Subjects": {"Amount": 10, "Size": 10}, "Area": "Small Warehouse/Parking Lot"}],
            [-4,{"Subjects": {"Amount": 20, "Size": 15}, "Area": "Large Warehouse/Supermarket"}],
            [-6,{"Subjects": {"Amount": 40, "Size": 20}, "Area": "Small Factory/Mall"}],
            [-8,{"Subjects": {"Amount": 80, "Size": 25}, "Area": "Large Factory/City Block"}],
             [-10, {"Subjects": {"Amount": 160, "Size": 30}, "Area": "Campus/Small Neighbourhood"}]]

class ChooseSpellTab(QWidget):
    def __init__(self, mainWidget, character):
        super().__init__()
        self.mainWidget = mainWidget
        self.character = character
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        rote = QRadioButton()
        rote.setText("Rotes")
        rote.setChecked(True)
        rote.toggled.connect(lambda: self.changeSpellType("rote"))
        self.grid.addWidget(rote, 0, 0)

        praxes = QRadioButton()
        praxes.setText("Praxes")
        praxes.toggled.connect(lambda: self.changeSpellType("praxes"))
        self.grid.addWidget(praxes, 0, 1)

        creativeThaum = QRadioButton()
        creativeThaum.setText("Creative Thaumaturgy")
        creativeThaum.toggled.connect(lambda: self.changeSpellType("creativeThaum"))
        self.grid.addWidget(creativeThaum, 0, 2)

    def changeSpellType(self, spellType):
        pass

class spellsList(QWidget):
    def __init__(self, mainWidget, character):
        super().__init__()

class CastWindow(QTabWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):
        self.chooseSpell = ChooseSpellTab(self, self.character)
        self.addTab(self.chooseSpell, "Choose Spell")

    def update_details(self):
        '''
        Check widgets, calculate details, update UI
        :return:
        '''
        arcanum = int(self.arcanum_entry.currentText()[-2:-1])
        self.cast_pool = self.character.stats['gnosis'] + arcanum

        # add yantra

        # add extended cast time
        # 0 = instant = +1 reach, ritual adds time based on Gnosis
        ## if statement defining cast time, updates pool and time summary label

        # remove potency

        # remove duration

        # remove scaling

        self.paradox_pool = 'None'

        # calculate free reaches

        # update paradox pool if free reaches surpassed
        # check if dedicated tool used and reduce paradox if so

        if self.cast_pool <= 0:
            self.cast_pool = 'Chance'

        if self.paradox_pool.isdigit() and self.paradox_pool <= 0:
            self.paradox_pool = 'Chance'

        self.pools.setText("Cast Pool: " + str(self.cast_pool) + "   Paradox Pool: " + str(self.paradox_pool))

    def state_spell_summary(self):
        pass

    def roll(self):
        pass

if __name__ == '__main__':
        import sys, player
        app = QApplication(sys.argv)
        char = player.Character()
        window = CastWindow(char)
        window.setFixedSize(500, 200)
        window.show()
        sys.exit(app.exec_())