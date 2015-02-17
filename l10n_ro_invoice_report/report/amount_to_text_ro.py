# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# -------------------------------------------------------------
# ROMANA
# -------------------------------------------------------------

from openerp import _


to_19 = ('zero',  'unu',   'doi',  'trei', 'patru',   'cinci',   'șase',
         'șapte', 'opt', 'nouă', 'zece',   'unsperezece', 'doisprezece', 'treisprezece',
         'paisprezece', 'cincisprezece', 'șiaisprezece', 'șaptesprezece', 'optsprezece', 'nousăprezece')

tens = ('douăzeci', 'treizeci', 'patruzeci', 'cincizeci',
        'șaizeci', 'șaptezeci', 'optzeci', 'nouăzeci')

denom = ('',
         'una mie',     'un milion',         'un miliard',    'un trilion',   'un cataralion',
         'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
         'Decillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
         'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion')

denom_s = ('',
           'mii',     'milione',         'miliarde',       'trilioane',       'catralioane',
           'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
           'Decillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
           'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Novemdecillion', 'Vigintillion')


# convert a value < 100 to Romana.
def _convert_nn_ro(val):
    if val == 1:
        return 'un'
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + ' și ' + to_19[val % 10]
            return dcap

# convert a value < 1000 to romanian, special cased because it is the level that kicks
# off the < 100 special case.  The rest are more general.  This also allows you to
# get strings in the form of 'forty-five hundred' if called directly.


def _convert_nnn_ro(val):
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem == 1:
        word = 'una sută '
    if rem == 2:
        word = 'două sute '
    if rem > 2:
        word = to_19[rem] + ' sute'
        if mod > 0:
            word = word + ' '
    if mod == 1 and rem != 0:
        word = word + 'unu'
    if mod == 1 and rem == 0:
        word = 'una'
    if mod > 1:
        word = word + _convert_nn_ro(mod)
    return word


def romana_number(val):
    if val < 100:
        return _convert_nn_ro(val)
    if val < 1000:
        return _convert_nnn_ro(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l == 1:
                ret = denom[didx]
            else:
                ret = _convert_nnn_ro(l) + ' ' + denom_s[didx]
            if r > 0:
                ret = ret + ' ' + romana_number(r)
            return ret


def amount_to_text_ro(number):
    number = '%.2f' % number
    units_name = 'Lei'
    list = str(number).split('.')
    start_word = romana_number(int(list[0]))
    end_word = romana_number(int(list[1]))
    bani_number = int(list[1])
    bani_name = (bani_number != 1) and 'Bani' or 'Ban'
    final_result = start_word + ' ' + units_name + \
        ' și ' + end_word + ' ' + bani_name

    return final_result
