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

    def __init__(self, tmpls_dict, path_to_tmpls, precision):
        """
        :param tmpls_dict:    dict, contains pairs - {path to template images: list of images, ...}
        :param path_to_tmpls: str, path to folder with image templates
        :param precision:     float
        """
        self.__tmpls_dict = tmpls_dict
        self.__path_to_tmpls = path_to_tmpls
        self.__prec = precision

        self.__img_indent = 0
        self.__threshold_indent = 0
        self.__coord_indent = 0

    def __count_indents(self):
        length_list = []
        for tmpl_pack in self.__tmpls_dict.items():
            if len(self.__path_to_tmpls[1]) == 0:
                tmpl_name = tmpl_pack[0].split(self.__path_to_tmpls[0])[1]
            else:
                tmpl_name = self.__path_to_tmpls[1]

            img_name = tmpl_name[1:] if tmpl_name is not None else ''
            length_img_name = len(img_name)
            length_list += list(map(lambda x: len(x) + length_img_name + 1, tmpl_pack[1]))
        self.__img_indent = max(length_list) + 4
        self.__threshold_indent = len(str(self.__prec)) + 6
        self.__coord_indent = 8

    def __calculate_header_indents(self, max_length, string_length):
        left_indent = (max_length - string_length) // 2
        right_indent = max_length - string_length - left_indent
        return left_indent, right_indent

    def print_header(self, scr_image):
        tmpls_folder = f'|   FOLDER - {self.__path_to_tmpls[0]}   |'
        screenshot = f'|   SCREENSHOT - {scr_image}   |'
        precision = f'|   PRECISION - {self.__prec}   ///   '
        time = datetime.datetime.now()
        time_as_str = time.strftime('%Y-%m-%d %H:%M:%S') + '   |'
        third_string = precision + time_as_str

        max_length = max(len(tmpls_folder), len(screenshot), len(third_string))

        # 1st string
        left, right = self.__calculate_header_indents(max_length, len(tmpls_folder))
        tmpls_folder = f'|   {" " * left}FOLDER - {self.__path_to_tmpls[0]}{" " * right}   |'

        # 2nd string
        left, right = self.__calculate_header_indents(max_length, len(screenshot))
        screenshot = f'|   {" " * left}SCREENSHOT - {scr_image}{" " * right}   |'

        # 3rd string
        left, right = self.__calculate_header_indents(max_length, len(third_string))
        precision = f'|   {" " * left}PRECISION - {self.__prec}   ///   '
        time_as_str = time.strftime('%Y-%m-%d %H:%M:%S') + f'{" " * right}   |'
        third_string = precision + time_as_str

        self.__count_indents()

        header = f'IMAGE{" " * (self.__img_indent - 5)}|THRESHOLD{" " * (self.__threshold_indent - 9)}|' \
                 f'X{" " * (self.__coord_indent - 1)}|Y{" " * (self.__coord_indent - 1)}'
        total_signs = self.__img_indent + self.__threshold_indent + 2 * self.__coord_indent + 3
        line = f'{"-" * total_signs}'

        print('-' * max_length)
        print(tmpls_folder)
        print(screenshot)
        print(third_string)
        print('-' * max_length)
        print(header)
        print(line)

        return ('-' * max_length + '\n', tmpls_folder + '\n', screenshot + '\n',
                third_string + '\n', header + '\n', line + '\n')

    @property
    def img_indent(self):
        return self.__img_indent

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

    def __init__(self, path_to_tmpls, thr, precision, tmpl_indent, thr_indent, coord_indent, tmpl=None, x=None, y=None):
        """
        :param path_to_tmpls: str, path to folder with image templates
        :param thr:           float
        :param precision:     float
        :param tmpl_indent:   int, calculated indent for the template name field
        :param thr_indent:    int, calculated indent for the threshold field
        :param coord_indent:  int, calculated indent for the coordinate fields
        :param tmpl:          str, file name of template with subdirs (if there is)
        :param x:             int, x coordinate, where template found on screen image
        :param y:             int, y coordinate, where template found on screen image
        """
        self.__path_to_tmpls = path_to_tmpls
        self.__thr = thr
        self.__prec = precision
        self.__tmpl_indent = tmpl_indent
        self.__threshold_indent = thr_indent
        self.__coord_indent = coord_indent
        self.__tmpl = None if tmpl is None else self.__get_tmpl_name_with_subdirs(tmpl)
        self.__x = x
        self.__y = y

    def __get_tmpl_name_with_subdirs(self, tmpl):
        tmpl_name = tmpl.split(self.__path_to_tmpls)[1]
        return tmpl_name[1:]

    def __round_threshold(self):
        self.__thr = round(self.__thr, len(str(self.__prec)) - 1)

    def print_one_found_entry(self):
        self.__round_threshold()

        one_entry = f'{self.__tmpl}{" " * (self.__tmpl_indent - len(self.__tmpl))}|' \
                    f'{self.__thr}{" " * (self.__threshold_indent - len(str(self.__thr)))}|' \
                    f'{self.__x}{" " * (self.__coord_indent - len(str(self.__x)))}|' \
                    f'{self.__y}{" " * (self.__coord_indent - len(str(self.__y)))}'
        print(one_entry)

        return one_entry + '\n'

    def print_one_not_found_entry(self):
        one_entry = f'{self.__tmpl}{" " * (self.__tmpl_indent - len(self.__tmpl))}|' \
                    f'Not found{" " * (self.__threshold_indent - 9)}|' \
                    f'None{" " * (self.__coord_indent - 4)}|' \
                    f'None{" " * (self.__coord_indent - 4)}'
        print(one_entry)

        return one_entry + '\n'


