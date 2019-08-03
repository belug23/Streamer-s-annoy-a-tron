import codecs
import ctypes
import json
import os
import sys

ScriptName = "Streamer's Annoy-A-Tron"
Website = "https://github.com/belug23/Streamer-s-annoy-a-tron"
Description = "Allow permited viewers to play a list of sounds."
Creator = "Belug"
Version = "1.0.0RC1"


class ChadBot(object):
    """ 
    Because I hate coding with only functions and using Global variables.
    Here is the Chad bot for the Streamer's Annoy-A-Tron.
    This simple script allow the streamer to expose sound commands
    to a list of specific viewer, in this case a list of patreon viewers.
    """
    config_file = "config.json"

    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.user_file = "users.txt"
        self.user_file_path = os.path.join(self.base_path, self.user_file)
        self.settings = {}
        self.allowedUsers = []
        self.commands = []
        self.volume = 0.1
        self.sounds_path = ""
        self.sounds_db = {}
        self.avail_sound_commands = ""
        self.parent = None

    def setParent(self, parent):
        self.parent = parent

    def setConfigs(self):
        self.loadSettings()

        # Set the sound folder
        self.sounds_path = os.path.join(self.base_path, "sounds")

        # Set the true volume for streamlabs Chatbot
        self.volume = self.settings["volume"] / 1000.0

        # Load sounds from the folder
        sounds = os.listdir(self.sounds_path)	
        self.commands = []

        # For each sound file set a command for it.
        for	sound in sounds:
            sound_name = sound.rsplit('.', 1)
            sound_command = "!{}".format(sound_name[0]).lower()
            self.commands.append(sound_command) 
            self.sounds_db[sound_command] = sound
        
        with open(self.user_file_path) as user_list:
            self.allowedUsers = [user.lower().strip('\n') for user in user_list]

        # Set the text message to list all the sounds
        self.avail_sound_commands = self.settings["commandsSeparator"].join(self.commands)

    def loadSettings(self):
        """
            This will parse the config file if present.
            If not present, set the settings to some default values
        """
        try:
            with codecs.open(os.path.join(self.base_path, self.config_file), encoding='utf-8-sig', mode='r') as file:
                self.settings = json.load(file, encoding='utf-8-sig')
        except Exception:
            self.settings = {
                "liveOnly": True,
                "helpCommand": "!AnnoyMe",
                "permission": "Everyone",
                "soundPermission": "Regular",
                "volume": 50.0,
                "useCooldown": True,
                "useCooldownMessages": True,
                "cooldown": 60,
                "onCooldown": "{user}, {command} is still on cooldown for {cd} minutes!",
                "userCooldown": 180,
                "onUserCooldown": "{user}, {command} is still on user cooldown for {cd} minutes!",
                "commandsSeparator" : ", ",
                "notPermitedResponse" : "To annoy the streamer you must be a member of his patreon : https://www.patreon.com/",
                "permitedResponse" : "Available sound commands: {avail_sound_commands}",
            }

    def scriptToggled(self, state):
        """
            Do an action if the state change. Like sending an announcement message
        """
        return

    def execute(self, data):
        """
            Parse the data sent from the bot to see if we need to do something.
        """
        # If it's from chat and the live setting correspond to the live status
        if self.canParseData(data):
            # If it's the defined help command
            if data.GetParam(0).lower() == self.settings["helpCommand"].lower():
                return self.helpMessage(data)
            # Else if it's one of the sound commands
            elif data.GetParam(0).lower() in self.commands:
                return self.playAnnoyingSound(data)
        return
    
    def canParseData(self, data):
        return (
            data.IsChatMessage() and
            (
                (self.settings["liveOnly"] and self.parent.IsLive()) or 
                (not self.settings["liveOnly"])
            )
        )
    
    def isOnCoolDown(self, data, command):
        if (
            self.settings["useCooldown"] and
            (self.parent.IsOnCooldown(ScriptName, command) or
            self.parent.IsOnUserCooldown(ScriptName, command, data.User))
        ):
            self.sendOnCoolDownMessage(data, command)
            return True
        else:
            return False
    
    def sendOnCoolDownMessage(self, data, command):
        if self.settings["useCooldownMessages"]:
            commandCoolDownDuration = self.parent.GetCooldownDuration(ScriptName, command)
            userCoolDownDuration = self.parent.GetUserCooldownDuration(ScriptName, command, data.User)

            if commandCoolDownDuration > userCoolDownDuration:
                cdi = commandCoolDownDuration
                message = self.settings["onCooldown"]
            else:
                cdi = userCoolDownDuration
                message = self.settings["onUserCooldown"]
            
            cd = str(cdi / 60) + ":" + str(cdi % 60).zfill(2) 
            self.sendMessage(data, message, command=command, cd=cd)
        

    def helpMessage(self, data):

        # If it's still on cool down
        if not self.isOnCoolDown(data, self.settings["helpCommand"]) and self.parent.HasPermission(data.User, self.settings["permission"], ""):
            if data.UserName.lower() in self.allowedUsers:
                self.sendMessage(data, self.settings["permitedResponse"])
            else:
                self.sendMessage(data, self.settings["notPermitedResponse"])
            
            self.setCoolDown(data, self.settings["helpCommand"])
    
    def playAnnoyingSound(self, data):
        sound = data.GetParam(0).lower()
        if (not self.isOnCoolDown(data, sound) and
                self.parent.HasPermission(data.User, self.settings["soundPermission"], "") and
                data.UserName.lower() in self.allowedUsers):

            if sound in self.sounds_db:
                soundpath = os.path.join(self.sounds_path, self.sounds_db[sound])
                if self.parent.PlaySound(soundpath, self.volume):
                    self.setCoolDown(data, sound)

    def setCoolDown(self, data, command):
        if self.settings["useCooldown"]:
            self.parent.AddUserCooldown(ScriptName, command, data.User, self.settings["userCooldown"])
            self.parent.AddCooldown(ScriptName, command, self.settings["cooldown"])


    def sendMessage(self, data, message, command=None, cd="0"):
        if command is None:
            command = self.settings["helpCommand"]

        outputMessage = message.format(
            user=data.UserName,
            cost=str(None),  # not used
            currency=self.parent.GetCurrencyName(),
            command=command,
            avail_sound_commands=self.avail_sound_commands,
            cd=cd
        )
        self.parent.SendStreamMessage(outputMessage)

    def tick(self):
        """
        not used, here for maybe future projects.
        """
        return
    
    def openReadMe(self):
        location = os.path.join(os.path.dirname(__file__), "README.txt")
        if sys.platform == "win32":
            os.startfile(location)  # noqa windows only
        else:
            import subprocess
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, location])
        return


chad_bot = ChadBot()
# Ugly StreamLab part, just map functions to the class
def ScriptToggled(state):
    return chad_bot.scriptToggled(state)

def Init():
    chad_bot.setParent(Parent)  # noqa defined by streamlabs chatbot
    return chad_bot.setConfigs()

def Execute(data):
    return chad_bot.execute(data)

def ReloadSettings(jsonData):
    return chad_bot.setConfigs()

def OpenReadMe():
    return chad_bot.openReadMe()

def Tick():
    return chad_bot.tick()
