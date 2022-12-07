
import subprocess
import time
import os


class Event:

    def __init__(self, func, *argv):
        self.argv = argv
        self.func = func
    def do(self):
        self.func(self.argv)

class AudioModule:



    def __init__(self, app, sg, name, exec, staticCLIArgs = True):
        self.app = app
        self.sg = sg
        self.name = name
        self.exec = exec
        self.path = None
        self.cliCommand = None
        self.staticCLIArgs = staticCLIArgs
        self.CLIArgs = {}
        self.filterShell = False

    def SaveSettings(self):
        if self.exec not in self.app.settings:
            self.app.settings[self.exec] ={}
        self.app.settings[self.exec]["CLICommand"] = self.cliCommand

    def LoadSettings(self):
        try:
            self.cliCommand = self.app.settings[self.exec]["CLICommand"]
        except:
            self.SaveSettings()

    def DiscoverCommand(self):
        if self.staticCLIArgs == True:
            command = None
            id = self.GetModuleStatus()
            if id != None:
                try:
                    command = subprocess.check_output(["ps -o cmd fp " + id], shell = True).decode("utf-8")
                    command = command.split('\n')[1]
                except Exception as e:
                    print(e)
            return command
        else:
            return self.GetCommand()

    def GetCommand(self):
        command = self.cliCommand
        for arg in self.CLIArgs.values():
            command += arg
        return command


    def StartModule(self):
        proc = self.GetModuleStatus()
        if(proc == None):
            try:
                process = subprocess.Popen(self.GetCommand(), shell = True)
            except Exception as e:
                print(e)

    def StopModule(self):
        proc = self.GetModuleStatus()
        if(proc != None):
            try:
                msg = (subprocess.check_output(["kill",proc]))
                self.app.window[self.exec+'Status'].update("Stopping...", text_color='Yellow')
                self.app.window.refresh()
                while(self.GetModuleStatus() != None):
                    time.sleep(100/1000)
            except Exception as e:
                print(e)

    def ToggleModule(self, *argv):
        stat = self.GetModuleStatus()
        if stat == None:
            self.StartModule()
        else:
            self.StopModule()

    def GetModuleStatus(self):
        try:
            command = 'pgrep -f '+ self.exec +' -l'
            pids = (subprocess.check_output(command , shell = True))
            pids = pids.decode("utf-8")
            pids = pids.strip()
            pids = pids.split('\n')
            proc = []
            for pid in pids:
                tmp = pid.split()
                if  tmp[1]!= "sh":
                    return tmp[0]

        except:
            return None;



    def UpdateStatusWindow(self):
        stat = self.GetModuleStatus()
        if stat == None:
            self.app.window[self.exec+'Status'].update("Stopped", text_color='Red')
            self.app.window[self.toggleEvent].update("Start")
        else:
            self.app.window[self.exec+'Status'].update("Running", text_color='Green')
            self.app.window[self.toggleEvent].update("Stop")
        self.app.window.refresh()


    def LoadModule(self):
        self.StopModule()
        self.StartModule()

    def CreateFrame(self):
        self.toggleEvent = Event(self.ToggleModule)
        if self.GetModuleStatus() == None:
            statusText = [self.sg.Text(self.name+" ="), self.sg.Text("Stopped", text_color='Red', key=self.exec+'Status'), self.sg.Button('start', key=self.toggleEvent)]
        else:
            statusText = [self.sg.Text(self.name+" ="), self.sg.Text("Running", text_color='Green', key=self.exec+'Status'), self.sg.Button('stop', key=self.toggleEvent)]
        return [statusText]


    def createOptionsFrame(self):
        if self.staticCLIArgs == True:
            input = self.sg.Input(default_text=self.cliCommand, key=self.exec+"Command")
            discoverEvent = Event(self.updateCommandOptionsInput, input)
            frame = [ [   self.sg.Text(self.name +" CLI Command"),
                                        input,
                                        self.sg.Button("Discover", key=discoverEvent)]]
            return frame
        else:
            return []

    def updateCommandOptionsInput(self, input):
        command = self.DiscoverCommand()
        if command != None:
            if self.sg.popup("Save current " + self.name + " command?", "CMD : " + command, button_type=1) == "Yes":
                input[0].update(value=command)
                self.cliCommand = command


