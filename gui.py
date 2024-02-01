import wx
import os


class GUIUtils:
    def __init__(self):
        pass

    @staticmethod
    def check_file_presence(f, any_list):
        return any(f == item[0] for item in any_list)

    @staticmethod
    def format_file_name(file_path):
        max_length = 60  # Максимальная длина строки для отображения пути
        file_name = os.path.basename(file_path)
        if len(file_path) <= max_length:
            return file_path
        else:
            return f"...{file_path[-(max_length - len(file_name)):]}"


class MyDropTarget(wx.FileDropTarget, GUIUtils):
    extensions = ['.jpg', '.png', '.webp']

    def __init__(self, window, l_filepaths):
        super().__init__()
        self.window = window
        self.l_filepaths = l_filepaths

    @classmethod
    def check_file_extension(cls, f):
        return os.path.splitext(f)[1] in cls.extensions

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            if os.path.isdir(filename):
                # Если это папка, добавляем имена файлов в папке в ListBox
                files_in_folder = [f for f in os.listdir(filename) if os.path.isfile(os.path.join(filename, f))]

                for file_in_folder in files_in_folder:
                    if not self.check_file_extension(file_in_folder):
                        continue
                    if self.check_file_presence(file_in_folder, self.l_filepaths):
                        continue
                    full_filename = os.path.join(filename, file_in_folder)
                    short_path = self.format_file_name(full_filename)
                    self.window.Append(short_path)
                    self.l_filepaths.append((full_filename, short_path))
            else:
                if not self.check_file_extension(filename):
                    continue
                if self.check_file_presence(filename, self.l_filepaths):
                    continue
                short_path = self.format_file_name(filename)
                self.window.Append(short_path)
                self.l_filepaths.append((filename, short_path))
        return True


