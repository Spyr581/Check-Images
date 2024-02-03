import os

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

    default_threshold = BaseSettingsDescriptor(0.6)
    default_precision = BaseSettingsDescriptor(0.0001)
    default_check_direction = BaseSettingsDescriptor(0)
    default_embedded_folders = BaseSettingsDescriptor(False)
    default_save_txt = BaseSettingsDescriptor(True)
    default_save_to = BaseSettingsDescriptor(os.path.join(os.getcwd(), 'threshold.txt'))

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)

    def __init__(self):
        self.threshold = SettingsDescriptor(None)
        self.precision = SettingsDescriptor(None)
        self.check_direction = SettingsDescriptor(None)
        self.embedded_folders = SettingsDescriptor(None)
        self.save_txt = SettingsDescriptor(None)
        self.save_to = SettingsDescriptor(None)

    def check_settings_on_load(self):
        # Проверка загружаемых настроек из ini файла
        if not (0 <= float(self.threshold) <= 0.999999):
            self.threshold = self.default_threshold

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