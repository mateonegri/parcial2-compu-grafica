#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  povview.py
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
# Alumnos:
# Mateo Negri Ocampo 2103108
# Pedro Diaz Romagnoli 2223997
# Manuela Simes 2103975
#


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')
from gi.repository import Gtk, GooCanvas

from main_menu import Main_menu
from povview_things import Vec3, Cone, Sphere
from pdb import set_trace as st
from povview_parser import make_pov_parser
import pyparsing as pp


TEST_OBJ = [['sphere', [[0.0, 0.0, 0.0], 40]]]

COLORS = {'White':  (1, 1, 1),
          'Black':  (0, 0, 0),
          'Red':    (1, 0, 0),
          'Green':  (0, 1, 0),
          'Blue':   (0, 0, 1),
          'Yellow': (1, 1, 0),
          'Orange': (1, 0.5, 0),
          'Cyan':   (0, 1, 1),
          'Purple': (1, 0, 1)}


class Views(Gtk.Grid):
    def __init__(self):
        super().__init__(row_spacing = 4, column_spacing = 4, margin = 4)

        self.objs = []

         # Store current rotation angles and sphere parameters
        self.current_rotation = {'x': 0, 'y': 0, 'z': 0}
        self.current_subdiv = 25
        self.current_size = 50
        self.current_position = [[0.0, 0.0, 0.0]]

        self.views = {}
        for x, y, lbl in [(0, 0, 'xy'), (1, 0, 'yz'), (0, 1, 'zx')]:
            frame = Gtk.Frame(label = lbl, label_xalign = 0.04,
                        hexpand = True, vexpand = True)
            self.attach(frame, x, y, 1, 1)

            self.canvas = GooCanvas.Canvas(
                        automatic_bounds = True,
                        bounds_from_origin = False,
                        bounds_padding = 10)
            frame.add(self.canvas)
            self.views[lbl] = {'frame': frame, 'canvas': self.canvas}

    def add_object(self, obj):

        self.clear_all()

        for item in obj:
            if item[0] == 'sphere':
                # Here, we assume obj[1] is [position, radius] for the sphere
                position = item[1][0]
                self.current_position = position
                radius = item[1][1]
                self.current_size = radius
                s = Sphere(position, radius)
                self.objs.append(s)
                s.draw_on(self.views)
    
    def clear(self):
        """
        Removes all items from all canvases in the views.
        Does NOT reset the objects list to allow for updates.
        """
        for view_key in self.views:
            canvas = self.views[view_key]['canvas']
            root = canvas.get_root_item()
            
            # Remove all children from the root item
            if root:
                # Get the number of children
                n_children = root.get_n_children()
                
                # Remove children from last to first to avoid indexing issues
                for i in range(n_children - 1, -1, -1):
                    child = root.get_child(i)
                    if child:
                        root.remove_child(i)

    def clear_all(self):
        """
        Completely clears both the canvases and the objects list.
        Use this when loading new objects, not when updating existing ones.
        """
        self.clear()
        self.objs = []
    
    # Callback for subdivision slider
    def on_subdiv_change(self, slider):
        sliderValue = slider.get_value()
        for s in self.objs:
            s.update_sphere_subdivision(sliderValue, self.views)

    # Callback for size slider
    def on_size_change(self, slider):
        sliderValue = slider.get_value()
        for s in self.objs:
            s.update_sphere_size(sliderValue, self.views)

    def on_rotation_change(self, slider, axis):
        angle = slider.get_value()
        for s in self.objs:
            if isinstance(s, Sphere):
                s.update_rotation(axis, angle, self.views)



        

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", lambda x: Gtk.main_quit())
        self.set_default_size(800, 600)

        mm = self.make_main_menu()

        cmd_entry = Gtk.Entry(text = TEST_OBJ, hexpand = True)
        cmd_entry.connect('activate', self.on_cmd_entry_activate)

        self.views = Views()

        # Create sliders for subdivision, rotation, and size
        self.subdiv_slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.subdiv_slider.set_range(3, 50)  # Min 3 subdivisions, max 50
        self.subdiv_slider.set_value(25)  # Default
        subdiv_slider_value = self.subdiv_slider.get_value()
        self.subdiv_slider.connect('value-changed', self.views.on_subdiv_change)

        self.size_slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.size_slider.set_range(10, 200)  # Adjust the range as needed
        self.size_slider.set_value(50)  # Default
        size_slider_value = self.size_slider.get_value()
        self.size_slider.connect('value-changed', self.views.on_size_change)

        # Rotation sliders
        self.rotation_sliders = {}
        for axis in ['x', 'y', 'z']:
            slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
            slider.set_range(0, 360)
            slider.set_value(0)
            slider.connect('value-changed', lambda w, a=axis: self.views.on_rotation_change(w, a))
            self.rotation_sliders[axis] = slider

        grid = Gtk.Grid(vexpand = True)
        grid.attach(mm, 0, 0, 2, 1)
        grid.attach(cmd_entry, 0, 1, 2, 1)
        grid.attach(self.views, 0, 2, 2, 1)

        # Attach sliders for subdivision, rotation, and size
        grid.attach(Gtk.Label("Subdivision"), 0, 3, 1, 1)
        grid.attach(self.subdiv_slider, 1, 3, 1, 1)
        
        grid.attach(Gtk.Label("Size"), 0, 4, 1, 1)
        grid.attach(self.size_slider, 1, 4, 1, 1)

        # Add rotation sliders
        grid.attach(Gtk.Label("Rotate X"), 0, 5, 1, 1)
        grid.attach(self.rotation_sliders['x'], 1, 5, 1, 1)
        
        grid.attach(Gtk.Label("Rotate Y"), 0, 6, 1, 1)
        grid.attach(self.rotation_sliders['y'], 1, 6, 1, 1)
        
        grid.attach(Gtk.Label("Rotate Z"), 0, 7, 1, 1)
        grid.attach(self.rotation_sliders['z'], 1, 7, 1, 1)

        self.add(grid)
        self.show_all()


    def run(self):
        Gtk.main()

    def make_main_menu(self):
        mm = Main_menu(['_File', '_Tests', '_Help'])
        mm.add_items_to('_File', (
                    ('Open POV scene...', self.on_open_pov_clicked),
                    (None, None),
                    ('_Quit', self.on_quit_clicked)))

        mm.add_items_to('_Tests', (
                    ('Add Sphere to viewer', self.on_add_sphere_clicked), ))

        return mm



    def on_add_sphere_clicked(self, menuitem):
        self.views.add_object(TEST_OBJ)


    def on_open_pov_clicked(self, menuitem):
        fc = Gtk.FileChooserDialog(
                    action = Gtk.FileChooserAction.OPEN)
        fc.add_buttons(
                    'Cancel', Gtk.ResponseType.CANCEL,
                    'Open', Gtk.ResponseType.ACCEPT)

        for f_name, f_pattern in (
                    ('POVday files (*.pov)', '*.pov'),
                    ('All files (*)', '*')):
            filter = Gtk.FileFilter()
            filter.set_name(f_name)
            filter.add_pattern(f_pattern)
            fc.add_filter(filter)

        if fc.run() == Gtk.ResponseType.ACCEPT:
            print(fc.get_filename())
            pov_filename = fc.get_filename()

            # Read the contents of the selected POV file
            with open(pov_filename, 'r') as pov_file:
                pov_content = pov_file.read()

            # Parse the contents of the POV file using your parser
            parser = make_pov_parser()
            try:
                parsed_data = parser.parseString(pov_content)
                print("Parsed Data:", parsed_data)

            except pp.ParseException as err:
                print("Error parsing the POV file:")
                print(err.line)
                print(" " * (err.column - 1) + "^")
                print(err)
        
        self.views.add_object(parsed_data)

        fc.destroy()


    def on_quit_clicked(self, menuitem):
        Gtk.main_quit()


    def on_cmd_entry_activate(self, entry):
        print('Command: ', entry.get_text())



def main(args):
    mainwdw = MainWindow()
    mainwdw.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
