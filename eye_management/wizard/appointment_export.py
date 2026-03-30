from odoo import _, api, fields, models
from datetime import datetime
import io, base64
from odoo import fields, models, _
from odoo.tools import date_utils
from odoo.exceptions import ValidationError

# from pprint import pprint

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class exportAppointmentWizard(models.TransientModel):
    _name = 'appointment.wizard'
    _description = 'Appointment Wizard'
    # _inherit="report.report_xlsx.abstract"

    name = fields.Char(string="Name", required=True, default="nama file export appointment")
    description = fields.Text(string="Description")
    cabang_ids = fields.Many2many('res.partner', string='cabang', domain=[('is_institution', '=', True)])
    start_time = fields.Datetime('start_time')
    end_time = fields.Datetime('end_time')
    
    def action_export_xlsx(self):
        # print('inini print darii action confirim wisard')
        # file_name = 'test.xlsx'
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        # sheet.set_default_row(19)
        
        header_kolom = ['created_on',
                        'appointment start',
                        'appointment end',
                        'traffic id',
                        'nama pasien',
                        'cabang',
                        'no telp',
                        'status kedatangan',
                        'status by',
                        'race',
                        'tujuan kedatangan',
                        'result',
                        'MyoCheck',
                        'agent yang membuat app',
                        'agent yang menangani',
                        'dokter',
                        'reason v2',
                        'reason',
                        'remarks',
                        ]
        for head_nulis in header_kolom:
            # print(head_nulis, header_kolom.index(head_nulis))
            sheet.write(0, header_kolom.index(head_nulis), head_nulis)
        # data_app = []
        
        # ii = self.env['medical.appointment'].search([('institusion', '=', [cabang.id for cabang in self.cabang_ids]), ('appointment_sdate', '>=', self.start_time), ('appointment_sdate', '<=', self.end_time)])
        data_all_app = self.env['medical.appointment'].search([('institution', 'in', [cabang.id for cabang in self.cabang_ids]), ('appointment_sdate', '>=', self.start_time), ('appointment_sdate', '<=', self.end_time)])
        list_index = 1
        for data in data_all_app:
            sheet.write(list_index, 0, (data.create_date).strftime("%H:%M:%S %d/%m/%Y"))
            sheet.write(list_index, 1, (data.appointment_sdate).strftime("%H:%M:%S %d/%m/%Y"))
            sheet.write(list_index, 2, (data.appointment_edate).strftime("%H:%M:%S %d/%m/%Y"))
            sheet.write(list_index, 3, data.name)
            sheet.write(list_index, 4, data.patient.partner_id.name)
            sheet.write(list_index, 5, data.institution.name)
            sheet.write(list_index, 6, data.no_hp)
            sheet.write(list_index, 7, data.state)
            sheet.write(list_index, 8, data.status_by)
            sheet.write(list_index, 9, data.race_tipe_id.nama)
            sheet.write(list_index, 10, data.tujuan_id.name)
            sheet.write(list_index, 11, data.service_id.name)
            sheet.write(list_index, 12, data.myocheck)
            sheet.write(list_index, 13, data.resolved)
            sheet.write(list_index, 14, ','.join([agent.nama for agent in data.agent_ids]))
            sheet.write(list_index, 15, data.doctor.res_partner_physician_id.name)
            sheet.write(list_index, 16, data.reason_1)
            sheet.write(list_index, 17, data.reason)
            sheet.write(list_index, 18, data.remarks)
            
            list_index+=1
            
    
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment_id = self.env['ir.attachment'].create({
            'name': f'{self.name}.xlsx',
            'store_fname': f'{self.name}.xlsx',
            'datas': result,
            })
        output.close()
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id,),
            'target': 'self',
        }
        return action
        
        
    @api.onchange('start_time')
    def _onchange_start_date(self):
        # start_time = start_time.timedelta(hours=0, minutes=0)
        # print('ini sdatte wizardd ', self.start_time, type(self.start_time))
        if self.start_time != False:
            self.start_time = datetime(self.start_time.year, self.start_time.month, self.start_time.day, 0, 0, 0)
            # print('ini sdatte wizardd ', self.start_time, type(self.start_time))
            
            
    @api.onchange('end_time')
    def _onchange_end_time(self):
        if self.end_time != False:
            self.end_time = datetime(self.end_time.year, self.end_time.month, self.end_time.day, 23, 59, 59)