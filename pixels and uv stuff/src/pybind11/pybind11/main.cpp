#include <pybind11/pybind11.h>

namespace py = pybind11;

float some_func(float arg1, float arg2) {
    return arg1 + arg2;
}

//I don't understand this syntax
PYBIND11_MODULE(module_name, handle) {
    handle.doc() = "This is the module docs.";
//    define the python name, and pass the c function that you want associated with that name they don't have to be the same
    handle.def("some_fn_python_name", &some_func);
}

