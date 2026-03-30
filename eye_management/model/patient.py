import logging

from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from odoo import http

_logger = logging.getLogger(__name__)


class medical_patient(models.Model):
    _inherit = "medical.patient"

    operation_ids = fields.One2many('patient.operation', 'patient_id')

    def get_patient_name(self):
        '''This method is called from js'''
        return str(self.partner_id.name)

    def open_chart(self):
        patient_brw = self
        patient_name = patient_brw.partner_id
        res_id = self.env['ir.model.data']._xmlid_lookup('eye_management.action_open_eye_chart')[2]
        # print('\n\n\n res_idres_id ', res_id)
        res_id_brw = self.env['ir.actions.client'].browse(res_id)
        dict_act_window = res_id_brw.read([])[0]
        if not dict_act_window.get('params', False):
            dict_act_window.update({'params': {}})

        dict_act_window['params'].update({
            'patient_name': patient_name.name or False,
            'patient_id': patient_brw.id or False,
            'model': 'medical.patient',
            'partner_patient': patient_name.id
        })
        return dict_act_window

    def fetch_patient_eye_operation(self):
        # print("\n\n\nfetch_patient_eye_operation===========",self)
        '''This method is called from js'''
        vals={}
        all_operation = []
        for each in self.operation_ids:
            if not each.state == 'complete':
                treatment_list = []
                for treatment in each.treatment_ids:
                    treatment_dict = {'id': treatment.id, 'name': treatment.name}
                    treatment_list.append(treatment_dict)
                vals = {'db_id': each.id, 'date': each.date, 'patient_id': each.patient_id.id, 'eye': each.eye_type,
                        'part': each.part_type, 'state': each.state, 'treatment_ids': treatment_list}
                all_operation.append(vals)
        return all_operation


class patient_operation(models.Model):
    _name = "patient.operation"
    _description = "Patient Operation"

    partner_patient = False

    date = fields.Date('Date')
    patient_id = fields.Many2one('medical.patient', 'Patient Name')
    part_type = fields.Selection([('corneal', 'Corneal'), ('viterous_body', 'Vitero-Retinal(Viterous Body)'),
                                  ('retina', 'Vitero-Retinal(Retina)'), ('eye_muscle', 'Eye Muscle'),
                                  ('eyelid', 'Eyelid'), ('sceleral', 'Scleral'), ('neural', 'Neural')],
                                 'Type of Surgery')
    eye_type = fields.Selection([('right_eye', 'Right Eye'), ('left_eye', 'Left Eye')], 'Eye')
    state = fields.Selection([('draft', 'Draft'), ('inprogress', 'In Progress'), ('complete', 'Complete')], 'State',
                             default='draft')
    treatment_ids = fields.Many2one('product.product', 'Treatments')
    physician_name = fields.Many2one('medical.physician', 'Physician',
                                     help="Physician who treated or diagnosed the patient")

    def create_patient_eye_operation(self, operation_list):
        vals = {}
        l1_list = []
        product_name = ''
        res_partner_id = False
        operation_list_recs = []
        treatment_ids_list = []
        partner_patient = False
        partner_obj = self.env['res.partner']
        product_obj = self.env['product.product']
        invoice_obj = self.env['account.move']
        invoice_line_obj = self.env['account.move.line']

        for each_operation in operation_list:
            # print("each_operation=====================", )
            doctor_id = self.env['medical.physician'].search([('name', '=', each_operation['physician_name'])]).id
            vals = {
                'patient_id': int(each_operation['patient_id']),
                'part_type': each_operation['part'],
                'eye_type': each_operation['eye'],
                'physician_name': doctor_id,
                'date': each_operation['date'],
                'state': each_operation['state'],
                'treatment_ids': int(each_operation['id']),

            }
            if partner_patient in each_operation:
                partner_patient = each_operation['partner_patient']
                # print("\n calling ------partner_patient--------",partner_patient)
            if each_operation.get('state') == 'complete':
                treatment_ids_list.append(int(each_operation['id']))
                operation_list_recs.append(each_operation)
            record_is_available = False
            if each_operation.get('db_id', False):
                record_is_available = self.env['patient.operation'].search([('id', '=', int(each_operation['db_id']))])
            if record_is_available:
                record_is_available.write({'state': each_operation['state']})
            else:
                operation_id = self.env['patient.operation'].create(vals)
                for treatment in each_operation['id']:
                    product_obj.browse(int(treatment)).write({'product_operation_id': operation_id.id})
                l1_list.append(operation_id)

        # Code added by shoaib for creating invoice based on treatments done having state as complete
        current_date = datetime.now().date()

        invoice_lines = {}
        invoice_line_list = []
        product_account_id = False
        medical_patient_id = self.env['medical.patient'].search([('id', '=', each_operation['patient_id'])])
        invoice = {'partner_id': medical_patient_id.partner_id.id,
                   'doctor_name': medical_patient_id.operation_ids.physician_name.id, 'date': current_date,
                   'move_type': 'out_invoice'}
        invoice_id = invoice_obj.create(invoice)
        # print("\n\n\n\n==============invoicecccccccccccccccccccc",invoice)
        _logger.info("Invoice is created: " + str(invoice_id))
        for treatment_id in treatment_ids_list:
            # fetching price per_unit of product
            product_template_id = product_obj.search([('id', '=', treatment_id)])
            product_name = product_template_id.name
            # code for searching appropriate account id of product
            product_account_id = product_template_id.property_account_income_id.id
            if not product_account_id:
                product_account_id = product_template_id.categ_id.property_account_income_categ_id.id

                if not product_account_id:
                    raise UserError(_("Account not set for " + product_name + "Please set its account to proceed"))
                    return "0"
                else:
                    invoice_lines = {'product_id': treatment_id, 'name': product_name, 'move_id': int(invoice_id),
                                     'price_unit': product_template_id.list_price,
                                     'account_id': product_account_id, 'quantity': 1, }
                    # print("\n\n\ninvoice_lines===========",invoice_lines)

                    invoice_line_list.append(invoice_lines)
                    res = invoice_line_obj.with_context(check_move_validity=False).create(invoice_lines)
            # end of code for searching appropriate account id of product

    def write_patient_eye_operation(self, operation_list):
        patient_oper_obj = self.env['patient.operation']
        for each_operation in operation_list:
            operation_obj = patient_oper_obj.search([('id', '=', int(each_operation['db_id']))])[0]
            operation_obj.write({'state': each_operation['state']})

    def delete_record(self, db_id):
        self.env["patient.operation"].browse(int(db_id)).unlink()


class product(models.Model):
    _inherit = "product.product"

    part_type = fields.Selection([('corneal', 'Corneal'), ('viterous_body', 'Vitero-Retinal(Viterous Body)'),
                                  ('retina', 'Vitero-Retinal(Retina)'), ('eye_muscle', 'Eye Muscle'),
                                  ('eyelid', 'Eyelid'), ('sceleral', 'Scleral'), ('neural', 'Neural')], 'Part Type',
                                #  required=True)
                                )
    product_operation_id = fields.Many2one('patient.operation', 'Patient')

    def get_operation_names(self):
        operations = {}
        product_records = self.env['product.product'].search([('is_treatment', '=', True)])
        for each_brw in product_records:
            operations[each_brw.name] = {
                'id': each_brw.id, 'type': each_brw.part_type}
        return operations
