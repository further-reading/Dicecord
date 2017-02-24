# Dicecord - A Discord Diceroller and Character Sheet
A python based client for dispalying character sheets, rolling dice and printing results to a Discord chat channel. Uses Chronicles of Darkenss ruleset.

Image Placeholder Here

## Character Sheet
In the current build it displays the character sheet for Mage: the Awakening modern eras. The client shows three tabs: Stats, Inventory and Notes.

### Edit Mode
In Edit Mode you change all of your character details. To activate edit mode click the edit button in the toolbar:
Image Placeholder Here.

#### Remove Dots
To remove all dots from a skill, click the first dot twice.

#### Skill Specialties
To add a skill specialty, click the skill name in edit mode. A dialogue will appear that allows you to set further details. Any skills with specialties will be bolded.

#### Edit Entry Details
Merit, Condition, Aspiration and Obsession tooltips can be edited by clicking the item's name while in edit mode. A dialogue will appear allowing you to input changes, or you can press the "delete" button to clear the entry from the character entirely.

### Free Edit
Edit mode will generally only restrict editing of items that should cost XP to change. The following items can be changed even when edit mode is inatcive:

- XP/Arcane XP
- Beats/Arcane Beats
- Modifiers
- Spent Mana
- Health damage
- Willpower spent

## Inventory
The Inventory tab shows a set of items/knowledge that the character posesses. Some widgets in this tab will calculate base dicepools associated with each entry.

### Edit Mode
Active Spells and Weapons can be changed at all times. All other widgets here require edit mode to be active.

### Enchanted Items and Mana
Enchanted items will update the mana widget on the stats page when new items are added. Note that there is a bug in the current version where this causes the mana object to appear squashed. To fix, save thw character and reopen it.

## Save and Import
Characters are saved as .xml files. Saved characters can be imported into the tool by sleecting file -> open in the top menu. If unsaved changes are dtected on the deactivation of edit mode or client exit a dialogue will appear asking the user to save changes.

## Roll Instructions
To open the roller, press the Dicecord symbol in the toolbar.
Image Placeholder Here
![Client](https://raw.githubusercontent.com/further-reading/Dicecord/master/client.png "Client")  
Before rolling you need to add your user details to the character sheet.
* Webhook URL: A [webhook](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks) for the channel that will share your rolls.
* Discord UserID: A numerical ID for your Discord username. You can get this by activating developer mode, right clicking on your name and selecting "Copy ID." When the correct ID is entered the results will include @mentions for you, which can make it easier to identify your own rolls.

When these items are added you will be able to make rolls. By default it will do a normal Chronicles of Darkness roll (rolls a number of D10s, 8 or above is a success, 10s grant additional rerolls).  
After making the roll, the client will post the result of each die to the channel before telling the final results. To avoid rate limiting (and add drama!) each message is sent after a delay of a second.  
Once the total successes are printed on the channel it will display it in the client too.  
You can change whether it is 10, 9 or 8 again using the radio buttons on the right.  
Checking the "Rote" box turns it into a rote roll, where any dice at 7 or less is rerolled once.  
Checking the "Quiet Mode" box will send a one line summary of the roll. 
To display your last roll, press Ctrl + H or go to File -> Show Last Roll. Quiet mode rolls will also be saved here.
The Chance Roll button rolls a chance die. On a chance die, only a 10 is a success but a 1 is a botch (critical failure). Also 10s are no longe rerolled.  

## Note On Rate Limit
Webhooks have a "rate limit" that will cause commands to fail if too many are sent in quick succession. Generally, if more than 3 people are rolling at once you may hit the rate limit. The client will try to avoid this by waiting extra when the remaining messages on the current refresh are low. If a rate limit is hit Discord will return an error which states when the limit will refresh, the client will wait about half a second longer than its suggestion and try sending the result again.

One way to avoid the rate limit is to create a dedicated webhook for each player. The downside of this approach is that the channel becomes pretty hard to read unless switched to compact mode.

## Other planned features
* Error handling for other webhook errors. Note that the final totals will be displayed in the client anyway.
* Custom message for exceptional success.
* Extended rolls.
* Additional client messaging.
* Dark era conversion.
* Additional CofD splats.
