#cwod dice roller UI version
#By Roy Healy
#Client for rolling dice into a designated Discord channel
#Current features:
#   Dice rolls (loud or quiet)
#   Send details of last roll
#   If rate limit reached, will wait and try sending again to channel
#   If Discord error received, prints in client
    

import http.client
import string
import random
import time
from character import Character
from tkinter import *

def send(message, webhook):
    '''
    Sends message to webhook
    '''
    
    conn = http.client.HTTPSConnection("discordapp.com")
    sep = "--" + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
    payload = sep + "\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + message + "\r\n" + sep + "--"



    headers = {
    'content-type': "multipart/form-data; boundary=" + sep[2:],
    'cache-control': "no-cache",
    }

    conn.request("POST", webhook, payload, headers)

    res = conn.getresponse()
    data = res.read()

    if data.decode("utf-8") != "":
        #occures if error sending webhook, usually a rate limit approached
        if "rate limited" in data.decode("utf-8"):
            #confirms that is is a rate limit
            index1 = data.decode("utf-8").find('"retry_after"')
            chop = data.decode("utf-8")[index1+13:]
            wait = ''
            for character in chop:
                #find the wait time requested
                #given in miliseconds usually
                if character in '0123456789':
                    wait += character
                if character == '\n':
                    break
            
            #wait will given in miliseconds, will add 0.5 just in case
            wait = int(wait)/1000 + 0.5
            #update console, should always be at least a 3 digit numbers.
            console.config(text= "Rate limit hit. Will try again in " + str(wait)[:4] + " seconds.")
            console.update_idletasks()
            
            time.sleep(wait)
            #try again after wait
            send(message, webhook)
        else:
            #Unexpected problem - Result printed to client console.
            index1 = data.decode("utf-8").find('"message"')
            index2 = data.decode("utf-8").find('\n', index1)
            chop = data.decode("utf-8")[index1:index2]
            console.config(text=chop)
            console.update_idletasks()

def chance_handler():
    '''
    Handler for chance roll button.
    '''
    
    #Check if details entered yet
    if webhook.get() == "" or userID.get() == "":
        #Tell user something is missing
        console.config(text= "User Details Missing.")
        return
    
    console.config(text= "Starting Chance Roll.")
    console.update_idletasks()

    messages = char.roll_chance()

    #waits a random amount of time, used to help prevent multiple users spamming channel at once
    wait = random.uniform(0.1, 0.4)
    time.sleep(round(wait, 2))

    
    for message in messages:
        send(message, webhook.get())
        time.sleep(1)

    #Prints final result to client console
    console.config(text=messages[-1].replace(char.ID,"You"))
    

def roll_handler():
    '''
    Handler for roll button.
    '''    
    #Check if details entered yet
    if webhook.get() == "" or userID.get() == "":
        #Tell user something is missing
        console.config(text= "User Details Missing.")
        return


    console.config(text= "Starting Roll.")
    console.update_idletasks()

    try:
        #check if int entered
        dice_number = int(dice.get())
    except ValueError:
        console.config(text= "Please enter a positive whole number.")
        return
        

    if dice_number < 1:
        #check if positive number entered
        console.config(text= "Please enter a positive whole number.")
        return
    
    try:
        #Try a roll. If error occurs will post this.
        #Must implement: traceback display in client.
        messages = char.roll_set(dice_number, rote.get(), again.get(), quiet.get())
    except:
        console.config(text= "Unknown Error occured during roll.")
        return

    #wait a random amount of time, used to help prevent multiple users spamming channel at once
    wait = random.uniform(0.0, 0.5)
    time.sleep(round(wait, 2))

    #Send each message one by one
    for message in messages:
        send(message, webhook.get())
        #wait one second each time to prevent spam + add drama!
        time.sleep(1)

    #Put final result in client console
    console.config(text=messages[-1].replace(" for " + char.ID,""))
    

