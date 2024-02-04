# Check images by OpenCV with GUI
# Version 1.0

import cv2
import numpy
import os
import datetime


class InitServiceOutputInfo:
    """
    The class calculates indents depending on the length of template image filenames and outputs the table header
    to the console and to the file.
    """

    def __init__(self, tmpl_paths: list, precision: float, direction: (0 | 1)):
        """
        :param tmpls_dict:    dict, contains pairs - {path to template images: list of images, ...}
        :param path_to_tmpls: tuple, 2 items: 0 - str, path to one image file or folder with image files, folder
                              1 - str, filename if the input is one file, else - empty string
        :param precision:     float
        """
        self.__tmpl_paths = tmpl_paths
        self.__prec = precision
        self.__direction = direction

        self.__img_indent = 0
        self.__count_indent = 0
        self.__threshold_indent = 0
        self.__coord_indent = 0

    def __count_indents(self):
        files = (os.path.basename(filename) for filename in self.__tmpl_paths)
        max_length = max(map(len, files))

        self.__img_indent = max_length + 5
        self.__count_indent = 8
        self.__threshold_indent = len(str(self.__prec)) + 6
        self.__coord_indent = 8

    @staticmethod
    def __calculate_header_indents(max_length: int, string_length: int) -> (int, int):
        left_indent = (max_length - string_length) // 2
        right_indent = max_length - string_length - left_indent
        return left_indent, right_indent

    def print_header(self, scr_image: str) -> (str, str, str, str):
        screenshot = f'|   {"SCREENSHOT" if 0 == self.__direction else "TEMPLATE"} - {scr_image}   |'
        precision = f'|   PRECISION - {self.__prec}   ///   '
        time = datetime.datetime.now()
        time_as_str = time.strftime('%Y-%m-%d %H:%M:%S') + '   |'
        second_string = precision + time_as_str

        max_length = max(len(screenshot), len(second_string))

        # 1st string
        left, right = self.__calculate_header_indents(max_length, len(screenshot))
        screenshot = f'|   {" " * left}{"SCREENSHOT" if 0 == self.__direction else "TEMPLATE"} - ' \
                     f'{scr_image}{" " * right}   |'

        # 2nd string
        left, right = self.__calculate_header_indents(max_length, len(second_string))
        precision = f'|   {" " * left}PRECISION - {self.__prec}   ///   '
        time_as_str = time.strftime('%Y-%m-%d %H:%M:%S') + f'{" " * right}   |'
        second_string = precision + time_as_str

        self.__count_indents()

        header = f'IMAGE{" " * (self.__img_indent - 5)}|COUNT   |THRESHOLD{" " * (self.__threshold_indent - 9)}|' \
                 f'X{" " * (self.__coord_indent - 1)}|Y{" " * (self.__coord_indent - 1)}'

        print('-' * max_length,
              screenshot,
              second_string,
              '-' * max_length,
              header,
              '-' * max_length,
              sep='\n')

        return ('-' * max_length + '\n',
                screenshot + '\n',
                second_string + '\n',
                header + '\n')

    @property
    def img_indent(self):
        return self.__img_indent

    @property
    def count_indent(self):
        return self.__count_indent

    @property
    def threshold_indent(self):
        return self.__threshold_indent

    @property
    def coord_indent(self):
        return self.__coord_indent


