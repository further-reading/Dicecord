# Discord Dice Roller
A python based client for rolling dice and printing results in Discord channel via webhooks. Uses Chronicles of Darkenss ruleset.

## Instructions
![Client](https://raw.githubusercontent.com/further-reading/Discord-Dice-Roller/master/client.PNG "Client")  
Before rolling you need to add your user details. Click on "Show User Details" on top left of window and enter the following:
* Webhook URL: A [webhook](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks) for the channel that will share your rolls.
* Discord UserID: A numerical ID for your Discord username. You can get this by activating developer mode, right clicking on your name and selecting "Copy ID." When the correct ID is entered the results will include @mentions for you, which can make it easier to identify your own rolls.

When these items are added you will be able to make rolls. By default it will do a normal Chronicles of darkenss roll (rolls a number of D10s, 8 or above is a success, 10s grant additional rerolls).  
After making the roll, the client will post the result of each die to the channel before telling the final results. To avoid rate limiting (and add drama!) each message is sent after a delay of a second.  
Once the total successes are printed on the channel it will display it in the client too.  
You can change whether it is 10, 9 or 8 again using the radio buttons on the right.  
Checking the "Rote" box turns it into a rote roll, where any dice at 7 or less is rerolled once.  
Checking the "Quiet Mode" box will skip the one by one die reporting and just print total successes.  
"Display Last Roll" will print the result of each die of the last roll. This will record rolls in "Quiet Mode" too, in case you change your mind!  
The Chance Roll button rolls a chance die. On a chance die, only a 10 is a success but a 1 is a botch (critical failure). Also 10s are no longe rerolled.  

## Note On Rate Limit
Webhooks have a "rate limit" that will cause commands to fail if too many are sent in quick succession. Generally, if more than 3 people are rolling at once you will hit the rate limit. When this happens the server will return an error that states the time needed to wait, the client will try again after waiting about half a second longer than the message advises. It will tell the user that a rate limit is hit and how long it will be until the next attempt to send the message.

One way to completely avoid the rate limit is to create a dedicated webhook for each player. The downside of this approach is that the channel becomes pretty hard to read unless switched to compact mode.

## Other planned features
* Fix "Show User Details" so it will actually show them if clicked again after they were entered.
* Show the last roll in a local text box rather than sending to the channel.
* Display tracebacks of unhandled errors to user.
* Error handling for other webhook errors. At present, chances are that the final totals will be displayed in the client anyway.
* Custom message for exceptional success.
* Extended rolls.
* Additional client messaging.