class AudioModuleWithProfiles(AudioModule):


    def __init__(self, app, sg, name, exec, staticCLIArgs = True):
        super().__init__(app, sg, name, exec, staticCLIArgs)
        self.events = {}
        self.currentProfileBtn = None
        self.profile = None
        self.profiles = []

    def SaveSettings(self):
        if self.exec not in self.app.settings:
            self.app.settings[self.exec] ={}
        self.app.settings[self.exec]['Path'] = self.path
        self.app.settings[self.exec]['Profiles'] = self.profiles
        self.app.settings[self.exec]['Profile'] = self.profile
        super().SaveSettings()

    def LoadSettings(self):
        super().LoadSettings()
        try:
            self.path = self.app.settings[self.exec]['Path']
            self.profiles = self.app.settings[self.exec]['Profiles']
            self.profile = self.app.settings[self.exec]['Profile']
            if self.profile != None:
                self.CLIArgs["Profile"] = self.path + "/" + self.profile
        except Exception as e:
            print(e)
            self.SaveSettings()

    def CreateFrame(self):
        frame = [[], [self.sg.HorizontalSeparator()], super().CreateFrame()[0]]
        frame.append([self.sg.Button('Add ' + self.exec + ' Profile', key=Event(self.AddProfile))])
        for fname in self.profiles:
            self.events[fname] = Event(self.LoadModule, fname)
            right = ["edit",["cancel", 'delete::' + self.exec + fname]]
            self.app.eventHandlers['delete::' + self.exec + fname] = Event(self.DeleteProfile, fname)
            if fname == self.profile:
                self.currentProfileBtn=self.events[fname]
                color='Red'
            else:
                color=self.sg.theme_button_color()
            frame[0].append(self.sg.Button(fname, key=self.events[fname], right_click_menu = right, button_color=color ))

        return frame

    def LoadModule(self, fname):
        fname = fname[0]
        self.StopModule()
        self.SetProfile(fname)
        self.StartModule()

    def SetProfile(self, fname):
        if self.currentProfileBtn != None:
            self.app.window[self.currentProfileBtn].update(button_color=self.sg.theme_button_color())
        btn = self.events[fname]
        self.app.window[btn].update(button_color='Red')
        self.app.currentProfileBtn = self.events[fname]
        self.profile = fname
        self.CLIArgs["Profile"] = self.path + "/" + self.profile
        self.SaveSettings()

    def AddProfile(self, *argv):
        fnames = self.sg.popup_get_file('Select Profile',
            title = 'Profile',
            modal = True,
            initial_folder=self.path,
            multiple_files = True,
            no_window = True)
        if len(fnames) > 0:
            for fname in fnames:
                fname = os.path.basename(fname)
                if fname not in self.profiles:
                    self.profiles.append(fname)
            self.app.SaveSettings()
            self.app.ReloadWindow()
    def DeleteProfile(self, fname):
        self.profiles.remove(fname[0])
        self.profile = None
        self.app.SaveSettings()
        self.app.ReloadWindow()

    def createOptionsFrame(self):
        frame = super().createOptionsFrame()
        input = self.sg.Input(default_text=self.path, key=self.exec+"Path")
        browseEvent = Event(self.updatePathOptionsInput, input)
        frame.append([   self.sg.Text(self.name +" Files Directory"),
                                    input,
                                    self.sg.Button("...", key=browseEvent)])
        return frame

    def updatePathOptionsInput(self, input):
        self.path = self.sg.popup_get_folder("", default_path=self.path, no_window=True)
        input[0].update(value=self.path)
