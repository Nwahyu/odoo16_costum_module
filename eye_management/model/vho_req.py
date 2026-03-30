from odoo import _, api, fields, models

class roadshow(models.Model):
    _name = 'roadshow'
    _description = 'road_show'
    _rec_name = 'nama'
    
    
    nama = fields.Char('nama')
    tipe_data = fields.Selection([
        ('hari', 'Hari'),
        ('roadshow', 'Roadshow'),
    ], string='Hari / Roadshow', default='roadshow')