
#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <vector>

using namespace std;

#include <pybind11/stl.h>

namespace py = pybind11;

// Swap two bytes
#define SWAP(x, y) do { (x)=(x)^(y); (y)=(x)^(y); (x)=(x)^(y); } while(0)


class BresenhamTriangle {
public:
//    vector<uint32_t> acceptedPoints;
// pair is an STD class
    vector<pair<int, int>> acceptedPoints;
    int max_height, max_width;

//    i want to pass in variables that are max width and height how to save again?
    BresenhamTriangle(int max_width, int max_height) {
        this->max_height = max_height;
        this->max_width = max_width;
    }

//    I don't know if we need to worry about the vector and memory leak
    ~BresenhamTriangle() = default;

    void savePoint(uint32_t x, uint32_t y) {
//        make_pair is an STD function
//        acceptedPoints.push_back(make_pair(x, y));
//        idk C wants this
        acceptedPoints.emplace_back(x, y);

//        acceptedPoints.push_back(x);
//        acceptedPoints.push_back(y);
    }

    void saveLinePoints(uint32_t x1, uint32_t x2, uint32_t y) {
        if (x1 >= x2) SWAP(x1, x2);
        for (; x1 <= x2; x1++) savePoint(x1, y);
    }

//array
// this is confusing but it explicitly casts vector to a python equivalent, in this case an array
    py::list getArray() {
        return py::cast(acceptedPoints);
    }

//    based on width conversion
    int convertUtoInt(float value) {
//        order matters parenthesis is critical to cast correctly
        return (int) (value * this->max_width);
    }

// based on height conversion
    int convertVtoInt(float value) {
        return (int) ((value - 1) * -this->max_height);
    }