class OutputInfo:
    """
    Outputs one line of information with the template and the maximum threshold and coordinates calculated for it to
    the console and to the file.
    """

    def __init__(self,
                 filename: str,
                 thr: (float, None),
                 precision: float,
                 tmpl_indent: int,
                 count_indent: int,
                 thr_indent: int,
                 coord_indent: int,
                 count=None,
                 x=None,
                 y=None):
        """
        :param path_to_tmpls: str, path to folder with image templates
        :param thr:           float
        :param precision:     float
        :param tmpl_indent:   int, calculated indent for the template name field
        :param count_indent:  int, calculated indent for the count of found templates on screen image field
        :param thr_indent:    int, calculated indent for the threshold field
        :param coord_indent:  int, calculated indent for the coordinate fields
        :param tmpl:          str, file name of template with subdirs (if there is)
        :param count:         int, count of found templates on screen image
        :param x:             int, x coordinate, where template found on screen image
        :param y:             int, y coordinate, where template found on screen image
        """
        self.__filename = filename
        self.__thr = thr
        self.__prec = precision
        self.__tmpl_indent = tmpl_indent
        self.__count_indent = count_indent
        self.__threshold_indent = thr_indent
        self.__coord_indent = coord_indent
        self.__count = count if count is not None else ''
        self.__x = x
        self.__y = y

    def print_one_found_entry(self) -> str:
        one_entry = f'{self.__filename}{" " * (self.__tmpl_indent - len(self.__filename))}|' \
                    f'{"  "}{self.__count}{" " * (self.__count_indent - len(str(self.__count)) - 2)}|' \
                    f'{self.__thr}{" " * (self.__threshold_indent - len(str(self.__thr)))}|' \
                    f'{self.__x}{" " * (self.__coord_indent - len(str(self.__x)))}|' \
                    f'{self.__y}{" " * (self.__coord_indent - len(str(self.__y)))}'
        print(one_entry)

        return one_entry + '\n'

    def print_one_not_found_entry(self) -> str:
        one_entry = f'{self.__filename}{" " * (self.__tmpl_indent - len(self.__filename))}|' \
                    f'{"  "}0{" " * (self.__count_indent - 3)}|' \
                    f'Not found{" " * (self.__threshold_indent - 9)}|' \
                    f'None{" " * (self.__coord_indent - 4)}|' \
                    f'None{" " * (self.__coord_indent - 4)}'
        print(one_entry)

        return one_entry + '\n'


