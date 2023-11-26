
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
#define SWAP(x,y) do { (x)=(x)^(y); (y)=(x)^(y); (x)=(x)^(y); } while(0)

vector<uint32_t> x_and_y;


void set_pixel(uint32_t x, uint32_t y) {
//    acceptedPoints[++index] = x;
    x_and_y.push_back(x);
    x_and_y.push_back(y);
//    acceptedPoints[++index] = y;
}

void lcd_hline(uint32_t x1, uint32_t x2, uint32_t y) {
	if(x1>=x2) SWAP(x1,x2);
	for(;x1<=x2;x1++) set_pixel(x1,y);
}

//array
// this is confusing but it explicitly casts vector to a python equivalent, in this case an array
py::list get_array() {
    return py::cast(x_and_y);
}



void fillTriangle(uint32_t x1,uint32_t y1,uint32_t x2,uint32_t y2,uint32_t x3,uint32_t y3) {
	uint32_t t1x,t2x,y,minx,maxx,t1xp,t2xp;
	bool changed1 = false;
	bool changed2 = false;
	int32_t signx1,signx2,dx1,dy1,dx2,dy2;
	uint32_t e1,e2;
    // Sort vertices
	if (y1>y2) { SWAP(y1,y2); SWAP(x1,x2); }
	if (y1>y3) { SWAP(y1,y3); SWAP(x1,x3); }
	if (y2>y3) { SWAP(y2,y3); SWAP(x2,x3); }

	t1x=t2x=x1; y=y1;   // Starting points

	dx1 = (int32_t)(x2 - x1); if(dx1<0) { dx1=-dx1; signx1=-1; } else signx1=1;
	dy1 = (int32_t)(y2 - y1);

	dx2 = (int32_t)(x3 - x1); if(dx2<0) { dx2=-dx2; signx2=-1; } else signx2=1;
	dy2 = (int32_t)(y3 - y1);

	if (dy1 > dx1) {   // swap values
        SWAP(dx1,dy1);
		changed1 = true;
	}
	if (dy2 > dx2) {   // swap values
        SWAP(dy2,dx2);
		changed2 = true;
	}

	e2 = (uint32_t)(dx2>>1);
    // Flat top, just process the second half
    if(y1==y2) goto next;
    e1 = (uint32_t)(dx1>>1);

	for (uint32_t i = 0; i < dx1;) {
		t1xp=0; t2xp=0;
		if(t1x<t2x) { minx=t1x; maxx=t2x; }
		else		{ minx=t2x; maxx=t1x; }
        // process first line until y value is about to change
		while(i<dx1) {
			i++;
			e1 += dy1;
	   	   	while (e1 >= dx1) {
				e1 -= dx1;
   	   	   	   if (changed1) t1xp=signx1;//t1x += signx1;
				else          goto next1;
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
				if (changed2) t2xp=signx2;//t2x += signx2;
				else          goto next2;
			}
			if (changed2)     break;
			else              t2x += signx2;
		}
	next2:
		if(minx>t1x) minx=t1x; if(minx>t2x) minx=t2x;
		if(maxx<t1x) maxx=t1x; if(maxx<t2x) maxx=t2x;
	   	lcd_hline(minx, maxx, y);    // Draw line from min to max points found on the y
		// Now increase y
		if(!changed1) t1x += signx1;
		t1x+=t1xp;
		if(!changed2) t2x += signx2;
		t2x+=t2xp;
    	y += 1;
		if(y==y2) break;

   }
	next:
	// Second half
	dx1 = (int32_t)(x3 - x2); if(dx1<0) { dx1=-dx1; signx1=-1; } else signx1=1;
	dy1 = (int32_t)(y3 - y2);
	t1x=x2;

	if (dy1 > dx1) {   // swap values
        SWAP(dy1,dx1);
		changed1 = true;
	} else changed1=false;

	e1 = (uint32_t)(dx1>>1);

	for (uint32_t i = 0; i<=dx1; i++) {
		t1xp=0; t2xp=0;
		if(t1x<t2x) { minx=t1x; maxx=t2x; }
		else		{ minx=t2x; maxx=t1x; }
	    // process first line until y value is about to change
		while(i<dx1) {
    		e1 += dy1;
	   	   	while (e1 >= dx1) {
				e1 -= dx1;
   	   	   	   	if (changed1) { t1xp=signx1; break; }//t1x += signx1;
				else          goto next3;
			}
			if (changed1) break;
			else   	   	  t1x += signx1;
			if(i<dx1) i++;
		}
	next3:
        // process second line until y value is about to change
		while (t2x!=x3) {
			e2 += dy2;
	   	   	while (e2 >= dx2) {
				e2 -= dx2;
				if(changed2) t2xp=signx2;
				else          goto next4;
			}
			if (changed2)     break;
			else              t2x += signx2;
		}
	next4:

		if(minx>t1x) minx=t1x; if(minx>t2x) minx=t2x;
		if(maxx<t1x) maxx=t1x; if(maxx<t2x) maxx=t2x;
	   	lcd_hline(minx, maxx, y);    // Draw line from min to max points found on the y
		// Now increase y
		if(!changed1) t1x += signx1;
		t1x+=t1xp;
		if(!changed2) t2x += signx2;
		t2x+=t2xp;
    	y += 1;
		if(y>y3) return;
	}
}




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



PYBIND11_MODULE(bresenham_triangle_base, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------
        .. currentmodule:: bresenham_triangle_base
        .. autosummary::
           :toctree: _generate
    )pbdoc";

    m.def("fill_triangle", &fillTriangle, R"pbdoc(
        Fills a triangle using bresenham_triangle_base.
    )pbdoc");

    m.def("get_array", &get_array, R"pbdoc(
        Fills a triangle using bresenham_triangle_base.
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