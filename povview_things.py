#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  povview_things.py
#
#  Copyright 2024 John Coppens <john@jcoppens.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '3.0')
from gi.repository import Gtk, GooCanvas

from math import cos, sin, pi
from pdb import set_trace as st
import numpy as np

SUBDIV = 12

class ThreeD_object:
    def __init__(self):
        pass



class Vec3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class RGB:
    def __init__(self, r, g = None, b = None):
        if isinstance(r, list):
            self._rgb = r
        else:
            self._rgb = [r, g, b]


    def __str__(self):
        return f"r: {self._rgb[0]}, g: {self._rgb[1]}, b: {self._rgb[2]}"


    @property
    def r(self):
        return self._rgb[0]

    @property
    def g(self):
        return self._rgb[1]

    @property
    def b(self):
        return self._rgb[2]

    @property
    def rgb(self):
        return self._rgb



class RGBA:
    def __init__(self, r, g, b, a):
        self.r, self.g, self.b, self.a = r, g, b, a



class Cone(ThreeD_object):
    """ tc      self.tc     vec3    Cone top center
        tr      self.tr     float   Cone top radius
        bc      self.bc     vec3    Cone bottom center
        br      self.br     float   Cone bottom radius
    """
    def __init__(self, cone_par):
        self.tc = cone_par[0]
        self.tr = cone_par[1]
        self.bc = cone_par[2]
        self.br = cone_par[3]

        self.create_wireframe()


    def __str__(self):
        return (f'Cone:\n'
                f'top:    {self.tc[0]:10g}, {self.tc[1]:10g}, {self.tc[2]:10g}'
                f' radius: {self.tr:10g}\n'
                f'bottom: {self.bc[0]:10g}, {self.bc[1]:10g}, {self.bc[2]:10g}'
                f' radius: {self.br:10g}\n')


    def create_wireframe(self):
        self.tx = []
        self.ty = []
        self.tz = []
        self.bx = []
        self.by = []
        self.bz = []
        dsub = 2*pi/SUBDIV

        for i in range(SUBDIV):
            self.tx += [self.tc[0] + self.tr * cos(dsub * i)]
            self.ty += [-self.tc[1]]
            self.tz += [self.tc[2] + self.tr * sin(dsub * i)]

            self.bx += [self.bc[0] + self.br * cos(dsub * i)]
            self.by += [-self.bc[1]]
            self.bz += [self.bc[2] + self.br * sin(dsub * i)]

        # ~ print(self.tx)
        # ~ print(self.ty)
        # ~ print(self.tz)
        # ~ print(self.bx)
        # ~ print(self.by)
        # ~ print(self.bz)


    def to_svg(self, side):
        if side == 'xy':
            # top surface
            svg = f"M{self.tx[0]:g},{self.ty[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.tx[s]:g},{self.ty[s]:g} "
            svg += 'Z '

            # bottom surface
            svg += f"M{self.bx[0]:g},{self.by[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.bx[s]:g},{self.by[s]:g} "
            svg += 'Z '

            # 'vertical' spokes
            for s in range(SUBDIV):
                svg += (f"M{self.tx[s]:g},{self.ty[s]:g} "
                        f"L{self.bx[s]:g},{self.by[s]:g} ")

        elif side == 'yz':
            # top surface
            svg = f"M{self.tz[0]:g},{self.ty[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.tz[s]:g},{self.ty[s]:g} "
            svg += 'Z '
            
            # bottom surface
            svg += f"M{self.bz[0]:g},{self.by[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.bz[s]:g},{self.by[s]:g} "
            svg += 'Z '

            # 'vertical' spokes
            for s in range(SUBDIV):
                svg += (f"M{self.tz[s]:g},{self.ty[s]:g} "
                        f"L{self.bz[s]:g},{self.by[s]:g} ")

        else:  # zx
            # top surface
            svg = f"M{self.tz[0]:g},{self.tx[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.tz[s]:g},{self.tx[s]:g} "
            svg += 'Z '
            
            # bottom surface
            svg += f"M{self.bz[0]:g},{self.bx[0]:g} "
            for s in range(1, SUBDIV):
                svg += f"L{self.bz[s]:g},{self.bx[s]:g} "
            svg += 'Z '

            # 'vertical' spokes
            for s in range(SUBDIV):
                svg += (f"M{self.tz[s]:g},{self.tx[s]:g} "
                        f"L{self.bz[s]:g},{self.bx[s]:g} ")
            
        print(svg)
        return svg


    def draw_on(self, views):
        for view in ['xy', 'yz', 'zx']:
            root = views[view]['canvas'].get_root_item()
            GooCanvas.CanvasPath(
                        parent = root,
                        data = self.to_svg(view),
                        line_width = 1, stroke_color = 'White',
                        fill_color = None)