class CheckImages:
    """
    The class searches for one template image or all template images from the folder and its subfolders `path_to_tmpls`
    in all screenshots `screen_img`. With the given `precision`, it gives the maximum possible threshold with which each
    template can be found on the screen image. It also additionally outputs the coordinates of the top left point
    of each template on the screen image where the template was found. The threshold is found in the range
    `min_threshold` ... `max_threshold`. Prints information to the console and to a file.
    """

    __extension_list = ['png', 'jpg', 'webp']
    __tmpls_dict = dict()
    __scr_img_gray_list = list()

    def __init__(self, path_to_tmpls, screen_img, min_threshold=0.8, max_threshold=0.999999, precision=0.001):
        """
        :param path_to_tmpls:      str, path to one image file or folder with image files, folder can be insist
                                   subfolders with images templates
        :param screen_img:         str, one or several paths to screenshot(-s), on which templates should be found,
                                   delimiter is ' * '
        :param min_threshold:      float
        :param max_threshold:      float
        :param precision:          float
        """
        self.__path_to_tmpls = self.__check_templates(path_to_tmpls)
        self.__screen_img_list = self.__check_screen_img_exist(screen_img)
        self.__min_threshold = self.__check_threshold(min_threshold, 'min')
        self.__max_threshold = self.__check_threshold(max_threshold, 'max')
        self.__precision = self.__check_precision(precision)
        self.__output_preparing = None
        self.__screen_index = 0

    def __check_templates(self, path):
        if os.path.isdir(path):
            return path, ''

        elif os.path.isfile(path):
            file_extension = path.split('.')[-1].lower()
            if file_extension in self.__extension_list:
                p = os.path.split(path)
                return p[0], p[1]
            else:
                error = f'File {path} not in proper format ({self.__extension_list})'
                raise IOError(error)

        else:
            error = f'{path} not found'
            raise IOError(error)

    def __check_screen_img_exist(self, screen_img):
        img_list = screen_img.split(' * ')
        checked_img_list = []
        for img in img_list:
            if os.path.isfile(img):
                extension = img.split('.')[-1].lower()
                if extension in self.__extension_list:
                    checked_img_list.append(img)

        if not checked_img_list:
            error = f'Any compatible image(-s) in {img_list} not found'
            raise IOError(error)

        return checked_img_list

    def __check_threshold(self, thr, type_):
        if not isinstance(thr, float):
            if type_ == 'min':
                error = f'min_threshold={thr} but it should be a number'
                raise TypeError(error)
            else:
                error = f'max_threshold={thr} but it should be a number'
                raise TypeError(error)

        if 0.1 > thr > 1:
            if type_ == 'min':
                error = f'min_threshold={thr} but have to be in range 0.1 ... 1'
                raise ValueError(error)
            else:
                error = f'max_threshold={thr} but have to be in range 0.1 ... 1'
                raise ValueError(error)

        return thr

    def __check_precision(self, prec):
        if not isinstance(prec, float) or not 0 < prec < 1:
            error = f'precision={prec} but it should be a number in range 0 ... 1'
            raise TypeError(error)

        return prec

    def __round_threshold(self, thr):
        return round(thr, len(str(self.__precision)) - 2)

    def __find_all_template_files(self):
        if len(self.__path_to_tmpls[1]) == 0:
            for root, dirs, images in os.walk(self.__path_to_tmpls[0]):
                prepared_images = []
                for img in images:
                    if img.split('.')[-1] in self.__class__.__extension_list:
                        prepared_images.append(img)
                self.__class__.__tmpls_dict[root] = prepared_images

        else:
            self.__class__.__tmpls_dict[self.__path_to_tmpls[0]] = [self.__path_to_tmpls[1]]

    def __any_img_to_grayscale(self, path):
        img_rgb = cv2.imread(path)
        return cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    def __find_one_image(self, img):
        img = self.__any_img_to_grayscale(img)
        return cv2.matchTemplate(img, self.__class__.__scr_img_gray_list[self.__screen_index], cv2.TM_CCOEFF_NORMED)

    def __find_thresholds_for_all_images(self):
        with open('thresholds.txt', 'at', encoding='utf-8') as f:
            header_info = self.__output_preparing.print_header(self.__screen_img_list[self.__screen_index])
            f.writelines(header_info[0])  # ------------------------------------------------------
            f.writelines(header_info[1])  # |      FOLDER - F:\work\Pictures\252_sizzling6       |
            f.writelines(header_info[2])  # |        SCREENSHOT - F:\work\template_on.png        |
            f.writelines(header_info[3])  # |   PRECISION - 0.0001   ///   2022-07-26 15:29:24   |
            f.writelines(header_info[0])  # ------------------------------------------------------
            f.writelines(header_info[4])  # IMAGE                  |THRESHOLD   |X       |Y
            f.writelines(header_info[5])  # ------------------------------------------------------

            for tmpls_pack in self.__class__.__tmpls_dict.items():
                for tmpl in tmpls_pack[1]:
                    threshold = (self.__min_threshold + self.__max_threshold) / 2
                    threshold_left = self.__min_threshold
                    threshold_right = self.__max_threshold
                    precision = 1
                    location = None
                    negative_result = True

                    while self.__precision <= precision or negative_result:
                        searching = self.__find_one_image(tmpls_pack[0] + os.sep + tmpl)
                        location = numpy.where(searching >= threshold)
                        negative_result = len(location[0]) == 0 and len(location[1]) == 0
                        positive_result = len(location[0]) != 0 and len(location[1]) != 0

                        if positive_result:
                            threshold_new = (threshold + threshold_right) / 2
                            threshold_left = threshold
                            precision = threshold_right - threshold_left
                            threshold = threshold_new
                        elif negative_result:
                            threshold_new = (threshold_left + threshold) / 2
                            threshold_right = threshold
                            precision = threshold_right - threshold_left
                            threshold = threshold_new
                        else:
                            error = f'Wrong searchng: {location[0]=}, {location[1]=}'
                            raise ValueError(error)

                        if self.__round_threshold(threshold) == self.__round_threshold(self.__min_threshold):
                            break

                    x, y = None, None
                    for item in zip(*location[::-1]):
                        x, y = int(item[0]), int(item[1])

                    one_entry_to_output = OutputInfo(self.__path_to_tmpls[0], threshold, self.__precision,
                                                     self.__output_preparing.img_indent,
                                                     self.__output_preparing.threshold_indent,
                                                     self.__output_preparing.coord_indent,
                                                     tmpls_pack[0] + os.sep + tmpl, x, y)

                    if len(location[0]) != 0 and len(location[1]) != 0:
                        f.writelines(one_entry_to_output.print_one_found_entry())      # addline_d.png    |0.9999      |430     |673
                    else:
                        f.writelines(one_entry_to_output.print_one_not_found_entry())  # add_n.png        |Not found   |None    |None

            f.writelines('\n\n')

    def run(self):
        for img in self.__screen_img_list:
            self.__class__.__scr_img_gray_list.append(self.__any_img_to_grayscale(img))
        self.__find_all_template_files()
        self.__output_preparing = InitServiceOutputInfo(self.__class__.__tmpls_dict, self.__path_to_tmpls,
                                                        self.__precision)
        for _ in range(len(self.__scr_img_gray_list)):
            self.__find_thresholds_for_all_images()
            self.__screen_index += 1


