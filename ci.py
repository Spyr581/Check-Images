# Check images by OpenCV with GUI
# Version 1.0

import argparse
import cv2
import numpy
import os
import datetime


class InitServiceOutputInfo:
    """
    The class calculates indents depending on the length of template image filenames and outputs the table header
    to the console and to the file.
    """

    def __init__(self, tmpls: list, precision: float):
        """
        :param tmpls_dict:    dict, contains pairs - {path to template images: list of images, ...}
        :param path_to_tmpls: tuple, 2 items: 0 - str, path to one image file or folder with image files, folder
                              1 - str, filename if the input is one file, else - empty string
        :param precision:     float
        """
        self.__tmpls = tmpls
        self.__prec = precision

        self.__img_indent = 0
        self.__count_indent = 0
        self.__threshold_indent = 0
        self.__coord_indent = 0

    def __count_indents(self):
        files = (os.path.basename(filename) for filename in self.__tmpls)
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
        screenshot = f'|   SCREENSHOT - {scr_image}   |'
        precision = f'|   PRECISION - {self.__prec}   ///   '
        time = datetime.datetime.now()
        time_as_str = time.strftime('%Y-%m-%d %H:%M:%S') + '   |'
        second_string = precision + time_as_str

        max_length = max(len(screenshot), len(second_string))

        # 1st string
        left, right = self.__calculate_header_indents(max_length, len(screenshot))
        screenshot = f'|   {" " * left}SCREENSHOT - {scr_image}{" " * right}   |'

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

    def __init__(self, filename: str, thr: float, precision: float, tmpl_indent: int, count_indent: int,
                 thr_indent: int, coord_indent: int, tmpl=None, count=None, x=None, y=None):
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
        self.__path_to_tmpls = filename
        self.__thr = thr
        self.__prec = precision
        self.__tmpl_indent = tmpl_indent
        self.__count_indent = count_indent
        self.__threshold_indent = thr_indent
        self.__coord_indent = coord_indent
        self.__tmpl = None if tmpl is None else self.__get_tmpl_name_with_subdirs(tmpl)
        self.__count = count if count is not None else ''
        self.__x = x
        self.__y = y

    def __get_tmpl_name_with_subdirs(self, tmpl: str) -> str:
        if tmpl == '':
            return tmpl
        tmpl_name = tmpl.split(self.__path_to_tmpls)[1]
        return tmpl_name[1:]   # Minus \ in begin filename

    def print_one_found_entry(self) -> str:
        one_entry = f'{self.__tmpl}{" " * (self.__tmpl_indent - len(self.__tmpl))}|' \
                    f'{"  "}{self.__count}{" " * (self.__count_indent - len(str(self.__count)) - 2)}|' \
                    f'{self.__thr}{" " * (self.__threshold_indent - len(str(self.__thr)))}|' \
                    f'{self.__x}{" " * (self.__coord_indent - len(str(self.__x)))}|' \
                    f'{self.__y}{" " * (self.__coord_indent - len(str(self.__y)))}'
        print(one_entry)

        return one_entry + '\n'

    def print_one_not_found_entry(self) -> str:
        one_entry = f'{self.__tmpl}{" " * (self.__tmpl_indent - len(self.__tmpl))}|' \
                    f'{"  "}0{" " * (self.__count_indent - 3)}|' \
                    f'Not found{" " * (self.__threshold_indent - 9)}|' \
                    f'None{" " * (self.__coord_indent - 4)}|' \
                    f'None{" " * (self.__coord_indent - 4)}'
        print(one_entry)

        return one_entry + '\n'