    py::list fillTriangle(uint32_t x1, uint32_t y1, uint32_t x2, uint32_t y2, uint32_t x3, uint32_t y3) {
        uint32_t t1x, t2x, y, minx, maxx, t1xp, t2xp;
        bool changed1 = false;
        bool changed2 = false;
        int32_t signx1, signx2, dx1, dy1, dx2, dy2;
        uint32_t e1, e2;
        // Sort vertices
        if (y1 > y2) {
            SWAP(y1, y2);
            SWAP(x1, x2);
        }
        if (y1 > y3) {
            SWAP(y1, y3);
            SWAP(x1, x3);
        }
        if (y2 > y3) {
            SWAP(y2, y3);
            SWAP(x2, x3);
        }

        t1x = t2x = x1;
        y = y1;   // Starting points

        dx1 = (int32_t) (x2 - x1);
        if (dx1 < 0) {
            dx1 = -dx1;
            signx1 = -1;
        } else signx1 = 1;
        dy1 = (int32_t) (y2 - y1);

        dx2 = (int32_t) (x3 - x1);
        if (dx2 < 0) {
            dx2 = -dx2;
            signx2 = -1;
        } else signx2 = 1;
        dy2 = (int32_t) (y3 - y1);

        if (dy1 > dx1) {   // swap values
            SWAP(dx1, dy1);
            changed1 = true;
        }
        if (dy2 > dx2) {   // swap values
            SWAP(dy2, dx2);
            changed2 = true;
        }

        e2 = (uint32_t) (dx2 >> 1);
        // Flat top, just process the second half
        if (y1 == y2) goto next;
        e1 = (uint32_t) (dx1 >> 1);

        for (uint32_t i = 0; i < dx1;) {
            t1xp = 0;
            t2xp = 0;
            if (t1x < t2x) {
                minx = t1x;
                maxx = t2x;
            } else {
                minx = t2x;
                maxx = t1x;
            }
            // process first line until y value is about to change
            while (i < dx1) {
                i++;
                e1 += dy1;
                while (e1 >= dx1) {
                    e1 -= dx1;
                    if (changed1) t1xp = signx1;//t1x += signx1;
                    else goto next1;
                }
                if (changed1) break;
                else t1x += signx1;
            }
            // Move line
            next1:
            // process second line until y value is about to change
            while (1) {
                e2 += dy2;
                while (e2 >= dx2) {
                    e2 -= dx2;
                    if (changed2) t2xp = signx2;//t2x += signx2;
                    else goto next2;
                }
                if (changed2) break;
                else t2x += signx2;
            }
            next2:
            if (minx > t1x) minx = t1x;
            if (minx > t2x) minx = t2x;
            if (maxx < t1x) maxx = t1x;
            if (maxx < t2x) maxx = t2x;
            saveLinePoints(minx, maxx, y);    // Draw line from min to max points found on the y
            // Now increase y
            if (!changed1) t1x += signx1;
            t1x += t1xp;
            if (!changed2) t2x += signx2;
            t2x += t2xp;
            y += 1;
            if (y == y2) break;

        }
        next:
        // Second half
        dx1 = (int32_t) (x3 - x2);
        if (dx1 < 0) {
            dx1 = -dx1;
            signx1 = -1;
        } else signx1 = 1;
        dy1 = (int32_t) (y3 - y2);
        t1x = x2;

        if (dy1 > dx1) {   // swap values
            SWAP(dy1, dx1);
            changed1 = true;
        } else changed1 = false;

        e1 = (uint32_t) (dx1 >> 1);

        for (uint32_t i = 0; i <= dx1; i++) {
            t1xp = 0;
            t2xp = 0;
            if (t1x < t2x) {
                minx = t1x;
                maxx = t2x;
            } else {
                minx = t2x;
                maxx = t1x;
            }
            // process first line until y value is about to change
            while (i < dx1) {
                e1 += dy1;
                while (e1 >= dx1) {
                    e1 -= dx1;
                    if (changed1) {
                        t1xp = signx1;
                        break;
                    }//t1x += signx1;
                    else goto next3;
                }
                if (changed1) break;
                else t1x += signx1;
                if (i < dx1) i++;
            }
            next3:
            // process second line until y value is about to change
            while (t2x != x3) {
                e2 += dy2;
                while (e2 >= dx2) {
                    e2 -= dx2;
                    if (changed2) t2xp = signx2;
                    else goto next4;
                }
                if (changed2) break;
                else t2x += signx2;
            }
            next4:

            if (minx > t1x) minx = t1x;
            if (minx > t2x) minx = t2x;
            if (maxx < t1x) maxx = t1x;
            if (maxx < t2x) maxx = t2x;
            saveLinePoints(minx, maxx, y);    // Draw line from min to max points found on the y
            // Now increase y
            if (!changed1) t1x += signx1;
            t1x += t1xp;
            if (!changed2) t2x += signx2;
            t2x += t2xp;
            y += 1;
//            this used to be an empty return
            if (y > y3) return getArray();
        }
        return getArray();
    }


//    take in float UV value and convert them to pixel coordinates based on max_width
//    and height provided in the constructor
    py::list fillUvTriangle(float x1, float y1, float x2, float y2, float x3, float y3) {
        int ix1 = convertUtoInt(x1);
        int iy1 = convertVtoInt(y1);
        int ix2 = convertUtoInt(x2);
        int iy2 = convertVtoInt(y2);
        int ix3 = convertUtoInt(x3);
        int iy3 = convertVtoInt(y3);
        return fillTriangle(ix1, iy1, ix2, iy2, ix3, iy3);
    }


