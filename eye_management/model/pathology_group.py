from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import base64
import odoo.addons.decimal_precision as dp
import time


class MedicalPathology(models.Model):

    _name = 'medical.pathology.group'
    _description = 'Medical Pathology Group'

    name = fields.Char(
        string='Name', size=128, help='Group name'
    )
    code = fields.Char('Code', size=128,
                       help='for example MDG6 code will contain the Millennium Development'
                            ' Goals # 6 diseases : Tuberculosis, Malaria and HIV/AIDS')
    desc = fields.Char('Short Description', size=128)
    info = fields.Text('Detailed information')
