# This file contains the default stats and general stat categories

ATTRIBUTE_TYPE = {'mental': ['intelligence', 'wits', 'resolve'],
                  'physical': ['strength', 'dexterity', 'stamina'],
                  'social': ['presence', 'manipulation', 'composure']
                  }

SKILL_TYPE = {'mental': ['academics',
                         'computer',
                         'crafts',
                         'enigmas',
                         'investigation',
                         'medicine',
                         'occult',
                         'politics',
                         'science'],
              'physical': ['archery',
                           'athletics',
                           'brawl',
                           'drive',
                           'firearms',
                           'larceny',
                           'ride',
                           'stealth',
                           'survival',
                           'weaponry'],
              'social': ['animal ken',
                         'empathy',
                         'expression',
                         'intimidation',
                         'persuasion',
                         'socialize',
                         'streetwise',
                         'subterfuge']}

STATS = {'skill specialties': {},
         'merits': {},
         'merit details': {},
         'size': 5,
         'conditions': {},
         'weapons': {},
         'aspirations': {},
         'willpower': 0,
         'willpower filled' : 0,
         'health': [0,  # max (derived)
                     0,  # bashing
                     0,  # lethal
                     0   # agg
                     ],
         'xp': 0,
         'beats': 0,
         'armor': 0,
         'initiative mod': 0,
         'size mod': 0,
         'speed mod': 0,
         'defense mod': 0}

SKILLS = list(SKILL_TYPE.values())
SKILLS = sum(SKILLS, [])
ATTRIBUTES = list(ATTRIBUTE_TYPE.values())
ATTRIBUTES = sum(ATTRIBUTES, [])
