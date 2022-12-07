import module
class opWin:
    def __init__(self, app, sg):
        self.app = app
        self.sg = sg
    def show(self):
        layout = [  [   self.app.jackd.createOptionsFrame()],
                    [   self.app.ajSnapshot.createOptionsFrame()],
                    [   self.app.jackMixer.createOptionsFrame()],
                    [self.sg.Button("Cancel"), self.sg.Button("Close")] ]

        self.window = self.sg.Window('Options', layout, icon="./flight-case (128).png", modal=True)

        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = self.window.read()
            # print(event)

            if isinstance(event, module.btnEvent):
                print(event)
                event.do()

            if event == self.sg.WIN_CLOSED or event == 'Cancel':
                self.window.close()
                break

            if event == self.sg.WIN_CLOSED or event == 'Close':
                self.app.SaveSettings()
                self.app.ajSnapshot.CLIArgs["Profile"] = self.ajSnapshot.path + "/" + self.ajSnapshot.profile
                self.app.jackMixer.CLIArgs["Profile"] = self.jackMixer.path + "/" + self.jackMixer.profile
                self.window.close()
                break
