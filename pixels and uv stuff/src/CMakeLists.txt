cmake_minimum_required(VERSION 3.25)
find_package(PythonLibs 3 REQUIRED)
#set(pybind11_DIR /pybind11)
#find_package(pybind11 CONFIG)
add_subdirectory(pybind11)
project(src)

set(CMAKE_CXX_STANDARD 23)


pybind11_add_module(obj_helper_functions obj_helper_functions/obj_helper_functions.cpp)

add_executable(src obj_helper_functions/obj_helper_functions.cpp)