class CheckImages:
    """
    The class searches for one template image or all template images from the folder and its subfolders `path_to_tmpls`
    in all screenshots `screen_img`. With the given `precision`, it gives the maximum possible threshold with which each
    template can be found on the screen image. The class looks for the number of occurrences of each template
    in the image. It also additionally outputs the coordinates of the top left point
    of each template on the screen image where the template was found. The threshold is found in the range
    `min_threshold` ... 1.0. Prints information to the console and to a file.
    """

    __extension_list = ['png', 'jpg', 'webp']
    __tmpls_dict = dict()   # {'D:\\Python\\Check Images\\tf': ['e.png', 't.png'], ...}
    __l_scr_img_gray = list()

    def __init__(self, tmpls: list, screen_imgs: list, min_threshold=0.6, precision=0.0001):
        """
        :param path_to_tmpls:      str, path to one image file or folder with image files, folder can be insist
                                   subfolders with images templates
        :param screen_img:         str, one or several paths to screenshot(-s), on which templates should be found,
                                   delimiter is ' * '
        :param min_threshold:      float
        :param precision:          float
        """
        self.__tmpls = tmpls           # tuple, 2 items: 0 - str, path to one image
                                                                       # file or folder with image files, folder
                                                                       # 1 - str, filename if the input is one file,
                                                                       # else - empty string
        self.__screen_imgs = screen_imgs
        self.__min_threshold = min_threshold
        self.__precision = precision
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

    def __filter_near_points(self, found_tmpl_dict: dict) -> list:
        prev_pt = None
        max_correlation = -1
        pt_with_max_correlation = None
        all_points_list = []

        if self.__width <= 18 and self.__height <= 18:
            search_area = int(self.__width * 2), int(self.__height * 2)
        else:
            search_area = self.__width, self.__height

        for pt in sorted(found_tmpl_dict.keys()):
            if prev_pt is None:  # First point in dict
                max_correlation = found_tmpl_dict[pt]
                pt_with_max_correlation = (pt, found_tmpl_dict[pt])
            else:
                if abs(pt[0] - prev_pt[0]) < search_area[0] or \
                        abs(pt[1] - prev_pt[1]) < search_area[1]:
                    if found_tmpl_dict[pt] > max_correlation:
                        max_correlation = found_tmpl_dict[pt]
                        pt_with_max_correlation = (pt, found_tmpl_dict[pt])
                else:
                    all_points_list.append(pt_with_max_correlation)
                    max_correlation = found_tmpl_dict[pt]
            prev_pt = pt
        if pt_with_max_correlation is not None:     # Add the last point if any point has been found
            all_points_list.append(pt_with_max_correlation)

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

                found_tmpl_dict = dict()
                for tmpl_path in self.__tmpls:
                    searching = self.__find_one_image(tmpl_path, scr_img_gray)
                    location = numpy.where(searching >= self.__min_threshold)
                    for pt in zip(*location[::-1]):
                        if found_tmpl_dict.get(pt) is None:
                            found_tmpl_dict[pt] = searching[pt[1], pt[0]]
                    all_points_list = self.__filter_near_points(found_tmpl_dict)   # [((849, 69), 0.8667161), ...]
                    num_tmpls_found = len(all_points_list)

                    if num_tmpls_found > 0:
                        iteration = 1
                        for pt in sorted(all_points_list):
                            x, y = int(pt[0][0]), int(pt[0][1])
                            threshold = float(self.__round_threshold(pt[1]))
                            if iteration > 1:
                                tmpl_to_find = ''
                                num_tmpls_found = ''

                            one_entry_to_output = OutputInfo(os.path.basename(tmpl_path),
                                                             threshold,
                                                             self.__precision,
                                                             self.__output_preparing.img_indent,
                                                             self.__output_preparing.count_indent,
                                                             self.__output_preparing.threshold_indent,
                                                             self.__output_preparing.coord_indent,
                                                             tmpl_to_find,
                                                             num_tmpls_found,
                                                             x,
                                                             y)
                            f.writelines(
                                one_entry_to_output.print_one_found_entry())  # exit.webp    |  1     |0.8136      |994     |2

                            iteration += 1
                    else:
                        one_entry_to_output = OutputInfo(os.path.basename(tmpl_path),
                                                         0,
                                                         self.__precision,
                                                         self.__output_preparing.img_indent,
                                                         self.__output_preparing.count_indent,
                                                         self.__output_preparing.threshold_indent,
                                                         self.__output_preparing.coord_indent,
                                                         tmpl_to_find,
                                                         count=0,
                                                         x=None,
                                                         y=None)
                        f.writelines(one_entry_to_output.print_one_not_found_entry())  # fg_win.webp    |  0     |Not found   |None    |None

                f.writelines('\n\n')

    def run(self):
        self.__output_preparing = InitServiceOutputInfo(self.__tmpls, self.__precision)
        self.__find_thresholds_for_all_images()


def main():
    parser = argparse.ArgumentParser(description='-p or --param <value>')
    parser.add_argument('-t', '--templates', type=str, dest="path_to_tmpls",
                        help="Path to template images folder, required parameter", default='')
    parser.add_argument('-i', '--image', type=str, dest="scr_img_path",
                        help="Path to screen image(-s) where templates will be searched, path can be one or several,"
                             " delimiter is ' * ', required parameter", default='')
    parser.add_argument('-n', '--min', type=float, dest="min_threshold",
                        help="Minimum threshold value in range", default=0.6)
    parser.add_argument('-p', '--precision', type=float, dest="precision",
                        help="The precision with which templates will be searched in the screen image",
                        default=0.0001)
    options = parser.parse_args()

    check = CheckImages(options.path_to_tmpls, options.scr_img_path, options.min_threshold, options.precision)
    check.run()


if __name__ == '__main__':
    main()

# # path_to_tmpls = 'D:\\My_documents\\Programming\\Python\\Check Images\\tf'
# # scr_img_path = 'D:\\My_documents\\Programming\\Python\\Check Images\\i1_2.png'
# path_to_tmpls = 'F:\\work\\autotest\\tests\\launcher\\l_screens\\games\\393'
# scr_img_path = 'E:\\Video edit\\Capture\\bandicam 2022-12-29 14-21-03-483.png * ' \
#                'E:\\Video edit\\Capture\\bandicam 2022-12-29 14-22-18-041.png * ' \
#                'E:\\Video edit\\Capture\\bandicam 2022-12-30 16-10-28-959.png'
#
# check = CheckImages(path_to_tmpls, scr_img_path)
# check.run()
