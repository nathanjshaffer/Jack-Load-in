
import subprocess
import time

class Jack:
    def __init__(self, app, sg):
        self.app = app
        self.sg = sg

    def DiscoverCommand(self):
        # ps -o cmd fp jackd
        process = None
        id = self.GetDaemonStat()
        if id != None:
            try:
                process = subprocess.check_output(["ps -o cmd fp " + id[0]], shell = True).decode("utf-8")
                process = process.split('\n')[1]
            except Exception as e:
                print(e)
        return process


    def StartDaemon(self):
        proc = self.GetDaemonStat()
        if(proc == None):
            bashCommand = self.app.appSettings.settings["jackCommand"]
            print(bashCommand)
            try:
                process = subprocess.Popen(bashCommand.split())
            except:
                print("sumting happen")

    def StopDaemon(self):
        proc = self.GetDaemonStat()
        if(proc != None):
            try:
                msg = (subprocess.check_output(["kill",proc[0]]))
                print(msg)
                self.app.window['jackStat'].update("msg", text_color='Yellow')
                while(self.GetDaemonStat() != None):
                    time.sleep(100/1000)

            except:
                print("sumting happen")

    def GetDaemonStat(self):
        try:
            daemon = (subprocess.check_output(["pidof","jackd"]))
            daemon = daemon.decode("utf-8")
            daemon = daemon.split()
        except :
            daemon = None;

        return daemon;