class CheckImages:
    def __init__(self,
                 tmpl_paths: list,
                 screen_imgs: list,
                 console,
                 min_threshold,
                 precision,
                 direction):

        self.__direction: (0 | 1) = direction
        print(f'{self.__direction=}')
        if 0 == self.__direction:
            self.__tmpl_paths: [str] = tmpl_paths
            self.__screen_imgs: [str] = screen_imgs
        else:
            self.__tmpl_paths: [str] = screen_imgs
            self.__screen_imgs: [str] = tmpl_paths

        print(f'{self.__tmpl_paths=}')
        print(f'{self.__screen_imgs=}')
        self.__console_window = console   # wx.TextCtrl object
        self.__min_threshold: float = min_threshold
        self.__precision: float = precision

        self.__output_preparing = None
        self.__height = None
        self.__width = None

    def __round_threshold(self, thr: float) -> float:
        multiplier = 10 ** (len(str(self.__precision)) - 2)
        thr = int(thr * multiplier)
        return thr / multiplier

    def __any_img_to_grayscale(self, path: str) -> numpy.ndarray:
        img_rgb = cv2.imread(path)
        return cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    def __find_one_image(self, img: str, scr_img: numpy.ndarray) -> numpy.ndarray:
        img = self.__any_img_to_grayscale(img)
        self.__height, self.__width = img.shape

        return cv2.matchTemplate(img, scr_img, cv2.TM_CCOEFF_NORMED)

    def __filter_near_points(self, d_found_tmpl: dict) -> [((int, int), float)]:   # [((x, y), threshold), ...]
        prev_coords = None
        max_correlation = -1
        coords_with_max_correlation = None
        all_points_list = []

        if self.__width <= 18 and self.__height <= 18:
            search_area = int(self.__width * 2), int(self.__height * 2)
        else:
            search_area = self.__width, self.__height

        for coords in sorted(d_found_tmpl.keys()):
            if prev_coords is None:  # First point in dict
                max_correlation = d_found_tmpl[coords]
                coords_with_max_correlation = (coords, d_found_tmpl[coords])
            else:
                if abs(coords[0] - prev_coords[0]) < search_area[0] or \
                        abs(coords[1] - prev_coords[1]) < search_area[1]:
                    if d_found_tmpl[coords] > max_correlation:
                        max_correlation = d_found_tmpl[coords]
                        coords_with_max_correlation = (coords, d_found_tmpl[coords])
                else:
                    all_points_list.append(coords_with_max_correlation)
                    max_correlation = d_found_tmpl[coords]
            prev_coords = coords
        if coords_with_max_correlation is not None:     # Add the last point if any point has been found
            all_points_list.append(coords_with_max_correlation)

        return list(set(all_points_list))

    def __find_thresholds_for_all_images(self):
        with open('thresholds.txt', 'at', encoding='utf-8') as f:
            for scr_path in self.__screen_imgs:
                scr_img_gray = self.__any_img_to_grayscale(scr_path)
                header_info = self.__output_preparing.print_header(scr_path)
                f.writelines(header_info[0])    # ------------------------------------------------------
                f.writelines(header_info[1])    # |   SCREENSHOT - D:\Python\Check Images\i1_2.png     |
                f.writelines(header_info[2])    # |   PRECISION - 0.0001   ///   2023-01-05 16:23:44   |
                f.writelines(header_info[0])    # ------------------------------------------------------
                f.writelines(header_info[3])    # IMAGE           |COUNT   |THRESHOLD   |X       |Y
                f.writelines(header_info[0])    # ------------------------------------------------------
                self.__console_window.AppendText(header_info[0])
                self.__console_window.AppendText(header_info[1])
                self.__console_window.AppendText(header_info[2])
                self.__console_window.AppendText(header_info[0])
                self.__console_window.AppendText(header_info[3])
                self.__console_window.AppendText(header_info[0])

                d_found_tmpl = dict()   # ex.: {(994, 1): 0.66438675, (994, 2): 0.99708754, (994, 3): 0.6657746}
                for tmpl_path in self.__tmpl_paths:
                    searching = self.__find_one_image(tmpl_path, scr_img_gray)
                    location = numpy.where(searching >= self.__min_threshold)

                    for coords in zip(*location[::-1]):
                        if d_found_tmpl.get(coords) is None:
                            d_found_tmpl[coords] = searching[coords[1], coords[0]]
                    all_points_list = self.__filter_near_points(d_found_tmpl)   # [((849, 69), 0.8667161), ...]
                    num_tmpls_found = len(all_points_list)

                    if num_tmpls_found > 0:
                        for idx, coords_thr in enumerate(sorted(all_points_list, key=lambda a: a[1], reverse=True)):
                            x, y = int(coords_thr[0][0]), int(coords_thr[0][1])
                            threshold = float(self.__round_threshold(coords_thr[1]))
                            one_entry_to_output = OutputInfo(os.path.basename(tmpl_path) if 0 == idx else '',
                                                             threshold,
                                                             self.__precision,
                                                             self.__output_preparing.img_indent,
                                                             self.__output_preparing.count_indent,
                                                             self.__output_preparing.threshold_indent,
                                                             self.__output_preparing.coord_indent,
                                                             num_tmpls_found if 0 == idx else '',
                                                             x,
                                                             y)
                            one_entry = one_entry_to_output.print_one_found_entry()
                            f.writelines(one_entry)  # exit.webp    |  1     |0.8136      |994     |2
                            self.__console_window.AppendText(one_entry)
                    else:
                        one_entry_to_output = OutputInfo(os.path.basename(tmpl_path),
                                                         None,
                                                         self.__precision,
                                                         self.__output_preparing.img_indent,
                                                         self.__output_preparing.count_indent,
                                                         self.__output_preparing.threshold_indent,
                                                         self.__output_preparing.coord_indent,
                                                         count=0,
                                                         x=None,
                                                         y=None)
                        one_entry = one_entry_to_output.print_one_not_found_entry()
                        f.writelines(one_entry)  # fg_win.webp    |  0     |Not found   |None    |None
                        self.__console_window.AppendText(one_entry)
                f.writelines('\n\n')
                self.__console_window.AppendText('\n\n')

    def run(self):
        self.__output_preparing = InitServiceOutputInfo(self.__tmpl_paths,
                                                        self.__precision,
                                                        self.__direction)
        self.__find_thresholds_for_all_images()


if __name__ == '__main__':
    pass
