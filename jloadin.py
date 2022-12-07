#!/bin/python3
import PySimpleGUI as sg
import json
import os
import subprocess
import re
import time
import module
import optionsWin

class jackMixerModule(module.AudioModuleWithProfiles):

    def GetCommand(self):
        command = self.cliCommand
        tmp = self.CLIArgs.copy()
        if self.profile == None:
            tmp.pop("fileOption")
        for arg in tmp.values():
            command += arg
        return command

class App:
    settings = {}
    window = None
    clearOnLoad = False
    eventHandlers = {}
    def __init__(self):
        self.jackd = module.AudioModule(self, sg, "Jack Audio Server", "jackd")
        self.ajSnapshot = module.AudioModuleWithProfiles(self, sg, "aj-snapshot", "aj-snapshot", False)
        self.ajSnapshot.CLIArgs["clearOnLoad"] = ""
        self.ajSnapshot.CLIArgs["daemonMode"] = " -d "
        self.ajSnapshot.CLIArgs["Profile"] = ""
        self.a2jmidid = module.AudioModule(self, sg, "a2jmidi Daemon", "a2jmidid")
        self.jackMixer = jackMixerModule(self, sg, "jack_mixer", "jack_mixer", False)
        self.jackMixer.CLIArgs["fileOption"] = " -c "
        self.jackMixer.CLIArgs["Profile"] = ""


    def SaveSettings(self):
        self.settings["clear-on-load"] = self.clearOnLoad
        self.jackd.SaveSettings()
        self.ajSnapshot.SaveSettings()
        self.a2jmidid.SaveSettings()
        self.jackMixer.SaveSettings()
        with open('settings.json', 'w') as json_file:
          json.dump(self.settings, json_file)

    def LoadSettings(self):
        if not os.path.isfile("settings.json"):
            self.jackd.cliCommand = "jackd -d alsa -P hw:PCH,0 -C hw:PCH,0 -r 48000 -n 3"
            self.ajSnapshot.path = "~/.local/share/aj-snapshot"
            self.ajSnapshot.cliCommand = "aj-snapshot"
            self.ajSnapshot.CLIArgs["Profile"] = ""
            self.a2jmidid.cliCommand = "/usr/bin/a2j_control --ehw --start"
            self.jackMixer.cliCommand = "jack_mixer"
            self.jackMixer.path = '~/.local/share/jack_mixer'
            self.jackMixer.CLIArgs["Profile"] = ""
            self.SaveSettings()
        else:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
                self.clearOnLoad = self.settings["clear-on-load"]
                self.SetClearOnLoad(self.clearOnLoad)
                self.jackd.LoadSettings()

                self.ajSnapshot.LoadSettings()
                if self.ajSnapshot.profile != None:
                    self.ajSnapshot.CLIArgs["Profile"] = self.ajSnapshot.path + "/" + self.ajSnapshot.profile

                self.a2jmidid.LoadSettings()

                self.jackMixer.LoadSettings()
                if self.jackMixer.profile != None:
                    self.jackMixer.CLIArgs["Profile"] = self.jackMixer.path + "/" + self.jackMixer.profile

    def ReloadAudio(self):
        self.jackd.StopModule()
        self.a2jmidid.StopModule()
        self.jackMixer.StopModule()
        self.ajSnapshot.StopModule()

        time.sleep(300/1000)

        self.jackd.StartModule()
        time.sleep(100/1000)
        self.a2jmidid.StartModule()
        time.sleep(100/1000)
        self.jackMixer.StartApp()
        self.ajs.StartModule()

    def LoadWindow(self):
        menu_def = [ ['&Edit', ['&Options'] ] ]


        ajSnapshotFrame = self.ajSnapshot.CreateFrame()
        ajSnapshotFrame[3].insert(0, sg.Button('Take Snapshot'))
        ajSnapshotFrame[3].insert(2, sg.Checkbox('Clear Connections', enable_events=True, key = "clear-on-load", tooltip = 'Clear jack connections when changing snapshot', default=self.clearOnLoad ))

        layout = [  [sg.Menu(menu_def)],
                    [sg.Button('Reload Audio System')],
                    [sg.HorizontalSeparator()],
                    [sg.Frame('Jack Server', self.jackd.CreateFrame(), font='Any 12', key='jackserver')],
                    [sg.Frame('A2J Daemon', self.a2jmidid.CreateFrame(), font='Any 12', key='a2jdaemon')],
                    [sg.Frame('Jack Mixer', self.jackMixer.CreateFrame(), font='Any 12', key='jackMixerApp')],
                    [sg.Frame('Jack Connection Snapshots', ajSnapshotFrame, font='Any 12', key='snapshots')],

                    [sg.Button('Exit')] ]
        self.window = sg.Window('Jack Load-In', layout, icon="./flight-case (128).png", finalize=True)

    def ReloadWindow(self):
        self.window.close()
        self.LoadWindow()

    def SetClearOnLoad(self, clearOnLoad):
        if clearOnLoad == True:
            self.ajSnapshot.CLIArgs["clearOnLoad"] = " -x"
        else:
            self.ajSnapshot.CLIArgs["clearOnLoad"] = ""


    def StartApp(self):
        self.LoadSettings()

        sg.theme('DarkGrey13')


        self.LoadWindow()
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = self.window.read(200)
            if event in self.eventHandlers:
                self.eventHandlers[event].do()
            if event == 'Take Snapshot':
                fname = sg.popup_get_text('Name this snapshot',
                    title = 'Snapshot Name',
                    modal = True,
                    default_text = self.ajSnapshot.profile)
                if fname != None and fname != '':
                    if fname not in self.ajSnapshot.profiles:
                        self.ajSnapshot.profiles.append(fname)
                        self.ajSnapshot.SaveSettings()
                        self.ajSnapshot.CLIArgs["Profile"] = self.ajSnapshot.path + "/" + self.ajSnapshot.profile
                    bashCommand = self.ajSnapshot.cliCommand + " -f " + self.ajSnapshot.CLIArgs["Profile"]
                    process = subprocess.Popen(bashCommand, shell = True)
                    self.SaveSettings()
                    self.ReloadWindow()

            if event == "clear-on-load":
                self.clearOnLoad = self.window["clear-on-load"].get()
                SetClearOnLoad(self.clearOnLoad)

            if event == 'Options':
                win = optionsWin.opWin(self, sg)
                win.show()

            if event == 'Reload Audio System':
                self.ReloadAudio()

            if isinstance(event, module.Event):
                event.do()
            if event == sg.WIN_CLOSED or event == 'Exit':
                self.SaveSettings()
                break

            self.jackd.UpdateStatusWindow()
            self.ajSnapshot.UpdateStatusWindow()
            self.a2jmidid.UpdateStatusWindow()
            self.jackMixer.UpdateStatusWindow()


        self.window.close()

theApp = App()
theApp.StartApp()
