
import json
import os.path
import subprocess
import re
import time

class AjSnapshot:
    def __init__(self, app, sg):
        self.app = app
        self.sg = sg
    def WriteSnapshot(self, fname):
        bashCommand = "aj-snapshot -f ./" + fname
        process = subprocess.Popen(bashCommand.split())

    def SetSnapshot(self,fname):
        if self.app.currentSnapBtn != None:
            self.app.window[self.app.currentSnapBtn].update(button_color=self.sg.theme_button_color())
        self.app.window[self.app.snapButtons[fname]].update(button_color='Red')
        self.app.currentSnapBtn = self.app.snapButtons[fname]
        self.app.appSettings.settings["snapshot"] = fname
        self.app.appSettings.SaveSettings()

    def LoadSnapshot(self,fname):
        self.StopDaemon()
        self.SetSnapshot(fname)
        self.StartDaemon()

    def StartDaemon(self):
        proc = self.GetDaemonStat()
        CoL = ""
        if self.app.window["clear-on-load"].get():
            CoL = " -x"
        if(proc == None):
            bashCommand = "aj-snapshot" + CoL + " -d ./" + self.app.appSettings.settings["snapshot"]
            print(bashCommand)
            try:
                process = subprocess.Popen(bashCommand.split())
            except Exception as e:
                print(e)

    def StopDaemon(self):
        proc = self.GetDaemonStat()
        if(proc != None):
            try:
                msg = (subprocess.check_output(["kill",proc[0]]))
                print(msg)
                self.app.window['ajsStat'].update("msg", text_color='Yellow')
                while(self.GetDaemonStat() != None):
                    time.sleep(100/1000)

            except Exception as e:
                print(e)

    def GetDaemonStat(self):
        try:
            daemon = (subprocess.check_output(["pidof","aj-snapshot"]))
            daemon = daemon.decode("utf-8")
            daemon = daemon.split()
        except :
            daemon = None;

        return daemon;
