from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime, date

# class program(models.Model):
#     _name = 'aff.program'

#     name = fields.Char(string='Nama Program')
#     rate = fields.Float('rate')
#     active = fields.Boolean('active', default=False)
#     traffic_ids = fields.One2many('aff.traffic', 'program_id', string='traffic')

#     @api.onchange('active')
#     def _onchange_active(self):
#         if len( self.env['aff.program'].serach([('active','=',True)]) ) > 1:
#             raise UserError('ada lebih dari satu program yang aktif')

# class traffic(models.Model):
#     _name = 'aff.traffic'

#     name = fields.Char(string='Nama traffic')
#     program_id = fields.Many2one('aff.program', string='program')
    
    
    
    
class ip_record(models.Model):
    _name = 'aff.ip.record'
    _rec_name = 'token'
    
    token = fields.Char('token')
    ip = fields.Char('ip')
    date_access = fields.Date('date_access', default=fields.Date.today())
    
    
    def clear_record(self):
        for _ in self.env['aff.ip.record'].search([]) :
            # print(_.date_access, type(_.date_access))
            # print( datetime.today().date()-timedelta(days=8), type( datetime.today().date()-timedelta(days=8) ))
            if _.date_access < datetime.today().date()-timedelta(days=8) :
                # hapus ip record > 8 hari
                super(ip_record, _).unlink()
                # print('suskses diapuusss coy')
                
    