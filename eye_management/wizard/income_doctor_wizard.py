# -*- coding: utf-8 -*-
import time
from odoo import fields, models, api,_
from odoo.exceptions import UserError

class income_by_doctor_report_wizard(models.TransientModel):
    _name='income.by.doctor.report.wizard'
    _description = "Invoice By Doctor WiZard"
   
    start_date = fields.Date('Start Date',required=True)
    end_date = fields.Date('End Date',required=True)
    
    def income_by_doctor_report(self):
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('eye_management.income_byreport_report').report_action(self, data=data)



