from tkinter import *
from tkinter import ttk

def button_set():
    pass


class App(Tk):
    def __init__(self):
        super().__init__()
        self.device_widgets = []
        self.title("Instrument Control Panel")
        self.mainframe = ttk.Frame(self, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(W, E, N, S))

        # device list a combobox
        ttk.Label(self.mainframe, text="Device").grid(column=1, row=1, sticky=W)
        self.device = StringVar()
        self.device.set("--Select--")
        self.device.trace_add("write", self.update_device)
        device_combobox = ttk.Combobox(self.mainframe, width=20, textvariable=self.device, justify=CENTER)
        device_combobox.grid(column=2, row=1, sticky=(W, E))
        device_combobox['values'] = ("Device1", "Device2")


    def update_device(self, *args):
        for widget in self.device_widgets:
            widget.destroy()
        self.device_widgets = []

        device = self.device.get()
        if device == "Device1":
            self.device1()
        elif device == "Device2":
            self.device2()


    def device1(self):
        # wavelength
        wtext = ttk.Label(self.mainframe, text="Wavelength")
        wtext.grid(column=1, row=2, sticky=W)
        self.wavelength = StringVar()
        self.wavelength.set("1550")
        wavelength_entry = ttk.Entry(self.mainframe, width=20, textvariable=self.wavelength, justify=CENTER)
        wavelength_entry.grid(column=2, row=2, sticky=(W, E))
        wunit = ttk.Label(self.mainframe, text="nm")
        wunit.grid(column=3, row=2, sticky=W)

        self.device_widgets.append(wavelength_entry)
        self.device_widgets.append(wunit)
        self.device_widgets.append(wtext)


    def device2(self):
        # power
        ptext = ttk.Label(self.mainframe, text="Power")
        ptext.grid(column=1, row=3, sticky=W)
        self.power = StringVar()
        self.power.set("0")
        power_entry = ttk.Entry(self.mainframe, width=20, textvariable=self.power, justify=CENTER)
        power_entry.grid(column=2, row=3, sticky=(W, E))
        punit = ttk.Label(self.mainframe, text="dBm")
        punit.grid(column=3, row=3, sticky=W)
        self.device_widgets.append(power_entry)
        self.device_widgets.append(punit)
        self.device_widgets.append(ptext)

    def add_button(self):
        # button
        ttk.Button(self.mainframe, text="Set", command=button_set).grid(column=3, row=4, sticky=E)


def main():
    app = App()
    app.geometry("300x250")
    app.mainloop()

if __name__ == "__main__":
    main()