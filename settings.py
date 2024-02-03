import os
import configparser


class BaseSettingsDescriptor:
    def __init__(self, default_value):
        self.default_value = default_value
        self.name = None

    def __get__(self, instance, owner):
        if self.name is None:
            raise AttributeError(f"Descriptor '{self.__class__.__name__}' has no associated name.")
        return instance.__dict__.get(self.name, self.default_value)

    def __set__(self, instance, value):
        raise AttributeError(f'Setting values for {self.name} is not allowed')

    def __set_name__(self, owner, name):
        self.name = name


class SettingsDescriptor(BaseSettingsDescriptor):
    def __set__(self, instance, value):
        if self.name is None:
            raise AttributeError(f"Descriptor '{self.__class__.__name__}' has no associated name.")
        instance.__dict__[self.name] = value


class SettingsData:
    _instance = None

    default_min_threshold = BaseSettingsDescriptor(0.6)
    default_precision = BaseSettingsDescriptor(0.0001)
    default_check_direction = BaseSettingsDescriptor(0)
    default_embedded_folders = BaseSettingsDescriptor(False)
    default_save_txt = BaseSettingsDescriptor(True)
    default_save_to = BaseSettingsDescriptor(os.path.join(os.getcwd(), 'thresholds.txt'))

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)

    def __init__(self):
        self.min_threshold = SettingsDescriptor(None)
        self.precision = SettingsDescriptor(None)
        self.check_direction = SettingsDescriptor(None)
        self.embedded_folders = SettingsDescriptor(None)
        self.save_txt = SettingsDescriptor(None)
        self.save_to = SettingsDescriptor(None)

    def check_settings_on_load(self):
        # Проверка загружаемых настроек из ini файла
        if not (0 <= float(self.min_threshold) <= 0.999999):
            self.min_threshold = self.default_min_threshold

        if not (0.0000001 <= float(self.precision) <= 0.1):
            self.precision = self.default_precision

        if not (0 == self.check_direction or 1 == self.check_direction):
            self.check_direction = self.default_check_direction

        if not isinstance(self.embedded_folders, bool):
            self.embedded_folders = self.default_embedded_folders

        if not isinstance(self.save_txt, bool):
            self.save_txt = self.default_save_txt

        forbidden_symbols = '*?\"<>|'
        if not os.path.isabs(self.save_to) or any(char in forbidden_symbols for char in self.save_to):
            self.save_to = self.default_save_to

    def load_settings(self):
        config = configparser.ConfigParser()

        try:
            # Пытаемся прочитать файл конфигурации
            config.read('./check_images.ini')

            # Получаем значения параметров из файла .ini
            self.min_threshold = config.getfloat('Settings', 'MinThreshold')
            self.precision = config.getfloat('Settings', 'Precision')
            self.check_direction = config.getint('Settings', 'CheckDirection')
            self.embedded_folders = config.getboolean('Settings', 'EmbeddedFolders')
            self.save_txt = config.getboolean('Settings', 'SaveTxt')
            self.save_to = config.get('Settings', 'SaveTo')

            self.check_settings_on_load()

        except (configparser.Error, FileNotFoundError):
            # Если возникает ошибка, используем значения по умолчанию
            self.min_threshold = self.default_min_threshold
            self.precision = self.default_precision
            self.check_direction = self.default_check_direction
            self.embedded_folders = self.default_embedded_folders
            self.save_txt = self.default_save_txt
            self.save_to = self.default_save_to

