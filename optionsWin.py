
class opWin:
    def __init__(self, app, sg):
        self.app = app
        self.sg = sg
    def show(self):
        layout = [  [   self.sg.Text("Jack Mixer Files Directory"),
                                    self.sg.Input(default_text=self.app.appSettings.settings["mixerConfPath"], key="mixerConfPath"),
                                    self.sg.Button("...", key="mixConfigPathBtn")],
                    [   self.sg.Text("aj-snapshot Files Directory"),
                                    self.sg.Input(default_text=self.app.appSettings.settings["snapshotPath"], key="snapshotPath"),
                                    self.sg.Button("...", key="snapshotPathBtn")],

                    [   self.sg.Text("Jackd Command"),
                                    self.sg.Input(self.app.appSettings.settings["jackCommand"], key="jackCommand"),
                                    self.sg.Button("Discover", key="discoverJackCommand")],
                    [self.sg.Button("Close")] ]

        self.window = self.sg.Window('Options', layout, icon="./flight-case (128).png", modal=True)

        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = self.window.read()
            print(event)
            if event == "mixConfigPathBtn":
                self.app.appSettings.settings["mixerConfPath"] = self.sg.popup_get_folder("Jack Mixer Files Directory", default_path=self.app.appSettings.settings["mixerConfPath"], no_window=True)
                self.window["mixerConfPath"].update(value=self.app.appSettings.settings["mixerConfPath"])
            if event == "snapshotPathBtn":
                self.app.appSettings.settings["mixerConfPath"] = self.sg.popup_get_folder("Jack Mixer Files Directory", default_path=self.app.appSettings.settings["mixerConfPath"], no_window=True)
                self.window["snapshotPath"].update(value=self.app.appSettings.settings["snapshotPath"])
            if event == "discoverJackCommand":
                command = self.app.jackd.DiscoverCommand()
                if self.sg.popup("Save current jack command?", "CMD : " + command, button_type=1) == "Yes":
                    self.window["jackCommand"].update(value=command)
            if event == self.sg.WIN_CLOSED or event == 'Close':
                self.app.appSettings.settings["jackCommand"] = self.window["mixerConfPath"].get()
                self.app.appSettings.settings["jackCommand"] = self.window["snapshotPath"].get()
                self.app.appSettings.settings["jackCommand"] = self.window["jackCommand"].get()
                self.window.close()
                break
