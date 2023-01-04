import wx

APP_EXIT = 1
VIEW_STATUS = 2
VIEW_RGB = 3
VIEW_SRGB = 4


class AppMainMenu:
    def __init__(self, parent):
        self.parent = parent

        menubar = wx.MenuBar()

        exp_menu = wx.Menu()
        exp_menu.Append(wx.ID_ANY, 'Экспорт текста')
        exp_menu.Append(wx.ID_ANY, 'Экспорт изображения')
        exp_menu.Append(wx.ID_ANY, 'Экспорт видео')

        filemenu = wx.Menu()
        filemenu.Append(wx.ID_NEW, '&Новый\tCtrl+N')
        filemenu.Append(wx.ID_OPEN, '&Открыть\tCtrl+O')
        filemenu.Append(wx.ID_SAVE, '&Сохранить\tCtrl+S')
        filemenu.AppendSubMenu(exp_menu, '&Экспорт')
        filemenu.AppendSeparator()

        item = wx.MenuItem(filemenu, APP_EXIT, 'Выход\tCtrl+Q', 'Выход из приложения')
        item.SetBitmap(wx.Bitmap('exit16.png'))
        filemenu.Append(item)

        view_menu = wx.Menu()
        self.vStatus = view_menu.Append(VIEW_STATUS, 'Статусная строка', kind=wx.ITEM_CHECK)
        view_menu.AppendSeparator()
        self.vRgb = view_menu.Append(VIEW_RGB, 'RGB', kind=wx.ITEM_RADIO)
        self.vSrgb = view_menu.Append(VIEW_SRGB, 'sRGB', kind=wx.ITEM_RADIO)

        menubar.Append(filemenu, '&Файл')
        menubar.Append(view_menu, '&Вид')
        self.parent.SetMenuBar(menubar)

        self.parent.Bind(wx.EVT_MENU, self.on_quit, id=APP_EXIT)
        self.parent.Bind(wx.EVT_MENU, self.on_status, id=VIEW_STATUS)
        self.parent.Bind(wx.EVT_MENU, self.on_img_type, id=VIEW_RGB)
        self.parent.Bind(wx.EVT_MENU, self.on_img_type, id=VIEW_SRGB)

    def on_status(self, event):
        if self.vStatus.IsChecked():
            print('Статусная строка включена')
        else:
            print('Статусная строка выключена')

    def on_img_type(self, event):
        if self.vRgb.IsChecked():
            print('Режим RGB')
        elif self.vSrgb.IsChecked():
            print('Режим sRGB')

    def on_quit(self, event):
        self.parent.Close()


class AppContextMenu(wx.Menu):
    def __init__(self, parent):
        self.parent = parent
        super().__init__()

        window_min = self.Append(wx.ID_ANY, 'Свернуть')
        if self.parent.IsMaximized():
            window_toggle_size = self.Append(wx.ID_ANY, 'Оконный режим')
        else:
            window_toggle_size = self.Append(wx.ID_ANY, 'На весь экран')

        self.Bind(wx.EVT_MENU, self.on_minimize, window_min)
        self.Bind(wx.EVT_MENU, self.on_maximize, window_toggle_size)

    def on_minimize(self, event):
        self.parent.Iconize()

    def on_maximize(self, event):
        if self.parent.IsMaximized():
            self.parent.Maximize(False)
        else:
            self.parent.Maximize(True)


class AppToolbar(wx.ToolBar):
    def __init__(self, parent):
        self.parent = parent
        super().__init__()

        toolbar = self.parent.CreateToolBar()
        tb_undo = toolbar.AddTool(wx.ID_UNDO, '', wx.Bitmap('undo32.png'), 'Назад')
        tb_redo = toolbar.AddTool(wx.ID_REDO, '', wx.Bitmap('redo32.png'), 'Вперед')
        toolbar.AddSeparator()

        toolbar.AddRadioTool(wx.ID_ANY, '', wx.Bitmap('sound-on32.png'))
        toolbar.AddRadioTool(wx.ID_ANY, '', wx.Bitmap('sound-off32.png'))
        toolbar.AddSeparator()

        tb_quit = toolbar.AddTool(wx.ID_ANY, 'Выход', wx.Bitmap('exit32.png'), 'Выход')

        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.on_quit, tb_quit)

    def on_quit(self, event):
        self.parent.Close()


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title)
        self.Centre()
        AppMainMenu(self)
        AppToolbar(self)

        # toolbar = self.CreateToolBar()
        # tb_undo = toolbar.AddTool(wx.ID_UNDO, '', wx.Bitmap('undo32.png'), 'Назад')
        # tb_redo = toolbar.AddTool(wx.ID_REDO, '', wx.Bitmap('redo32.png'), 'Вперед')
        # toolbar.AddSeparator()
        #
        # toolbar.AddRadioTool(wx.ID_ANY, '', wx.Bitmap('sound-on32.png'))
        # toolbar.AddRadioTool(wx.ID_ANY, '', wx.Bitmap('sound-off32.png'))
        # toolbar.AddSeparator()
        #
        # tb_quit = toolbar.AddTool(wx.ID_ANY, 'Выход', wx.Bitmap('exit32.png'), 'Выход')
        #
        # toolbar.Realize()
        #
        # self.Bind(wx.EVT_TOOL, self.on_quit, tb_quit)

        self.context_menu = AppContextMenu(self)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)

    def on_right_down(self, event):
        self.context_menu = AppContextMenu(self)
        self.PopupMenu(self.context_menu, event.GetPosition())

    # def on_quit(self, event):
    #     self.Close()

app = wx.App()
frame = MyFrame(None, 'Hello')
frame.Show()

app.MainLoop()