#!/bin/python3
import PySimpleGUI as sg
import json
import os
import subprocess
import re
import time
import ajsnapshot
import jackServer
import a2j
import jMixer
import optionsWin


class AppSettings:
    settings = {}

    def SaveSettings(self):
        with open('settings.json', 'w') as json_file:
          json.dump(self.settings, json_file)

    def LoadSettings(self):
        if not os.path.isfile("settings.json"):
            self.settings = {"snapshot": "default",
                    "snapshotPath": "~/.local/share/aj-smapshot",
                    "snapshotFiles": ['default'],
                    "clear-on-load": False,
                    "jackCommand": "jackd -d alsa -P hw:PCH,0 -C hw:PCH,0 -r 48000 -n 3",
                    "a2jCommand": "/usr/bin/a2j_control --ehw --start",
                    "mixer-files":[],
                    "mixerConf":None,
                    "mixerConfPath":"~/.local.share/jack_mixer",
                    "jackMixerCommand":"jack_mixer"
                    }
            self.SaveSettings()
            print(self.settings)
        else:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)

class btnEvent:

    def __init__(self, key, func):
        self.key = key
        self.func = func
    def __str__(self):
        return self.key
    def do(self):
        self.func(self.key)

class App:
    def __init__(self):
        self.currentSnapBtn = None
        self.currentMixerBtn = None
        self.snapButtons = {}
        self.mixerButtons = {}
        self.window = None

        self.appSettings = AppSettings()
        self.ajs = ajsnapshot.AjSnapshot(self, sg)
        self.jackd = jackServer.Jack(self, sg)
        self.a2j = a2j.a2jmidid(self, sg)
        self.jackMixer = jMixer.App(self, sg)

    def DeleteSnapshot(self, fname):
        self.appSettings.settings['snapshotFiles'].remove(fname)
        self.snapButtons.pop(fname, None)
        self.window.close()
        self.LoadWindow()


    def DeleteMix(self, fname):
        self.appSettings.settings['mixer-files'].remove(fname)
        self.mixerButtons.pop(fname, None)
        self.window.close()
        self.LoadWindow()

    def updateajsStat(self):
        stat = self.ajs.GetDaemonStat()
        if stat == None:
            self.window['ajsStat'].update("Stopped", text_color='Red')
            self.window['ajsBtn'].update("Start")
        else:
            self.window['ajsStat'].update("Running", text_color='Green')
            self.window['ajsBtn'].update("Stop")
        self.window.refresh()

    def updateJackStat(self):
        stat = self.jackd.GetDaemonStat()
        if stat == None:
            self.window['jackStat'].update("Stopped", text_color='Red')
            self.window['jackBtn'].update("Start")
        else:
            self.window['jackStat'].update("Running", text_color='Green')
            self.window['jackBtn'].update("Stop")
        self.window.refresh()

    def updateA2JStat(self):
        stat = self.a2j.GetDaemonStat()
        if stat == None:
            self.window['a2jStat'].update("Stopped", text_color='Red')
            self.window['a2jBtn'].update("Start")
        else:
            self.window['a2jStat'].update("Running", text_color='Green')
            self.window['a2jBtn'].update("Stop")
        self.window.refresh()

    def updatejackMixerStat(self):
        stat = self.jackMixer.GetAppStat()
        #print(stat)
        if stat == None:
            self.window['jackMixerStat'].update("Stopped", text_color='Red')
            self.window['jackMixerBtn'].update("Start")
        else:
            self.window['jackMixerStat'].update("Running", text_color='Green')
            self.window['jackMixerBtn'].update("Stop")
        self.window.refresh()

    def ReloadAudio(self):
        self.jackd.StopDaemon()
        self.a2j.StopDaemon()
        self.jackMixer.StopApp()
        self.ajs.StopDaemon()

        time.sleep(300/1000)

        self.jackd.StartDaemon()
        time.sleep(100/1000)
        self.a2j.StartDaemon()
        time.sleep(100/1000)
        self.jackMixer.StartApp()
        self.ajs.StartDaemon()

    def LoadWindow(self):
        menu_def = [ ['&Edit', ['&Options'] ] ]

        #####
        ajsStatText = [sg.Text("aj-snapshot ="), sg.Text("Stopped", text_color='Red', key='ajsStat'), sg.Button('start', key='ajsBtn')]

        if self.ajs.GetDaemonStat() != None:
            ajsStatText = [sg.Text("aj-snapshot ="), sg.Text("Running", text_color='Green', key='ajsStat'), sg.Button('stop', key='ajsBtn')]

        ajSnapshotFrame = [[], [sg.HorizontalSeparator()], ajsStatText, [sg.Button('Take Snapshot'), sg.Button('Add Snapshot', tooltip="Add existing snapshot file"), sg.Checkbox('Clear Connections', key = "clear-on-load",
            tooltip = 'Clear jack connections when changing snapshot', default=self.appSettings.settings["clear-on-load"] )]]

        for fname in self.appSettings.settings["snapshotFiles"]:
            self.snapButtons[fname] = btnEvent(fname, self.ajs.LoadSnapshot)
            right = ["edit",["cancel", 'delete::snap ' + fname]]
            if fname == self.appSettings.settings["snapshot"]:
                self.currentSnapBtn=self.snapButtons[fname]
                color='Red'
            else:
                color=sg.theme_button_color()
            ajSnapshotFrame[0].append(sg.Button(fname, key=self.snapButtons[fname], right_click_menu = right, button_color=color ))
        ####
        jackStatText = [sg.Text("Jack ="), sg.Text("Stopped", text_color='Red', key='jackStat'), sg.Button('start', key='jackBtn')]
        if self.jackd.GetDaemonStat() != None:
            jackStatText = [sg.Text("Jack ="), sg.Text("Running", text_color='Green', key='jackStat'), sg.Button('stop', key='jackBtn')]
        jackFrame = [jackStatText]

        ####
        a2jStatText = [sg.Text("a2jmidid ="), sg.Text("Stopped", text_color='Red', key='a2jStat'), sg.Button('start', key='a2jBtn')]
        if self.a2j.GetDaemonStat() != None:
            a2jStatText = [sg.Text("a2jmidid ="), sg.Text("Running", text_color='Green', key='a2jStat'), sg.Button('stop', key='a2jBtn')]
        a2jFrame = [a2jStatText]

        ####
        jackMixerStatText = [sg.Text("jack_mixer ="), sg.Text("Stopped", text_color='Red', key='jackMixerStat'), sg.Button('start', key='jackMixerBtn')]
        if self.jackMixer.GetAppStat() != None:
            jackMixerStatText = [sg.Text("jack_mixer ="), sg.Text("Running", text_color='Green', key='jackMixerStat'), sg.Button('stop', key='jackMixerBtn')]
        jackMixerFrame = [[], [sg.HorizontalSeparator()], jackMixerStatText, [sg.Button('Add Mixer Config', key="addMixConf")]]

        for fname in self.appSettings.settings["mixer-files"]:
            self.mixerButtons[fname] = btnEvent(fname, self.jackMixer.Loadmixer)
            right = ["edit",["cancel", 'delete::mixer ' + fname]]
            if fname == self.appSettings.settings["mixerConf"]:
                self.currentMixerBtn=self.mixerButtons[fname]
                color='Red'
            else:
                color=sg.theme_button_color()
            jackMixerFrame[0].append(sg.Button(fname, key=self.mixerButtons[fname], right_click_menu = right, button_color=color ))


        layout = [  [sg.Menu(menu_def)],
                    [sg.Button('Reload Audio System')],
                    [sg.HorizontalSeparator()],
                    [sg.Frame('Jack Server', jackFrame, font='Any 12', key='jackserver')],
                    [sg.Frame('A2J Daemon', a2jFrame, font='Any 12', key='a2jdaemon')],
                    [sg.Frame('Jack Mixer', jackMixerFrame, font='Any 12', key='jackMixerApp')],
                    [sg.Frame('Jack Connection Snapshots', ajSnapshotFrame, font='Any 12', key='snapshots')],
                    [sg.Button('Exit')] ]
        self.window = sg.Window('Jack Load-In', layout, icon="./flight-case (128).png", finalize=True)


    def StartApp(self):
        self.appSettings.LoadSettings()

        sg.theme('DarkGrey13')
        print(sg.theme_button_color())


        self.LoadWindow()
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = self.window.read(200)
            # print(event)
            if event == 'ajsBtn':
                stat = self.ajs.GetDaemonStat()
                if stat == None:
                    self.ajs.StartDaemon()
                else:
                    self.ajs.StopDaemon()

            if event == 'jackBtn':
                stat = self.jackd.GetDaemonStat()
                if stat == None:
                    self.jackd.StartDaemon()
                else:
                    self.jackd.StopDaemon()

            if event == 'a2jBtn':
                stat = self.a2j.GetDaemonStat()
                if stat == None:
                    self.a2j.StartDaemon()
                else:
                    self.a2j.StopDaemon()

            if event == 'jackMixerBtn':
                stat = self.jackMixer.GetAppStat()
                if stat == None:
                    self.jackMixer.StartApp()
                else:
                    self.jackMixer.StopApp()

            if event == 'addMixConf':
                # print(os.getcwd())
                fnames = sg.popup_get_file('Select Mixer File',
                    title = 'Mixer File',
                    modal = True,
                    initial_folder=self.appSettings.settings["mixerConfPath"],
                    multiple_files = True,
                    no_window = True)
                print(fnames)
                if len(fnames) > 0:
                    for fname in fnames:
                        fname = os.path.basename(fname)
                        if fname not in self.appSettings.settings["mixer-files"]:
                            self.appSettings.settings["mixer-files"].append(fname)
                    self.appSettings.SaveSettings()
                    self.window.close()
                    self.LoadWindow()

            if event == 'Add Snapshot':
                fnames = sg.popup_get_file('Select Snapshot File',
                    title = 'Snapshot File',
                    modal = True,
                    initial_folder=self.appSettings.settings["snapshotPath"],
                    multiple_files = True,
                    no_window = True)
                if len(fnames) > 0:
                    for fname in fnames:
                        if fname not in self.appSettings.settings["snapshotFiles"]:
                            self.appSettings.settings["snapshotFiles"].append(fname)
                            self.appSettings.SaveSettings()
                    self.window.close()
                    self.LoadWindow()

            if event == 'Take Snapshot':
                name = sg.popup_get_text('Name this snapshot',
                    title = 'Snapshot Name',
                    modal = True,
                    default_text = self.appSettings.settings["snapshot"])
                if name != None and name != '':
                    if name not in self.appSettings.settings["snapshotFiles"]:
                        self.appSettings.settings["snapshotFiles"].append(name)
                        self.appSettings.SaveSettings()
                    self.ajs.WriteSnapshot(name)
                    self.window.close()
                    self.LoadWindow()

            if event == 'Options':
                win = optionsWin.opWin(self, sg)
                win.show()

            if event == 'Reload Audio System':
                self.ReloadAudio()

            if isinstance(event, btnEvent):
                event.do()
            if str(event).startswith('delete::snap'):
                print(event.split())
                self.DeleteSnapshot(event.split()[1])
            if str(event).startswith('delete::mixer'):
                print(event.split())
                self.DeleteMix(event.split()[1])
            if event == sg.WIN_CLOSED or event == 'Exit':
                self.appSettings.settings["clear-on-load"] = self.window["clear-on-load"].get()
                self.appSettings.SaveSettings()
                break
            self.updateajsStat()
            self.updateJackStat()
            self.updateA2JStat()
            self.updatejackMixerStat()


        self.window.close()

theApp = App()
theApp.StartApp()
