@echo off
set infile=runes-data.csv
set /p infile=Enter file location - or enter to use default:
py rune_eff_calculator.py %infile%
pause