#Character object

import random

class Character:
    def __init__(self, ID, stats={}):
        '''
        Class for holding players, making their rolls and saving their last rolls
        '''
        #Some means of identifying user
        #Generally either numeric ID or discord username depending on bot versus client implementation
        self.ID = ID
        #results of last roll, starts blank
        self.last_roll = []
        self.stats = stats
        
        ##place holder code indicating other attributes which need to be created
        #for full implementation the imported character details should give "current" ratings
        #self.mana = {'current': 0, 'max': 0} #max should be calculated based on supplied gnosis
        #self.health = [0, #max - will be calculated based on relevant attributes
                       #0, #bashing
                       #0, #lethal
                       #0] #agg
        #self.xp = {"standard": 0, "arcane": 0}
        #self.beats = {"standard": 0, "arcane": 0}
        
    def get_stat(self, stat):
        '''
        gets value of a stat
        string -> int
        string -> string if error
        '''
        try: s = self.stats[stat.lower()]
        except KeyError:
            #occurs if stats not present, will return a not found string
            return stat + " not found."
        return s

    def earn_xp(self, xp_type, amount):
        '''
        Adds xp
        '''
        pass
        self.xp[xp_type] += amount

    def spend_xp(self, stat, xp_type):
        '''
        Spend xp to update stat.
        '''
        pass

    def earn_beat(self, beat_type):
        '''
        Earn a beat, add 1 xp if 5 beats reached
        '''
        pass
        self.beats[beat_type] += 1
        if self.beats[beat_type] == 5:
            self.beats[beat_type] = 0
            self.earn_xp(beat_type, 1)
            return "Beat converted to xp."
        return "Beat added."
    
    def state_health(self):
        '''
        States current character health
        '''
        pass
        out = ["Bashing: " + str(self.health[1]), "Lethal: " + str(self.health[2]), "Agg: " + str(self.health[3])]
        for element in out:
            element += "/" + str(self.health[0])
        return out
    
    def change_health(self, amount, dam_type):
        '''
        Updates current health
        '''
        pass
        if dam_type <= 0 or dam_type > 3:
            return "Invalid input."
        self.health[dam_type] += amount
        if self.health[dam_type] > self.health[0]:
            over = abs(self.health[0] - self.health[dam_type])
            self.health[dam_type] = self.health[0]
            if dam_type != 3:
                self.change_health(over, dam_type + 1)
                
        self.state_health()

    def roll_set(self, dice, rote=False, again=10, quiet=False):
        '''
        roll a hand of dice subject to supplied conditions
        dice: int, the number of dice to roll
        rote: boolean, a rote roll rerolls all failed dice once
        again: int, which die faces explode
        quiet: Boolean about whether quiet mode will be used
        Returns a list of strings stating each die result and then total successes
        If quiet mode, only returns total successes
        '''
        
        #self.last_roll field collects the value of each rolled die
        #initialised to blank here, will be set in each self.roll_die call
        self.last_roll = []
        
        #successes collector variable 
        successes = 0
        
        #fail collector in case it is a rote
        fails = []

        
        for die in range(0,dice):
            result = self.roll_die(again)
            if result == 0:
                #if not a success adds entry to fail list for rote reroll
                fails += ["fail"]
                #add result to success counter
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
            messages.extend(self.last_roll)

        messages.append("Total Successes for " + self.ID + " : " + str(successes))
        
        return messages
            
    def roll_die(self, again = 10, explode_reroll = False, rote_reroll = False):
        '''
        Rolls a single die, calculates number of successes
        Also updates the last_roll attribute with each roll result
        Handles explosions and gives custom last_roll text for rote/explosions
        '''
        value = random.randrange(1, 11)
    
        #recording value, adds details for rote/reroll
        if explode_reroll and rote_reroll:
            self.last_roll.append(self.ID + " rolled rote exploded die: " + str(value))
        elif explode_reroll:
            self.last_roll.append(self.ID + " rolled exploded die: " + str(value))
        elif rote_reroll:
            self.last_roll.append(self.ID + " rolled rote die: " + str(value))
        else:
            self.last_roll.append(self.ID + " rolled " + str(value))

        #checks for success/explosions
        if value >= again:
            #Exploding!
            return 1 + self.roll_die(again, True, rote_reroll)
        elif value >= 8:
            return 1
        else:
            return 0
    
    def roll_special(self):
        '''
        Rolls a single die, successes are not counted and last_roll not updated
        '''
        value = random.randrange(1, 11)
        return self.ID + " rolled a " + str(value) + "!"

    def roll_chance(self):
        '''
        Rolls a chance die.
        '''
        #make roll by choosing random bumber between 1 and 10
        value = random.randrange(1, 11)

        #clear last roll and append chance die result
        self.last_roll = []
        self.last_roll.append("chance die: " + str(value))

        #Give value
        messages = [self.ID + "chance rolled " + str(value)]

        ##check if failure, botch or success
        if value == 10:
            messages.append(self.ID + " got a success!")
        elif value == 1:
            messages.append(self.ID + " botched!")
        else:
            messages.append(self.ID + " failed!")

        #Give result
        return messages

    def get_last_roll(self):
        #used for getting results of last roll made
        if self.last_roll == []:
            return [self.ID + " has no previous rolls."]
        return self.last_roll
