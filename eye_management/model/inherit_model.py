from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning
# from datetime import timedelta,datetime


class ResUsers(models.Model):
    _inherit='res.users'
    _description = "Res Users"
    
    is_patient = fields.Boolean('Is Patient?')
    is_doctor = fields.Boolean('Is Doctor?')
    
    
    
class ResPartner(models.Model):
    _inherit='res.partner'
    
    
    
    # @api.model
    # def create(self, vals):
    #     return super(ResPartner,self).create(vals)
    
    
class ResComp(models.Model):
    _inherit='res.company'
    
    is_company_khusus = fields.Boolean('is_company_khusus')

class crmLead(models.Model):
    _inherit='crm.lead'

    appointment_ids = fields.One2many('medical.appointment', 'lead_id', string='appointment')
    
    # untuk input multi app dari qontak
    def action_view_appointment(self):
        self.ensure_one()
        # domain = [('room_id','=', self.room_id)]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Traffic',
            'view_mode': 'tree,form',
            'res_model': 'medical.appointment',
            'domain': [('room_id','=', self.room_id)],
            'context': {
                'default_room_id': self.room_id,
                'default_status': 'app_crs'
            }
        }
        
        
class groupsInherit(models.Model):
    _inherit = "res.groups"
    
    is_super_admin_traffic = fields.Boolean('is_super_admin')
    
    
    
    
# class exportAppointmentWizard(models.TransientModel):
#     _name = 'appointment.wizard'
#     _description = 'Appointment Wizard'

#     name = fields.Char(string="Name", required=True)
#     description = fields.Text(string="Description")
#     cabang_ids = fields.Many2many('res.partner', string='cabang', domain=[('is_institution', '=', True)], editable='bottom')
#     start_time = fields.Datetime('start_time')
#     end_time = fields.Datetime('end_time')
#     def action_confirm(self):
#         # Your logic here
#         return {
#             'type': 'ir.actions.act_window_close'
#         }
        
        
#     @api.onchange('start_time')
#     def _onchange_start_date(self):
#         # start_time = start_time.timedelta(hours=0, minutes=0)
#         print('ini sdatte wizardd ', self.start_time, type(self.start_time))
#         self.start_time = datetime(self.start_time.year, self.start_time.month, self.start_time.Day, 0, 0, 0)
#         print('ini sdatte wizardd ', self.start_time, type(self.start_time))