def main():
    parser = argparse.ArgumentParser(description='-p or --param <value>')
    parser.add_argument('-t', '--templates', type=str, dest="path_to_tmpls",
                        help="Path to template images folder, required parameter", default='')
    parser.add_argument('-i', '--image', type=str, dest="scr_img_path",
                        help="Path to screen image(-s) where templates will be searched, path can be one or several,"
                             " delimiter is ' * ', required parameter", default='')
    parser.add_argument('-n', '--min', type=float, dest="min_threshold",
                        help="Minimum threshold value in range", default=0.6)
    parser.add_argument('-x', '--max', type=float, dest="max_threshold",
                        help="Maximum threshold value in range", default=0.999999)
    parser.add_argument('-p', '--precision', type=float, dest="precision",
                        help="The precision with which templates will be searched in the screen image",
                        default=0.001)
    options = parser.parse_args()

    check = CheckImages(options.path_to_tmpls, options.scr_img_path, options.min_threshold, options.max_threshold,
                        options.precision)
    check.run()


if __name__ == '__main__':
    main()

# path_to_tmpls = 'D:\\My_documents\\Programming\\Python\\Check Images\\t.png'
# scr_img_path = 'D:\\My_documents\\Programming\\Python\\Check Images\\i1.png * D:\\My_documents\\Programming\\Python\\' \
#                'Check Images\\i2.png'
# min_threshold = 0.6
# max_threshold = 0.999999
# precision = 0.0001

# check = CheckImages(path_to_tmpls, scr_img_path, min_threshold, max_threshold, precision)
# check.run()
