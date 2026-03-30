from odoo import _, api, fields, models

class res_users(models.Model):
    _inherit = 'res.users'
    _description = 'res.users desc'
    
    
    physician_id = fields.Many2one('medical.physician', string='physician')