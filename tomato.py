# -*- coding: UTF-8 -*-

import time
import json
import wx
import wx.adv
from win10toast import ToastNotifier

WORK = 1
BREAK = 2

# https://blog.csdn.net/ygdxt/java/article/details/89238491
class MyNumberValidator(wx.Validator):# 创建验证器子类      
	def __init__(self):
		wx.Validator.__init__(self)
		self.ValidInput = ['0','1','2','3','4','5','6','7','8','9']
		self.StringLength = 0
		self.Bind(wx.EVT_CHAR,self.OnCharChanged)  #  绑定字符改变事件

	def OnCharChanged(self,event):
		# 得到输入字符的 ASCII 码
		keycode = event.GetKeyCode()
		# 退格（ASCII 码 为8），删除一个字符。
		if keycode == 8:
			self.StringLength -= 1
			#事件继续传递
			event.Skip()
			return

		# 把 ASII 码 转成字符
		InputChar = chr(keycode)

		if InputChar in self.ValidInput:
			# 第一个字符为 .,非法，拦截该事件，不会成功输入
			if InputChar == '.' and self.StringLength == 0:
				return False
			# 在允许输入的范围，继续传递该事件。
			else:
				event.Skip()
				self.StringLength += 1
				return True
		return False

	def Clone(self):
		return MyNumberValidator()

	def Validate(self,win):#1 使用验证器方法
		return True

	def TransferToWindow(self):
		return True

	def TransferFromWindow(self):
		return True

