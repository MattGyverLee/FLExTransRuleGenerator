@echo off
REM Launch FLExTrans Rule Generator (Python/PyQt6 version)
REM
REM Usage:
REM   run_rule_generator.bat [rule_file] [flex_data_file] [test_data_file] [from_lrt] [lang_code]
REM
REM If no arguments are given, launches with bundled sample data.

setlocal

set "SCRIPT_DIR=%~dp0"

REM Default sample data paths
if "%~1"=="" (
    set "RULE_FILE=%SCRIPT_DIR%tests\test_data\Ex1a_Def-Noun.xml"
) else (
    set "RULE_FILE=%~1"
)

if "%~2"=="" (
    set "FLEX_DATA=%SCRIPT_DIR%tests\test_data\FLExDataSpanFrench.xml"
) else (
    set "FLEX_DATA=%~2"
)

set "TEST_DATA=%~3"
if "%~4"=="" (set "FROM_LRT=n") else (set "FROM_LRT=%~4")
set "LANG_CODE=%~5"

echo Launching FLExTrans Rule Generator...
echo   Rule file:     %RULE_FILE%
echo   FLEx data:     %FLEX_DATA%
if not "%TEST_DATA%"=="" echo   Test data:     %TEST_DATA%
echo.

cd /d "%SCRIPT_DIR%"
set "PYTHONPATH=%SCRIPT_DIR%src;%PYTHONPATH%"

if not "%TEST_DATA%"=="" (
    python -m flextrans_rule_generator.main "%RULE_FILE%" "%FLEX_DATA%" "%TEST_DATA%" "%FROM_LRT%" "%LANG_CODE%"
) else (
    python -m flextrans_rule_generator.main "%RULE_FILE%" "%FLEX_DATA%" "" "%FROM_LRT%" "%LANG_CODE%"
)
