
#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <deque>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

#include <pybind11/stl.h>
#include <iostream>
//#include <pybind11/pybind11.h>

namespace py = pybind11;


vector<pair<int, int>> neighbor_offsets = {{1,  -1},
                                           {0,  -1},
                                           {-1, -1},
                                           {-1, 0},
                                           {-1, 1},
                                           {0,  1},
                                           {1,  1},
                                           {1,  0}};

py::list get_neighbors_from_point(int x_given, int y_given, int max_width, int max_height) {

//    release the GIL while working, actually the GIL is already released because of our declaration
//    py::gil_scoped_release release;
    vector<pair<int, int>> neighbors;
    // Define offsets for each direction
    for (auto &[dx, dy]: neighbor_offsets) {
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

vector<pair<int, int>> get_neighbors_from_point_C_only(int x_given, int y_given, int max_width, int max_height) {

//    release the GIL while working, actually the GIL is already released because of our declaration
//    py::gil_scoped_release release;
    vector<pair<int, int>> neighbors;
    // Define offsets for each direction
    for (auto &[dx, dy]: neighbor_offsets) {
        // Calculate the x and y coordinates for the neighboring cell
        int x = x_given + dx;
        int y = y_given + dy;
        // Check if the neighboring cell is within bounds
        if (0 <= x && x < max_width && 0 <= y && y < max_height) {
            neighbors.emplace_back(x, y);
        }
    }
    return neighbors;
}


py::list get_neighbors_from_points(const vector<pair<int, int>> &points, int max_width, int max_height) {
    vector<vector<pair<int, int>>> result;
    for (const auto &point: points) {
        vector<pair<int, int>> neighbors;
        // Define offsets for each direction
        for (auto &[dx, dy]: neighbor_offsets) {
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


// custom hash function for pair
struct PairHash {
    template<typename T1, typename T2>
    size_t operator()(const pair<T1, T2> &p) const {
        size_t h1 = hash < T1 > {}(p.first);
        size_t h2 = hash < T2 > {}(p.second);
        return h1 ^ (h2 << 1);
    }
};

// assume these variables exist and are accessible within the function
//unordered_map<pair<int, int>, vector<int>, PairHash> coords_dict=  {
//        {{0, 0}, {255, 0, 0}}, // matches to red acceptable colors
//        {{1, 1}, {4, 5, 6}},
//        {{2, 2}, {7, 8, 9}},
//        {{3, 3}, {10, 11, 12}},
//        {{4, 4}, {13, 14, 15}}
//};
// for testing these are the 8 neighbors of 50, 50
unordered_map<pair<int, int>, vector<int>, PairHash> coords_dict = {
        {{50, 50}, {255, 0, 0}}, // matches to red acceptable colors
        {{51, 49}, {255, 0, 0}},
        {{50, 49}, {255, 0, 0}},
        {{49, 49}, {255, 0, 0}},
        {{49, 50}, {255, 0, 0}},
        {{49, 51}, {255, 0, 0}},
        {{50, 51}, {255, 0, 0}},
        {{51, 51}, {255, 0, 0}},
        {{51, 50}, {255, 0, 0}}
};

//for some reason I can't do it here...?
//coords_dict.insert({{5, 5}, {6, 6, 6}});

//unordered_map<string, vector<vector<int>>> acceptable_colors_by_label;

unordered_map<string, vector<vector<int>>> acceptable_colors_by_label = {
        {"red",    {{255, 0,   0},   {128, 0,   0},   {255, 99,  71}}},
        {"green",  {{0,   255, 0},   {0,   128, 0},   {34,  139, 34}}},
        {"blue",   {{0,   0,   255}, {0,   0,   128}, {65,  105, 225}}},
        {"yellow", {{255, 255, 0},   {255, 215, 0},   {255, 255, 224}}},
        {"purple", {{128, 0,   128}, {75,  0,   130}, {218, 112, 214}}}
};


// helper function for the search algorithm to make it more readable
void DFS_helper(const pair<int, int> &current_coords, const vector<int> &rgb,
                const vector<vector<int>> &acceptable_colors,
                deque<pair<int, int>> &queue, unordered_map<pair<int, int>, vector<int>, PairHash> &visited,
                deque<pair<int, int>> &accepted_pixels) {
    // you can think of .end() as -1 or not found
//    can probably change this to contains
    if (!visited.contains(current_coords)) {
        visited[current_coords] = rgb;
        // if rgb value is not equal to the targeted rgb then we ignore it and don't continue searching from there
        bool found_rgb = false;
        for (const auto &color: acceptable_colors) {
            if (color == rgb) {
                found_rgb = true;
                break;
            }
        }
        if (!found_rgb) {
            return;
        }
        // if it's acceptable then add to the queue to continue searching from there as well as you know that it's
        // an acceptable rgb value
        queue.push_back(current_coords);
        accepted_pixels.push_back(current_coords);
    }
}


// searching algorithm for neighboring pixels that match
//deque<pair<int, int>>, should i return a python deque?
py::list DFS(const pair<int, int> &starting_coords, const string &label_name,
                          const int &min_X, const int &min_Y, const int &max_X, const int &max_Y) {
//    coords_dict.insert({{5, 5}, {6, 6, 6}});
    int x = starting_coords.first;
    int y = starting_coords.second;
    // deque is a doubly linked list, a normal vector is fine
    // queue is just a tuple list of coords
    deque<pair<int, int>> queue;
    // important that this is an unordered_map it's much faster look up time!
    unordered_map<pair<int, int>, vector<int>, PairHash> visited;
    // this can just be a normal list or vector
    deque<pair<int, int>> accepted_pixels;
    // add the start to the queue and the visited unordered_map
    queue.push_back(starting_coords);

    // the value stored is arbitrary in this case it's rgb from coords dict
    visited[starting_coords] = coords_dict[starting_coords];
    accepted_pixels.push_back(starting_coords);
    auto acceptable_colors = acceptable_colors_by_label[label_name];

    while (!queue.empty()) {
        auto current_coords = queue.front();
        queue.pop_front();
        x = current_coords.first;
        y = current_coords.second;
//        remove later this is just to prevent the crashing since we have a limited amount of points
        if (!coords_dict.contains(current_coords)) {
            cout << "Starting coords do not exist in dict! Skipping this one!" << endl;
        } else {
            auto pixel_rgb = coords_dict[current_coords];
//        FIXME later should not be fixed 4096
            auto neighbors = get_neighbors_from_point_C_only(x, y, 4096, 4096);

            // this is no more than 8 long at a time
            for (const auto &neighbor: neighbors) {
                auto current_x = neighbor.first;
                auto current_y = neighbor.second;
                // need to check that it's within the confines as well
                if (max_X >= current_x && current_x >= min_X && max_Y >= current_y && current_y >= min_Y) {
                    DFS_helper(make_pair(current_x, current_y), pixel_rgb, acceptable_colors, queue, visited,
                               accepted_pixels);
                }
            }
        }
    }
    // return revealed which should be all matching pixels within range
    cout << "visited vs revealed" << endl;
    cout << visited.size() << endl;
    cout << accepted_pixels.size() << endl;
    return py::cast(accepted_pixels);
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

    m.def("DFS", &DFS, R"pbdoc(DFS TEST)pbdoc", py::arg("starting_coords"), py::arg("label_name"),
          py::arg("min_X"), py::arg("min_Y"), py::arg("max_X"), py::arg("max_Y"));

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}