class Sphere(ThreeD_object):
    """ self object
        center      vec3    Center of the self
        radius      float   Radius of the self
        color       RGB     Optional color for the self
    """
    def __init__(self, center, radius, color=None):
        self.center = center
        self.radius = radius
        self.shape = None  # Initialize shape to None
        self.color = color if color else RGB(1, 0, 0)  # Default color is red if not provided
        self.tx = []  # Points for longitude lines (horizontal slices)
        self.ty = []
        self.tz = []
        self.bx = []  # Points for latitude lines (vertical slices)
        self.by = []
        self.bz = []
        self.create_wireframe()

    def create_wireframe(self):
        """ Generate wireframe points for the self """
        dtheta = 2 * pi / SUBDIV  # Horizontal angle increment (longitude)
        dphi = pi / SUBDIV  # Vertical angle increment (latitude)

        # Loop for horizontal divisions (longitude)
        for i in range(SUBDIV + 1):
            theta = i * dtheta
            tx = []
            ty = []
            tz = []
            # Loop for vertical divisions (latitude)
            for j in range(SUBDIV + 1):
                phi = j * dphi
                x = self.center[0] + self.radius * sin(phi) * cos(theta)
                y = self.center[1] + self.radius * sin(phi) * sin(theta)
                z = self.center[2] + self.radius * cos(phi)

                tx.append(x)
                ty.append(y)
                tz.append(z)

            self.tx.append(tx)
            self.ty.append(ty)
            self.tz.append(tz)

        # Loop for vertical divisions (latitude, through the poles)
        for j in range(SUBDIV + 1):
            phi = j * dphi
            bx = []
            by = []
            bz = []
            # Loop for horizontal divisions (longitude)
            for i in range(SUBDIV + 1):
                theta = i * dtheta
                x = self.center[0] + self.radius * sin(phi) * cos(theta)
                y = self.center[1] + self.radius * sin(phi) * sin(theta)
                z = self.center[2] + self.radius * cos(phi)

                bx.append(x)
                by.append(y)
                bz.append(z)

            self.bx.append(bx)
            self.by.append(by)
            self.bz.append(bz)

    def __str__(self):
        return (f'Sphere:\n'
                f'Center: {self.center[0]:10g}, {self.center[1]:10g}, {self.center[2]:10g}\n'
                f'Radius: {self.radius:10g}\n'
                f'Color: {self.color}')

    def to_svg(self, side):
        """ Creates the SVG representation for the self using wireframe (projected views) """
        svg = ""
        if side == 'xy':
            # Draw the wireframe for the xy-plane
            for i in range(len(self.tx)):
                svg += f"M{self.tx[i][0]:g},{self.ty[i][0]:g} "
                for j in range(1, len(self.tx[i])):
                    svg += f"L{self.tx[i][j]:g},{self.ty[i][j]:g} "
                svg += "Z "

            for j in range(len(self.bx)):
                svg += f"M{self.bx[j][0]:g},{self.by[j][0]:g} "
                for i in range(1, len(self.bx[j])):
                    svg += f"L{self.bx[j][i]:g},{self.by[j][i]:g} "
                svg += "Z "

        elif side == 'yz':
            # Draw the wireframe for the yz-plane
            for i in range(len(self.tx)):
                svg += f"M{self.tz[i][0]:g},{self.ty[i][0]:g} "
                for j in range(1, len(self.tx[i])):
                    svg += f"L{self.tz[i][j]:g},{self.ty[i][j]:g} "
                svg += "Z "

            for j in range(len(self.bz)):
                svg += f"M{self.bz[j][0]:g},{self.by[j][0]:g} "
                for i in range(1, len(self.bz[j])):
                    svg += f"L{self.bz[j][i]:g},{self.by[j][i]:g} "
                svg += "Z "

        else:  # zx-plane
            for i in range(len(self.tx)):
                svg += f"M{self.tz[i][0]:g},{self.tx[i][0]:g} "
                for j in range(1, len(self.tx[i])):
                    svg += f"L{self.tz[i][j]:g},{self.tx[i][j]:g} "
                svg += "Z "

            for j in range(len(self.bz)):
                svg += f"M{self.bz[j][0]:g},{self.bx[j][0]:g} "
                for i in range(1, len(self.bz[j])):
                    svg += f"L{self.bz[j][i]:g},{self.bx[j][i]:g} "
                svg += "Z "

        return svg

    def draw_on(self, views):
        for view in ['xy', 'yz', 'zx']:
            root = views[view]['canvas'].get_root_item()
            self.shape = GooCanvas.CanvasPath(
                parent=root,
                data=self.to_svg(view),
                line_width=1, stroke_color='Black',
                fill_color=None
            )

    
    def redraw(self, views):
        """Clear the canvas and redraw the sphere."""

        self.shape.remove()
        
        # Now draw the updated sphere
        self.draw_on(views)

    def update_sphere_size(self, new_radius, views):
        """ Update the radius of the self and regenerate its wireframe. """
        self.radius = new_radius
        self.create_wireframe()  # Recreate the self's geometry
        self.redraw(views)

        

    def update_sphere_subdivision(self, new_subdiv, views):
        """ Update the subdivision of the sphere and regenerate its wireframe. """
        global SUBDIV
        SUBDIV = int(new_subdiv)
        self.create_wireframe()  # Recreate the sphere with new subdivisions
        self.redraw(views)
        

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", lambda x: Gtk.main_quit())
        self.set_default_size(400, 300)

        self.canvas = GooCanvas.Canvas(
                    automatic_bounds = True,
                    bounds_from_origin = False,
                    bounds_padding = 10)
        cvroot = self.canvas.get_root_item()

        # cone = Cone([[20, 20, 30], 20, [20, -30, 30], 30])

        # Create a self object
        self = self([200, 150, 0], 50, RGB(1, 0, 0))  # Initialize RGB instance

        self.path = GooCanvas.CanvasPath(
                    parent = cvroot,
                    data = self.to_svg('xy'),
                    line_width = 1, stroke_color = 'Black',
                    fill_color = None)

        bounds = self.canvas.get_bounds()
        print('Bounds:', bounds)
        self.set_scale(4)

        print("SVG data:", self.to_svg('xy'))

        # Draw the self on the canvas
        self.draw_on({'xy': {'canvas': self.canvas}, 'yz': {'canvas': self.canvas}, 'zx': {'canvas': self.canvas}})

        self.add(self.canvas)
        self.show_all()

    def run(self):
        Gtk.main()

    def set_scale(self, scale):
        self.canvas.set_scale(scale)
        self.path.set_property('line_width', 1/scale)

def main(args):
    mainwdw = MainWindow()
    mainwdw.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