    py::list fillTriangleslope(uint32_t x0, uint32_t y0,uint32_t x1, uint32_t y1, uint32_t x2, uint32_t y2) {
 	uint32_t a, b, y, last;
  	// Sort coordinates by Y order (y2 >= y1 >= y0)
  	if (y0 > y1) { SWAP(y0, y1); SWAP(x0, x1); }
  	if (y1 > y2) { SWAP(y2, y1); SWAP(x2, x1); }
  	if (y0 > y1) { SWAP(y0, y1); SWAP(x0, x1); }

  	if(y0 == y2) { // All on same line case
    	a = b = x0;
    	if(x1 < a)      a = x1;
    	else if(x1 > b) b = x1;
    	if(x2 < a)      a = x2;
    	else if(x2 > b) b = x2;
        saveLinePoints(a, b, y0);
        return getArray();
    }

    uint32_t
        dx01 = x1 - x0,
        dy01 = y1 - y0,
        dx02 = x2 - x0,
        dy02 = y2 - y0,
        dx12 = x2 - x1,
        dy12 = y2 - y1;
    uint32_t sa = 0, sb = 0;

    // For upper part of triangle, find scanline crossings for segment
    // 0-1 and 0-2.  If y1=y2 (flat-bottomed triangle), the scanline y
    // is included here (and second loop will be skipped, avoiding a /
    // error there), otherwise scanline y1 is skipped here and handle
    // in the second loop...which also avoids a /0 error here if y0=y
    // (flat-topped triangle)
    if(y1 == y2) last = y1;   // Include y1 scanline
    else         last = y1-1; // Skip it

    for(y=y0; y<=last; y++) {
        a   = x0 + sa / dy01;
        b   = x0 + sb / dy02;
        sa += dx01;
        sb += dx02;
        // longhand a = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
        //          b = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
        saveLinePoints(a, b, y);
    }

    // For lower part of triangle, find scanline crossings for segment
    // 0-2 and 1-2.  This loop is skipped if y1=y2
    sa = dx12 * (y - y1);
    sb = dx02 * (y - y0);
    for(; y<=y2; y++) {
        a   = x1 + sa / dy12;
        b   = x0 + sb / dy02;
        sa += dx12;
        sb += dx02;
        // longhand a = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
        //          b = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
        saveLinePoints(a, b, y);
    }
    return getArray();
}
};




//int main()
//{
//    acceptedPoints[0] = 0;
//    uint32_t x1 = 2469;
//    uint32_t y1 =362 ;
//    uint32_t x2 =2470;
//    uint32_t y2 =365;
//    uint32_t x3 =2473;
//    uint32_t y3 =365;
//    uint32_t count = 0;
//    fillTriangle(x1,y1,x2,y2,x3,y3);
//    for (int i = 0; i < 100; i++)
//        if(acceptedPoints[i]!=0) {
//            printf("%d ", acceptedPoints[i]);
//            count+=1;
//        }
//    printf("Total coords is %d", count/2);
//    return 0;
//}



PYBIND11_MODULE(bresenham_triangle_class, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------
        .. currentmodule:: bresenham_triangle_class
        .. autosummary::
           :toctree: _generate
    )pbdoc";
//    First expose the class
// the "bresenhamTriangle" part is the interface to expose further functions you want
    py::class_<BresenhamTriangle> bresenhamTriangle(m, "BresenhamTriangle", R"pbdoc(
        Class that will fill the points within a triangle
)pbdoc");
//    this is how you pass in constructor arguments
    bresenhamTriangle.def(py::init<int, int>());
//    to expose the function you need to set the point to the class function not just the function call itself
    bresenhamTriangle.def("fill_triangle", &BresenhamTriangle::fillTriangle, R"pbdoc(
        Fills a triangle using the bresenham triangle algorithm.
    )pbdoc");

    bresenhamTriangle.def("fill_UV_triangle", &BresenhamTriangle::fillUvTriangle, R"pbdoc(
        Fills a UV triangle by converting it to ints and using the bresenham triangle algorithm.
    )pbdoc");

    bresenhamTriangle.def("get_array", &BresenhamTriangle::getArray, R"pbdoc(
        Returns the vector that stores all the acceptable points as a python list.
    )pbdoc");

    bresenhamTriangle.def("fill_triangle_by_slope", &BresenhamTriangle::fillTriangleslope, R"pbdoc(
        Fills a triangle of ints using the slop method.
    )pbdoc");

//    m.def("lcd_hline", &saveLinePoints, R"pbdoc(
//        Starts the draw method
//    )pbdoc");
//
//    m.def("set_pixel", &savePoint, R"pbdoc(
//        Returns the global array
//    )pbdoc");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}