#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  povview_parser.py
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

import pyparsing as pp


def make_pov_parser(which = 'parser'):
     # Rule to ignore comments or #include directives
    include_directive = pp.Suppress(pp.Literal("#include") + '"color.inc"')
    comment_line = pp.Suppress(pp.Literal("#") + pp.SkipTo(pp.LineEnd()))

    optsign = pp.Optional(pp.oneOf("+ -"))
    uinteger = (pp.Word('123456789', pp.nums) ^ '0')
    sinteger = pp.Combine(optsign + uinteger)

    expon = pp.one_of('e E') + sinteger

    ufloat = pp.Combine(uinteger + pp.Optional('.' + uinteger) + pp.Optional(expon))
    sfloat = pp.Combine(sinteger + pp.Optional('.' + uinteger) + pp.Optional(expon))

    uinteger.set_parse_action(lambda t: int(t[0]))
    sinteger.set_parse_action(lambda t: int(t[0]))
    ufloat.set_parse_action(lambda t: float(t[0]))
    sfloat.set_parse_action(lambda t: float(t[0]))

    vec2 = ('<' + sfloat + pp.Suppress(',')
                + sfloat + '>')
    vec3 = pp.Group(pp.Suppress('<') + sfloat + pp.Suppress(',')
                + sfloat + pp.Suppress(',')
                + sfloat + pp.Suppress('>'))
    vec4 = ('<' + sfloat + pp.Suppress(',')
                + sfloat + pp.Suppress(',')
                + sfloat + pp.Suppress(',')
                + sfloat + '>')
    
    include = ('#' + pp.Keyword('include') + '"' + 'colors.inc' + '"')

    color = pp.Keyword('rgb') + vec3

    # Pigment block, which includes the color rule
    pigment = pp.Keyword('pigment') + pp.Suppress('{') + pp.Keyword('color') + color + pp.Suppress('}')

    # Define the sphere parsing rule, including pigment block
    sphere = pp.Group(pp.Keyword('sphere') + pp.Suppress('{') +
              pp.Group(vec3 + pp.Suppress(',') + ufloat) +
              pp.Optional(pigment) + pp.Suppress('}'))

    light_source = pp.Group(pp.Keyword('light_source') + '{' +
                vec3 + pp.Suppress(',') + pp.Keyword('color') + color + '}')

    parser_basic = vec2 ^ vec3 ^ vec4 ^ sinteger ^ sfloat
    parser_with_include = sphere + light_source

    # Add the include directive to be skipped
    # parser = pp.ZeroOrMore(include_directive) + parser_with_include

    # Set up the parser to ignore include directives and comments
    parser = pp.OneOrMore(parser_with_include).ignore(include_directive).ignore(comment_line)

    return eval(which)


def test_basic_parser():
    tests = ['123',
             '-123',
             '12.34',
             '-12.23',
             '-13.57e5',
             '12.34e34',
             '-12.34e-34',
             '<12.34, -23.34, 34.45>',
             '<-23.34, 34.45>',
             '<12.34, -23.34, 34.45e2, -45.44>']

    for test in tests:
        parser = make_pov_parser('parser_basic')
        print(test, '==>\n    ', parser.parseString(test))


def test_object_parser():
    tests = [ '''
        sphere {
            <0, 0, 0>, 40
            pigment {
                color rgb <1, 1, 0>
            }
        }
        
        light_source {
            <4, 5, -6>, color rgb <1, 1, 1>
        }
        ''']

    for test in tests:
        parser = make_pov_parser()
        print(test, '==>')
        try:
            r = parser.parseString(test)
            print(r)

        except pp.ParseException as err:
            print(err.line)
            print(" " * (err.column - 1) + "^")
            print(err)


def main(args):
    # ~ test_basic_parser()
    test_object_parser()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
