import subprocess
import time

class a2jmidid:
    def __init__(self, app, sg):
        self.app = app
        self.sg = sg


    def StartDaemon(self):
        proc = self.GetDaemonStat()
        if(proc == None):
            bashCommand = self.app.appSettings.settings["a2jCommand"]
            print(bashCommand)
            try:
                process = subprocess.Popen(bashCommand.split())
            except:
                print("a2jmidid failed to start")

    def StopDaemon(self):
        proc = self.GetDaemonStat()
        if(proc != None):
            try:
                msg = (subprocess.check_output(["kill",proc[0]]))
                print(msg)
                self.app.window['a2jStat'].update("msg", text_color='Yellow')
                while(self.GetDaemonStat() != None):
                    time.sleep(100/1000)

            except:
                print("a2jmidid failed to stop")

    def GetDaemonStat(self):
        try:
            daemon = (subprocess.check_output(["pidof","a2jmidid"]))
            daemon = daemon.decode("utf-8")
            daemon = daemon.split()
        except :
            daemon = None;

        return daemon;
