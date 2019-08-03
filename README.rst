===============================================================================
 Name: 		Streamer's Annoy-A-Tron for Streamlabs Chatbot
 Version: 	0.0.0b1
 Creator: 	Belug
 Website:	https://github.com/belug23/Streamer-s-annoy-a-tron
===============================================================================

This allow the streamer to select some viewers by adding them in the `users.txt`
file, one user per line, and let them play annoying sounds at him.

===
To add sounds:
===
 1. Add the sound files in the sound folder
 2. Rename the file to `command.ext` where command is the name of the command you want the viewers to see and ext is the extensio of the file
 3. Reload the script in Chatbot

Exemple:
---
If you have the files `kids.mp3` and `boo.mp3` this will add the `!kids` and `!boo` command to the chatbot.

===
String placeholders
===

This script support some placeholders in the strings here's the list

 - {user} = Viewer's username
 - {helpCommand} = The help command that display conditions or list of sounds commands
 - {avail_sound_commands} = The list of sounds commands
 - {cd} = The cool down time left

Have fun.