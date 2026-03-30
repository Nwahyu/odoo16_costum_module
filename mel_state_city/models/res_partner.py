from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_lab = fields.Boolean(string='Lab')
    city_id = fields.Many2one("state.city", string='City', ondelete='restrict', domain="[('state_id', '=?', state_id)]")
    district_id = fields.Many2one('state.district', string='district', domain="[('city_id', '=?', city_id )]")