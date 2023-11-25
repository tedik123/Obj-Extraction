@echo on
call venv\Scripts\activate
call cd ".\src\obj_helper_functions"
call python obj_helper_functions_setup.py install