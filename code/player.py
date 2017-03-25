# Chronicles of Darkness Character and PyQT objects created for use in conjunction with Dicecord.
#    Copyright (C) 2017  Roy Healy

import random
from xml.etree import ElementTree as etree
import mageUI, vampireUI

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
            pass
            # mageUI.update_vitae(self)

        # Willpower = Resolve + Composure
        self.stats['willpower'] = self.stats['resolve'] + self.stats['composure']

        # Max health = Stamina + Size
        self.stats['health'][0] = self.stats['stamina'] + self.stats['size']

        # Speed = dexterity + strength + 5
        self.stats['speed'] = self.stats['dexterity'] + self.stats['strength'] + 5

        # initiative = dexterity + composure
        self.stats['initiative'] = self.stats['dexterity'] + self.stats['composure']

        # defense is lower of dex and wits
        self.stats['defense'] = min(self.stats['dexterity'], self.stats['wits'])

    
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

        if self.splat == 'mage':
            mageUI.save_xml(self, path)

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

        if not splat:
            # pre 1.02 file
            input_splat = 'mage'
        else:
            input_splat = splat.text

        if input_splat == 'mage':
            input_stats = mageUI.from_xml(dom)


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
                   splat = input_splat)


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
