from odoo import tools
from odoo import api, fields, models

class PrescriptionReport(models.AbstractModel):
    _name = 'report.eye.report_prescription'
    _description = 'Prescription Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['medical.prescription.order'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'medical.prescription.order',
            'docs': docs,
            'proforma': True
        }