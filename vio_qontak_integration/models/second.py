from odoo import models, fields, api, _
from odoo.exceptions import UserError

class result(models.Model):
    _name = 'tag.tujuan.kedatangan'

    name = fields.Char(string='nama')