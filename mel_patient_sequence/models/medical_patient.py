from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    # patient_id = fields.Char('ID', size=64, default=False,
    #                          help="Patient Identifier provided by the Health Center. Is not the patient id from the partner form")
    card_number = fields.Char(string='Card Number')
    # street = fields.Char()
    # street2 = fields.Char()
    zip = fields.Char(change_default=True)
    # city = fields.Char()
    # state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    # country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    home_number = fields.Char(unaccent=False)
    office_number = fields.Char(unaccent=False)
    mobile = fields.Char(unaccent=False)
    # email = fields.Char()
    sales_catergory = fields.Selection(
        [('1', 'Normal'),
         ('2', 'Member'),
         ('3', 'Min SP'),
        ], string='Sales Category',)

    # @api.model
    # def create(self, vals):
        # medical_patient_note = self.env['ir.sequence'].get('medical.patient.sequence')
        # if medical_patient_note:
            # vals['name'] = medical_patient_note
        # print('oooioioio inin create patient')
        # return super(MedicalPatient, self).create(vals)