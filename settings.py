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
        return cls._instance

    def __init__(self):
        self.min_threshold = SettingsDescriptor(None)
        self.precision = SettingsDescriptor(None)
        self.check_direction = SettingsDescriptor(None)
        self.embedded_folders = SettingsDescriptor(None)
        self.save_txt = SettingsDescriptor(None)
        self.save_to = SettingsDescriptor(None)


class SettingsUtils:
    def __init__(self):
        self.settings = SettingsData()  # не нужно, просто чтобы интерпретатор не ругался, работает потому,
        # что везде названо self.settings

    def check_settings_on_load(self):
        # Проверка загружаемых настроек из ini файла
        if not (0 <= float(self.settings.min_threshold) <= 0.999999):
            self.settings.min_threshold = self.settings.default_min_threshold

        if not (0.0000001 <= float(self.settings.precision) <= 0.1):
            self.settings.precision = self.settings.default_precision

        if self.settings.check_direction not in (0, 1):
            self.settings.check_direction = self.settings.default_check_direction

        if not isinstance(self.settings.embedded_folders, bool):
            self.settings.embedded_folders = self.settings.default_embedded_folders

        if not isinstance(self.settings.save_txt, bool):
            self.settings.save_txt = self.settings.default_save_txt

        forbidden_symbols = '*?\"<>|'
        if not os.path.isabs(self.settings.save_to) or any(char in forbidden_symbols for char in self.settings.save_to):
            self.settings.save_to = self.settings.default_save_to

    def load_settings(self):
        config = configparser.ConfigParser()

        try:
            # Пытаемся прочитать файл конфигурации
            config.read('./check_images.ini')

            # Получаем значения параметров из файла .ini
            self.settings.min_threshold = config.getfloat('Settings', 'MinThreshold')
            self.settings.precision = config.getfloat('Settings', 'Precision')
            self.settings.check_direction = config.getint('Settings', 'CheckDirection')
            self.settings.embedded_folders = config.getboolean('Settings', 'EmbeddedFolders')
            self.settings.save_txt = config.getboolean('Settings', 'SaveTxt')
            self.settings.save_to = config.get('Settings', 'SaveTo')

            self.check_settings_on_load()

        except (configparser.Error, ValueError, FileNotFoundError):
            # Если возникает ошибка, используем значения по умолчанию
            self.settings.min_threshold = self.settings.default_min_threshold
            self.settings.precision = self.settings.default_precision
            self.settings.check_direction = self.settings.default_check_direction
            self.settings.embedded_folders = self.settings.default_embedded_folders
            self.settings.save_txt = self.settings.default_save_txt
            self.settings.save_to = self.settings.default_save_to

        print(f'load settings: {self.settings.check_direction=}, {id(self.settings.check_direction)=}')

    def save_settings(self, value1, value2, value3, value4, value5, value6):
        config = configparser.ConfigParser()

        self.settings.min_threshold = value1
        self.settings.text_precision = value2
        self.settings.check_direction = value3
        self.settings.embedded_folders = value4
        self.settings.save_txt = value5
        self.settings.save_to = value6

        print(f'save settings: {self.settings.check_direction=}, {id(self.settings.check_direction)=}')

        # Устанавливаем значения параметров
        config['Settings'] = {
            'MinThreshold': self.settings.min_threshold,
            'Precision': self.settings.precision,
            'CheckDirection': str(self.settings.check_direction),
            'EmbeddedFolders': str(self.settings.embedded_folders),
            'SaveTxt': str(self.settings.save_txt),
            'SaveTo': self.settings.save_to,
        }

        # Сохраняем конфигурацию в файл
        with open('./check_images.ini', 'w') as configfile:
            config.write(configfile)
