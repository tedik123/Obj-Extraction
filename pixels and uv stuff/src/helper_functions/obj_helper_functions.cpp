
#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <vector>

using namespace std;

#include <pybind11/stl.h>

namespace py = pybind11;



//array
// this is confusing but it explicitly casts vector to a python equivalent, in this case an array
//py::list getArray() {
//        return py::cast(acceptedPoints);
//}

vector<pair<int, int>> neighbor_offsets = {{1, -1}, {0, -1}, {-1, -1}, {-1, 0}, {-1, 1}, {0, 1}, {1, 1}, {1, 0}};

py::list get_neighbors_from_point(int x_given, int y_given, int max_width, int max_height) {

//    release the GIL while working, actually the GIL is already released because of our declaration
//    py::gil_scoped_release release;
    vector<pair<int, int>> neighbors;
    // Define offsets for each direction
    for (auto& [dx, dy] : neighbor_offsets) {
        // Calculate the x and y coordinates for the neighboring cell
        int x = x_given + dx;
        int y = y_given + dy;
        // Check if the neighboring cell is within bounds
        if (0 <= x && x < max_width && 0 <= y && y < max_height) {
            neighbors.emplace_back(x, y);
        }
    }
    // Lock the GIL before returning the result
    py::gil_scoped_acquire acquire;
    // return a python list
    return py::cast(neighbors);
}


py::list get_neighbors_from_points(const vector<pair<int, int>>& points, int max_width, int max_height) {
    vector<vector<pair<int, int>>> result;
    for (const auto& point : points) {
        vector<pair<int, int>> neighbors;
        // Define offsets for each direction
        for (auto& [dx, dy] : neighbor_offsets) {
            // Calculate the x and y coordinates for the neighboring cell
            // .first and .second is special C++ syntax it returns the first/second element
            int x = point.first + dx;
            int y = point.second + dy;

            if (0 <= x && x < max_width && 0 <= y && y < max_height) {
                neighbors.emplace_back(x, y);
            }
        }
        result.emplace_back(neighbors);
    }
    // Lock the GIL before returning the result
    py::gil_scoped_acquire acquire;
    return py::cast(result);
}







PYBIND11_MODULE(obj_helper_functions, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------
        .. currentmodule:: obj_helper_functions
        .. autosummary::
           :toctree: _generate
    )pbdoc";


//    m.def("get_neighbor_list", &get_neighbors,py::call_guard<py::gil_scoped_release>(), R"pbdoc(
//        Returns a list of tuples of x,y coordinates representing the at most 8 neighbors surrounding a given coordinate.
//    )pbdoc",py::arg("x_given"), py::arg("y_given"), py::arg("max_x_range"), py::arg("max_y_range"));
       m.def("get_neighbors_from_point", &get_neighbors_from_point, py::call_guard<py::gil_scoped_release>(), R"pbdoc(
               Returns a list of tuples of x,y coordinates representing the at most 8 neighbors surrounding a given coordinate.

               Args:
                   x_given (int): The x coordinate of the given point.
                   y_given (int): The y coordinate of the given point.
                   max_width (int): The maximum x value.
                   max_height (int): The maximum y value.

               Returns:
                   list of tuples: A list of tuples representing the at most 8 neighbors surrounding the given coordinate.
           )pbdoc",
           py::arg("x_given"), py::arg("y_given"), py::arg("max_width"), py::arg("max_height"));


      m.def("get_neighbors_from_points", &get_neighbors_from_points, py::call_guard<py::gil_scoped_release>(), R"pbdoc(
          Returns a 2D vector of tuples containing the neighbors for each point in the input list.

          Args:
              points (list of tuples): The list of points to calculate neighbors for.
              max_width (int): The maximum width of the 2D space.
              max_height (int): The maximum height of the 2D space.

          Returns:
              list of list of tuples: A 2D vector of tuples containing the neighbors for each point in the input list.
      )pbdoc",
      py::arg("points"), py::arg("max_width"), py::arg("max_height"));


#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}