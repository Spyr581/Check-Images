# Check images by OpenCV with GUI
# Version 1.0

import wx
import os
import configparser
from ci import CheckImages


class SettingsData:
    _instance = None
    __default_settings = {
        'threshold': 0.6,
        'precision': 0.0001,
        'check_direction': 0,
        'embedded_folders': False,
        'save_txt': True,
        'text_save_to': os.path.join(os.getcwd(), 'threshold.txt')
    }
    settings = None   # текущие валидные настройки

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)

    # def __init__(self):
    #     self.__threshold =

    @property
    def get_default_settings(self):
        return self.__default_settings

    @classmethod
    def check_settings_on_load(cls, d_loaded):
        # Проверка загружаемых настроек из ini файла
        if not (0 <= float(d_loaded['threshold']) <= 0.999999):
            d_loaded['threshold'] = cls.__default_settings['threshold']

        if not (0.0000001 <= float(d_loaded['precision']) <= 0.1):
            d_loaded['precision'] = cls.__default_settings['precision']

        if not (0 == d_loaded['check_direction'] or 1 == d_loaded['check_direction']):
            d_loaded['check_direction'] = cls.__default_settings['check_direction']

        if not isinstance(d_loaded['embedded_folders'], bool):
            d_loaded['embedded_folders'] = cls.__default_settings['embedded_folders']

        if not isinstance(d_loaded['save_txt'], bool):
            d_loaded['save_txt'] = cls.__default_settings['save_txt']

        forbidden_symbols = '*?\"<>|'
        if (
                not os.path.isabs(d_loaded['text_save_to']) or
                any(char in forbidden_symbols for char in d_loaded['text_save_to'])
        ):
            d_loaded['text_save_to'] = cls.__default_settings['text_save_to']

        return d_loaded


