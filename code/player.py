#Chronicles of Darkness Character and PyQT objects created for use in conjunction with Dicecord.
#   Copyright (C) 2017  Roy Healy

import random
import sys
import stats
from xml.etree.ElementTree import Element
from xml.etree import ElementTree as etree
from xml.dom import minidom

class Character:
    def __init__(self, stats=stats.STATS, notes = "", dark_age = False):
        '''
        Class for holding players, making their rolls and saving their last rolls.
        Initialised with an ID, optional other variables include stats, whether it is a dark age game and webhook.
        '''
        
        #results of last roll, starts blank
        self.last_roll = []
        
        #stats are a dict, default assigned to STATS global
        #sets it into a copy to avoid mutation based errors
        self.stats = stats.copy()

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
            self.stats['mana'] = 5 + self.stats['gnosis']
        elif self.stats['gnosis'] <= 8:
            self.stats['mana'] = 20 + 10*(self.stats['gnosis'] - 6)
        elif self.stats['gnosis'] == 9:
            self.stats['mana'] = 50
        else:
            self.stats['mana'] = 75

        #Willpower = Resolve + Composure
        self.stats['willpower'] = self.stats['resolve'] + self.stats['composure']

        #Max health = Stamina + Size
        self.stats['health'][0] = self.stats['stamina'] + self.stats['size']

        #Speed = dexterity + strength + 5
        self.stats['speed'] = self.stats['dexterity'] + self.stats['strength'] + 5

        #initiative = dexterity + composure
        self.stats['initiative'] = self.stats['dexterity'] + self.stats['composure']

        ##defense is lower of dex and wits
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

    def save_xml(self, path):
        '''
        Saves a copy of the character sheet as an XML file.
        '''
        
        root = Element('root')

        #notes
        if self.notes != '':
            item = Element('notes')
            root.append(item)

            content = Element('content')
            item.append(content)
            content.text = self.notes

        
        for stat in self.stats:
            #skills
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
                    #record specialties
                    tooltip = Element('tooltip')
                    item.append(tooltip)
                    tooltip.text = self.stats['skill specialties'][stat]

                if stat in self.stats['rote skills']:
                    #flag rotes
                    rote = Element('rote')
                    item.append(rote)
                    rote.text = "True"

            #merits
            elif stat == 'merits':
                for merit in self.stats['merits']:
                    item = Element('merit')
                    root.append(item)

                    name = Element('name')
                    item.append(name)
                    name.text = merit
                    
                    rating = Element('rating')
                    item.append(rating)
                    rating.text = str(self.stats['merits'][merit])

                    if merit in self.stats['merit details']:
                        tooltip = Element('tooltip')
                        item.append(tooltip)
                        tooltip.text = self.stats['merit details'][merit]

            elif stat in ('skill specialties','merit details', 'rote skills'):
                #skip these - added when associated merit/skill added
                pass

            #labels and tooltips
            elif stat in ('conditions', 'aspirations', 'obsessions', 'active spells', 'attainments', 'magtool'):
                if self.stats[stat] != {}:
                    item = Element(stat)
                    root.append(item)

                    for entry in self.stats[stat]:
                        leaf = Element('entry')
                        name = Element('name')
                        leaf.append(name)
                        name.text = entry

                        if self.stats[stat][entry] != '':
                            tooltip = Element('tooltip')
                            leaf.append(tooltip)
                            tooltip.text = self.stats[stat][entry]
                        
                        item.append(leaf)
                    
            #any other stat but health, praxes, rote, weapons or enchanted items
            elif stat not in ('health', 'rotes', 'ench items', 'praxes', 'weapons'):
                item = Element('other')
                root.append(item)
                ##print(stat)

                name = Element('name')
                item.append(name)
                name.text = stat

                rating = Element('rating')
                item.append(rating)
                
                #note, this can be strings or numbers
                rating.text = str(self.stats[stat])

            elif stat == 'weapons':
                if self.stats['weapons'] != {}:
                    for weapon in self.stats['weapons']:
                        item = Element('weapon')
                        root.append(item)
                        
                        name = Element('name')
                        item.append(name)
                        name.text = weapon

                        details = self.stats['weapons'][weapon]

                        for detail in details:
                            #loop over dict, skip blank entries
                            if details[detail] != '':
                                entry = Element(detail)
                                item.append(entry)
                                entry.text = str(details[detail])
                
            elif stat == 'praxes':
                if self.stats['praxes'] != {}:
                    for praxis in self.stats['praxes']:
                        item = Element('praxis')
                        root.append(item)
                        
                        name = Element('name')
                        item.append(name)
                        name.text = praxis

                        if self.stats['praxes'][praxis]['tooltip']!= '':
                            tooltip = Element('tooltip')
                            item.append(tooltip)
                            tooltip.text = self.stats['praxes'][praxis]['tooltip']

                        arcanum = Element('arcanum')
                        item.append(arcanum)
                        arcanum.text = self.stats['praxes'][praxis]['arcanum']


            elif stat == 'rotes':
                for rote in self.stats['rotes']:
                    item = Element('rote')
                    root.append(item)
                    content = self.stats['rotes'][rote]

                    name = Element('name')
                    item.append(name)
                    name.text = rote

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
            
            #health
            elif stat == 'health':
                health = self.stats['health']
                item = Element('health')
                root.append(item)

                bashing = Element('bashing')
                lethal = Element('lethal')
                agg = Element('agg')
                
                #max ignored since it is derived
                bashing.text = str(health[1])
                lethal.text = str(health[2])
                agg.text = str(health[3])

                item.append(bashing)
                item.append(lethal)
                item.append(agg)

            elif stat == 'ench items':
                for name in self.stats['ench items']:
                    item = Element('enchitem')
                    root.append(item)
                    
                    content = self.stats['ench items'][name]
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
                    

        #write file
        rough_string = etree.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        text = reparsed.toprettyxml(indent="  ")

        f = open(path, 'w')
        f.write(text)
        f.close()

    @classmethod
    def from_xml(cls, path):
        '''
        Create character object based on xml file
        '''
        dom = etree.parse(path)
        skills = dom.findall('skill')
        merits = dom.findall('merit')
        health = dom.find('health')
        specials = ['conditions', 'aspirations', 'obsessions', 'active spells', 'attainments', 'magtool']
        praxes = dom.findall('praxis')
        rotes = dom.findall('rote')
        others = dom.findall('other')
        notes = dom.find('notes')
        ench_items = dom.findall('enchitem')
        weapons = dom.findall('weapon')
        
        input_stats = {}
        input_stats['merits'] = {}
        input_stats['skill specialties'] = {}
        input_stats['merit details'] = {}
        input_stats['rote skills'] = set([])
        input_stats['rotes'] = {}
        input_stats['health'] = [0,0,0,0]
        input_stats['ench items'] = {}
        input_stats['praxes'] = {}
        input_stats['weapons'] = {}

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

            input_stats['weapons'][name] = {'damage':int(damage),
                                            'range':weapon_range,
                                            'clip':int(clip),
                                            'init':int(init),
                                            'str':int(strength),
                                            'size':int(size)}

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
                stats = leaf.findall('entry')
                for stat in stats:
                    name = stat.find('name').text
                    if stat.find('tooltip') != None:
                        tooltip = stat.find('tooltip').text
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
                #happens when tooltip is blank
                tooltip = ''

            input_stats['rotes'][name] = [tooltip, arcanum, skill]
            

        for other in others:
            name = other.find('name').text
            rating = other.find('rating').text
            if rating == None:
                #happens only for blank string inputs
                input_stats[name] = ''
            elif rating.isdigit() and name != 'user id':
                #numbers, but not user id
                input_stats[name] = int(rating)
            else:
                #string input
                input_stats[name] = rating

        
        if notes == None:
            input_notes = ''
        else:
            input_notes = notes.find('content').text
            

        return cls(stats = input_stats, notes = input_notes)


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

        else:
            #add a summary message
            out = self.stats['user id'] + " rolled " + str(dice) + " dice and got " + str(successes) + " successes."
            for message in self.last_roll:
                #find dice value
                value = ''.join(x for x in message[len(self.stats['user id']) + 1:] if x.isdigit())
                if "exploded" in message:
                    out += "(" + value + ")"
                elif "rote" in message:
                    out += " Rote:" + value
                else:
                    out += " " + value

            messages.append(out)
                

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
