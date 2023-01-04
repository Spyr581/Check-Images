import wx
import wx.lib.agw.multidirdialog as MDD


class CIMainMenu:
    def __init__(self, parent):
        self.parent = parent

        menubar = wx.MenuBar()

        filemenu = wx.Menu()
        filemenu.Append(wx.ID_NEW, '&Искать\tCtrl+F')
        filemenu.Append(wx.ID_SAVE, '&Сохранить в файл\tCtrl+S')
        filemenu.Append(wx.ID_OPEN, '&Очистить\tCtrl+O')
        filemenu.AppendSeparator()

        item = wx.MenuItem(filemenu, wx.ID_EXIT, 'Выход\tCtrl+Q')
        item.SetBitmap(wx.Bitmap('exit16.png'))
        filemenu.Append(item)

        # view_menu = wx.Menu()
        # self.vStatus = view_menu.Append(VIEW_STATUS, 'Статусная строка', kind=wx.ITEM_CHECK)
        # view_menu.AppendSeparator()
        # self.vRgb = view_menu.Append(VIEW_RGB, 'RGB', kind=wx.ITEM_RADIO)
        # self.vSrgb = view_menu.Append(VIEW_SRGB, 'sRGB', kind=wx.ITEM_RADIO)

        help = wx.Menu()
        help.Append(wx.ID_ABOUT, 'О программе')

        menubar.Append(filemenu, '&Файл')
        menubar.Append(help, '&Помощь')
        self.parent.SetMenuBar(menubar)

        self.parent.Bind(wx.EVT_MENU, self.on_quit, id=wx.ID_EXIT)
        # self.parent.Bind(wx.EVT_MENU, self.on_status, id=VIEW_STATUS)
        # self.parent.Bind(wx.EVT_MENU, self.on_img_type, id=VIEW_RGB)
        # self.parent.Bind(wx.EVT_MENU, self.on_img_type, id=VIEW_SRGB)

    def on_quit(self, event):
        self.parent.Close()

class CIComboBox:
    def __init__(self, parent):
        self.parent = parent
        cb = wx.ComboBox(self.parent, wx.ID_ANY)


