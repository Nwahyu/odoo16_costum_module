# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import logging
from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.exceptions import UserError
from psycopg2 import IntegrityError
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

class StateCity(models.Model):
    _description = "State City"
    _name = 'state.city'
    _order = 'code'

    state_id = fields.Many2one('res.country.state', string='State', required=True)
    name = fields.Char(string='City Name', required=True, help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')
    code = fields.Char(string='City Code', help='The state code.', required=True)
    district_ids = fields.One2many('state.district', 'city_id', string='district')
    
    
    
class district(models.Model):
    _name = 'state.district'
    
    name = fields.Char('District Name')
    code = fields.Char('code')
    city_id = fields.Many2one('state.city', string='city')