class MyFrame(wx.Frame, GUIUtils):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(1280, 720))

        self.l_left_selection = []
        self.l_right_selection = []

        self.tooltip = wx.ToolTip("")
        self.last_selected_index_left = wx.NOT_FOUND
        self.last_selected_index_right = wx.NOT_FOUND

        # Создаем панель
        panel = wx.Panel(self)

        # Создаем вертикальный бокссайзер для разделения окна на три части
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Создаем горизонтальный бокссайзер для первых двух областей
        hbox_top = wx.BoxSizer(wx.HORIZONTAL)

        # Левая часть (поле выбора и кнопки)
        vbox_left = wx.BoxSizer(wx.VERTICAL)
        self.listbox_left = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE, id=1)
        # Устанавливаем DropTarget
        self.listbox_left.SetDropTarget(MyDropTarget(self.listbox_left, self.l_left_selection))
        vbox_left.Add(self.listbox_left, 1, wx.EXPAND | wx.ALL, 5)

        hbox_top.Add(vbox_left, 1, wx.EXPAND | wx.ALL, 5)

        # Кнопки +, -, Очистить для левого поля
        vbox_buttons_left = wx.BoxSizer(wx.VERTICAL)
        btn_plus_left = wx.Button(panel, label="+", size=(50, 30), id=10)
        btn_minus_left = wx.Button(panel, label="-", size=(50, 30), id=11)
        btn_clear_left = wx.Button(panel, label="Очистить", size=(80, 30), id=12)

        vbox_buttons_left.Add(btn_plus_left, 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_left.Add(btn_minus_left, 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_left.Add(btn_clear_left, 0, wx.EXPAND | wx.ALL, 5)

        hbox_top.Add(vbox_buttons_left, 0, wx.EXPAND | wx.ALL, 5)

        # Правая часть (поле выбора и кнопки)
        vbox_right = wx.BoxSizer(wx.VERTICAL)
        self.listbox_right = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE, id=2)
        # Устанавливаем DropTarget
        self.listbox_right.SetDropTarget(MyDropTarget(self.listbox_right, self.l_right_selection))
        vbox_right.Add(self.listbox_right, 1, wx.EXPAND | wx.ALL, 5)

        # Кнопки +, -, Очистить для правого поля
        vbox_buttons_right = wx.BoxSizer(wx.VERTICAL)
        btn_plus_right = wx.Button(panel, label="+", size=(50, 30), id=20)
        btn_minus_right = wx.Button(panel, label="-", size=(50, 30), id=21)
        btn_clear_right = wx.Button(panel, label="Очистить", size=(80, 30), id=22)

        vbox_buttons_right.Add(btn_plus_right, 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_right.Add(btn_minus_right, 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_right.Add(btn_clear_right, 0, wx.EXPAND | wx.ALL, 5)

        hbox_top.Add(vbox_right, 1, wx.EXPAND | wx.ALL, 5)
        hbox_top.Add(vbox_buttons_right, 0, wx.EXPAND | wx.ALL, 5)

        vbox.Add(hbox_top, 1, wx.EXPAND | wx.ALL, 5)

        # Кнопки "Искать" и "Настройки" (расположены посередине)
        hbox_bottom_buttons = wx.BoxSizer(wx.HORIZONTAL)
        btn_search = wx.Button(panel, label="Искать", size=(80, 30))
        btn_settings = wx.Button(panel, label="Настройки", size=(80, 30))

        hbox_bottom_buttons.AddStretchSpacer()
        hbox_bottom_buttons.Add(btn_search, 0, wx.EXPAND | wx.ALL, 5)
        hbox_bottom_buttons.Add(btn_settings, 0, wx.EXPAND | wx.ALL, 5)
        hbox_bottom_buttons.AddStretchSpacer()

        vbox.Add(hbox_bottom_buttons, 0, wx.EXPAND | wx.ALL, 5)

        # Создаем третью область под первой и второй
        self.console_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        vbox.Add(self.console_text, 1, wx.EXPAND | wx.ALL, 5)

        # Устанавливаем бокссайзер для панели
        panel.SetSizer(vbox)

        # Устанавливаем обработчики событий для выбора элементов в левом и правом полях
        self.Bind(wx.EVT_LISTBOX, self.on_left_selection, self.listbox_left)
        self.Bind(wx.EVT_LISTBOX, self.on_right_selection, self.listbox_right)

        # Установка/снятие выбора в списке
        self.listbox_left.Bind(wx.EVT_LEFT_UP, self.on_left_click)
        self.listbox_right.Bind(wx.EVT_LEFT_UP, self.on_left_click)

        # Устанавливаем обработчики событий для кнопок
        self.Bind(wx.EVT_BUTTON, self.on_plus, btn_plus_left)
        self.Bind(wx.EVT_BUTTON, self.on_minus, btn_minus_left)
        self.Bind(wx.EVT_BUTTON, self.on_clear, btn_clear_left)

        self.Bind(wx.EVT_BUTTON, self.on_plus, btn_plus_right)
        self.Bind(wx.EVT_BUTTON, self.on_minus, btn_minus_right)
        self.Bind(wx.EVT_BUTTON, self.on_clear, btn_clear_right)

        self.Bind(wx.EVT_BUTTON, self.on_search, btn_search)
        self.Bind(wx.EVT_BUTTON, self.on_settings, btn_settings)

        self.Bind(wx.EVT_BUTTON, self.show_settings_dialog, btn_settings)

        self.Centre()
        self.Show(True)

    def on_left_selection(self, event):
        selected_item = self.listbox_left.GetStringSelection()
        self.console_text.AppendText(f"Selected from left: {selected_item}\n")

    def on_right_selection(self, event):
        selected_item = self.listbox_right.GetStringSelection()
        self.console_text.AppendText(f"Selected from right: {selected_item}\n")

    def on_plus(self, event):
        button_id = event.GetEventObject().GetId()
        wildcard = "All Supported Images|*.jpg;*.png;*.webp"
        dialog = wx.FileDialog(self, "Выберите файлы", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            selected_files = dialog.GetPaths()
            for file_path in selected_files:

                short_path = self.format_file_name(file_path)
                if button_id == 10:
                    self.listbox_left.Append(short_path)
                    self.l_left_selection.append((file_path, short_path))
                elif button_id == 20:
                    self.listbox_right.Append(short_path)
                    self.l_right_selection.append((file_path, short_path))
        dialog.Destroy()

    def on_minus(self, event):
        button_id = event.GetEventObject().GetId()
        if button_id == 11:
            print(self.l_left_selection)
            selected_item_left = self.listbox_left.GetSelection()
            if selected_item_left != wx.NOT_FOUND:
                self.listbox_left.Delete(selected_item_left)
                print(selected_item_left)
                del self.l_left_selection[selected_item_left]
        elif button_id == 21:
            print(self.l_right_selection)
            selected_item_right = self.listbox_right.GetSelection()
            if selected_item_right != wx.NOT_FOUND:
                self.listbox_right.Delete(selected_item_right)
                del self.l_left_selection[selected_item_right]

    def on_clear(self, event):
        button_id = event.GetEventObject().GetId()
        if button_id == 12:
            self.listbox_left.Clear()
            self.l_left_selection.clear()
        elif button_id == 22:
            self.listbox_right.Clear()
            self.l_right_selection.clear()

    def on_search(self, event):
        self.console_text.AppendText("Button 'Искать' pressed\n")

    def on_settings(self, event):
        self.console_text.AppendText("Button 'Настройки' pressed\n")

    def on_left_click(self, event):
        # Получаем координаты мыши
        x, y = event.GetPosition()
        print(x, y)
        selected_id = event.GetId()

        # Если индекс совпадает с последним выбранным, снимаем выделение
        if selected_id == 1:
            # Определяем индекс элемента, над которым находится мышь
            index = self.listbox_left.HitTest((x, y))
            if index == self.last_selected_index_left:
                self.listbox_left.Deselect(index)
                self.last_selected_index_left = wx.NOT_FOUND
            else:
                # Иначе, устанавливаем выделение на текущем элементе
                self.listbox_left.SetSelection(index)
                self.last_selected_index_left = index
        elif selected_id == 2:
            index = self.listbox_right.HitTest((x, y))
            if index == self.last_selected_index_right:
                self.listbox_right.Deselect(index)
                self.last_selected_index_right = wx.NOT_FOUND
            else:
                # Иначе, устанавливаем выделение на текущем элементе
                self.listbox_right.SetSelection(index)
                self.last_selected_index_right = index

        event.Skip()

    def show_settings_dialog(self, event):
        # Создание и отображение диалогового окна
        dlg = SettingsDialog(self, title="Настройки", size=(620, 320))
        result = dlg.ShowModal()
        dlg.Destroy()


class SettingsDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        gbs = wx.GridBagSizer(8, 6)   # row, col

        # Минимальный порог
        label_threshold = wx.StaticText(panel, label="Минимальный порог")
        text_threshold = wx.TextCtrl(panel)
        gbs.Add(label_threshold, pos=(0, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(text_threshold, pos=(0, 2), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Точность
        label_precision = wx.StaticText(panel, label="Точность")
        text_precision = wx.TextCtrl(panel)
        gbs.Add(label_precision, pos=(1, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(text_precision, pos=(1, 2), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Выпадающий список
        label_dropdown = wx.StaticText(panel, label="Направление поиска")
        choices = ["Картинки по скриншотам", "Скриншоты по картинкам"]
        dropdown = wx.Choice(panel, choices=choices)
        dropdown.SetSelection(0)
        gbs.Add(label_dropdown, pos=(2, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(dropdown, pos=(2, 2), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Галочка "Учитывать вложенные папки"
        label_checkbox_folders = wx.StaticText(panel, label="Учитывать вложенные папки")
        checkbox_nested_folders = wx.CheckBox(panel)
        gbs.Add(label_checkbox_folders, pos=(3, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(checkbox_nested_folders, pos=(3, 2), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Сохранять в
        label_save_to = wx.StaticText(panel, label="Сохранять в")
        self.text_save_to = wx.TextCtrl(panel)
        btn_browse = wx.Button(panel, label="Обзор")
        gbs.Add(label_save_to, pos=(4, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.text_save_to, pos=(4, 2), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(btn_browse, pos=(4, 5), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        vbox.Add(gbs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        gbs.AddGrowableCol(3)

        vbox.Add(wx.StaticText(panel, label=""), 1, wx.EXPAND)

        # Кнопки Ок и Отмена
        btn_ok = wx.Button(panel, label="OK")
        btn_cancel = wx.Button(panel, label="Отмена")
        hbox_btns = wx.BoxSizer(wx.HORIZONTAL)
        hbox_btns.Add(btn_ok, 0, wx.ALL, 10)
        hbox_btns.Add(btn_cancel, 0, wx.ALL, 10)
        vbox.Add(hbox_btns, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(vbox)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.on_browse, btn_browse)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)

    def on_ok(self, event):
        # Обработка нажатия кнопки "OK"
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        # Обработка нажатия кнопки "Отмена"
        self.EndModal(wx.ID_CANCEL)

    def on_browse(self, event):
        # Обработка нажатия кнопки "Обзор"
        dlg = wx.DirDialog(self, "Выберите папку", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.text_save_to.SetValue(dlg.GetPath())
            dlg.Destroy()


app = wx.App(False)
frame = MyFrame(None, "Check Images")
app.MainLoop()