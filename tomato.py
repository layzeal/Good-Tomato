import time
import wx
import wx.adv
from win10toast import ToastNotifier


class Tomato(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = wx.Icon('tomato.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.timer = wx.Timer(self)
        self.in_countdown = False

        # 默认时间：集中25分钟，休息3分钟
        self.work_mins = 25
        self.break_mins = 3

        self._init_ui()
        self._init_taskbarIcon()
        self._init_event()
        self.toaster = ToastNotifier()

    def _init_ui(self):        
        pnl = wx.Panel(self)
        self.st = wx.StaticText(pnl, label=f"{self.work_mins:02}:00")
        self.st.SetFont(wx.Font(wx.FontInfo(40)))
        self.btn_start = wx.Button(pnl, label="START")
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer()
        main_sizer.Add(self.st, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(20)
        main_sizer.Add(self.btn_start, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddStretchSpacer()
        pnl.SetSizer(main_sizer)

    def _init_taskbarIcon(self):
        self.taskbarIcon = wx.adv.TaskBarIcon()
        self.taskbarIcon.SetIcon(self.icon, "Tomato")

    def _init_event(self):
        self.Bind(wx.EVT_BUTTON, self.on_click_start, self.btn_start)
        self.Bind(wx.EVT_TIMER, self.update_tomato, self.timer)
        self.Bind(wx.EVT_CLOSE, self.on_close, self)

    def TaskBarMenu(self):
        menu = wx.Menu()
        
    def on_click_start(self, event):
        if not self.in_countdown:
            self.total_seconds = self.work_mins * 60
            self.in_countdown = True
            self.timer.Start(1000)
            self.taskbarIcon.SetIcon(self.icon,f"Tomato\nwork\n{self.work_mins:02}:00")
            self.btn_start.SetLabel("STOP")
        else:
            self.timer.Stop()
            self.in_countdown = False
            self.btn_start.SetLabel("START")
            self.st.SetLabel(f"{self.work_mins:02}:00")
    

    def update_tomato(self, event):
        self.total_seconds -= 1
        if self.total_seconds > 0:
            minutes = self.total_seconds // 60
            seconds = self.total_seconds % 60
            self.taskbarIcon.SetIcon(self.icon,"Tomato\nwork\n{:02}:{:02}".format(minutes, seconds))
            self.st.SetLabel("{:02}:{:02}".format(minutes, seconds))
        else:
            self.timer.Stop()
            self.toaster.show_toast('Tomato','{} minutes finnished, have a break!'.format(self.work_mins), icon_path='tomato.ico', threaded=True)
            self.in_countdown = False
            self.btn_start.SetLabel("START")
            self.st.SetLabel(f"{self.work_mins:02}:00")

    def on_close(self, event):
        self.taskbarIcon.Destroy()
        self.Destroy()

# 命令行实现

def countdown(total_seconds):
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    print(f"\r{minutes:02}:{seconds:02}", end='')


def tomato(minutes=25, break_min=5, counter=countdown, notifier=None):
    
    start_time = time.perf_counter()
    while True:
        diff_seconds = int(round(time.perf_counter() - start_time))
        left_seconds = minutes * 60 - diff_seconds
        if left_seconds <= 0:
            break
        counter(left_seconds)
        time.sleep(1)
    toaster = ToastNotifier()
    toaster.show_toast('Tomato🍅','{} minutes finnished, have a break!'.format(minutes))
    return


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = Tomato(None, title='Tomato')
    frm.Show()
    frm.Center()
    app.MainLoop()