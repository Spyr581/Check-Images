# Check images by OpenCV with GUI
# Version 1.2
# https://github.com/Spyr581/Check-Images/tree/GUI


import wx
import os
import subprocess
from ci import CheckImages
from settings import SettingsData, SettingsUtils


class GUIUtils:
    def __init__(self):
        pass

    @staticmethod
    def check_file_presence(f, any_list):
        return any(f == item[0] for item in any_list)

    @staticmethod
    def format_file_name(file_path, max_length):
        if len(file_path) <= max_length:
            return file_path
        else:
            return f"...{file_path[-max_length:]}"

    def get_max_text_length(self, element, file_path):
        # Получим размер текста в пикселях
        text_width, text_height = element.GetTextExtent(file_path)
        # Получим ширину списка в пикселях
        listbox_width = element.GetSize().GetWidth()
        # Определим и вернем, сколько символов влезет в ширину списка
        max_width = int(listbox_width / (text_width / len(file_path)))
        # Поправка
        if max_width >= 8:
            max_width = max_width - 8

        return max_width


class DropTarget(wx.FileDropTarget, GUIUtils):
    extensions = ['.jpg', '.png', '.webp']

    def __init__(self, element, l_filepaths, emb_folders):
        super().__init__()
        self.element = element
        self.l_filepaths = l_filepaths
        self.emb_folders = emb_folders

    def reinitialize(self, element, l_filepaths, emb_folders):
        self.element = element
        self.l_filepaths = l_filepaths
        self.emb_folders = emb_folders

    @classmethod
    def check_file_extension(cls, f):
        return os.path.splitext(f)[1] in cls.extensions

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            if os.path.isdir(filename):
                # Если это папка, добавляем имена файлов в папке в ListBox
                if self.emb_folders:
                    for root, dirs, files in os.walk(filename):
                        for file in files:
                            if not self.check_file_extension(file):
                                continue
                            full_filename = os.path.join(root, file)
                            if self.check_file_presence(full_filename, self.l_filepaths):
                                continue
                            max_length = self.get_max_text_length(self.element, full_filename)
                            short_path = self.format_file_name(full_filename, max_length)
                            self.element.Append(short_path)
                            self.l_filepaths.append((full_filename, short_path))

                else:
                    files_in_folder = [f for f in os.listdir(filename) if os.path.isfile(os.path.join(filename, f))]
                    for file_in_folder in files_in_folder:
                        if not self.check_file_extension(file_in_folder):
                            continue
                        full_filename = os.path.join(filename, file_in_folder)
                        if self.check_file_presence(full_filename, self.l_filepaths):
                            continue
                        max_length = self.get_max_text_length(self.element, full_filename)
                        short_path = self.format_file_name(full_filename, max_length)
                        self.element.Append(short_path)
                        self.l_filepaths.append((full_filename, short_path))
            else:
                if not self.check_file_extension(filename):
                    continue
                if self.check_file_presence(filename, self.l_filepaths):
                    continue
                max_length = self.get_max_text_length(self.element, filename)
                short_path = self.format_file_name(filename, max_length)
                self.element.Append(short_path)
                self.l_filepaths.append((filename, short_path))

        return True


