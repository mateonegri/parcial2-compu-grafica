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
#


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '3.0')
from gi.repository import Gtk, GooCanvas

from main_menu import Main_menu
from povview_things import Vec3, Cone, Sphere
from pdb import set_trace as st
from povview_parser import make_pov_parser
import pyparsing as pp


TEST_OBJ = ['sphere', [[0.0, 0.0, 0.0], 40]]

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

        self.views = {}
        for x, y, lbl in [(0, 0, 'xy'), (1, 0, 'yz'), (0, 1, 'zx')]:
            frame = Gtk.Frame(label = lbl, label_xalign = 0.04,
                        hexpand = True, vexpand = True)
            self.attach(frame, x, y, 1, 1)

            canvas = GooCanvas.Canvas(
                        automatic_bounds = True,
                        bounds_from_origin = False,
                        bounds_padding = 10)
            frame.add(canvas)
            self.views[lbl] = {'frame': frame, 'canvas': canvas}

    def add_object(self, obj):

        for item in obj:
            if item[0] == 'sphere':
                # Here, we assume obj[1] is [position, radius] for the sphere
                position = item[1][0]
                radius = item[1][1]
                s = Sphere(position, radius)
                self.objs.append(s)
                s.draw_on(self.views)

class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", lambda x: Gtk.main_quit())
        self.set_default_size(800, 600)

        mm = self.make_main_menu()

        cmd_entry = Gtk.Entry(text = TEST_OBJ, hexpand = True)
        cmd_entry.connect('activate', self.on_cmd_entry_activate)

        self.views = Views()

        grid = Gtk.Grid(vexpand = True)
        grid.attach(mm, 0, 0, 2, 1)
        grid.attach(cmd_entry, 0, 1, 2, 1)
        grid.attach(self.views, 0, 2, 2, 1)
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