class CIFrame(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        super().__init__(parent, title=title, size=(1280, 720))
        self.Centre()

        CIMainMenu(self)
        panel = wx.Panel(self)

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(15)
        vbox_main = wx.BoxSizer(wx.VERTICAL)

        grid_bag_adding = wx.GridBagSizer(0, 0)
        text_tmpl = wx.StaticText(panel, label='Что ищем:')
        text_tmpl.SetFont(font)
        grid_bag_adding.Add(text_tmpl, pos=(0, 0), flag=wx.ALIGN_CENTER | wx.BOTTOM, border=2)
        check_list_tmpl = wx.CheckListBox(panel, wx.ID_ANY)
        grid_bag_adding.Add(check_list_tmpl, pos=(1, 0), span=(3, 1), flag=wx.EXPAND | wx.LEFT, border=12)
        btn_1_tmpl = wx.Button(panel, label='Добавить', size=(70, 30))
        btn_2_tmpl = wx.Button(panel, label='Убрать', size=(70, 30))
        btn_3_tmpl = wx.Button(panel, label='Очистить', size=(70, 30))
        grid_bag_adding.Add(btn_1_tmpl, pos=(1, 1), flag=wx.LEFT | wx.BOTTOM, border=8)
        grid_bag_adding.Add(btn_2_tmpl, pos=(2, 1), flag=wx.LEFT | wx.BOTTOM, border=8)
        grid_bag_adding.Add(btn_3_tmpl, pos=(3, 1), flag=wx.LEFT | wx.BOTTOM, border=8)

        text_img = wx.StaticText(panel, label='Где ищем:')
        text_img.SetFont(font)
        grid_bag_adding.Add(text_img, pos=(0, 4), flag=wx.ALIGN_CENTER | wx.BOTTOM, border=2)
        check_list_img = wx.CheckListBox(panel, wx.ID_ANY)
        grid_bag_adding.Add(check_list_img, pos=(1, 4), span=(3, 1), flag=wx.EXPAND | wx.LEFT, border=12)
        btn_1_img = wx.Button(panel, label='Добавить', size=(70, 30))
        btn_2_img = wx.Button(panel, label='Убрать', size=(70, 30))
        btn_3_img = wx.Button(panel, label='Очистить', size=(70, 30))
        grid_bag_adding.Add(btn_1_img, pos=(1, 5), flag=wx.LEFT | wx.BOTTOM, border=8)
        grid_bag_adding.Add(btn_2_img, pos=(2, 5), flag=wx.LEFT | wx.BOTTOM, border=8)
        grid_bag_adding.Add(btn_3_img, pos=(3, 5), flag=wx.LEFT | wx.BOTTOM, border=8)

        empty_space = wx.StaticText(panel, label='')
        grid_bag_adding.Add(empty_space, pos=(0, 6), span=(4, 1), flag=wx.RIGHT, border=22)

        grid_bag_adding.AddGrowableCol(0)
        grid_bag_adding.AddGrowableCol(4)

        grid_bag_output = wx.GridBagSizer(0, 0)
        empty_element = wx.StaticText(panel, label='')
        grid_bag_output.Add(empty_element, pos=(0, 0))
        grid_bag_output.AddGrowableRow(0)
        grid_bag_output.AddGrowableCol(0)

        grid_bag_btns = wx.GridBagSizer(0, 0)
        empty_element = wx.StaticText(panel, label='')
        grid_bag_btns.Add(empty_element, pos=(0, 0))
        btn_ctrl_1 = wx.Button(panel, label='Искать', size=(100, 30))
        btn_ctrl_2 = wx.Button(panel, label='Выход', size=(60, 30))
        grid_bag_btns.Add(btn_ctrl_1, pos=(0, 1), flag=wx.RIGHT | wx.BOTTOM, border=16)
        grid_bag_btns.Add(btn_ctrl_2, pos=(0, 2), flag=wx.RIGHT | wx.BOTTOM, border=20)
        grid_bag_btns.AddGrowableCol(0)

        vbox_main.Add(grid_bag_adding, wx.ID_ANY, flag=wx.EXPAND)
        vbox_main.Add(grid_bag_output, wx.ID_ANY, flag=wx.EXPAND)
        vbox_main.Add(grid_bag_btns, wx.ID_ANY, flag=wx.EXPAND)

        panel.SetSizer(vbox_main)

        btn_ctrl_2.Bind(wx.EVT_BUTTON, self.on_quit, id=btn_ctrl_2.GetId())
        btn_1_tmpl.Bind(wx.EVT_BUTTON, self.on_add_files, id=btn_1_tmpl.GetId())

    def on_quit(self, event):
        self.Close()

    def on_add_files(self, event):
        # dlg = MDD.MultiDirDialog(self, title="Choose a directory:",
        #                          defaultPath='',
        #                          agwStyle=1)
        # if dlg.ShowModal() == wx.ID_OK:
        #     paths = dlg.GetPaths()
        #     print("You chose the following file(s):")
        #     for path in paths:
        #         print(path)
        # dlg.Destroy()
        with wx.FileDialog(self, 'Открыть файл(-ы):', wildcard='Изображения|*.png;*.jpg;*.webp',
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # print(dir(fileDialog))
            pathname = fileDialog.GetPaths()
            print(pathname)
            # try:
            #     with open(pathname, 'r') as file:
            #         # self.doLoadDataOrWhatever(file)
            #         print(pathname)
            # except IOError:
            #     wx.LogError("Cannot open file '%s'." % pathname)


ci_app = wx.App()
main_frame = CIFrame(None, 'Hello')
main_frame.Show()

ci_app.MainLoop()
