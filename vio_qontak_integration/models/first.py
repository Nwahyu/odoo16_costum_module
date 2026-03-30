from odoo import _, api, fields, models


class crm_lead_inherit(models.Model):
    _inherit = 'crm.lead'
    _description = 'crm.lead'
    
    room_id = fields.Char('room_id', track_visibility='onchange')
    resolved = fields.Char('Agent CRS')
    kriteria_id = fields.Many2one('tag.kriteria', string='Kriteria')
    solusi_id = fields.Many2one('tag.solusi', string='Solusi')
    race_id = fields.Many2one('tag.race', string='Race')
    tujuan_id = fields.Many2one('product.product', string='tujuan')
    # appointment_ids = fields.One2many('medical.appointment', 'lead_id', string='appointment')
    # line_ids = fields.One2many(comodel_name='store.order.line', inverse_name='order_id', string='Line')

    
    
    
    @api.onchange('kriteria_id')
    def change_stage(self):
        self.stage_id = self.kriteria_id.stage_id.id