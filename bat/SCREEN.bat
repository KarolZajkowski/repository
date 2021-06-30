@echo off

set nazwapliku=%time: =0%
set nazwapliku=%nazwapliku:,=_%
set nazwapliku=%nazwapliku:.=_%
set nazwapliku=%nazwapliku::=_%

adb shell screencap -p /sdcard/%nazwapliku%.png
adb pull /sdcard/%nazwapliku%.png
adb shell rm /sdcard/%nazwapliku%.png

convert %nazwapliku%.png %nazwapliku%.jpg

del %nazwapliku%.png

