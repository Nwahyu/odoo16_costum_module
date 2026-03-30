from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    city = fields.Char('(no use)')
    city_id = fields.Many2one("state.city", string='City', ondelete='restrict', domain="[('state_id', '=?', state_id)]")
    district_id = fields.Many2one('state.district', string='district')

    @api.onchange('city_id')
    def get_state_country_id(self):
        self.state_id = self.city_id.state_id
        self.country_id = self.city_id.state_id.country_id
        # print('citytyyy state cityyy')
        
    @api.onchange('district_id')
    def _onchange_(self):
        self.city_id = self.district_id.city_id.id
        # print('dissstciriiiic state disttriccccttt')