def last_roll_handler():
    '''
    Handler for last roll button.
    '''
    #Check if details entered yet
    if webhook.get() == "" or userID.get() == "":
        #Tell user something is missing
        console.config(text= "User Details Missing.")
        return
    
    if char.last_roll == []:
        console.config(text= "No previous roll saved.")
        return

    messages = char.get_last_roll()

    #wait a random amount of time, used to help prevent multiple users spamming channel at once
    wait = random.uniform(0.0, 0.5)
    time.sleep(round(wait, 2))

    for message in messages:
        send(message, webhook.get())
        time.sleep(1)

    console.config(text="Results sent to channel.")

def setup_screen():
    '''
    Creates screen for user set up
    '''
    
    def save_setup():
        '''
        Function to saves setup and close window
        '''
        global char
        #char will be a global Character object
        
        webhook.set(webhook_entry.get())
        userID.set("<@" + userID_entry.get() + ">")
        
        top.destroy()
        if webhook.get() == "" or userID.get() == "":
            return
        else:
            console.config(text= "Details saved!")
            char = Character(userID.get())
    
    #code for window UI
    top = Tk()
    top.title("Enter Details")
    webhook_entry = Entry(top, textvariable=webhook, width= 25)
    userID_entry = Entry(top, textvariable=userID, width= 25)
    save_button = Button(top, text ="Save and Close", command = save_setup)

    webhook_label = Label(top, text="Webhook URL")
    userID_label = Label(top, text="Discord UserID")

    webhook_label.grid(column=0, pady=5, padx=5)
    userID_label.grid(column=0, pady=5, padx=5)

    webhook_entry.grid(row = 0, column=1, pady=5, padx=5, sticky=W)
    userID_entry.grid(row = 1, column=1, pady=5, padx=5)
    save_button.grid(pady=5, padx=5)
    webhook_entry.insert(0, webhook.get())
    userID_entry.insert(0, userID.get()[2:-1])
    
    top.mainloop()

#Main window UI
if __name__ == '__main__':
    root = Tk()
    rote = BooleanVar()
    userID = StringVar()
    again = IntVar()
    again.set(10)
    dice = StringVar()
    quiet = BooleanVar()
    webhook = StringVar()

    menubar = Menu(root)
    root.title("Discord Dice Roller")
    menubar.add_command(label="Show User Details", command=setup_screen)
    root.config(menu=menubar)

    dice_label = Label(root, text="Enter Dice Pool")
    dice_entry = Entry(root, textvariable=dice, width= 3)

    rote_check = Checkbutton(root, text = "Rote", variable = rote, onvalue = True, offvalue = False)

    rote_check.grid(row = 1, column=0, pady=5)

    quiet_check = Checkbutton(root, text = "Quiet Mode", variable = quiet, onvalue = True, offvalue = False)

    quiet_check.grid(row = 1, column=1, pady=5)

    last_roll_button = Button(root, text ="Display Last Roll", command = last_roll_handler)

    again10 = Radiobutton(root, text="10 again", variable=again, value=10)
    again9 = Radiobutton(root, text="9 again", variable=again, value=9)
    again8 = Radiobutton(root, text="8 again", variable=again, value=8)

    again10.grid(row = 0, column = 2, pady=5)
    again9.grid(row = 1, column = 2, pady=5)
    again8.grid(row = 2, column = 2, pady=5)

    dice_label.grid(row = 0, column=0, pady=5, sticky=W)
    dice_entry.grid(row = 0, column=0, pady=5, sticky=E)

    roll_button = Button(root, text ="Roll", command = roll_handler)
    chance_button = Button(root, text ="Chance Roll", command = chance_handler)

    roll_button.grid(row = 0, column = 1, padx=5, pady=5)
    chance_button.grid(row = 2, column = 1, padx=5, pady=5)
    last_roll_button.grid(row = 2, column=0, padx=5, pady=5, sticky = E)

    console = Label(root, text="Please Enter User Details", bg = "grey", width = 50)
    console.grid(row = 4, columnspan = 3)
    
    root.mainloop()
