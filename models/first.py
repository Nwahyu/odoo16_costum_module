from odoo import _, api, fields, models

class first(models.Model):
    _name = 'base.first'
    _description = 'base.first'
    _rec_name = 'nama'
    
    nama = fields.Char('nama')
    password = fields.Char('password')
    