import subprocess
import time

class App:
    def __init__(self, app, sg):
        self.app = app
        self.sg = sg


    def StartApp(self):
        proc = self.GetAppStat()
        if(proc == None):
            fname = ""
            if self.app.appSettings.settings["mixerConf"] != None:
                fname = " -c " + self.app.appSettings.settings["mixerConfPath"] + "/" + self.app.appSettings.settings["mixerConf"]
            bashCommand = self.app.appSettings.settings["jackMixerCommand"] + fname

            print(bashCommand)
            try:
                process = subprocess.Popen(bashCommand.split())
            except:
                print("jackMixer failed to start")

    def StopApp(self):
        proc = self.GetAppStat()
        if(proc != None):
            try:
                msg = (subprocess.check_output(["kill",proc[0]]))
                print(msg)
                self.app.window['jackMixerStat'].update("msg", text_color='Yellow')
                while(self.GetAppStat() != None):
                    time.sleep(100/1000)

            except:
                print("jackMixer failed to stop")

    def GetAppStat(self):
        try:
            app = (subprocess.check_output('pgrep -f "python3.*jack_mixer" -l | grep -v "sh"', shell = True))
            #print("stat")
            #app = app.decode("utf-8")
            app = app.split()
        except Exception as e:
            app = None;

        return app;

    def Loadmixer(self,fname):
        self.StopApp()
        self.SetMixer(fname)
        self.StartApp()

    def SetMixer(self,fname):
        if self.app.currentMixerBtn != None:
            self.app.window[self.app.currentMixerBtn].update(button_color=self.sg.theme_button_color())
        self.app.window[self.app.mixerButtons[fname]].update(button_color='Red')
        self.app.currentMixerBtn = self.app.mixerButtons[fname]
        self.app.appSettings.settings["mixerConf"] = fname
        self.app.appSettings.SaveSettings()
