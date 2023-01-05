@ECHO off

REM 	Программа ищет изображения (png, jpg, webp) на картинке скриншотов (png, jpg, webp) с помощью OpenCV.
REM В итоге получается таблица, где будет указано количество вхождений каждого шаблона на изображении, на котором
REM производится поиск, и соответствующие им максимальные пороги на данном изображении с заданной точностью
REM (precision).
REM Также будут указаны координаты левой верхней точки, где шаблон был найден на скриншоте.
REM 	В качестве шаблонов TEMPLATES может быть использован либо один единственный файл, либо папка с подпапками, в 
REM которых есть какие-то изображения, вложенность в теории не ограничена.
REM 	В качестве картинок (скриншотов) SCREENSHOT могут быть использованы несколько файлов, разделенных между собой
REM этими символами: <пробел><звездочка><пробел> ( * ).
REM 	Диапазон порога для поиска лежит в диапазоне min ... 1.0. Параметр HOME_DIR - это папка, где лежит
REM файл check_images.py. Вывод информации происходит в консоль и в файл thresholds.txt по пути HOME_DIR. Информация
REM на каждом прогоне добавляется в конец файла (он не создается каждый раз новый).

SET HOME_DIR=D:\My_documents\Programming\Python\Check Images
SET TEMPLATES=F:\work\autotest\tests\launcher\l_screens\games\393
SET SCREENSHOT=E:\Video edit\Capture\bandicam 2022-12-29 14-21-03-483.png * E:\Video edit\Capture\bandicam 2022-12-29 14-22-18-041.png

REM All parameters:
REM -t, --templates - path to one image file or folder with image files, required parameter
REM -i, --image     - path to screen image(-s) where templates will be searched, path can be one or several, delimiter is ' * ', required parameter
REM -n, --min       - minimum threshold value in range, default=0.6, optional parameter
REM -p, --precision - the precision with which templates will be searched in the screen image, default=0.0001, optional parameter

python "%HOME_DIR%\check_images.py" -t "%TEMPLATES%" -i "%SCREENSHOT%"

pause