class GUIUtils:
    def __init__(self):
        pass

    @staticmethod
    def check_file_presence(f, any_list):
        return any(f == item[0] for item in any_list)

    @staticmethod
    def format_file_name(file_path, max_length):
        file_name = os.path.basename(file_path)
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

    def __init__(self, element, l_filepaths):
        super().__init__()
        self.element = element
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

        self.l_left_selection = []
        self.l_right_selection = []

        self.tooltip = wx.ToolTip("")
        self.last_selected_index_left = wx.NOT_FOUND
        self.last_selected_index_right = wx.NOT_FOUND

        # Создаем панель
        panel = wx.Panel(self)

        # Создаем общий вертикальный бокссайзер для разделения окна на три части
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Создаем горизонтальный бокссайзер для первых двух областей
        hbox_top = wx.BoxSizer(wx.HORIZONTAL)

        # Левая часть (название, поле выбора и кнопки)
        vbox_left = wx.BoxSizer(wx.VERTICAL)

        label_left = wx.StaticText(panel, label="СКРИНШОТЫ")
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        label_left.SetFont(font)
        vbox_left.Add(label_left, 0, wx.ALIGN_CENTER)

        # Создаем горизонтальный бокссайзер для поля выбора и кнопок слева
        hbox_left = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox_left = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE, id=1)
        # Устанавливаем DropTarget
        self.listbox_left.SetDropTarget(DropTarget(self.listbox_left, self.l_left_selection))
        hbox_left.Add(self.listbox_left, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Кнопки +, -, Очистить для левого поля
        vbox_buttons_left = wx.BoxSizer(wx.VERTICAL)
        btn_plus_left = wx.Button(panel, label="+", size=(50, 30), id=10)
        btn_minus_left = wx.Button(panel, label="-", size=(50, 30), id=11)
        btn_clear_left = wx.Button(panel, label="Очистить", size=(80, 30), id=12)

        vbox_buttons_left.Add(btn_plus_left, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        vbox_buttons_left.Add(btn_minus_left, 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_left.Add(btn_clear_left, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        hbox_left.Add(vbox_buttons_left, 0, wx.EXPAND | wx.ALL, 5)

        vbox_left.Add(hbox_left, 1, wx.EXPAND)
        hbox_top.Add(vbox_left, 1, wx.EXPAND | wx.ALL, 5)

        # Правая часть (название, поле выбора и кнопки)
        vbox_right = wx.BoxSizer(wx.VERTICAL)

        label_right = wx.StaticText(panel, label="КАРТИНКИ")
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        label_right.SetFont(font)
        vbox_right.Add(label_right, 0, wx.ALIGN_CENTER)

        # Создаем горизонтальный бокссайзер для поля выбора и кнопок справа
        hbox_right = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox_right = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE, id=2)
        # Устанавливаем DropTarget
        self.listbox_right.SetDropTarget(DropTarget(self.listbox_right, self.l_right_selection))
        hbox_right.Add(self.listbox_right, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Кнопки +, -, Очистить для правого поля
        vbox_buttons_right = wx.BoxSizer(wx.VERTICAL)
        btn_plus_right = wx.Button(panel, label="+", size=(50, 30), id=20)
        btn_minus_right = wx.Button(panel, label="-", size=(50, 30), id=21)
        btn_clear_right = wx.Button(panel, label="Очистить", size=(80, 30), id=22)

        vbox_buttons_right.Add(btn_plus_right, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        vbox_buttons_right.Add(btn_minus_right, 0, wx.EXPAND | wx.ALL, 5)
        vbox_buttons_right.Add(btn_clear_right, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        hbox_right.Add(vbox_buttons_right, 0, wx.EXPAND | wx.ALL, 5)

        vbox_right.Add(hbox_right, 1, wx.EXPAND)
        hbox_top.Add(vbox_right, 1, wx.EXPAND | wx.ALL, 5)

        vbox.Add(hbox_top, 1, wx.EXPAND | wx.ALL, 5)

        # Кнопки "Искать" и "Настройки" (расположены посередине)
        hbox_bottom_buttons = wx.BoxSizer(wx.HORIZONTAL)
        btn_search = wx.Button(panel, label="Искать", size=(80, 30))
        btn_settings = wx.Button(panel, label="Настройки", size=(80, 30))

        hbox_bottom_buttons.AddStretchSpacer()
        hbox_bottom_buttons.Add(btn_search, 0, wx.EXPAND | wx.RIGHT, 20)
        hbox_bottom_buttons.Add(btn_settings, 0, wx.EXPAND | wx.LEFT, 20)
        hbox_bottom_buttons.AddStretchSpacer()

        vbox.Add(hbox_bottom_buttons, 0, wx.EXPAND | wx.ALL, 5)

        # Создаем третью область под первой и второй
        self.console_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        vbox.Add(self.console_text, 1, wx.EXPAND | wx.ALL, 5)

        # Устанавливаем бокссайзер для панели
        panel.SetSizer(vbox)

        # Устанавливаем обработчики событий для выбора элементов в левом и правом полях
        # self.Bind(wx.EVT_LISTBOX, self.on_left_selection, self.listbox_left)
        # self.Bind(wx.EVT_LISTBOX, self.on_right_selection, self.listbox_right)

        # Установка/снятие выбора в списке
        self.listbox_left.Bind(wx.EVT_LEFT_UP, self.on_left_click)
        self.listbox_right.Bind(wx.EVT_LEFT_UP, self.on_left_click)

        # Изменение ширины листбокса
        self.Bind(wx.EVT_SIZE, self.on_size)

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

    # def on_left_selection(self, event):
    #     selected_item = self.listbox_left.GetStringSelection()
    #     self.console_text.AppendText(f"Selected from left: {selected_item}\n")
    #
    # def on_right_selection(self, event):
    #     selected_item = self.listbox_right.GetStringSelection()
    #     self.console_text.AppendText(f"Selected from right: {selected_item}\n")

    def on_plus(self, event):
        button_id = event.GetEventObject().GetId()
        wildcard = "All Supported Images|*.jpg;*.png;*.webp"
        dialog = wx.FileDialog(self, "Выберите файлы", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            selected_files = dialog.GetPaths()
            for file_path in selected_files:
                if button_id == 10:
                    max_length = self.get_max_text_length(self.listbox_left, file_path)
                    short_path = self.format_file_name(file_path, max_length)
                    self.listbox_left.Append(short_path)
                    self.l_left_selection.append((file_path, short_path))
                elif button_id == 20:
                    max_length = self.get_max_text_length(self.listbox_right, file_path)
                    short_path = self.format_file_name(file_path, max_length)
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
        scr_paths = [double_path[0] for double_path in self.l_left_selection]
        tmpl_paths = [double_path[0] for double_path in self.l_right_selection]
        check = CheckImages(tmpl_paths, scr_paths, 0.6, 0.0001)
        check.run()

    def on_settings(self, event):
        self.console_text.AppendText("Button 'Настройки' pressed\n")

    def on_left_click(self, event):
        # Получаем координаты мыши
        x, y = event.GetPosition()
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

    def on_size(self, event):
        for idx, filepaths in enumerate(self.l_left_selection):   # filepaths - это кортеж, нужен 0 элемент
            max_length = self.get_max_text_length(self.listbox_left, filepaths[0])
            short_path = self.format_file_name(filepaths[0], max_length)
            self.listbox_left.SetString(idx, short_path)

        for idx, filepaths in enumerate(self.l_right_selection):   # filepaths - это кортеж, нужен 0 элемент
            max_length = self.get_max_text_length(self.listbox_right, filepaths[0])
            short_path = self.format_file_name(filepaths[0], max_length)
            self.listbox_left.SetString(idx, short_path)

        event.Skip()

    def show_settings_dialog(self, event):
        # Создание и отображение диалогового окна
        dlg = SettingsDialog(self, title="Настройки", size=(640, 400))
        dlg.ShowModal()
        dlg.Destroy()


class SettingsDialog(wx.Dialog, SettingsData):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.d_loaded = dict()
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        gbs = wx.GridBagSizer(9, 6)   # row, col

        # Минимальный порог
        label_threshold = wx.StaticText(panel, label="Минимальный порог")
        self.text_threshold = wx.TextCtrl(panel)
        gbs.Add(label_threshold, pos=(0, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.text_threshold, pos=(0, 2), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Точность
        label_precision = wx.StaticText(panel, label="Точность")
        self.text_precision = wx.TextCtrl(panel)
        gbs.Add(label_precision, pos=(1, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.text_precision, pos=(1, 2), span=(1, 3), flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)

        # Выпадающий список
        dropdown_check_direction = wx.StaticText(panel, label="Направление поиска")
        choices = ["Картинки по скриншотам", "Скриншоты по картинкам"]
        self.dropdown_check_direction = wx.Choice(panel, choices=choices)
        # self.dropdown.SetSelection(0)
        gbs.Add(dropdown_check_direction, pos=(2, 0), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=5)
        gbs.Add(self.dropdown_check_direction, pos=(2, 2), span=(1, 3),
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

        # Кнопки Ок и Отмена
        btn_ok = wx.Button(panel, label="OK")
        btn_cancel = wx.Button(panel, label="Отмена")
        hbox_btns = wx.BoxSizer(wx.HORIZONTAL)
        hbox_btns.Add(btn_ok, 0, wx.RIGHT, 20)
        hbox_btns.Add(btn_cancel, 0, wx.LEFT, 20)
        vbox.Add(hbox_btns, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)

        self.load_settings()
        panel.SetSizer(vbox)
        self.Centre()

        self.text_threshold.Bind(wx.EVT_CHAR, self.on_text_char)
        self.text_precision.Bind(wx.EVT_CHAR, self.on_text_char)
        self.Bind(wx.EVT_BUTTON, self.on_browse, self.btn_browse)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox_change, self.checkbox_save_txt)

    @staticmethod
    def on_text_char(event):
        # Обработчик события ввода символа в текстовое поле
        key = event.GetKeyCode()

        # Разрешаем ввод только цифр 0-9 и точки
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in '0123456789.':
            event.Skip()

    def on_browse(self, event):
        # Создаем диалоговое окно сохранения файла
        wildcard = "Text files (*.txt)|*.txt"
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
        # Проверка порога
        if not (0 <= float(self.text_threshold.GetValue()) <= 0.999999):
            wx.MessageBox("Значение минимального порога должно быть\nв пределах 0...0.999999.",
                          "Неправильный порог", wx.OK | wx.ICON_ERROR)
            return

        # Проверка точности
        if not (0.0000001 <= float(self.text_precision.GetValue()) <= 0.1):
            wx.MessageBox("Значение точности должно быть\nв пределах 0.0000001...0.1.",
                          "Неправильный порог", wx.OK | wx.ICON_ERROR)
            return

        # Проверка пути сохранения файла
        if self.checkbox_save_txt.GetValue():
            save_path = self.text_save_to.GetValue()
            forbidden_symbols = '*?\"<>|'

            if not os.path.isabs(save_path) or any(char in forbidden_symbols for char in save_path):
                wx.MessageBox("Введите правильный путь к файлу.", "Некорректный путь", wx.OK | wx.ICON_ERROR)
                return

        # Сравнение текущих значений с загруженными
        threshold = float(self.text_threshold.GetValue())
        precision = float(self.text_precision.GetValue())
        check_direction = self.dropdown_check_direction.GetSelection()
        embedded_folders = self.checkbox_embedded_folders.GetValue()
        save_txt = self.checkbox_save_txt.GetValue()
        text_save_to = self.text_save_to.GetValue()

        if (
                threshold != self.d_loaded['threshold'] or
                precision != self.d_loaded['precision'] or
                check_direction != self.d_loaded['check_direction'] or
                embedded_folders != self.d_loaded['embedded_folders'] or
                save_txt != self.d_loaded['save_txt'] or
                text_save_to != self.d_loaded['text_save_to']
        ):
            # Если значения отличаются, сохраняем изменения в файл конфигурации
            self.save_settings()

        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        # Обработка нажатия кнопки "Отмена"
        self.EndModal(wx.ID_CANCEL)

    def on_checkbox_change(self, event):
        checkbox = event.GetEventObject()

        # Получаем состояние галочки
        is_checked = checkbox.GetValue()

        # Устанавливаем активность/неактивность для текстового поля и кнопки
        self.text_save_to.Enable(is_checked)
        self.btn_browse.Enable(is_checked)

    def save_settings(self):
        config = configparser.ConfigParser()

        # Устанавливаем значения параметров
        config['Settings'] = {
            'Threshold': self.text_threshold.GetValue(),
            'Precision': self.text_precision.GetValue(),
            'CheckDirection': str(self.dropdown_check_direction.GetSelection()),
            'EmbeddedFolders': str(self.checkbox_embedded_folders.GetValue()),
            'SaveTxt': str(self.checkbox_save_txt.GetValue()),
            'TextSaveTo': self.text_save_to.GetValue(),
        }

        # Сохраняем конфигурацию в файл
        with open('./check_images.ini', 'w') as configfile:
            config.write(configfile)

    def load_settings(self):
        config = configparser.ConfigParser()

        try:
            # Пытаемся прочитать файл конфигурации
            config.read('./check_images.ini')

            # Получаем значения параметров из файла .ini
            d_settings = dict()
            d_settings['threshold'] = config.getfloat('Settings', 'Threshold')
            d_settings['precision'] = config.getfloat('Settings', 'Precision')
            d_settings['check_direction'] = config.getint('Settings', 'CheckDirection')
            d_settings['embedded_folders'] = config.getboolean('Settings', 'EmbeddedFolders')
            d_settings['save_txt'] = config.getboolean('Settings', 'SaveTxt')
            d_settings['text_save_to'] = config.get('Settings', 'TextSaveTo')

            d_settings = self.check_settings_on_load(d_settings)
            self.settings = d_settings

            # Устанавливаем значения в соответствующие элементы окна
            self.text_threshold.SetValue(str(d_settings['threshold']))
            self.text_precision.SetValue(str(d_settings['precision']))
            self.dropdown_check_direction.SetSelection(d_settings['check_direction'])
            self.checkbox_embedded_folders.SetValue(d_settings['embedded_folders'])
            self.checkbox_save_txt.SetValue(d_settings['save_txt'])
            self.text_save_to.SetValue(d_settings['text_save_to'])

            # Активируем/деактивируем текстовое поле и кнопку "Обзор"
            self.text_save_to.Enable(d_settings['save_txt'])
            self.btn_browse.Enable(d_settings['save_txt'])

        except (configparser.Error, FileNotFoundError):
            # Если возникает ошибка, используем значения по умолчанию
            self.text_threshold.SetValue(str(self.get_default_settings['threshold']))
            self.text_precision.SetValue(str(self.get_default_settings['precision']))
            self.dropdown_check_direction.SetSelection(self.get_default_settings['check_direction'])
            self.checkbox_embedded_folders.SetValue(self.get_default_settings['embedded_folders'])
            self.checkbox_save_txt.SetValue(self.get_default_settings['save_txt'])
            self.text_save_to.SetValue(self.get_default_settings['text_save_to'])

            self.settings = self.get_default_settings

        self.d_loaded['threshold'] = float(self.text_threshold.GetValue())
        self.d_loaded['precision'] = float(self.text_precision.GetValue())
        self.d_loaded['check_direction'] = self.dropdown_check_direction.GetSelection()
        self.d_loaded['embedded_folders'] = self.checkbox_embedded_folders.GetValue()
        self.d_loaded['save_txt'] = self.checkbox_save_txt.GetValue()
        self.d_loaded['text_save_to'] = self.text_save_to.GetValue()

        self.d_loaded = self.check_settings_on_load(self.d_loaded)


if __name__ == '__main__':
    app = wx.App(False)
    frame = CIMainWindow(None, "Check Images")
    app.MainLoop()