class CIMainWindow(wx.Frame, GUIUtils):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(1280, 800))

        self.added_files = {'left': [],
                            'right': []}
        self.listbox = {}
        self.droptarget = {}
        self.listbox_buttons = {'left': {}, 'right': {}}

        self.mouse_position = None

        self.settings = SettingsData()
        self.settings_utils = SettingsUtils()
        self.settings_utils.load_settings()

        # Создаем горизонтальный разделитель и две панели, которые он будет разделять
        splitter = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_3D)
        panel_top = wx.Panel(splitter, wx.ID_ANY)
        panel_bottom = wx.Panel(splitter, wx.ID_ANY)

        # Устанавливаем минимальный размер для каждой из панелей (чтобы не утянуть разделитель к краю окна)
        splitter.SetMinimumPaneSize(50)

        # Создаем горизотнтальный и вертикальный сайзеры
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Создаем горизонтальный бокссайзер для первых двух областей
        hbox_top = wx.BoxSizer(wx.HORIZONTAL)

        # Левая часть (название, поле выбора и кнопки)
        vbox_left = wx.BoxSizer(wx.VERTICAL)

        label_left = wx.StaticText(panel_top, label="СКРИНШОТЫ")
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        label_left.SetFont(font)
        vbox_left.Add(label_left, 0, wx.ALIGN_CENTER)

        # Создаем горизонтальный бокссайзер для поля выбора и кнопок слева
        hbox_left = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox['left'] = wx.ListBox(panel_top, choices=[], style=wx.LB_MULTIPLE, id=1)
        # Устанавливаем DropTarget
        self.droptarget['left'] = DropTarget(self.listbox['left'],
                                          self.added_files['left'],
                                          self.settings.embedded_folders)
        self.listbox['left'].SetDropTarget(self.droptarget['left'])
        hbox_left.Add(self.listbox['left'], 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Кнопки +, -, Очистить для левого поля
        vbox_buttons_left = wx.BoxSizer(wx.VERTICAL)
        self.listbox_buttons['left']['plus'] = wx.Button(panel_top, label="+", size=(50, 30), id=10)
        self.listbox_buttons['left']['minus'] = wx.Button(panel_top, label="-", size=(50, 30), id=11)
        self.listbox_buttons['left']['refresh'] = wx.Button(panel_top, label="Обновить", size=(80, 30), id=12)
        self.listbox_buttons['left']['clear'] = wx.Button(panel_top, label="Очистить", size=(80, 30), id=13)

        vbox_buttons_left.Add(self.listbox_buttons['left']['plus'], 0,
                              wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        vbox_buttons_left.Add(self.listbox_buttons['left']['minus'], 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_left.Add(self.listbox_buttons['left']['refresh'], 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_left.Add(self.listbox_buttons['left']['clear'], 0,
                              wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        hbox_left.Add(vbox_buttons_left, 0, wx.EXPAND | wx.ALL, 5)

        vbox_left.Add(hbox_left, 1, wx.EXPAND)
        hbox_top.Add(vbox_left, 1, wx.EXPAND | wx.ALL, 5)

        # Правая часть (название, поле выбора и кнопки)
        vbox_right = wx.BoxSizer(wx.VERTICAL)

        label_right = wx.StaticText(panel_top, label="КАРТИНКИ")
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        label_right.SetFont(font)
        vbox_right.Add(label_right, 0, wx.ALIGN_CENTER)

        # Создаем горизонтальный бокссайзер для поля выбора и кнопок справа
        hbox_right = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox['right'] = wx.ListBox(panel_top, choices=[], style=wx.LB_MULTIPLE, id=2)
        # Устанавливаем DropTarget
        self.droptarget['right'] = DropTarget(self.listbox['right'], self.added_files['right'], self.settings.embedded_folders)
        self.listbox['right'].SetDropTarget(self.droptarget['right'])
        hbox_right.Add(self.listbox['right'], 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Кнопки +, -, Очистить для правого поля
        vbox_buttons_right = wx.BoxSizer(wx.VERTICAL)
        self.listbox_buttons['right']['plus'] = wx.Button(panel_top, label="+", size=(50, 30), id=20)
        self.listbox_buttons['right']['minus'] = wx.Button(panel_top, label="-", size=(50, 30), id=21)
        self.listbox_buttons['right']['refresh'] = wx.Button(panel_top, label="Обновить", size=(80, 30), id=22)
        self.listbox_buttons['right']['clear'] = wx.Button(panel_top, label="Очистить", size=(80, 30), id=23)

        vbox_buttons_right.Add(self.listbox_buttons['right']['plus'], 0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        vbox_buttons_right.Add(self.listbox_buttons['right']['minus'], 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_right.Add(self.listbox_buttons['right']['refresh'], 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_right.Add(self.listbox_buttons['right']['clear'], 0,
                               wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        hbox_right.Add(vbox_buttons_right, 0, wx.EXPAND | wx.ALL, 5)

        vbox_right.Add(hbox_right, 1, wx.EXPAND)
        hbox_top.Add(vbox_right, 1, wx.EXPAND | wx.ALL, 5)

        # Добавляем получившиеся элементы в вертикальный сайзер
        vbox.Add(hbox_top, 1, wx.EXPAND)

        # Кнопки "Искать", "Очистить", "Настройки"
        hbox_bottom_buttons = wx.BoxSizer(wx.HORIZONTAL)
        btn_search = wx.Button(panel_top, label="ИСКАТЬ", size=(80, 30))
        btn_clear_bottom = wx.Button(panel_top, label="Очистить", size=(80, 30))
        btn_clear_all = wx.Button(panel_top, label="Очистить все", size=(100, 30))
        btn_settings = wx.Button(panel_top, label="Настройки", size=(80, 30))

        hbox_bottom_buttons.AddStretchSpacer()
        hbox_bottom_buttons.Add(btn_search, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        hbox_bottom_buttons.Add(btn_clear_bottom, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)
        hbox_bottom_buttons.Add((50, 0), 0)
        hbox_bottom_buttons.Add(btn_clear_all, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        hbox_bottom_buttons.AddStretchSpacer()
        hbox_bottom_buttons.Add(btn_settings, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        # Добавляем в вертикальный сайзер еще кнопки
        vbox.Add(hbox_bottom_buttons, 0, wx.EXPAND | wx.TOP, 10)

        # Кидаем вертикальный сайзер в горизонтальный, чтобы работал разделитель
        hbox.Add(vbox, 1, wx.EXPAND)

        # Привязываемся к верхней панели
        panel_top.SetSizer(hbox)

        # Создаем нижнюю область
        sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.console_text = wx.TextCtrl(panel_bottom, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.console_text.SetFont(wx.Font(wx.FontInfo(12).Family(wx.FONTFAMILY_TELETYPE)))
        sizer_bottom.Add(self.console_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        panel_bottom.SetSizer(sizer_bottom)

        # Устанавливаем вертикальное разделение между верхней и нижней панелями, число - это размер верхней панели
        splitter.SplitHorizontally(panel_top, panel_bottom, 300)

        # Создаем бокс-сайзер для размещения SplitterWindow в основном окне
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Изменение ширины листбокса
        self.Bind(wx.EVT_SIZE, self.on_size)

        # # Привязываем событие щелчка мыши для сохранения позиции
        self.listbox['left'].Bind(wx.EVT_LEFT_DOWN, self.on_listbox_left_click)
        self.listbox['right'].Bind(wx.EVT_LEFT_DOWN, self.on_listbox_left_click)

        # Двойной щелчок по пути файла
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_double_click)

        # Устанавливаем обработчики событий для кнопок
        self.Bind(wx.EVT_BUTTON, self.on_plus, self.listbox_buttons['left']['plus'])
        self.Bind(wx.EVT_BUTTON, self.on_minus, self.listbox_buttons['left']['minus'])
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.listbox_buttons['left']['refresh'])
        self.Bind(wx.EVT_BUTTON, self.on_clear, self.listbox_buttons['left']['clear'])

        self.Bind(wx.EVT_BUTTON, self.on_plus, self.listbox_buttons['right']['plus'])
        self.Bind(wx.EVT_BUTTON, self.on_minus, self.listbox_buttons['right']['minus'])
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.listbox_buttons['right']['refresh'])
        self.Bind(wx.EVT_BUTTON, self.on_clear, self.listbox_buttons['right']['clear'])

        self.Bind(wx.EVT_BUTTON, self.on_search, btn_search)
        self.Bind(wx.EVT_BUTTON, self.on_clear_bottom, btn_clear_bottom)
        self.Bind(wx.EVT_BUTTON, self.on_clear_all, btn_clear_all)
        self.Bind(wx.EVT_BUTTON, self.show_settings_dialog, btn_settings)

        self.Centre()
        self.Show(True)

    def on_listbox_left_click(self, event):
        self.mouse_position = event.GetPosition()
        event.Skip()

    def on_double_click(self, event):
        if self.mouse_position is not None:
            listbox_id = event.GetEventObject().GetId()
            if 1 == listbox_id:
                left_or_right = 'left'
            elif 2 == listbox_id:
                left_or_right = 'right'
            else:
                raise ValueError(f'Incorrect id of listbox: {listbox_id}')
            index = self.listbox[left_or_right].HitTest(self.mouse_position)
            image_path = self.added_files[left_or_right][index][0]
            self.open_image(image_path)
        event.Skip()

    def open_image(self, image_path):
        # Открытие изображения в стандартном просмотрщике
        if wx.Platform == "__WXMSW__":
            os.startfile(image_path)
        elif wx.Platform == "__WXMAC__":
            subprocess.call(["open", image_path])
        else:
            subprocess.call(["xdg-open", image_path])

    def __reinitialize_droptarget(self, left_or_right):
        self.droptarget[left_or_right].reinitialize(self.listbox[left_or_right],
                                                    self.added_files[left_or_right],
                                                    self.settings.embedded_folders)

    def __add_files(self, left_or_right, selected_files):
        for file_path in selected_files:
            max_length = self.get_max_text_length(self.listbox[left_or_right], file_path)
            short_path = self.format_file_name(file_path, max_length)
            self.listbox[left_or_right].Append(short_path)
            self.added_files[left_or_right].append((file_path, short_path))
            self.__reinitialize_droptarget(left_or_right)

    def __remove_entries(self, left_or_right):
        selected_items = self.listbox[left_or_right].GetSelections()
        if len(selected_items) != 0:
            for idx in sorted(selected_items, reverse=True):
                self.listbox[left_or_right].Delete(idx)
                del self.added_files[left_or_right][idx]
        self.__reinitialize_droptarget(left_or_right)

    def __refresh_listbox(self, left_or_right):
        self.__flush_listbox_entries(left_or_right)
        l_temp = []
        for path, short_path in sorted(self.added_files[left_or_right], key=lambda x: x[0]):
            if os.path.exists(path):
                l_temp.append((path, short_path))
                self.listbox[left_or_right].Append(short_path)
        self.added_files[left_or_right] = l_temp
        self.__reinitialize_droptarget(left_or_right)

    def __clear_listbox(self, left_or_right):
        self.__flush_listbox_entries(left_or_right)
        self.added_files[left_or_right].clear()
        self.__reinitialize_droptarget(left_or_right)

    def __flush_listbox_entries(self, left_or_right):
        selections = self.listbox[left_or_right].GetSelections()  # list
        for idx in selections:
            self.listbox[left_or_right].Deselect(idx)
        self.listbox[left_or_right].Clear()

    def on_plus(self, event):
        button_id = event.GetEventObject().GetId()
        wildcard = "Все изображения|*.jpg;*.png;*.webp"
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        dialog = wx.FileDialog(self, "Выберите файлы", wildcard=wildcard, style=style)
        if dialog.ShowModal() == wx.ID_OK:
            selected_files = dialog.GetPaths()
            if button_id == 10:
                self.__add_files('left', selected_files)
            elif button_id == 20:
                self.__add_files('right', selected_files)
        dialog.Destroy()

    def on_minus(self, event):
        button_id = event.GetEventObject().GetId()
        if button_id == 11:
            self.__remove_entries('left')
        elif button_id == 21:
            self.__remove_entries('right')

    def on_refresh(self, event):
        button_id = event.GetEventObject().GetId()
        if button_id == 12:
            self.__refresh_listbox('left')
        elif button_id == 22:
            self.__refresh_listbox('right')

    def on_clear(self, event):
        button_id = event.GetEventObject().GetId()
        if button_id == 13:
            self.__clear_listbox('left')
        elif button_id == 23:
            self.__clear_listbox('right')

    def on_search(self, event):
        if not self.added_files['left'] or not self.added_files['right']:
            return

        scr_paths = [double_path[0] for double_path in self.added_files['left']]
        tmpl_paths = [double_path[0] for double_path in self.added_files['right']]
        check = CheckImages(tmpl_paths,
                            scr_paths,
                            self.console_text,
                            self.settings.min_threshold,
                            self.settings.precision,
                            self.settings.direction,
                            self.settings.save_txt,
                            self.settings.save_to)
        check.run()

    def on_clear_bottom(self, event):
        self.console_text.SetValue("")

    def on_size(self, event):
        for idx, filepaths in enumerate(self.added_files['left']):   # filepaths - это кортеж, нужен 0 элемент
            max_length = self.get_max_text_length(self.listbox['left'], filepaths[0])
            short_path = self.format_file_name(filepaths[0], max_length)
            self.listbox['left'].SetString(idx, short_path)

        for idx, filepaths in enumerate(self.added_files['right']):   # filepaths - это кортеж, нужен 0 элемент
            max_length = self.get_max_text_length(self.listbox['right'], filepaths[0])
            short_path = self.format_file_name(filepaths[0], max_length)
            self.listbox['right'].SetString(idx, short_path)

        event.Skip()

    def on_clear_all(self, event):
        self.__clear_listbox('left')
        self.__clear_listbox('right')
        self.console_text.SetValue("")

    def show_settings_dialog(self, event):
        # Создание и отображение диалогового окна
        dlg = SettingsDialog(self, title="Настройки", size=(640, 400))
        dlg.ShowModal()
        dlg.Destroy()
        self.__reinitialize_droptarget('left')
        self.__reinitialize_droptarget('right')


class SettingsDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.__min_thr = 0.01
        self.__max_thr = 1
        self.__min_prec = 1
        self.__max_prec = 8

        self.settings = SettingsData()
        self.settings_utils = SettingsUtils()
        self.d_loaded = dict()
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        gbs = wx.GridBagSizer(9, 6)   # row, col

        # Минимальный порог
        label_threshold = wx.StaticText(panel, label=f"Минимальный порог: {self.__min_thr}-{self.__max_thr}")
        self.spin_threshold = wx.SpinCtrlDouble(panel, min=self.__min_thr, max=self.__max_thr, inc=0.01)
        gbs.Add(label_threshold, pos=(0, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.spin_threshold, pos=(0, 2), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Точность
        label_precision = wx.StaticText(panel, label=f"Точность (10^-N): {self.__min_prec}-{self.__max_prec}")
        self.spin_precision = wx.SpinCtrl(panel, min=self.__min_prec, max=self.__max_prec)
        self.spin_precision.SetIncrement(1)
        gbs.Add(label_precision, pos=(1, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.spin_precision, pos=(1, 2), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Выпадающий список
        dropdown_direction = wx.StaticText(panel, label="Направление поиска")
        choices = ["Картинки по скриншотам", "Скриншоты по картинкам"]
        self.dropdown_direction = wx.Choice(panel, choices=choices)
        gbs.Add(dropdown_direction, pos=(2, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.dropdown_direction, pos=(2, 2), span=(1, 3),
                flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Галочка "Учитывать вложенные папки"
        label_checkbox_embedded_folders = wx.StaticText(panel, label="Учитывать вложенные папки")
        self.checkbox_embedded_folders = wx.CheckBox(panel)
        gbs.Add(label_checkbox_embedded_folders, pos=(3, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.checkbox_embedded_folders, pos=(3, 2), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Галочка "Сохранять txt файл"
        label_checkbox_save_txt = wx.StaticText(panel, label="Сохранять txt файл")
        self.checkbox_save_txt = wx.CheckBox(panel)
        gbs.Add(label_checkbox_save_txt, pos=(4, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.checkbox_save_txt, pos=(4, 2), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Путь к файлу
        self.text_save_to = wx.TextCtrl(panel)
        self.btn_browse = wx.Button(panel, label="Обзор")
        gbs.Add(self.text_save_to, pos=(5, 0), span=(1, 5), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        gbs.Add(self.btn_browse, pos=(5, 5), flag=wx.LEFT | wx.RIGHT, border=5)

        vbox.Add(gbs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        gbs.AddGrowableCol(3)

        vbox.Add(wx.StaticText(panel, label=""), 1, wx.EXPAND)

        # Кнопки Ок, Отмена, По умолчанию
        btn_ok = wx.Button(panel, label="OK")
        btn_cancel = wx.Button(panel, label="Отмена")
        btn_default = wx.Button(panel, label="По умолчанию")
        hbox_btns = wx.BoxSizer(wx.HORIZONTAL)
        hbox_btns.Add(btn_ok, 0, wx.RIGHT, 20)
        hbox_btns.Add(btn_cancel, 0, wx.RIGHT, 30)
        hbox_btns.Add(btn_default, 0, wx.RIGHT, 20)
        vbox.Add(hbox_btns, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)

        self.set_window_settings()
        panel.SetSizer(vbox)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.on_browse, self.btn_browse)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_default, btn_default)
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_change, self.checkbox_save_txt)

    def on_browse(self, event):
        # Создаем диалоговое окно сохранения файла
        wildcard = "Текстовые файлы (*.txt)|*.txt"
        file_dialog = wx.FileDialog(self, "Выберите файл для сохранения",
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                                    wildcard=wildcard)

        if file_dialog.ShowModal() == wx.ID_OK:
            # Получаем выбранный путь файла
            selected_path = file_dialog.GetPath()
            # Устанавливаем путь в текстовом поле
            self.text_save_to.SetValue(selected_path)

        file_dialog.Destroy()

    def on_ok(self, event):
        # Обработка нажатия кнопки "OK"
        # Проверка пути сохранения файла
        if self.checkbox_save_txt.GetValue():
            save_path = self.text_save_to.GetValue()
            forbidden_symbols = '*?\"<>|'

            if not os.path.isabs(save_path) or any(char in forbidden_symbols for char in save_path):
                wx.MessageBox("Введите правильный путь к файлу.", "Некорректный путь", wx.OK | wx.ICON_ERROR)
                return

        # Сравнение текущих значений с загруженными
        min_threshold = float(self.spin_threshold.GetValue())
        precision = int(self.spin_precision.GetValue())
        direction = self.dropdown_direction.GetSelection()
        embedded_folders = self.checkbox_embedded_folders.GetValue()
        save_txt = self.checkbox_save_txt.GetValue()
        save_to = self.text_save_to.GetValue()

        if (
                min_threshold != self.d_loaded['min_threshold'] or
                precision != self.d_loaded['precision'] or
                direction != self.d_loaded['direction'] or
                embedded_folders != self.d_loaded['embedded_folders'] or
                save_txt != self.d_loaded['save_txt'] or
                save_to != self.d_loaded['save_to']
        ):
            # Если значения отличаются, сохраняем изменения в файл конфигурации
            self.settings_utils.save_settings(min_threshold, precision, direction, embedded_folders, save_txt, save_to)

        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        # Обработка нажатия кнопки "Отмена"
        self.EndModal(wx.ID_CANCEL)

    def on_default(self, event):
        self.settings_utils.reset_settings()
        self.__set_settings_to_fields()

    def on_checkbox_change(self, event):
        checkbox = event.GetEventObject()

        # Получаем состояние галочки
        is_checked = checkbox.GetValue()

        # Устанавливаем активность/неактивность для текстового поля и кнопки
        self.text_save_to.Enable(is_checked)
        self.btn_browse.Enable(is_checked)

    def __set_settings_to_fields(self):
        self.spin_threshold.SetValue(self.settings.min_threshold)
        self.spin_precision.SetValue(self.settings.precision)
        self.dropdown_direction.SetSelection(self.settings.direction)
        self.checkbox_embedded_folders.SetValue(self.settings.embedded_folders)
        self.checkbox_save_txt.SetValue(self.settings.save_txt)
        self.text_save_to.SetValue(self.settings.save_to)

        # Активируем/деактивируем текстовое поле и кнопку "Обзор"
        self.text_save_to.Enable(self.settings.save_txt)
        self.btn_browse.Enable(self.settings.save_txt)

    def set_window_settings(self):
        self.settings_utils.load_settings()

        # Устанавливаем значения в соответствующие элементы окна
        self.__set_settings_to_fields()

        self.d_loaded['min_threshold'] = float(self.settings.min_threshold)
        self.d_loaded['precision'] = int(self.settings.precision)
        self.d_loaded['direction'] = self.settings.direction
        self.d_loaded['embedded_folders'] = self.settings.embedded_folders
        self.d_loaded['save_txt'] = self.settings.save_txt
        self.d_loaded['save_to'] = self.settings.save_to


if __name__ == '__main__':
    app = wx.App(False)
    frame = CIMainWindow(None, "Check Images")
    app.MainLoop()
