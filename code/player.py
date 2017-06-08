# Chronicles of Darkness Character and PyQT objects created for use in conjunction with Dicecord.
#    Copyright (C) 2017  Roy Healy

import random
import mageUI, vampireUI, stats
from xml.dom import minidom
from xml.etree.ElementTree import Element
from xml.etree import ElementTree as etree

class Character:
    def __init__(self,
                 stats=None,
                 goodMessages = '',
                 badMessages = '',
                 goodrate = 100,
                 badrate = 50,
                 notes = "",
                 splat = 'mage'):
        '''
        Class for holding players, making their rolls and saving their last rolls.
        Initialised with an ID, optional other variables include stats, whether it is a dark age game and webhook.
        '''
        
        # results of last roll, starts blank
        self.last_roll = []

        self.splat = splat

        # stats are a dict, default depends on splat
        if not stats:
            if splat == 'mage':
                stats = mageUI.DEFAULT
            elif splat == 'vampire':
                stats = vampireUI.DEFAULT

        # sets it into a copy to avoid mutation based errors
        self.stats = stats.copy()

        # character object has a text editor for taking notes
        self.notes = notes

        # personality settings
        if not goodMessages:
            if splat == 'mage':
                goodMessages = mageUI.goodMessages
            elif splat == 'vampire':
                goodMessages = vampireUI.goodMessages

        if not badMessages:
            if splat == 'mage':
                badMessages = mageUI.badMessages
            elif splat == 'vampire':
                badMessages = vampireUI.badMessages

        self.goodMessages = goodMessages
        self.badMessages = badMessages
        self.goodRate = goodrate
        self.badRate = badrate

        # some stats are derived, this function will calulate them based on the supplied stats sheet
        self.update_derivitives()
        
    def update_derivitives(self):
        '''
        Update values of derived stats.
        '''

        # max resource depends on power stat
        if self.splat == "mage":
            mageUI.update_mana(self)
        elif self.splat == "vampire":
            vampireUI.update_vitae(self)

        # Willpower = Resolve + Composure
        self.stats['willpower'] = self.stats['resolve'] + self.stats['composure']

        # Max health = Stamina + Size
        self.stats['health'][0] = self.stats['stamina'] + self.stats['size']

        # Speed = dexterity + strength + 5
        self.stats['speed'] = self.stats['dexterity'] + self.stats['strength'] + 5

        # initiative = dexterity + composure
        self.stats['initiative'] = self.stats['dexterity'] + self.stats['composure']

        # defense is lower of dex or wits, + atheltics
        self.stats['defense'] = min(self.stats['dexterity'], self.stats['wits']) + self.stats['athletics']

    
    def state_health(self):
        '''
        States current character health.
        '''
        out = ["Bashing: " + str(self.stats['health'][1]), "Lethal: " + str(self.stats['health'][2]), "Agg: " + str(self.stats['health'][3])]
        for element in out:
            element += "/" + str(self.stats['health'][0])
        return out
    
    def change_health(self, amount, dam_type):
        '''
        Updates current health by amount of damage.
        '''
        # Note this needs extra work to take into account whether the user already has a higher level of damage.
        # e.g. if I am at 2 lethal and I get a bashing, bashing goes in box number 3.
        # Right now the code only handles overflow when max health reached.
        # Might just do all this via UI depending on UAT
        
        if dam_type <= 0 or dam_type > 3:
            # check if input makes sense
            return "Invalid input."

        # add appropiate damage
        self.stats['health'][dam_type] += amount

        # check for overflow
        if self.stats['health'][dam_type] > self.stats['health'][0]:
            # if new damage is more than max, get difference
            over = self.stats['health'][dam_type] - self.stats['health'][0]
            # set current type to equal max
            self.stats['health'][dam_type] = self.stats['health'][0]
            if dam_type != 3:
                # if this is lethal or bashing, damage will upgrade to next type
                self.change_health(over, dam_type + 1)
                
        # output will be a list of strings simialr to last roll which should state the current rating and overflows maybe?

    def save_xml(self, path):
        '''
        Saves a copy of the character sheet as an XML file.
        '''

        root = Element('root')

        # notes
        if self.notes != '':
            item = Element('notes')
            root.append(item)

            content = Element('content')
            item.append(content)
            content.text = self.notes

        # splat
        item = Element('splat')
        root.append(item)
        item.text = self.splat

        if self.splat == 'mage':
            # rote skills
            for skill in self.stats['rote skills']:
                item = Element('rote_skill')
                root.append(item)
                item.text = skill

            
        for stat in self.stats:
            # skills
            if stat in stats.SKILLS:
                item = Element('skill')
                root.append(item)

                name = Element('name')
                item.append(name)
                name.text = stat

                rating = Element('rating')
                item.append(rating)
                rating.text = str(self.stats[stat])

                if stat in self.stats['skill specialties']:
                    # record specialties
                    tooltip = Element('tooltip')
                    item.append(tooltip)
                    tooltip.text = self.stats['skill specialties'][stat]

            elif stat in ('skill specialties'):
                # skip these - added when associated skill added
                pass

            # stat contains a dict
            elif type(self.stats[stat]) is dict:
                if self.stats[stat] != {}:
                    item = Element('dict')
                    root.append(item)

                    statname = Element('statname')
                    item.append(statname)
                    statname.text = stat

                    for entry in self.stats[stat]:
                        details = self.stats[stat][entry]
                        # can be a dict itself, or a value
                        if type(details) is dict:
                            name = Element('name')
                            item.append(name)
                            name.text = str(entry)

                            for detail in details:
                                # loop over dict, skip blank entries
                                if details[detail] != '':
                                    attribute_name = detail.replace(' ', '_')
                                    content = Element(attribute_name)
                                    item.append(content)
                                    content.text = str(details[detail])
                        else:
                            name = Element('name')
                            item.append(name)
                            name.text = str(entry)

                            tooltip = Element('tooltip')
                            item.append(tooltip)
                            tooltip.text = str(details)

            # health
            elif stat == 'health':
                health = self.stats['health']
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

            # stat is a string or a number
            elif type(stat) is int or type(stat) is str:
                if self.stats[stat] != '':
                    item = Element('other')
                    root.append(item)

                    name = Element('name')
                    item.append(name)
                    name.text = stat

                    rating = Element('rating')
                    item.append(rating)
                    rating.text = str(self.stats[stat])

        # Personality
        for message in self.goodMessages:
            item = Element('goodmessage')
            root.append(item)

            mess = Element('message')
            item.append(mess)
            mess.text = message

        for message in self.badMessages:
            item = Element('badmessage')
            root.append(item)

            mess = Element('message')
            item.append(mess)
            mess.text = message

        item = Element('badrate')
        root.append(item)
        item.text = str(self.badRate)

        item = Element('goodrate')
        root.append(item)
        item.text = str(self.goodRate)

        # write file
        rough_string = etree.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        text = reparsed.toprettyxml(indent="  ")

        # used to remove ’ style apostrophes that cause crashes when reading the file
        text = text.replace('’', "'")

        f = open(path, 'w')
        f.write(text)
        f.close()

    @classmethod
    def from_xml(cls, path):
        '''
        Create character object based on xml file
        '''
        dom = etree.parse(path)
        splat = dom.find('splat')
        notes = dom.find('notes')
        goodMessages = dom.findall('goodmessage')
        badMessages = dom.findall('badmessage')
        goodRate = dom.find('badrate')
        badRate = dom.find('goodrate')

        skills = dom.findall('skill')
        dicts = dom.findall('dict')
        health = dom.find('health')
        others = dom.findall('other')

        ### backwards compatibility
        if not dicts:
            # pre 1.1 mage only
            return mageUI.from_xml(cls, dom)

        ### backwards compatibility

        input_splat = splat.text
        char = cls(splat = input_splat)
            
        for element in dicts:
            stat = element.find('statname').text
            char.stats[stat] = {}

            entries = list(element)
            for entry in entries:
                if entry.tag == 'name':
                    # will start a new dict each time it sees the tag 'name'
                    name = entry.text
                    char.stats[stat][name] = {}
                elif entry.tag != 'statname':
                    entry_name = entry.tag.replace('_', ' ')
                    char.stats[stat][name][entry_name] = entry.text

        for skill in skills:
            name = skill.find('name').text
            rating = skill.find('rating').text
            char.stats[name] = int(rating)

            if skill.find('tooltip') != None:
                tooltip = skill.find('tooltip').text
                char.stats['skill specialties'][name] = tooltip

        dam_type = 1
        for damage in ['bashing', 'lethal', 'agg']:
            amount = int(health.find(damage).text)
            char.stats['health'][dam_type] = amount
            dam_type += 1

        for other in others:
            name = other.find('name').text
            rating = other.find('rating').text
            if rating == None:
                # happens only for blank string inputs
                char.stats[name] = ''
            elif rating.isdigit() and name != 'user id':
                # numbers, but not user id
                char.stats[name] = int(rating)
            else:
                # string input
                char.stats[name] = rating

        if input_splat == 'mage':
            # code for mage rote skills
            char.stats['rote skills'] = set()
            roteskills = dom.findall('rote_skill')
            for skill in roteskills:
                char.stats['rote skills'].add(skill.text)
            
        char.goodMessages = []
        char.badMessages = []

        if notes != None:
            char.notes = notes.find('content').text

        for message in goodMessages:
            mess = message.find('message').text
            char.goodMessages.append(mess)

        for message in badMessages:
            mess = message.find('message').text
            char.badMessages.append(mess)

        char.goodRate = int(goodRate.text)

        char.badRate = int(badRate.text)

        return char


    def roll_set(self, dice, rote=False, again=10, quiet=False):
        '''
        roll a hand of dice subject to supplied conditions
        dice: int, the number of dice to roll
        rote: boolean, a rote roll rerolls all failed dice once
        again: int, which die faces explode
        quiet: Boolean about whether quiet mode will be used
        Returns a list of strings stating each die result and then total successes
        If quiet mode, returns a one element list that only returns total successes.
        '''
        
        # Check that more than 1 die selected
        if dice < 1:
            return ['Select at least 1 die.']

        # self.last_roll field collects the value of each rolled die
        # initialised to blank here, will be set in each self.roll_die call
        self.last_roll = []
        
        # successes collector variable 
        successes = 0
        
        # fail collector in case it is a rote
        fails = []

        
        for die in range(0,dice):
            # roll each die
            result = self.roll_die(again)
            if result == 0:
                # if not a success adds entry to fail list for rote reroll
                fails += ["fail"]
            else:
                # add the result to successes counter
                successes += result

        if rote:
            # if a rote all failed dice are rerolled once
            for die in fails:
                successes += self.roll_die(again, rote_reroll = True)

        # send message
        messages = []
        
        if not quiet:
            # add all messages if quiet mode
            messages.extend(self.last_roll)

        else:
            # add a summary message
            out = self.stats['user id'] + " rolled " + str(dice) + " dice and got " + str(successes) + " successes."
            for message in self.last_roll:
                # find dice value
                value = ''.join(x for x in message[len(self.stats['user id']) + 1:] if x.isdigit())
                if "exploded" in message:
                    out += "(" + value + ")"
                elif "rote" in message:
                    out += " Rote:" + value
                else:
                    out += " " + value

            messages.append(out)
                

        # add total results message
        messages.append("Total Successes for " + self.stats['user id'] + " : " + str(successes))
        
        return messages
            
    def roll_die(self, again = 10, explode_reroll = False, rote_reroll = False):
        '''
        Rolls a single 10 sided die, calculates number of successes.
        Also updates the self.last_roll attribute with each roll result.
        Handles explosions and gives custom last_roll text for rote/explosions
        '''

        # make roll by choosing random number between 1 and 10
        value = random.randrange(1, 11)
    
        # recording value, adds details for rote/reroll
        if explode_reroll and rote_reroll:
            self.last_roll.append(self.stats['user id'] + " rolled rote exploded die: " + str(value))
        elif explode_reroll:
            self.last_roll.append(self.stats['user id'] + " rolled exploded die: " + str(value))
        elif rote_reroll:
            self.last_roll.append(self.stats['user id'] + " rolled rote die: " + str(value))
        else:
            self.last_roll.append(self.stats['user id'] + " rolled " + str(value))

        # checks for success/explosions
        if value >= again:
            # Exploding!
            return 1 + self.roll_die(again, True, rote_reroll)
        elif value >= 8:
            # normal success
            return 1
        else:
            # failure
            return 0
    
    def roll_special(self):
        '''
        Rolls a single die, successes are not counted and last_roll not updated
        '''
        value = random.randrange(1, 11)
        return self.stats['user id'] + " rolled a " + str(value) + "!"

    def roll_chance(self):
        '''
        Rolls a chance die.
        '''
        # make roll by choosing random number between 1 and 10
        value = random.randrange(1, 11)

        # clear last roll and append chance die result
        self.last_roll = []
        self.last_roll.append(self.stats['user id'] + " rolled a chance die: " + str(value))

        # Give value
        messages = [self.stats['user id'] + " chance rolled " + str(value)]

        # # check if failure, botch or success
        if value == 10:
            messages.append(self.stats['user id'] + " got a success!")
        elif value == 1:
            messages.append(self.stats['user id'] + " botched!")
        else:
            messages.append(self.stats['user id'] + " failed!")

        # Give result
        return messages

    def get_last_roll(self):
        # used for getting results of last roll made
        return self.last_roll
