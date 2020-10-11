@ECHO  OFF
set script_add=%~dp0
set export_add=%1
python %script_add%export.py %export_add% "LibGen"