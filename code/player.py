#Chronicles of Darkness Character and PyQT objects created for use in conjunction with Dicecord.
#   Copyright (C) 2017  Roy Healy
#
#version 0.1 -> Added stats and derivation calculations for Mage: the Awakening 2e. Initial work on Sheet UI begins.

import random
import sys
import stats

class Character:
    def __init__(self, stats=stats.STATS, notes = "", dark_age = False):
        '''
        Class for holding players, making their rolls and saving their last rolls.
        Initialised with an ID, optional other variables include stats, whether it is a dark age game and webhook.
        '''
        
        #results of last roll, starts blank
        self.last_roll = []
        
        #stats are a dict, default assigned to STATS global
        self.stats = stats

        #character object has a text editor for taking notes
        self.notes = notes

        #some stats are derived, this function will calulate them based on the supplied stats sheet
        self.update_derivitives()
        
    def update_derivitives(self):
        '''
        Update values of derived stats.
        '''

        #max mana depends on gnosis
        if self.stats['gnosis'] <= 5:
            self.stats['mana']['max'] = 5 + self.stats['gnosis']
        elif self.stats['gnosis'] <= 8:
            self.stats['mana']['max'] = 20 + 10*(self.stats['gnosis'] - 6)
        elif self.stats['gnosis'] == 9:
            self.stats['mana']['max'] = 50
        else:
            self.stats['mana']['max'] = 75

        #Max health = Stamina + Size
        self.stats['health'][0] = self.stats['stamina'] + self.stats['size']

        #Speed = dexterity + strength + 5
        self.stats['speed'] = self.stats['dexterity'] + self.stats['strength'] + 5

        #initiative = dexterity + composure
        self.stats['initiative'] = self.stats['dexterity'] + self.stats['composure']

        ##defense is lower of dex and wits
        #BUG: self.defense calculation is causing "TypeError: 'builtin_function_or_method' object is not subscriptable"
        ##self.defense = min[stats['attributes']['physical']['dexterity'], stats['attributes']['mental']['wits']]

    def earn_xp(self, xp_type, amount):
        '''
        Adds xp
        '''
        self.stats['xp'][xp_type] += amount

    def spend_xp(self, stat, xp_type):
        '''
        Spend xp to update stat.
        '''
        #costs depend on category of stat.
        pass

    def earn_beat(self, beat_type):
        '''
        Earn a beat, add 1 xp if 5 beats reached
        '''
        
        self.stats['beats'][beat_type] += 1
        if self.stats['beats'][beat_type] == 5:
            self.stats['beats'][beat_type] = 0
            self.earn_xp(beat_type, 1)
            return "Beat converted to xp."
        return "Beat added."
    
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
        #Note this needs extra work to take into account whether the user already has a higher level of damage.
        #e.g. if I am at 2 lethal and I get a bashing, bashing goes in box number 3.
        #Right now the code only handles overflow when max health reached.
        #Might just do all this via UI depending on UAT
        
        if dam_type <= 0 or dam_type > 3:
            #check if input makes sense
            return "Invalid input."

        #add appropiate damage
        self.stats['health'][dam_type] += amount

        #check for overflow
        if self.stats['health'][dam_type] > self.stats['health'][0]:
            #if new damage is more than max, get difference
            over = self.stats['health'][dam_type] - self.stats['health'][0]
            #set current type to equal max
            self.stats['health'][dam_type] = self.stats['health'][0]
            if dam_type != 3:
                #if this is lethal or bashing, damage will upgrade to next type
                self.change_health(over, dam_type + 1)
                
        #output will be a list of strings simialr to last roll which should state the current rating and overflows maybe?

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
        
        #Check that more than 1 die selected
        if dice < 1:
            return ['Select at least 1 die.']

        #self.last_roll field collects the value of each rolled die
        #initialised to blank here, will be set in each self.roll_die call
        self.last_roll = []
        
        #successes collector variable 
        successes = 0
        
        #fail collector in case it is a rote
        fails = []

        
        for die in range(0,dice):
            #roll each die
            result = self.roll_die(again)
            if result == 0:
                #if not a success adds entry to fail list for rote reroll
                fails += ["fail"]
            else:
                #add the result to successes counter
                successes += result

        if rote:
            #if a rote all failed dice are rerolled once
            for die in fails:
                successes += self.roll_die(again, rote_reroll = True)

        #send message
        messages = []
        
        if not quiet:
            #add all messages if quiet mode
            messages.extend(self.last_roll)

        #add total results message
        messages.append("Total Successes for " + self.stats['user id'] + " : " + str(successes))
        
        return messages
            
    def roll_die(self, again = 10, explode_reroll = False, rote_reroll = False):
        '''
        Rolls a single 10 sided die, calculates number of successes.
        Also updates the self.last_roll attribute with each roll result.
        Handles explosions and gives custom last_roll text for rote/explosions
        '''

        #make roll by choosing random number between 1 and 10
        value = random.randrange(1, 11)
    
        #recording value, adds details for rote/reroll
        if explode_reroll and rote_reroll:
            self.last_roll.append(self.stats['user id'] + " rolled rote exploded die: " + str(value))
        elif explode_reroll:
            self.last_roll.append(self.stats['user id'] + " rolled exploded die: " + str(value))
        elif rote_reroll:
            self.last_roll.append(self.stats['user id'] + " rolled rote die: " + str(value))
        else:
            self.last_roll.append(self.stats['user id'] + " rolled " + str(value))

        #checks for success/explosions
        if value >= again:
            #Exploding!
            return 1 + self.roll_die(again, True, rote_reroll)
        elif value >= 8:
            #normal success
            return 1
        else:
            #failure
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
        #make roll by choosing random number between 1 and 10
        value = random.randrange(1, 11)

        #clear last roll and append chance die result
        self.last_roll = []
        self.last_roll.append(self.stats['user id'] + " rolled a chance die: " + str(value))

        #Give value
        messages = [self.stats['user id'] + " chance rolled " + str(value)]

        ##check if failure, botch or success
        if value == 10:
            messages.append(self.stats['user id'] + " got a success!")
        elif value == 1:
            messages.append(self.stats['user id'] + " botched!")
        else:
            messages.append(self.stats['user id'] + " failed!")

        #Give result
        return messages

    def get_last_roll(self):
        #used for getting results of last roll made
        return self.last_roll
