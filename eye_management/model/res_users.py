# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit='res.users'
    _description = "Res Users"
    
    is_patient = fields.Boolean('Is Patient?')
    is_doctor = fields.Boolean('Is Doctor?')