class Tomato(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = wx.Icon('./tomato.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        with open("./config.json", 'r') as f:
            self.config = json.load(f)
        self.timer = wx.Timer(self)
        self.running = False

        # 默认时间：集中25分钟，休息3分钟
        default = self.config.get("default_case")
        self.work_min = self.config["cases"][default]['work_min']
        self.break_min = self.config["cases"][default]['break_min']

        self._init_ui()
        self._init_taskbarIcon()
        self._init_menu()
        self._init_event()
        self.toaster = ToastNotifier()

    def _init_ui(self):        
        pnl = wx.Panel(self)
        self.st = wx.StaticText(pnl, label=f"{self.work_min:02}:00")
        self.st.SetFont(wx.Font(wx.FontInfo(40)))
        self.btn_start = wx.Button(pnl, label="START")
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer()
        main_sizer.Add(self.st, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(20)
        main_sizer.Add(self.btn_start, flag=wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddStretchSpacer()
        pnl.SetSizer(main_sizer)

    def _init_menu(self):
        "create menu bar"
        menu = wx.Menu()
        menu_new_case = menu.Append(-1, "New Case")
        menu_choose_case = menu.Append(-1, "Choose Case")
        menu_about = menu.Append(wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_new_case, menu_new_case)
        self.Bind(wx.EVT_MENU, self.on_choose_case, menu_choose_case)
        self.Bind(wx.EVT_MENU, self.on_about, menu_about)
        menubar = wx.MenuBar()
        menubar.Append(menu, "Menu")
        self.SetMenuBar(menubar)
        

    def _init_taskbarIcon(self):
        self.taskbarIcon = wx.adv.TaskBarIcon()
        self.taskbarIcon.SetIcon(self.icon, "Tomato")

    def _init_event(self):
        self.Bind(wx.EVT_BUTTON, self.on_click_start, self.btn_start)
        self.Bind(wx.EVT_TIMER, self.update_timer, self.timer)
        self.Bind(wx.EVT_CLOSE, self.on_close, self)

    def TaskBarMenu(self):
        menu = wx.Menu()
    
    # TODO: 重构dialog类，自定义几种常用的dialog
    def on_new_case(self, event):
        dlg = wx.Dialog(self, title='New Case', size=(300,200))
        
        name_sizer = wx.BoxSizer()
        label_name = wx.StaticText(dlg, label='Case Name:      ')
        text_name = wx.TextCtrl(dlg)
        name_sizer.Add(label_name)
        name_sizer.Add(text_name)
        work_sizer = wx.BoxSizer()
        label_work_min = wx.StaticText(dlg, label='Work Minutes:  ')
        text_work_min = wx.TextCtrl(dlg, validator=MyNumberValidator())
        work_sizer.Add(label_work_min)
        work_sizer.Add(text_work_min)
        break_sizer = wx.BoxSizer()
        label_break_min = wx.StaticText(dlg, label='Break Minutes: ')
        text_break_min = wx.TextCtrl(dlg, validator=MyNumberValidator())
        break_sizer.Add(label_break_min)
        break_sizer.Add(text_break_min)

        ok = dlg.CreateButtonSizer(wx.OK)
        cancel = dlg.CreateButtonSizer(wx.CANCEL)

        hsizer = wx.BoxSizer()
        hsizer.Add(ok)
        hsizer.AddSpacer(20)
        hsizer.Add(cancel)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddStretchSpacer()
        vsizer.Add(name_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddSpacer(10)
        vsizer.Add(work_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddSpacer(10)
        vsizer.Add(break_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddSpacer(20)
        vsizer.Add(hsizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddStretchSpacer()
        dlg.SetSizer(vsizer)
        dlg.Center()
        if dlg.ShowModal() == wx.ID_OK:
            name = text_name.GetValue()
            work_min = text_work_min.GetValue()
            break_min = text_break_min.GetValue()
            self.create_new_case(name, int(work_min), int(break_min))
        dlg.Destroy()
    
    def on_choose_case(self, event):
        dlg = wx.Dialog(self, title="Choose Case", size=(300,200))
        cases = self.config.get("cases")
        choices = [case['case_name'] for case in cases]
        select_box = wx.ComboBox(dlg, size=(100,-1), choices=choices)
        select_box.SetSelection(self.config["default_case"])

        ok = dlg.CreateButtonSizer(wx.OK)
        cancel = dlg.CreateButtonSizer(wx.CANCEL)

        hsizer = wx.BoxSizer()
        hsizer.Add(ok)
        hsizer.AddSpacer(20)
        hsizer.Add(cancel)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddStretchSpacer()
        vsizer.Add(select_box, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddSpacer(40)
        vsizer.Add(hsizer, flag=wx.ALIGN_CENTER_HORIZONTAL)
        vsizer.AddStretchSpacer()
        dlg.SetSizer(vsizer)

        dlg.Center()
        if dlg.ShowModal() == wx.ID_OK:
            default = select_box.GetCurrentSelection()
            self.config["default_case"] = default
            self.work_min = self.config["cases"][default]['work_min']
            self.break_min = self.config["cases"][default]['break_min']
            self.st.SetLabel(f"{self.work_min:02}:00")
            
        dlg.Destroy()

    def on_about(self, event):
        wx.MessageBox("github: https://github.com/layzeal/Good-Tomato",
                      "About Tomato",
                      wx.OK|wx.ICON_INFORMATION)

        
    def on_click_start(self, event):
        if not self.running:
            self.total_seconds = self.work_min * 60
            self.running = WORK
            self.timer.Start(1000)
            self.taskbarIcon.SetIcon(self.icon,f"Tomato\nwork\n{self.work_min:02}:00")
            self.btn_start.SetLabel("STOP")
        else:
            self.timer.Stop()
            self.running = False
            self.btn_start.SetLabel("START")
            self.st.SetLabel(f"{self.work_min:02}:00")
    
    def create_new_case(self, name, work_min, break_min):
        case_id = self.config.get('next_case_id')
        self.config['next_case_id'] += 1
        new_case = {
            "case_id": case_id,
            "case_name": name,
            "work_min": work_min,
            "break_min": break_min
        }
        self.config['cases'].append(new_case)

    def have_a_break(self):
        if self.running == WORK:
            self.running = BREAK
            self.total_seconds = self.break_min * 60
            self.timer.Start(1000)
            self.taskbarIcon.SetIcon(self.icon,f"Tomato\nbreak\n{self.work_break:02}:00")
            self.btn_start.SetLabel("BREAK")

    def update_timer(self, event):
        self.total_seconds -= 1
        if self.total_seconds > 0:
            minutes = self.total_seconds // 60
            seconds = self.total_seconds % 60
            status = 'work' if self.running==WORK else 'break'
            self.taskbarIcon.SetIcon(self.icon,"Tomato\n{}\n{:02}:{:02}".format(status, minutes, seconds))
            self.st.SetLabel("{:02}:{:02}".format(minutes, seconds))
        else:
            self.timer.Stop()
            if self.running == WORK:
                self.toaster.show_toast('Tomato','{} minutes work finnished, have a {}-minutes break!'.format(self.work_min, self.break_min), icon_path='tomato.ico', threaded=True)
                self.have_a_break()
            else:
                self.toaster.show_toast('Tomato','Break time END!', icon_path='tomato.ico', threaded=True)
                self.btn_start.SetLabel("START")
                self.st.SetLabel(f"{self.work_min:02}:00")

    def on_close(self, event):
        with open('./config.json', 'w') as f:
            json.dump(self.config, f,indent=4)
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