import cv2
import wx
import wx.lib.agw.shapedbutton as shapedbutton
import mainCamera
import threading


class AppWindow(wx.Frame):
    def __init__(self, title):
        super().__init__(parent=None, title=title)

        # Size modification
        self.SetMinSize((700, 500))
        self.Maximize()
        self.maximized_size = self.GetSize()

        self.auto_mode = True

        self.frame_sizer = self.layout()
        self.SetSizerAndFit(self.frame_sizer)
 
        self.Center()

    def layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.quick_control_bar(), proportion=1, flag=wx.EXPAND)
        main_sizer.Add(self.speed_settings_bar(), proportion=1, flag=wx.EXPAND)
        main_sizer.Add(self.main_area(), proportion=4,
                       flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
        main_sizer.Add(self.bottom_bar(), proportion=2,
                       flag=wx.EXPAND | wx.ALL)
        return main_sizer

    def quick_control_bar(self):
        self.control_bar_panel = wx.Panel(self)
        grid = wx.GridSizer(rows=1, cols=5, vgap=0, hgap=10)
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        self.control_bar_panel.SetSizerAndFit(outer_sizer)

        self.manual_button = wx.ToggleButton(self.control_bar_panel, label="Manual")
        self.auto_button = wx.ToggleButton(self.control_bar_panel, label="Auto")
        emergency_button = wx.Button(self.control_bar_panel, label="Emergency".upper())
        home_button = wx.Button(self.control_bar_panel, label="Send Home")
        vacuum_button = wx.Button(self.control_bar_panel, label="Vacuum activate/\ndeactivate")

        line = wx.StaticLine(self.control_bar_panel, style=wx.LI_HORIZONTAL, size=(1, 4))

        outer_sizer.Add(grid, proportion=1, flag=wx.EXPAND)
        outer_sizer.Add(line, proportion=0, flag=wx.EXPAND)

        grid.Add(self.manual_button, flag=wx.ALIGN_CENTER)
        grid.Add(self.auto_button, flag=wx.ALIGN_CENTER)
        grid.Add(emergency_button, flag=wx.ALIGN_CENTER)
        grid.Add(home_button, flag=wx.ALIGN_CENTER)
        grid.Add(vacuum_button, flag=wx.ALIGN_CENTER)

        # Find max button size regarding maxized window
        grid_max_size = wx.Size(int(self.maximized_size.GetWidth()),
                                int(self.maximized_size.GetHeight() / 8))
        grid_button_max_size = wx.Size(int(grid_max_size.GetWidth() / 5 - grid.GetHGap() * 4),
                                       int(grid_max_size.GetHeight() * 70 / 100))

        # Find largest min button size
        greatest_min_size = [0, 0]
        for button in [self.manual_button, self.auto_button, emergency_button,
                       home_button, vacuum_button]:
            height = button.GetSize().GetHeight()
            width = button.GetSize().GetWidth()
            if greatest_min_size[0] < width and greatest_min_size[1] < height:
                greatest_min_size[0] = width
                greatest_min_size[1] = height
        greatest_min_size = wx.Size(greatest_min_size[0], greatest_min_size[1])

        # Find average by max and min
        average_size = [int((greatest_min_size.GetWidth() + grid_button_max_size.GetWidth())/2),
                        int((greatest_min_size.GetHeight() + grid_button_max_size.GetHeight())/2)]
        average_size = wx.Size(average_size[0], average_size[1])

        # Finalize button size
        final_width = self.get_larger_value(average_size.GetWidth(), greatest_min_size.GetWidth())
        final_height = self.get_larger_value(average_size.GetHeight(), greatest_min_size.GetHeight())
        final_size = wx.Size(final_width, final_height)

        for button in [self.manual_button, self.auto_button, emergency_button,
                       home_button, vacuum_button]:
            button.SetMinSize(final_size)

        # Mode switching for toggle buttons
        if self.auto_mode:
            self.auto_button.SetValue(True)
            self.manual_button.SetValue(False)
        else:
            self.auto_button.SetValue(False)
            self.manual_button.SetValue(True)

        self.manual_button.Bind(wx.EVT_TOGGLEBUTTON, self.switch_mode)
        self.auto_button.Bind(wx.EVT_TOGGLEBUTTON, self.switch_mode)

        return self.control_bar_panel

    # line.Bind(wx.EVT_LEFT_UP, self.test)
    # def test(self, event):
    #     print(event.GetButton())
    def speed_settings_bar(self):
        self.speed_settings_bar_panel = wx.Panel(self)

        velocity = self.create_speed_bar_group(self.speed_settings_bar_panel, "velocity")
        accelerate = self.create_speed_bar_group(self.speed_settings_bar_panel,"acceleration")
        convey = self.create_speed_bar_group(self.speed_settings_bar_panel,"v_convey")
        button = wx.Button(self.speed_settings_bar_panel, label="Input")

        grid = wx.GridSizer(rows=1, cols=4, vgap=0, hgap=0)
        grid.Add(velocity, flag=wx.ALIGN_CENTER)
        grid.Add(accelerate, flag=wx.ALIGN_CENTER)
        grid.Add(convey, flag=wx.ALIGN_CENTER)
        grid.Add(button, flag=wx.ALIGN_CENTER)

        self.speed_settings_bar_panel.SetSizerAndFit(grid)
        return self.speed_settings_bar_panel

    def main_area(self):
        self.main_area_panel = wx.Panel(self)
        grid = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=10)
        box = wx.BoxSizer(wx.VERTICAL)

        grid.Add(self.create_gcode_pane(self.main_area_panel), flag=wx.EXPAND)
        grid.Add(self.create_camera_view(self.main_area_panel))
        grid.Add(self.create_coordinate_pane(self.main_area_panel))

        grid.AddGrowableRow(0)
        grid.AddGrowableCol(0)
        # grid.AddGrowableCol(1)

        box.Add(grid, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        self.main_area_panel.SetSizerAndFit(box)
        return self.main_area_panel

    def bottom_bar(self):
        self.manual_bottom_bar_panel = wx.Panel(self)
        self.manual_bottom_bar_panel.SetSizerAndFit(self.create_manual_bottom(self.manual_bottom_bar_panel))
        self.auto_bottom_bar_panel = wx.Panel(self)
        self.auto_bottom_bar_panel.SetSizerAndFit(self.create_auto_bottom(self.auto_bottom_bar_panel))
        if self.auto_mode:
            self.manual_bottom_bar_panel.Hide()
            self.auto_bottom_bar_panel.Show()
            return self.auto_bottom_bar_panel
        else:
            self.auto_bottom_bar_panel.Hide()
            self.manual_bottom_bar_panel.Show()
            return self.manual_bottom_bar_panel

    def create_speed_bar_group(self, panel, title):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(panel, label=title.capitalize() + ":")
        input = wx.TextCtrl(panel)
        hbox.Add(text, flag=wx.ALIGN_CENTER)
        hbox.Add(input, flag=wx.LEFT | wx.ALIGN_CENTER, border=5)
        return hbox

    def create_gcode_pane(self, panel):
        sizer = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        for title in ('G-Code', 'Insert', 'Save', 'Run'):
            hbox1.Add(wx.Button(panel, label=title))

        # TO BE IMPLEMENTED FOR ADDING MORE TABS
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        for label in ('Tab 1', '+'):
            hbox2.Add(wx.Button(panel, label=label, style=wx.BU_EXACTFIT))

        sizer.Add(hbox1)
        sizer.Add(wx.TextCtrl(panel, style=wx.TE_MULTILINE),
                  flag=wx.EXPAND, proportion=1)
        sizer.Add(hbox2)

        return sizer

    def create_camera_view(self, panel):
        sizer = wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.Button(panel, label='Camera'))
        hbox.Add(wx.Button(panel, label='Map'))

        sizer.Add(hbox)

        # Use temp button to help measure and resize video stream pane to have
        # same height as gcode pane
        temp = wx.Button(panel, label="Hidden", style=wx.BU_EXACTFIT)
        temp.Hide()
        button_height = temp.GetSize()[1]

        stream = Stream(panel)
        sizer.Add(stream, flag=wx.BOTTOM, border=button_height)
        return sizer

    def create_coordinate_pane(self, panel):
        sizer = wx.GridBagSizer(vgap=10, hgap=10)
        sizer.Add(wx.StaticText(panel, label="Frame Coordinate"),
                  span=(1, 3), pos=(0, 0))
        # Skip 1 row for spacing
        row = 2
        for title in ['X', 'Y', 'Z', 'RX', 'RY', 'RZ']:
            sizer.Add(wx.StaticText(panel, label=title), pos=(row, 0))
            sizer.Add(wx.TextCtrl(panel), pos=(row, 1))
            sizer.Add(wx.Button(panel, label="-", style=wx.BU_EXACTFIT),
                      pos=(row, 2))
            sizer.Add(wx.Button(panel, label="+", style=wx.BU_EXACTFIT),
                      pos=(row, 3))
            row += 1
        return sizer

    def get_larger_value(self, value1, value2):
        if value1 >= value2:
            final = value1
        else:
            final = value2
        return final

    def create_manual_bottom(self, panel):
        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        list = wx.ListBox(panel)

        add_button = wx.Button(panel, label="Add")
        save_button = wx.Button(panel, label="Save action")

        bitmap_size = int((self.maximized_size[1] / 8 * 2) / 4)    # height
        play_bitmap = wx.Image("./play.png").Scale(bitmap_size, bitmap_size,
                                                   wx.IMAGE_QUALITY_HIGH)
        play_bitmap = play_bitmap.ConvertToBitmap()
        start_button = shapedbutton.SBitmapButton(panel, id=-1,
                                                  bitmap=play_bitmap)

        vbox.Add(add_button, flag=wx.EXPAND, proportion=1)
        vbox.Add(save_button, flag=wx.EXPAND, proportion=1)

        hbox.Add(list, flag=wx.EXPAND | wx.RIGHT, proportion=1, border=10)
        hbox.Add(vbox, flag=wx.EXPAND)
        hbox.Add(start_button, flag=wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT,
                 border=10)

        outer_sizer.Add(hbox, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        return outer_sizer

    def create_auto_bottom(self, panel):
        alignment_sizer = wx.BoxSizer(wx.HORIZONTAL)
        outer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        box = wx.StaticBox(panel, label="Variables/ Statistics")
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        grid = wx.GridSizer(cols=2, rows=2, vgap=10, hgap=10)

        grid.Add(wx.StaticText(panel, label="Number of targets:"))
        targets = wx.TextCtrl(panel, style=wx.TE_CENTER)
        targets.Disable()
        targets.SetLabel("0")
        grid.Add(targets)

        grid.Add(wx.StaticText(panel, label="Number of targets done:"))
        done = wx.TextCtrl(panel, style=wx.TE_CENTER)
        done.Disable()
        done.SetLabel("0")
        grid.Add(done)

        sizer.Add(grid, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)

        # Add box sizer and spacers (to keep box in middle)
        alignment_sizer.Add(0, 0, proportion=1)
        alignment_sizer.Add(sizer, flag=wx.EXPAND)
        alignment_sizer.Add(0, 0, proportion=1)

        outer_sizer.Add(alignment_sizer, proportion=1, flag=wx.EXPAND | wx.ALL,
                        border=5)
        return outer_sizer

# Event handlers
    def switch_mode(self, event):
        button = event.GetEventObject()

        # button is pressed when it is True (value become False)
        if button.GetValue() is False:      
            button.SetValue(True)
        mode = button.GetLabel()
        if mode == "Manual":
            self.auto_mode = False
            self.auto_button.SetValue(False)
            if not self.manual_bottom_bar_panel.IsShown():
                self.manual_bottom_bar_panel.Show()
                self.auto_bottom_bar_panel.Hide()
                self.frame_sizer.Replace(self.auto_bottom_bar_panel, 
                                         self.manual_bottom_bar_panel)
                self.Layout()
        else:
            self.auto_mode = True
            self.manual_button.SetValue(False)
            if not self.auto_bottom_bar_panel.IsShown():
                self.auto_bottom_bar_panel.Show()
                self.manual_bottom_bar_panel.Hide()
                self.frame_sizer.Replace(self.manual_bottom_bar_panel,
                                         self.auto_bottom_bar_panel)
                self.Layout()


class Stream(wx.Panel):
    FPS = 10

    def __init__(self, parent):
        super().__init__(parent)
        self.SetDoubleBuffered(True)
        self.mainCamera = mainCamera.MainCamera()
        self.inferenceThread = threading.Thread(target=self.mainCamera.startCameraDetection, args=(False,), daemon=True)
        self.inferenceThread.start()

        # Source
        while not self.mainCamera.getHasFrame():
            pass
        self.frame = self.mainCamera.getFrame()
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.frame = cv2.flip(self.frame, 1)
        height = self.frame.shape[0]
        width = self.frame.shape[1]

        self.bitmap = wx.Bitmap.FromBuffer(width, height,
                                           self.frame)
        self.SetMaxSize(wx.Size(width, height))
        self.SetMinSize(wx.Size(width, height))

        # Timer for repainting panel regarding expected FPS
        self.timer = wx.Timer(self)
        self.timer.Start(int(1000 / self.FPS))

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_TIMER, self.next_frame)

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bitmap, 0, 0)

    def next_frame(self, event):
        self.frame = self.mainCamera.getFrame()
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        # self.frame = cv2.flip(self.frame, 1)
        self.bitmap.CopyFromBuffer(self.frame)
        self.Refresh()


def main():
    app = wx.App()
    window = AppWindow("Cashew Filter")
    window.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
