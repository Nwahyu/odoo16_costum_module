from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import base64
import odoo.addons.decimal_precision as dp
import time, logging, re
from calendar import monthrange
# from datetime import timedelta
_logger = logging.getLogger(__name__)


# def timer_decorator(some_function):
#     def wrapper(*args, **kwargs):
#         t1 = time.time()
#         result = some_function(*args, **kwargs)
#         elapsed_time = time.time() - t1
#         print(f"Elapsed time: {elapsed_time:.6f} seconds")
#         return result

#     return wrapper


class insurance_plan(models.Model):
    _name = "medical.insurance.plan"
    _description = "Medical Insurance Plan"

    name = fields.Char(related='product_medical_insurance_plan_id.name')
    product_medical_insurance_plan_id = fields.Many2one('product.product', 'Plan', domain=[('type', '=', 'service'), (
    'is_insurance_plan', '=', True)], help='Insurance company plan')
    company = fields.Many2one('res.partner', 'Insurance Company', domain=[('is_insurance_company', '=', "1")])
    is_default = fields.Boolean('Default plan',
                                help='Check if this is the default plan when assigning this insurance company to a patient')
    notes = fields.Text('Extra info')


class insurance(models.Model):

    def name_get(self):
        if not len(self):
            return []
        reads = self.read(['number', 'company'])
        res = []
        for record in reads:
            name = record['number']
            if record['company']:
                name = record['company'][1] + ': ' + name
            res.append((record['id'], name))
        return res

    _name = "medical.insurance"
    _description = "Medical Insurance"

    name = fields.Char(related="res_partner_insurance_id.name")
    res_partner_insurance_id = fields.Many2one('res.partner', 'Owner')
    number = fields.Char('Number', size=64, required=True)
    company = fields.Many2one('res.partner', 'Insurance Company', domain=[('is_insurance_company', '=', "1")],
                              required=True, )
    member_since = fields.Date('Member since')
    member_exp = fields.Date('Expiration date')
    category = fields.Char('Category', size=64, help="Insurance company plan / category")
    type = fields.Selection([('state', 'State'), ('labour_union', 'Labour Union / Syndical')], 'Insurance Type')
    notes = fields.Text('Extra Info')
    plan_id = fields.Many2one('medical.insurance.plan', 'Plan', help='Insurance company plan')


class partner_patient(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner']

    date = fields.Date('Partner since', help="Date of activation of the partner or patient")
    ref = fields.Char('ID Number')
    is_person = fields.Boolean('Person', help="Check if the partner is a person.")
    is_patient = fields.Boolean('Patient', help="Check if the partner is a patient")
    is_doctor = fields.Boolean('Doctor', help="Check if the partner is a doctor")
    is_institution = fields.Boolean('Institution', help="Check if the partner is a Medical Center")
    is_insurance_company = fields.Boolean('Insurance Company', help="Check if the partner is a Insurance Company")
    is_pharmacy = fields.Boolean('Pharmacy', help="Check if the partner is a Pharmacy")
    lastname = fields.Char('Last Name', size=128, help="Last Name")
    insurance = fields.One2many('medical.insurance', 'company', "Insurance")

    _sql_constraints = [
        ('ref_uniq', 'unique (ref)', 'The partner or patient code must be unique')
    ]

    @api.depends('name', 'lastname')
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name
            if partner.lastname:
                name = partner.lastname + ', ' + name
            result.append((partner.id, name))
        return result
    
    @api.onchange('company_type')
    def _onchange_company_type(self):
        if self.company_type == 'person':
            self.is_patient = True
            self.is_person = True
        else:
            self.is_patient = False
            self.is_person = False


class product_medical(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    is_medicament = fields.Boolean('Medicament', help="Check if the product is a medicament")
    is_insurance_plan = fields.Boolean('Insurance Plan', help='Check if the product is an insurance plan')
    is_treatment = fields.Boolean('Treatment', help="Check if the product is a Treatment")
    is_tujuan = fields.Boolean('Tujuan Kedatangan')
    is_result = fields.Boolean('Result Kedatangan')
    is_reasoning = fields.Boolean('is_reasoning')


class pathology_category(models.Model):

    def name_get(self):
        if not len(self):
            return []
        reads = self.read(['name', 'parent_id'])
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self):
        res = self.name_get()
        return dict(res)

    def _check_recursion(self):
        level = 100
        ids = [x.id for x in self]
        while len(ids):
            self._cr.execute('select distinct parent_id from medical_pathology_category where id in (' + ','.join(
                map(str, ids)) + ')')
            ids = filter(None, list(map(lambda x: x[0], self._cr.fetchall())))
            if not level:
                return False
            level -= 1
        return True

    _description = 'Disease Categories'
    _name = 'medical.pathology.category'

    _order = 'parent_id,id'

    name = fields.Char('Category Name', required=True, size=128)
    parent_id = fields.Many2one('medical.pathology.category', 'Parent Category', )
    complete_name = fields.Char(compute='_name_get_fnc', string='Name')
    child_ids = fields.One2many('medical.pathology.category', 'parent_id', 'Children Category')
    active = fields.Boolean('Active', default=lambda *a: 1)

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]


class pathology(models.Model):
    _name = "medical.pathology"
    _description = "Diseases"

    name = fields.Char('Name', required=True, size=128, help="Disease name")
    code = fields.Char('Code', size=32, required=True, help="Specific Code for the Disease (eg, ICD-10, SNOMED...)")
    category = fields.Many2one('medical.pathology.category', 'Disease Category')
    chromosome = fields.Char('Affected Chromosome', size=128, help="chromosome number")
    protein = fields.Char('Protein involved', size=128, help="Name of the protein(s) affected")
    gene = fields.Char('Gene', size=128, help="Name of the gene(s) affected")
    info = fields.Text('Extra Info')
    line_ids = fields.One2many('medical.pathology.group.member', 'name',
                               'Groups', help='Specify the groups this pathology belongs. Some'
                                              ' automated processes act upon the code of the group')

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The disease code must be unique')]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        args2 = args[:]
        if name:
            args += [('name', operator, name)]
            args2 += [('code', operator, name)]
        ids = self.search(args, limit=limit)
        ids += self.search(args2, limit=limit)
        res = ids.name_get()
        return res


class pathology_group_member(models.Model):
    _description = 'Pathology Group Member'
    _name = 'medical.pathology.group.member'

    name = fields.Many2one('medical.pathology', 'Disease', readonly=True)
    disease_group = fields.Many2one('medical.pathology.group', 'Group')


# MEDICATION TEMPLATE
# TEMPLATE USED IN MEDICATION AND PRESCRIPTION ORDERS


class medication_template(models.Model):
    _name = "medical.medication.template"
    _description = "Template for medication"

    medicament = fields.Many2one('medical.medicament', 'Medicament', help="Prescribed Medicament", required=True)
    indication = fields.Many2one('medical.pathology', 'Indication',
                                 help="Choose a disease for this medicament from the disease list. It can be an existing disease of the patient or a prophylactic.")
    dose = fields.Float('Dose', help="Amount of medication (eg, 250 mg ) each time the patient takes it")
    dose_unit = fields.Many2one('medical.dose.unit', 'dose unit', help="Unit of measure for the medication to be taken")
    route = fields.Many2one('medical.drug.route', 'Administration Route',
                            help="HL7 or other standard drug administration route code.")
    form = fields.Many2one('medical.drug.form', 'Form', help="Drug form, such as tablet or gel")
    qty = fields.Integer('x', help="Quantity of units (eg, 2 capsules) of the medicament")
    common_dosage = fields.Many2one('medical.medication.dosage', 'Frequency',
                                    help="Common / standard dosage frequency for this medicament")
    frequency = fields.Integer('Frequency',
                               help="Time in between doses the patient must wait (ie, for 1 pill each 8 hours, put here 8 and select 'hours' in the unit field")
    frequency_unit = fields.Selection([
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('wr', 'when required'),
    ], 'unit', )
    admin_times = fields.Char('Admin hours', size=128,
                              help='Suggested administration hours. For example, at 08:00, 13:00 and 18:00 can be encoded like 08 13 18')
    duration = fields.Integer('Treatment duration',
                              help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately")
    duration_period = fields.Selection(
        [('minutes', 'minutes'), ('hours', 'hours'), ('days', 'days'), ('months', 'months'), ('years', 'years'),
         ('indefinite', 'indefinite'), ], 'Treatment period',
        help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately")
    start_treatment = fields.Datetime('Start of treatment')
    end_treatment = fields.Datetime('End of treatment')

    _sql_constraints = [
        ('dates_check', "CHECK (start_treatment < end_treatment)",
         "Treatment Star Date must be before Treatment End Date !"),
    ]


class medicament_category(models.Model):

    def name_get(self):
        if not len(self):
            return []
        reads = self.read(['name', 'parent_id'])
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self):
        res = self.name_get()
        return dict(res)

    def _check_recursion(self):
        level = 100
        ids = [x.id for x in self]
        while len(ids):
            self._cr.execute('select distinct parent_id from medical_pathology_category where id in (' + ','.join(
                map(str, ids)) + ')')
            ids = list(filter(None, map(lambda x: x[0], self._cr.fetchall())))
            if not level:
                return False
            level -= 1
        return True

    _description = 'Medicament Categories'
    _name = 'medicament.category'

    _order = 'parent_id,id'

    name = fields.Char('Category Name', required=True, size=128)
    parent_id = fields.Many2one('medicament.category', 'Parent Category')
    complete_name = fields.Char(compute='_name_get_fnc', string='Name')
    child_ids = fields.One2many('medicament.category', 'parent_id', 'Children Category')

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]


class medicament(models.Model):
    _name = "medical.medicament"
    _description = "Medical Medicament"

    name = fields.Char(related="product_medicament_id.name")
    product_medicament_id = fields.Many2one('product.product', 'Name', required=True,
                                            domain=[('is_medicament', '=', "1")], help="Commercial Name")
    category = fields.Many2one('medicament.category', 'Category')
    active_component = fields.Char('Active component', size=128, help="Active Component")
    therapeutic_action = fields.Char('Therapeutic effect', size=128, help="Therapeutic action")
    composition = fields.Text('Composition', help="Components")
    indications = fields.Text('Indication', help="Indications")
    dosage = fields.Text('Dosage Instructions', help="Dosage / Indications")
    overdosage = fields.Text('Overdosage', help="Overdosage")
    pregnancy_warning = fields.Boolean('Pregnancy Warning',
                                       help="Check when the drug can not be taken during pregnancy or lactancy")
    pregnancy = fields.Text('Pregnancy and Lactancy', help="Warnings for Pregnant Women")
    presentation = fields.Text('Presentation', help="Packaging")
    adverse_reaction = fields.Text('Adverse Reactions')
    storage = fields.Text('Storage Conditions')
    price = fields.Float(related='product_medicament_id.lst_price', string='Price')
    qty_available = fields.Float(string='Quantity Available')
    notes = fields.Text('Extra Info')
    pregnancy_category = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('X', 'X'), ('N', 'N')],
                                          'Pregnancy Category',
                                          help='** FDA Pregancy Categories ***\n'
                                               'CATEGORY A :Adequate and well-controlled human studies have failed'
                                               ' to demonstrate a risk to the fetus in the first trimester of'
                                               ' pregnancy (and there is no evidence of risk in later'
                                               ' trimesters).\n\n'
                                               'CATEGORY B : Animal reproduction studies have failed todemonstrate a'
                                               ' risk to the fetus and there are no adequate and well-controlled'
                                               ' studies in pregnant women OR Animal studies have shown an adverse'
                                               ' effect, but adequate and well-controlled studies in pregnant women'
                                               ' have failed to demonstrate a risk to the fetus in any'
                                               ' trimester.\n\n'
                                               'CATEGORY C : Animal reproduction studies have shown an adverse'
                                               ' effect on the fetus and there are no adequate and well-controlled'
                                               ' studies in humans, but potential benefits may warrant use of the'
                                               ' drug in pregnant women despite potential risks. \n\n '
                                               'CATEGORY D : There is positive evidence of human fetal  risk based'
                                               ' on adverse reaction data from investigational or marketing'
                                               ' experience or studies in humans, but potential benefits may warrant'
                                               ' use of the drug in pregnant women despite potential risks.\n\n'
                                               'CATEGORY X : Studies in animals or humans have demonstrated fetal'
                                               ' abnormalities and/or there is positive evidence of human fetal risk'
                                               ' based on adverse reaction data from investigational or marketing'
                                               ' experience, and the risks involved in use of the drug in pregnant'
                                               ' women clearly outweigh potential benefits.\n\n'
                                               'CATEGORY N : Not yet classified')


class speciality(models.Model):
    _name = "medical.speciality"
    _description = "Medical Specialty"

    name = fields.Char('Description', size=128, required=True, help="ie, Addiction Psychiatry")
    code = fields.Char('Code', size=128, help="ie, ADP")

    _sql_constraints = [
        ('code_uniq', 'unique (product_medicament_id)', 'The Medical Specialty code must be unique')]


class physician(models.Model):
    _name = "medical.physician"
    _description = "Information about the doctor"

    name = fields.Char(related="res_partner_physician_id.name")
    res_partner_physician_id = fields.Many2one('res.partner', 'Physician', required=True,
                                               domain=[('is_doctor', '=', "1"), ('is_person', '=', "1")],
                                               help="Physician's Name, from the partner list")
    institution = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', "1")],
                                  help="Institution where she/he works")
    
    institution_ids = fields.Many2many('res.partner', string='institution', domain=[('is_institution', '=', "1")])
    code = fields.Char('ID', size=128, help="MD License ID")
    speciality = fields.Many2one('medical.speciality', 'Specialty', required=True, help="Specialty Code")
    info = fields.Text('Extra info')
    ssn = fields.Char('SSN', size=128, required=True)
    user_id = fields.Many2one('res.partner', string='Physician User', store=True)
    email = fields.Char('Email')
    mobile = fields.Char('Mobile')
    slot_ids = fields.One2many('doctor.slot', 'doctor_id', 'Availabilities', copy=True)


class family_code(models.Model):
    _name = "medical.family_code"
    _description = "medical family code"

    name = fields.Char(related="res_partner_family_medical_id.name")
    res_partner_family_medical_id = fields.Many2one('res.partner', 'Name', required=True,
                                                    help="Family code within an operational sector")
    members_ids = fields.Many2many('res.partner', 'family_members_rel', 'family_id', 'members_id', 'Members',
                                   domain=[('is_person', '=', "1")])
    info = fields.Text('Extra Information')


class patient_data(models.Model):

    # def name_get(self):
    #     if not len(self):
    #         return []

    #     def _name_get(d):
    #         name = d.get('partner_id', '')
    #         id = d.get('patient_id', False)
    #         # print('iiiiiiniiiii datatata namemme')
    #         if id:
    #             name = '[%s] %s' % (id, name[1])
    #             print(name)
    #         return (d['id'], name)

    #     # nyatuin id_pat n name
    #     # force if (dibikin null)
    #     result = list(map(_name_get, self.read(['partner_id', 'patient_id'])))
    #     # result = list(map(_name_get, self.read(['partner_id', 'patient_id']))) if list(map(_name_get, self.read(['partner_id', 'patient_id']))) else ()
    #     return result

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=80):
    #     if not args:
    #         args = []
    #     if name:
    #         ids = self.search([('patient_id', '=', name)] + args, limit=limit)
    #         if not len(ids):
    #             ids += self.search([('partner_id', operator, name)] + args, limit=limit)
    #     else:
    #         ids = self.search(args, limit=limit)
    #     result = ids.name_get()
    #     return result


    def name_get(self):
        res = []
        if not len(self):
            return res
        for rec in self:
            res.append((rec.id, f"{rec.partner_id.name}"))
        return res
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        if not args:
            args = []
        if name:
            args += ['|', '|', ('partner_id', operator, name), ('no_hp', operator, name), ('patient_id', operator, name)]
        ids = self.search(args, limit=limit)
        result = ids.name_get()
        # print('ini masuk', name, args, result)
        return result


    @api.onchange('dob')
    def onchange_dob(self):
        c_date = datetime.today().strftime('%Y-%m-%d')
        if self.dob:
            if (str(self.dob) <= c_date):
                self.dob = self.dob
            else:
                raise UserError('Birthdate cannot be After Current Date')

    # Automatically assign the family code
    @api.onchange('partner_id')
    def onchange_partnerid(self):
        if self.partner_id:
            self._cr.execute('select family_id from family_members_rel where members_id=%s limit 1',
                             (self.partner_id.id,))
            a = self._cr.fetchone()
            if a:
                self.family_code = a[0]
            else:
                self.family_code = False
        else:
            self.family_code = False

    # Get the patient age in the following format : "YEARS MONTHS DAYS"
    # It will calculate the age of the patient while the patient is alive. When the patient dies, it will show the age at time of death.

    def _patient_age(self):

        def compute_age_from_dates(patient_dob, patient_deceased, patient_dod):
            now = datetime.now()
            if (patient_dob):
                dob = datetime.strptime(str(patient_dob), '%Y-%m-%d')
                if patient_deceased:
                    dod = datetime.strptime(str(patient_dod), '%Y-%m-%d %H:%M:%S')
                    delta = relativedelta(dod, dob)
                    deceased = " (deceased)"
                else:
                    delta = relativedelta(now, dob)
                    deceased = ''
                years_months_days = str(delta.years) + "y " + str(delta.months) + "m " + str(
                    delta.days) + "d" + deceased
            else:
                years_months_days = "No DoB !"
            return years_months_days

        for patient in self:
            patient.age = compute_age_from_dates(patient.dob, patient.deceased, patient.dod)

    _name = "medical.patient"
    _description = "Patient related information"
    _rec_name = "partner_id"

    partner_id = fields.Many2one('res.partner', 'Patient', domain=[('is_patient', '=', True), ('is_person', '=', True)],
                                 help="Patient Name")
    nama = fields.Char('nama')
    patient_id = fields.Char('ID', default=lambda self: _("New Patient"))
    # patient_id = fields.Char('ID', size=64, default=lambda obj: obj.env['ir.sequence'].get('medical.patient'),
    #                          help="Patient Identifier provided by the Health Center. Is not the patient id from the partner form")
    nik = fields.Char('NIK', size=128)
    lastname = fields.Char(related='partner_id.lastname', string='Lastname')
    family_code = fields.Many2one('medical.family_code', 'Family', help="Family Code")
    identifier = fields.Char(related='partner_id.ref', string='NIK Identifier', help="Social Security Number or National ID")
    current_insurance = fields.Many2one('medical.insurance', "Insurance", domain="[('name','=',partner_id)]",
                                        help="Insurance information. You may choose from the different insurances belonging to the patient")
    sec_insurance = fields.Many2one('medical.insurance', "Insurance", domain="[('partner_id','=',partner_id)]",
                                    help="Insurance information. You may choose from the different insurances belonging to the patient")
    image_128 = fields.Image(related="partner_id.image_1024", string="Photo", store=True, readonly=False)
    dob = fields.Date('Date of Birth')
    age = fields.Char(compute='_patient_age', size=32, string='Patient Age',
                      help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female'), ], 'Gender', )
    no_hp = fields.Char('Nomor Telepon', unaccent=False, default=lambda self: _('62'))
    race_id = fields.Many2one('tag.race.tipe', string='race')

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char()
    
    marital_status = fields.Selection(
        [('s', 'Single'), ('m', 'Married'), ('w', 'Widowed'), ('d', 'Divorced'), ('x', 'Separated'), ],
        'Marital Status')
    blood_type = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ], 'Blood Type')
    rh = fields.Selection([('+', '+'), ('-', '-'), ], 'Rh')
    user_id = fields.Many2one(related='partner_id.user_id', string='Doctor',
                              help="Physician that logs in the local Medical system (HIS), on the health center. It doesn't necesarily has do be the same as the Primary Care doctor",
                              store=True)
    medications = fields.One2many('medical.patient.medication', 'name', 'Medications')
    prescriptions = fields.One2many('medical.prescription.order', 'patient_id', "Prescriptions")
    diseases_ids = fields.One2many('medical.patient.disease', 'name', 'Diseases')
    critical_info = fields.Text('Important disease, allergy or procedures information',
                                help="Write any important information on the patient's disease, surgeries, allergies, ...")
    general_info = fields.Text('General Information', help="General information about the patient")
    deceased = fields.Boolean('Deceased', help="Mark if the patient has died")
    dod = fields.Datetime('Date of Death')
    apt_id = fields.Many2many('medical.appointment', 'pat_apt_rel', 'patient', 'apid', 'Appointments')
    attachment_ids = fields.One2many('ir.attachment', 'patient_id', 'attachments')
    assistant_doctor_details_ids = fields.One2many('assistant.doctor.details', 'patient_id', 'Readings')
    invoice_count = fields.Integer(compute='compute_count')
    
    is_reff_race = fields.Boolean('is_reff_race')
    kode_reff = fields.Text('kode_reff')
    after_trx = fields.Boolean('after_trx', default=False)
    
    @api.onchange('race_id')
    def _onchange_reff_race(self):
        if self.race_id.is_reff :
            self.is_reff_race = True
        else: self.is_reff_race = False
    
    @api.onchange('deceased')
    def _onchange_deceased(self):
        # self.dod = datetime.today().strftime('%m-%d-%Y %h:%m:00')
        self.dod = datetime.today().strftime('%Y-%m-%d %H:%M:00')

    def compute_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('partner_id', '=', self.partner_id.id),('move_type', '!=','entry' )])

    def get_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('partner_id', '=', self.partner_id.id), ('move_type', '!=','entry' )],
            'context': "{'create': False}"
        }

    _sql_constraints = [
        ('name_uniq', 'unique (partner_id)', 'The Patient already exists'),
        ('ssn_uniq', 'unique (ssn)', 'The Patient SSN already exists')]

    def get_physician_name(self):
        '''This method is called from js'''
        if self.apt_id and self.apt_id[0].doctor.name:
            return str(self.apt_id[0].doctor.name)

    @api.model
    def create(self, vals):
        c_date = datetime.today().strftime('%Y-%m-%d')
        if vals.get('dob', False):
            if (vals.get('dob') > c_date):
                raise UserError(('Birthdate cannot be After Current Date'))
                
        # pat_sequence = self.env['ir.sequence'].next_by_code('medical.patient')
        # vals['patient_id'] = self.env['ir.sequence'].next_by_code('medical.patient.all')
            
        ini_resnya = self.env['res.partner'].sudo().create({
            'name':vals['nama'],
            'is_patient': 1,
            'is_person': 1,
            'company_type': 0
        })
        
        vals['patient_id'] = "no trx"
        vals['partner_id'] = ini_resnya.id
        # print('aaaaaaaaaaaaaaa ini dari creaet patin di eye', vals['patient_id'])
        return super(patient_data, self).create(vals)
    
    
    def write(self, vals):
        if 'after_trx' in vals:
            if vals['after_trx'] == True :
                vals['patient_id'] = self.env['ir.sequence'].next_by_code('medical.patient')
            # print('inii selefff writee',vals['patient_id'])
            else: vals['patient_id'] = 'no trx'
            
        if 'nama' in vals:
            self.partner_id.write({
                'name': vals['nama']
            })
        return super().write(vals)
    
    @api.onchange('no_hp')
    def _onchange_no_hp(self):
        # return re.sub(r'[^0-9]', '', self.no_hp)
        p = []
        nom = ['0','1','2','3','4','5','6','7','8','9']
        idx = 0
        for ini in self.no_hp:
            if idx == 0 and ini == '0':
                p.append('62')
            elif idx == 2 and ini == '0':
                pass
            elif ini in nom:
                p.append(ini)
            idx += 1
        k = ''.join(p) 
        self.no_hp = k

# PATIENT DISESASES INFORMATION
class patient_disease_info(models.Model):

    def name_get(self):
        if not len(self):
            return []
        rec_name = 'pathology'
        res = [(r['id'], r[rec_name][1]) for r in self.read([rec_name])]
        return res

    _name = "medical.patient.disease"
    _description = "Disease info"

    _order = 'is_active desc, disease_severity desc, is_infectious desc, is_allergy desc, diagnosed_date desc'

    name = fields.Many2one('medical.patient', 'Patient ID', readonly=True)
    pathology = fields.Many2one('medical.pathology', 'Disease', help="Disease")
    disease_severity = fields.Selection([('1_mi', 'Mild'), ('2_mo', 'Moderate'), ('3_sv', 'Severe'), ], 'Severity')
    is_on_treatment = fields.Boolean('Currently on Treatment')
    is_infectious = fields.Boolean('Infectious Disease',
                                   help="Check if the patient has an infectious / transmissible disease")
    short_comment = fields.Char('Remarks', size=128,
                                help="Brief, one-line remark of the disease. Longer description will go on the Extra info field")
    doctor = fields.Many2one('medical.physician', 'Physician', help="Physician who treated or diagnosed the patient")
    diagnosed_date = fields.Date('Date of Diagnosis')
    healed_date = fields.Date('Healed')
    is_active = fields.Boolean('Active disease', default=lambda *a: True)
    age = fields.Integer('Age when diagnosed', help='Patient age at the moment of the diagnosis. Can be estimative')
    pregnancy_warning = fields.Boolean('Pregnancy warning')
    weeks_of_pregnancy = fields.Integer('Contracted in pregnancy week #')
    is_allergy = fields.Boolean('Allergic Disease')
    allergy_type = fields.Selection(
        [('da', 'Drug Allergy'), ('fa', 'Food Allergy'), ('ma', 'Misc Allergy'), ('mc', 'Misc Contraindication'), ],
        'Allergy type', index=True)
    treatment_description = fields.Char('Treatment Description', size=128)
    date_start_treatment = fields.Date('Start of treatment')
    date_stop_treatment = fields.Date('End of treatment')
    status = fields.Selection(
        [('c', 'chronic'), ('s', 'status quo'), ('h', 'healed'), ('i', 'improving'), ('w', 'worsening'), ],
        'Status of the disease', )
    extra_info = fields.Text('Extra Info')

    _sql_constraints = [
        ('validate_disease_period', "CHECK (diagnosed_date < healed_date )",
         "DIAGNOSED Date must be before HEALED Date !"),
        ('end_treatment_date_before_start', "CHECK (date_start_treatment < date_stop_treatment )",
         "Treatment start Date must be before Treatment end Date !")
    ]


class medical_dose(models.Model):
    _name = "medical.dose.unit"
    _description = "Medical Dose Unit"

    name = fields.Char('Unit', size=32, required=True, )
    desc = fields.Char('Description', size=64)

    _sql_constraints = [
        ('dose_name_uniq', 'unique(name)', 'The Unit must be unique !'),
    ]


class medical_drug_route(models.Model):
    _name = "medical.drug.route"
    _description = "Medical Drug Route"

    name = fields.Char('Route', size=64, required=True)
    code = fields.Char('Code', size=32)

    _sql_constraints = [
        ('route_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]


class medical_drug_form(models.Model):
    _name = "medical.drug.form"
    _description = "Medical Drug Form"

    name = fields.Char('Form', size=64, required=True, )
    code = fields.Char('Code', size=32)

    _sql_constraints = [
        ('drug_name_uniq', 'unique(name)', 'The Name must be unique !'),
    ]


class medication_dosage(models.Model):
    _name = "medical.medication.dosage"
    _description = "Medicament Common Dosage combinations"

    name = fields.Char('Frequency', size=256, help='Common frequency name', required=True, )
    code = fields.Char('Code', size=64, help='Dosage Code, such as SNOMED, 229798009 = 3 times per day')
    abbreviation = fields.Char('Abbreviation', size=64,
                               help='Dosage abbreviation, such as tid in the US or tds in the UK')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Unit already exists')]


class appointment(models.Model):
    _name = "medical.appointment"
    _description = "Appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _order = "appointment_sdate desc"

    @api.model
    def _get_default_pricelist(self):
        pricelist_id = self.env['product.pricelist'].search([('name', '=', 'Public Pricelist')], limit=1)
        return pricelist_id
    
    @api.model
    def _get_default_institution(self):
        if len(self.env.user.company_ids) > 1:
            return ''
        else:
            return self.env['res.partner'].search([('company_id', '=', self.env.user.company_id[0].id)]).id
    
    @api.model
    def _get_default_status_by(self):
        if len(self.env.user.company_ids) > 1:
            return ''
        else:
            return 'wi'
    
    doctor = fields.Many2one('medical.physician', 'Dokter', help="Dokter yang menangani")
    name = fields.Char('Traffic ID', size=64)
    patient = fields.Many2one('medical.patient', 'Pasien', help="Nama pasien", tracking=True)
    no_hp = fields.Char('Nomor Telepon', related='patient.no_hp')
    appointment_sdate = fields.Datetime('Appointment Start', default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), tracking=True)
    appointment_edate = fields.Datetime('Appointment End', onchange="_onchange_edate_as_sdate")
    institution = fields.Many2one('res.partner', 'Cabang', domain=[('is_institution', '=', "1")],
                                  help="Medical Center", default=_get_default_institution)
                                #   help="Medical Center")
    urgency = fields.Selection([('a', 'Normal'), ('b', 'Urgent'), ('c', 'Medical Emergency'), ], 'Urgency Level',
                               default=lambda *a: 'a')
    comments = fields.Text('Comments')
    no_invoice = fields.Boolean('Invoice exempt')
    validity_status = fields.Selection([('invoiced', 'Invoiced'), ('tobe', 'To be Invoiced')], 'Status', default='tobe',
                                       copy=False)
    # ini apaan
    user_id = fields.Many2one(related='doctor.user_id', string='Physician', store=True)
    
    inv_id = fields.Many2one('account.move', 'Invoice')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Waiting List'),
         ('still_pending', 'In Progress'),
         ('done', 'Done'),
         ('cancel', 'Cancel'),
         ('reschedule', 'Reschedule')], 'Status Kedatangan', default='confirmed', readonly="1", tracking=True)
    apt_id = fields.Boolean(default=False)
    apt_process_ids = fields.Many2many('medical.procedure', 'apt_process_rel', 'appointment_id', 'process_id',
                                       "Initial Treatment")
    service_id = fields.Many2one('product.product', 'Result', domain=[('type', '=', "service"), ('is_result', '=', True)],
                                 help="Result", tracking=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', default=_get_default_pricelist)
    pres_id1 = fields.One2many('medical.prescription.order', 'pid1', 'Prescription')
    assistant_doctor_details_ids = fields.One2many('assistant.doctor.details', 'appointment_id', 'Readings')
    status_by = fields.Selection([
        ('app_crs', 'App by CRS'),
        ('app_ces', 'App by CES'),
        ('app_outlet', 'App by OUTLET'),
        ('app_other', 'App by LAINNYA'),
        ('app_vho', 'App by VHO'),
        ('wi', 'Walk In'),
    ], string='Status By', default=_get_default_status_by,tracking=True)
    
    status = fields.Selection([
        ('app_crs', 'App by CRS'),
        ('app_ces', 'App by CES'),
        ('app_outlet', 'App by OUTLET'),
        ('app_other', 'App by LAINNYA'),
        ('app_vho', 'App by VHO'),
        ('wi', 'Walk In'),
    ], string='Status By', tracking=True)
    
    
    color = fields.Integer('color', default=4)
    myocheck = fields.Boolean('myocheck')
    age = fields.Char('age', related='patient.age')
    
    agent_ids = fields.Many2many('inisial.sales', string='Agent Operation', tracking=True)
    race_tipe_id = fields.Many2one('tag.race.tipe', string='Race', domain="[('is_active', '=', '1')]")
    resolved = fields.Char('Agent Create APP', tracking=True)
    room_id = fields.Char('room_id', readonly=True)
    tujuan_id = fields.Many2one('product.product', string='Tujuan Kedatangan', domain=[('type', '=', "service"), ('is_tujuan','=', True)], required=True, tracking=True)
    # field untuk tampung dari field dari tujuannya
    is_reason_service = fields.Boolean('is_reason_service', related="service_id.is_reasoning")
    is_cabang_khusus = fields.Boolean('is_cabang_khusus', related="institution.company_id.is_company_khusus")
    reason = fields.Text('reason', tracking=1)
    reason_1 = fields.Selection([
        ('resep_kacamata', 'Minta Resep Kacamata'),
        ('resep_buta_warna', 'Minta Resep Buta Warna'),
        ('pikir', 'Pikir-Pikir'),
        ('diskusi_keluarga', 'Diskusi Keluarga'),
        ('rujuk', 'Rujuk'),
        ('penyakit_mata', 'Penyakit Mata'),
        ('kendala_biaya', 'Kendala Biaya'),
        ('emetropia', 'Emetropia (Mata Normal)'),
        ('not_good_candidate', 'Not Good Candidate'),
        ('others', 'Others'),
    ], string='reason v2')
    remarks = fields.Text('remarks', tracking=True)
    is_buatan_qontak = fields.Boolean('is_buatan_qontak')
    is_force = fields.Boolean('paksa buat app', default=False, tracking=True)
    
    # vho
    cust_book = fields.Selection([
        ('book_fee', 'Bayar fee booking'),
        ('no_fee', 'Walk-in roadshow'),
        ('checkup', 'Check Up')
    ], string='Cust book fee')
    
    bukti_trf = fields.Binary('Bukti transfer', tracking=1)
    rek_vio = fields.Selection([
        ('bca', 'BCA 5210 389 441'),
        ('mandiri', 'Mandiri 125 00 0 00 17 079'),
    ], string='Rek Vio', tracking=1)
    tgl_trf = fields.Date('Tanggal transfer')
    nama_rek = fields.Char('Nama rekening pengirim', tracking=1)
    roadshow_id = fields.Many2one('roadshow', string='Roadshow', domain=[('tipe_data', '=', 'roadshow')])
    
    lead_id = fields.Many2one('crm.lead', string='lead asal')
    company_id = fields.Many2one('res.company', string='company', related='institution.company_id')
    is_reschedule = fields.Boolean('is_reschedule')
    
    is_deleted = fields.Boolean('is_deleted', tracking=True)

    _sql_constraints = [
        ('date_check', "CHECK (appointment_sdate <= appointment_edate)",
         "Appointment Start Date must be before Appointment End Date !"),
    ]
    
    # @api.onchange('patient', 'institution')
    @api.onchange('institution')
    def _onchange_list_doctor(self):
        
        weeknya = self.appointment_sdate.weekday()
        jam_msk = (self.appointment_sdate.hour)+7
        cabang = self.env['res.partner'].search([('company_id', '=', self.env.user.company_id.id), ('is_institution', '=', True)]).id
        slot_jadwal = self.env['doctor.slot'].search([('institution_id','=', cabang)])
        #print('slotttt jadwal ', slot_jadwal)
        for _ in slot_jadwal:
            #print(int(_.weekday) ,'==', weeknya ,'and', jam_msk ,'>=', _.start_hour ,'and', jam_msk ,'<', _.end_hour)
            if int(_.weekday) == weeknya and jam_msk >= _.start_hour and jam_msk < _.end_hour:
                _logger.debug(_.doctor_id.id)
                #print('ini dokter', _.doctor_id.id)
                self.doctor = _.doctor_id.id
                break
            else:
                self.doctor = self.env['medical.physician'].search([('name','ilike','Eye Care')]).id
                
                
        return {'domain': {'doctor': ['|', ('institution_ids', 'in', self.institution.id), ('institution_ids', '=', False)]}}
    

    def done(self):
        if self.service_id:
            self.write({'state': 'done',
                        'color': 10})
        else:
            raise ValidationError("Mohon isi RESULT")

    def cancel(self):
        self.write({'state': 'cancel',
                    'color': 9})
        return True

    def confirm(self):
        self.write({'state': 'confirmed',
                    # 'color': 1})
                    'color': 4})
        return True

    def still_pending(self):
        self.write({'state': 'still_pending',
                    'color': 2})
        return True
    
    def draft(self):
        return super(appointment, self).write({'state': 'confirmed',
                                               'color': 4})
        
    @api.onchange('appointment_sdate')
    def _onchange_edate_as_sdate(self):
        self.appointment_sdate = self.appointment_sdate.strftime("%Y-%m-%d %H:%M:00")
        self.appointment_edate = self.appointment_sdate+timedelta(minutes=14, seconds=59)
        
        # print('iiiiiiiiiiiiiiiiiiiiiii jjjjjjjjjjjjjjjjj luar ', self.institution.name, self.appointment_sdate.weekday())
        tanggal_dipilih = self.appointment_sdate+timedelta(hours=7, days=1)  #untuk penyingkronan antara date app dan date jadwal dokter
        # tanggal_dipilih = datetime.now()
        
        slot_jadwal = self.env['doctor.slot'].search([('institution_id','=', self.institution.id)])
        # print('ini slot_jadwal ', slot_jadwal)
        for _ in slot_jadwal:
            # print('iniiiiiiii hari dokter ',_.weekday)
            # print('iiiiiiiiiiiiiiiiiiiiiii jjjjjjjjjjjjjjjjj',_.weekday,   datetime.today().wekday())
            # print('iiiiiiiiiiiiiiiiiiiiiii jjjjjjjjjjjjjjjjj dalam ',_.weekday, tanggal_dipilih.strftime("%y-%m-%d-%H-%M"))
            if int(_.weekday) == tanggal_dipilih.weekday() :
                # print(_.start_hour, type(_.start_hour), float(tanggal_dipilih.strftime("%H"))+(float(tanggal_dipilih.strftime("%M"))/60) )
                if _.start_hour <= float(tanggal_dipilih.strftime("%H"))+(float(tanggal_dipilih.strftime("%M"))/60) and _.end_hour >= float(tanggal_dipilih.strftime("%H"))+(float(tanggal_dipilih.strftime("%M"))/60):
                    self.doctor = _.doctor_id.id
                    # print('inin doctor_id ', _.doctor_id.id)
                    # print('inin doctor_id ', _.doctor_id)
                    break
        else:
            # self.doctor = self.env['medical.physician'].search([('name', '=', 'Eye Care Profesional')]).id
            self.doctor = self.env['medical.physician'].search([('name', 'ilike', 'Eye Care')]).id
            
    
    # @api.constrains('doctor')
    # def _constrain_dokter(self):
    #     jadwal_dokter = self.env['doctor.slot'].search([('doctor_id', '=', self.doctor.id)])
    #     for jadwal in jadwal_dokter:
    #         if int(jadwal.weekday) == self.appointment_sdate.weekday():
    #             if jadwal.start_hour <= float(self.appointment_sdate.strftime('%H'))+(float(self.appointment_sdate.strftime('%M'))/60) and jadwal.end_hour >= float(self.appointment_sdate.strftime('%H'))+(float(self.appointment_sdate.strftime('%M'))/60):
    #                 break
    #     else: raise UserError('dokter diluar jadwal praktek')

    def create_invoices(self):
        """ create invoices for appointment """
        invoice_obj = self.env['account.move']
        invoice_line_obj = self.env['account.move.line']
        for obj in self:
            if obj.state == 'draft':
                raise UserError(_('The appointment is in Draft State.'))
            if obj.no_invoice:
                raise UserError(_('The appointment is invoice exempt.'))
            if obj.state == 'still_pending':
                if obj.validity_status == 'invoiced':
                    raise UserError(_('Appointments is already invoiced.'))
            if obj.state == 'done':
                if obj.validity_status == 'invoiced':
                    raise UserError(_('Appointments is already invoiced.'))
            if obj.validity_status == 'invoiced':
                raise UserError(_('Appointments is already invoiced.'))
            journal_ids = self.env['account.journal'].search(
                [('type', '=', 'sale'), ('company_id', '=', obj.institution.company_id.id)], limit=1)
            if not journal_ids:
                raise UserError(_('Please define sales journal for this company: "%s" (id:%d).') % (
                obj.institution.company_id.name, obj.institution.company_id.id))
            invoice_vals = {
                'name': obj.name,
                'move_type': 'out_invoice',
                'date': obj.appointment_sdate.date(),
                'ref': obj.name,
                'partner_id': obj.patient.partner_id.id,
                'journal_id': journal_ids[0].id or False,
                'invoice_user_id': obj.user_id and obj.user_id.id or False,
                'fiscal_position_id': obj.patient.partner_id.property_account_position_id and obj.patient.partner_id.property_account_position_id.id or False,
                'currency_id': obj.pricelist_id.currency_id.id,
                'doctor_name': obj.doctor.id,
                'invoice_line_ids': []
            }
            # new_invoice_obj = invoice_obj.new(invoice_vals)
            # new_invoice_obj._onchange_journal_id()
            # # new_invoice_obj._onchange_currency()
            # new_invoice_obj._onchange_partner_id()
            product_context = dict(self.env.context, partner_id=obj.patient.partner_id.id, date=obj.appointment_sdate, uom=obj.service_id.uom_id.id)
            final_price, rule_id = obj.pricelist_id.with_context(product_context)._get_product_price_rule(obj.service_id, 1.0)
            in_line_vals = {
                'product_id': obj.service_id.id,
                'name': obj.service_id.name,
                'quantity': 1,
                # 'move_id': new_invoice_obj.id,
                'price_unit': final_price,
                'currency_id': obj.pricelist_id.currency_id.id,
            }
            # inv_line_new = invoice_line_obj.new(in_line_vals)
            # inv_line_new._inverse_product_id()
            # inv_line_new.price_unit = final_price
            # # inv_line_new._onchange_mark_recompute_taxes()
            # inv_line_new._compute_totals()
            # # inv_line_new._get_fields_onchange_balance()
            # new_invoice_obj._onchange_quick_edit_line_ids()
            # account_move_vals = new_invoice_obj._convert_to_write({name: new_invoice_obj[name] for name in new_invoice_obj._cache})
            invoice_vals['invoice_line_ids'].append((0, 0, in_line_vals))
            account_move_rec = self.env['account.move'].create(invoice_vals)
            obj.write({'inv_id': account_move_rec.id, 'validity_status': 'invoiced'})
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def create(self, vals):
        if vals.get('name', '0') == '0':
            history_id = self.env['medical.appointment'].search([('state', 'not in', ['cancel', 'done'] )])
            for data_app in history_id:
                # cek dokter yg sama
                if data_app.doctor.id == vals['doctor']:
                    # cek list app pasien yg non-done di pasien tersebut
                    if data_app.patient.id == vals['patient']:
                        a = vals['is_force'] if 'is_force' in vals else False
                        # dilangsungin filter di search, ga usah di loop
                        len_app_pasien = self.env['medical.appointment'].search_count([('patient', '=', vals['patient']), ('state', 'not in', ['done', 'cancel'])])
                        if len_app_pasien > 0 and a is False:
                            raise UserError('Pasien ini memiliki app yang belum done.')
                        elif len_app_pasien > 5:
                            raise UserError('Pasien ini memiliki app yang belum done. =>' + str(len_app_pasien) + ' (maksimum 5 app).')
                    # ambil company dari cabang, cabang dari def default cabang
                    vals['company_id'] = self.env['res.partner'].search(['&', ('is_institution', '=', 1), ('id', '=', vals['institution'])], limit=1).company_id.id
                    
                    ifif = (data_app.company_id.id == vals['company_id'] and vals['is_buatan_qontak'] is False and data_app.state != 'done') if 'is_buatan_qontak' in vals else data_app.company_id.id == vals['company_id'] and data_app.state != 'done'
                    if ifif:
                        if str(data_app.appointment_sdate) <= vals['appointment_sdate'] and vals[
                            'appointment_edate'] <= str(data_app.appointment_edate):
                            raise UserError('Appointment Tumpang Tindih')

                        if str(data_app.appointment_sdate) <= vals['appointment_sdate'] and str(
                                data_app.appointment_edate) >= vals['appointment_sdate']:
                            raise UserError('Appointment Tumpang Tindih')

                        if str(data_app.appointment_sdate) <= vals['appointment_edate'] and str(
                                data_app.appointment_edate) >= vals['appointment_edate']:
                            raise UserError('Appointment Tumpang Tindih')

                        if str(data_app.appointment_sdate) >= vals['appointment_sdate'] and str(
                                data_app.appointment_edate) <= vals['appointment_edate']:
                            raise UserError('Appointment Tumpang Tindih')

                        if vals['appointment_sdate'] >= vals['appointment_edate']:
                            raise UserError('end appointment lebih awal dari start appointment')
            

            name = self.env['ir.sequence'].get('medical.appointment')
            # name = self.env['ir.sequence'].get('medical.invoice.ol')
            if name:
                vals['name'] = name
            vals['company_id'] = self.env['res.partner'].search(['&', ('is_institution', '=', 1), ('id', '=', vals['institution'])], limit=1).company_id.id
            apt_id = super(appointment, self).create(vals)
            self._cr.execute('insert into pat_apt_rel(patient,apid) values (%s,%s)', (vals['patient'], apt_id.id))
            
            if apt_id.room_id is not False:
                tos = self.env['crm.lead'].search([('room_id', '=', apt_id.room_id)])
                tos.write({
                    'appointment_ids': [(1,apt_id.id,{'lead_id':tos.id})]
                })
            return apt_id
        
        
    def unlink(self):
        # bikin bypass untuk user pic kalo hapus langsung ilang
        for data in self:
            # cek is_deleted dan group admin, langsung apus
            if data.is_deleted or self.env.user.has_group('eye_management.group_admin'):
                super(appointment, data).unlink()
            else: data.write({'is_deleted': True,
                            'state': 'cancel'})
            
        
    def write(self, vals):
        # print('write 1')
        print('prittt inini wrtieee appp')
        if self.state not in ['done','cancel']:
            if 'appointment_sdate' in vals:
                
                
                # cari cara biar bypass yg non-dokter atau semua dokter dikasih jadwal
                # cek dokter yg dipilih didalam jadwal dokter
                jadwal_dokter = self.env['doctor.slot'].search([('doctor_id', '=', vals['doctor'])]) if 'doctor' in vals else self.env['doctor.slot'].search([('doctor_id', '=', self.doctor.id)])
            # jadwal_dokter = self.env['doctor.slot'].search([('doctor_id', '=', vals['doctor'])])
                for jadwal in jadwal_dokter:
                    print('iiiii write deffff ', vals['appointment_sdate'], type(vals['appointment_sdate']), time.strptime(vals['appointment_sdate'],"%Y-%m-%d %H:%M:00"), type(time.strptime(vals['appointment_sdate'],"%Y-%m-%d %H:%M:00")), self.appointment_sdate)
                    aaa = datetime.strptime(vals['appointment_sdate'],"%Y-%m-%d %H:%M:00")
                    jam_mulai = jadwal.start_hour <= float(aaa.hour+7)+float(aaa.minute)/60
                    jam_akhir = jadwal.end_hour > float(aaa.hour+7)+float(aaa.minute)/60
                    # print(aaa, type(aaa))
                    # print(int(jadwal.weekday), aaa.weekday()+1)
                    # print(jadwal.start_hour, float(aaa.hour+7)+float(aaa.minute)/60)
                    # print(jadwal.end_hour , float(aaa.hour+7)+float(aaa.minute)/60)
                    if int(jadwal.weekday) == aaa.weekday()+1:
                        if jam_mulai and jam_akhir:
                            print('ini iiii masukkkk writeeed okterrr')
                            break
                else:
                    # print(jadwal_dokter, type(jadwal_dokter))
                    if len(jadwal_dokter) > 0:
                        raise UserError('dokter diluar jadwal praktek')
                
                # untuk cek tumpang tindih ketika reschdue
                # try: history_id = self.env['medical.appointment'].search([('state', 'not in', ['cancel', 'done']), ('institution', '=', vals['institution']) ]) if 'institution' in vals else self.env['medical.appointment'].search([('state', 'not in', ['cancel', 'done']), ('institution', '=', self.institution.id) ])
                history_id = self.env['medical.appointment'].search([('state', 'not in', ['cancel', 'done']), ('institution', '=', vals['institution']) ]) if 'institution' in vals else self.env['medical.appointment'].search([('state', 'not in', ['cancel', 'done']), ('institution', '=', self.institution.id) ])
                # except: history_id = self.env['medical.appointment'].search([('state', 'not in', ['cancel', 'done']), ('institution', '=', self.institution.id) ])
                
                for data_app in history_id:
                    if str(data_app.appointment_sdate) <= vals['appointment_sdate'] and vals[
                        'appointment_edate'] <= str(data_app.appointment_edate):
                        raise UserError('Appointment Tumpang Tindih')

                    if str(data_app.appointment_sdate) <= vals['appointment_sdate'] and str(
                            data_app.appointment_edate) >= vals['appointment_sdate']:
                        raise UserError('Appointment Tumpang Tindih')

                    if str(data_app.appointment_sdate) <= vals['appointment_edate'] and str(
                            data_app.appointment_edate) >= vals['appointment_edate']:
                        raise UserError('Appointment Tumpang Tindih')

                    if str(data_app.appointment_sdate) >= vals['appointment_sdate'] and str(
                            data_app.appointment_edate) <= vals['appointment_edate']:
                        raise UserError('Appointment Tumpang Tindih')

                    if vals['appointment_sdate'] >= vals['appointment_edate']:
                        raise UserError('end appointment lebih awal dari start appointment')
                
                # print('write 2')
                vals['state'] = 'reschedule'
                vals['is_reschedule'] = True
                vals['color'] = 3
                slot_jadwal = self.env['doctor.slot'].search([('institution_id','=', self.institution.id)])
                for _ in slot_jadwal:
                    # print('iniiiiiiii hari dokter ',_.weekday)
                    # print('iiiiiiiiiiiiiiiiiiiiiii jjjjjjjjjjjjjjjjj slot:',_.weekday, 'app :',self.appointment_sdate.weekday(), type(self.appointment_sdate))
                    # print(vals['appointment_sdate'], '%Y-%m-%d %h:%m:%s', datetime.strptime(vals['appointment_sdate'], '%Y-%m-%d %H:%M:%S'))
                    if int(_.weekday) == (datetime.strptime(vals['appointment_sdate'], '%Y-%m-%d %H:%M:%S').weekday())+1:
                    # if int(_.weekday) == (self.appointment_sdate.weekday()+1 if self.appointment_sdate.weekday()+1  == 7 else 0) :
                        self.doctor = _.doctor_id.id
                        break
                else:
                    self.doctor = self.env['medical.physician'].search([('name', '=', 'Eye Care Profesional')]).id
                
            # # kayak ad yg miss
            # if self.state != 'done' or self.state != 'reschedule':
            #     # cek buat isi agent op
            #     # print('iniii dari agenttt ',self.agent_ids, vals)
            #     if 'state' in vals:
            #         if len(self.agent_ids) < 1 and vals['state'] == 'done':
            #             raise ValidationError('mohon isi Agent Operation')
            #     # print('hairsnnyaaa asukdn ongggg')    
            #     return super(appointment, self).write(vals)
            # else: raise UserError('appointment sudah done')
            
            
            if 'state' in vals:
                if len(self.agent_ids) < 1 and vals['state'] == 'done':
                    raise ValidationError('mohon isi Agent Operation')
            return super(appointment, self).write(vals)
            
        else:
            for grup in self.env.user.groups_id:
                for i in grup:
                    if i.is_super_admin_traffic :
                        return super(appointment, self).write(vals)
                    else: raise UserError('appointment sudah done')
                        

            if 'remarks' in vals:
                try:
                    vals = {'remarks': vals['remarks']}
                except: vals = {}
                return super(appointment, self).write(vals)

class patient_medication(models.Model):
    _name = "medical.patient.medication"
    _inherits = {'medical.medication.template': 'template'}
    _description = "Patient Medication"

    template = fields.Many2one('medical.medication.template', 'Template ID', required=True, ondelete="cascade")
    name = fields.Many2one('medical.patient', 'Patient ID', readonly=True)
    doctor = fields.Many2one('medical.physician', 'Physician', help="Physician who prescribed the medicament")
    is_active = fields.Boolean('Active', default=lambda *a: True,
                               help="Check this option if the patient is currently taking the medication")
    discontinued = fields.Boolean('Discontinued')
    course_completed = fields.Boolean('Course Completed')
    discontinued_reason = fields.Char('Reason for discontinuation', size=128,
                                      help="Short description for discontinuing the treatment")
    adverse_reaction = fields.Text('Adverse Reactions',
                                   help="Specific side effects or adverse reactions that the patient experienced")
    notes = fields.Text('Extra Info')
    patient_id = fields.Many2one('medical.patient', 'Patient')

    #     Override below fields from medical.medication.template to set default value
    start_treatment = fields.Datetime('Start of treatment', default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    frequency_unit = fields.Selection([
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('wr', 'when required'),
    ], 'unit', default=lambda *a: 'hours')

    duration_period = fields.Selection(
        [('minutes', 'minutes'), ('hours', 'hours'), ('days', 'days'), ('months', 'months'), ('years', 'years'),
         ('indefinite', 'indefinite'), ], 'Treatment period', default=lambda *a: 'days',
        help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately", )

    qty = fields.Integer('x', default=lambda *a: 1, help="Quantity of units (eg, 2 capsules) of the medicament")

    @api.onchange('course_completed')
    @api.depends('discontinued', 'is_active')
    def onchange_course_completed(self):
        if self.course_completed == True:
            self.is_active = False
            self.discontinued = False
        elif self.is_active == False and self.discontinued == False and self.course_completed == False:
            self.is_active = False

    @api.onchange('discontinued')
    @api.depends('course_completed', 'is_active')
    def onchange_discontinued(self):
        if self.discontinued == True:
            self.is_active = False
            self.course_completed = False
        elif self.is_active == False and self.discontinued == False and self.course_completed == False:
            self.is_active = True

    @api.onchange('is_active')
    @api.depends('course_completed', 'discontinued')
    def onchange_is_active(self):
        if self.is_active == True:
            self.discontinued = False
            self.course_completed = False
        elif self.is_active == False and self.discontinued == False and self.course_completed == False:
            self.course_completed = True


class patient_prescription_order(models.Model):
    _name = "medical.prescription.order"
    _description = "prescription order"

    patient_id = fields.Many2one('medical.patient', 'Patient ID')
    name = fields.Char('Prescription ID', size=128, help='Type in the ID of this prescription')
    prescription_date = fields.Datetime('Prescription Date', default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    user_id = fields.Many2one('res.users', 'Log In User', default=lambda obj: obj.env.uid)
    pharmacy = fields.Many2one('res.partner', 'Pharmacy', domain=[('is_pharmacy', '=', True)])
    prescription_line = fields.One2many('medical.prescription.line', 'name', 'Prescription line')
    notes = fields.Text('Prescription Notes')
    pid1 = fields.Many2one('medical.appointment', 'Appointment', )
    doctor = fields.Many2one('medical.physician', 'Prescribing Doctor', help="Physician's Name")
    p_name = fields.Char('Demo')
    no_invoice = fields.Boolean('Invoice exempt')
    invoice_done = fields.Boolean('Invoice Done')
    state = fields.Selection([('invoiced', 'Invoiced'), ('tobe', 'To be Invoiced')], 'Invoice Status',
                             default=lambda *a: 'tobe')
    inv_id = fields.Many2one('account.move', 'Invoice')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')

    _sql_constraints = [
        ('pid1', 'unique (pid1)', 'Prescription must be unique per Appointment')]

    @api.onchange('p_name')
    def onchange_p_name(self):
        n_name = self._context.get('name')
        d_name = self._context.get('physician_id')
        self.name = n_name
        self.doctor = d_name

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('medical.prescription') or '0'
        return super(patient_prescription_order, self).create(vals)

    @api.onchange('name')
    def onchange_name(self):
        l1 = []
        pres_order_obj = self.env['medical.prescription.order']
        prid1 = pres_order_obj.search([])
        for p in prid1:
            l1.append(p.pid1.id)
        return {'domain': {'pid1': [('id', 'not in', l1)]}}

    def create_invoices(self):
        """ create invoices for appointment """
        invoice_obj = self.env['account.move']
        invoice_line_obj = self.env['account.move.line']
        for obj in self:
            journal_ids = self.env['account.journal'].search(
                [('type', '=', 'sale'), ('company_id', '=', obj.user_id.company_id.id)], limit=1)
            if not journal_ids:
                raise UserError(_('Please define sales journal for this company: "%s" (id:%d).') % (
                obj.user_id.company_id.name, obj.user_id.company_id.id))
        
            invoice_vals = {
                'move_type': 'out_invoice',
                'date': time.strftime('%Y-%m-%d'),
                'ref': obj.name,
                'partner_id': obj.patient_id.partner_id.id,
                'journal_id': journal_ids[0].id or False,
                'invoice_user_id': obj.user_id and obj.user_id.id or False,
                'fiscal_position_id': obj.patient_id.partner_id.property_account_position_id and obj.patient_id.partner_id.property_account_position_id.id or False,
                'currency_id': obj.pricelist_id.currency_id.id,
                'user_id': obj.user_id and obj.user_id.id or False,
                'doctor_name': self.doctor.id,
                'invoice_line_ids': [],
            }
            # new_invoice_obj = invoice_obj.new(invoice_vals)
            # new_invoice_obj._onchange_journal()
            # new_invoice_obj._onchange_currency()
            # new_invoice_obj._onchange_partner_id()
            invoice_line_ids = []
            for line in obj.prescription_line:
                product_context = dict(self.env.context, partner_id=obj.patient_id.partner_id.id, date=time.strftime('%Y-%m-%d'), uom=line.medicament.product_medicament_id.uom_id.id)
                final_price, rule_id = obj.pricelist_id.with_context(product_context)._get_product_price_rule(line.medicament.product_medicament_id, line.quantity)
                # final_price, rule_id = obj.pricelist_id.with_context(product_context)._get_product_price_rule(obj.service_id, 1.0)


                in_line_vals = {
                    'product_id': line.medicament.product_medicament_id.id,
                    'name': line.medicament.product_medicament_id.name,
                    'quantity': line.quantity,
                    # 'move_id': new_invoice_obj,
                    'price_unit': final_price,
                    'currency_id': obj.pricelist_id.currency_id.id,
                }
                invoice_line_ids.append((0, 0, in_line_vals))
            #     inv_line_new = invoice_line_obj.new(in_line_vals)
            #     inv_line_new._inverse_product_id()
            #     inv_line_new.price_unit = final_price
            #     # inv_line_new._onchange_mark_recompute_taxes()
            #     inv_line_new._compute_totals()
            #     # inv_line_new._get_fields_onchange_balance()

            # new_invoice_obj._onchange_invoice_line_ids()
            # account_move_vals = new_invoice_obj._convert_to_write({name: new_invoice_obj[name] for name in new_invoice_obj._cache})
            # account_move_rec = self.env['account.move'].create(account_move_vals) 

            invoice_vals['invoice_line_ids'] = invoice_line_ids
            account_move_rec = self.env['account.move'].create(invoice_vals)

            obj.write({'inv_id': account_move_rec.id, 'invoice_done': True, 'state': 'invoiced'})
        return {'type': 'ir.actions.act_window_close'}


# PRESCRIPTION LINE
class prescription_line(models.Model):
    _name = "medical.prescription.line"
    _description = "Basic prescription object"
    _inherits = {'medical.medication.template': 'template'}

    template = fields.Many2one('medical.medication.template', 'Template ID', required=True, ondelete="cascade")
    name = fields.Many2one('medical.prescription.order', 'Prescription ID')
    review = fields.Datetime('Review')
    quantity = fields.Integer('Quantity', default=lambda *a: 1)
    refills = fields.Integer('Refills #')
    allow_substitution = fields.Boolean('Allow substitution')
    short_comment = fields.Char('Comment', size=128, help='Short comment on the specific drug')
    prnt = fields.Boolean('Print', default=lambda *a: True,
                          help='Check this box to print this line of the prescription.')

    #     Override FIelds
    frequency_unit = fields.Selection([
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('wr', 'when required'),
    ], 'unit', default=lambda *a: 'hours')

    duration_period = fields.Selection(
        [('minutes', 'minutes'), ('hours', 'hours'), ('days', 'days'), ('months', 'months'), ('years', 'years'),
         ('indefinite', 'indefinite'), ], 'Treatment period', default=lambda *a: 'days',
        help="Period that the patient must take the medication. in minutes, hours, days, months, years or indefinately", )

    qty = fields.Integer('x', default=lambda *a: 1, help="Quantity of units (eg, 2 capsules) of the medicament")


class hospital_building(models.Model):
    _name = "medical.hospital.building"
    _description = "Hospital Building"

    name = fields.Char('Name', size=128, help="Name of the building within the institution")
    institution = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', "1")],
                                  help="Medical Center")
    code = fields.Char('Code', size=64)
    extra_info = fields.Text('Extra Info')


class hospital_unit(models.Model):
    _name = "medical.hospital.unit"
    _description = "Hospital Unit"

    name = fields.Char('Name', size=128, help="Name of the unit, eg Neonatal, Intensive Care, ...")
    institution = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', "1")],
                                  help="Medical Center")
    code = fields.Char('Code', size=64)
    extra_info = fields.Text('Extra Info')


class hospital_oprating_room(models.Model):
    _name = "medical.hospital.oprating.room"
    _description = "Oprating Room"

    name = fields.Char('Name', size=128, help='Name of the Operating Room')
    institution = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', True)],
                                  help='Medical Center')
    building = fields.Many2one('medical.hospital.building', 'Building', )
    unit = fields.Many2one('medical.hospital.unit', 'Unit')
    extra_info = fields.Text('Extra Info')

    _sql_constraints = [
        ('name_uniq', 'unique (name, institution)', 'The Operating Room code must be unique per Health Center.')]


class procedure_code(models.Model):
    _description = "Medical Procedure"
    _name = "medical.procedure"

    name = fields.Char('Code', size=128)
    description = fields.Char('Process', size=256)


class teeth_code(models.Model):
    _description = "teeth code"
    _name = "teeth.code"

    name = fields.Char('Code', size=128)
    code = fields.Char('Name', size=128)


class ir_attachment(models.Model):
    _description = "Attachments"
    _inherit = "ir.attachment"

    patient_id = fields.Many2one('medical.patient', 'Patient')


class AccountMove(models.Model):

    _inherit = "account.move"
    _description = "Account Move"

    doctor_name = fields.Many2one('medical.physician', 'Physician', help="Physician who treated or diagnosed the patient")
    insurance_company = fields.Many2one('res.partner', 'Insurance Company',
                                        domain=[('is_insurance_company', '=', True)])
    ol = fields.Boolean('Customer Online')

class DoctorSlot(models.Model):
    _name = 'doctor.slot'
    _description = 'Doctor Slot'

    doctor_id = fields.Many2one('medical.physician', string='Dokter')
    doctor_ganti_id = fields.Many2one('medical.physician', string='Dokter Ganti')
    
    weekday = fields.Selection([
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday'),
    ], string='Week Day', required=True)
    start_hour = fields.Float('Starting Hour')
    end_hour = fields.Float('Ending Hour')
    institution_id = fields.Many2one('res.partner', 'Institution', domain=[('is_institution', '=', "1")])
    
    ganti_jadwal = fields.Boolean('ganti jadwal')
    tgl_ganti = fields.Integer('tgl yg diganti')
    bln_ganti = fields.Integer('bln yg ganti')
    
    
    @api.model
    def get_doctors_slot(self, target_date=False, doctor=False):
        if target_date:
            ask_time = datetime.strptime(target_date, "%a %b %d %Y %H:%M:%S %Z%z").date()
            weekday = ask_time.isoweekday()
        else:
            weekday = datetime.today().isoweekday()

        domain = [('weekday', '=', str(weekday))]
        if doctor:
            domain += [('doctor_id', '=', int(doctor))]
        slot_ids = sorted(self.search(domain), reverse=True)
        data_dict = {}
        for lt in slot_ids:
            doctor_id = lt.doctor_id
            start_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(lt.start_hour * 60, 60))
            end_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(lt.end_hour * 60, 60))
            if doctor_id.id not in data_dict:
                data_dict[doctor_id.id] = {
                    'id': doctor_id.id,
                    'name': doctor_id.res_partner_medical_physician_id.name,
                    'count': 1,
                    'time_slots': [{'start_hour': start_hour, 'end_hour': end_hour}]
                }
            else:
                data_dict[doctor_id.id]['count'] += 1
                data_dict[doctor_id.id]['time_slots'].append({'start_hour': start_hour, 'end_hour': end_hour})

        final_list = []
        for i in data_dict:
            final_list.append(data_dict.get(i))
        return final_list

    @api.model
    def get_doctors_slot_validation(self, target_date=False, doctor=False):
        is_available_slot = False
        if target_date:
            ask_time = datetime.strptime(target_date, "%a %b %d %Y %H:%M:%S %Z%z").date()
            weekday = ask_time.isoweekday()
        else:
            weekday = datetime.today().isoweekday()
        domain = [('weekday', '=', str(weekday))]
        if doctor:
            domain += [('doctor_id', '=', int(doctor))]
        slot_ids = sorted(self.search(domain), reverse=True)
        for lt in slot_ids:
            start_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(lt.start_hour * 60, 60))
            end_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(lt.end_hour * 60, 60))
            ask_time = datetime.strptime(target_date, "%a %b %d %Y %H:%M:%S %Z%z").date()

            start_time = datetime.strptime(start_hour, '%H:%M').time()
            start_date_time = datetime.combine(ask_time, start_time)

            end_time = datetime.strptime(end_hour, '%H:%M').time()
            end_date_time = datetime.combine(ask_time, end_time)

            if self.env.context.get('dateToString') and self.env.context.get('from_time'):
                str_date = datetime.strptime(self.env.context.get('dateToString'), "%a %b %d %Y %H:%M:%S %Z%z").date()
                str_date = str(str_date) + ' ' + self.env.context.get('from_time')
                datetime_object = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
                if datetime_object>=start_date_time and datetime_object<=end_date_time:
                    is_available_slot = True
        return is_available_slot
    
    def kalkulasi_date(self, data_jam_float, thn, bln_ganti, tgl_ganti):
        """return thn, bln_ganti, tgl_ganti, hour, minute"""
        # ubah float ke jam menit
        hour, minute = divmod(data_jam_float * 60, 60)
        hour-= 7
        
        # mundurin bulan jika tgl < 1 dan kalkulasi ulang tgl
        # print('1 ini tahunnn ',hour, tgl_ganti, bln_ganti, thn)
        tgl_ganti = tgl_ganti - 1 if hour < 0 else tgl_ganti
        hour = hour + 23 if hour < 0 else hour
        
        print('2 ini tahunnn ', hour, tgl_ganti, bln_ganti, thn)
        bln_ganti = bln_ganti - 1 if tgl_ganti < 1 else bln_ganti
        tgl_ganti = tgl_ganti + monthrange(thn, bln_ganti)[1] if tgl_ganti < 1 else tgl_ganti
        
        print('3 ini tahunnn ', hour, tgl_ganti, bln_ganti, thn)
        thn = thn - 1 if bln_ganti < 1 else thn
        print('3.5 ini tahunnn ', hour, tgl_ganti, bln_ganti, thn)
        bln_ganti = bln_ganti + 12 if bln_ganti < 1 else bln_ganti
        
        # print('4 ini tahunnn ', hour, tgl_ganti, bln_ganti, thn)
        return thn, bln_ganti, tgl_ganti, int(hour), int(minute)
    
    
    def write(self, vals):
        # if 'start_hour' in vals and 'end_hour' in vals:
        #     # lah = self.env['medical.appointment'].search([ ('state', 'not in', ['cancel','done']), ('doctor', '=', self.doctor_id.id), ('appointment_sdate', '>=', datetime.today()) ])
        #     lah = self.env['medical.appointment'].search([ ('state', 'not in', ['cancel','done']), ('appointment_sdate', '>=', datetime.today()), ('institution', '=', self.institution_id.id) ])
        #     print('inin manaaa ', lah, type(lah))
        #     print('iininin ', vals['start_hour'], vals['end_hour'])
        #     # data_app = self.env['medical.appointment'].search(['&','&', ('appointment_sdate', '>=', vals['start_hour']), ('appointment_sdate', '<=', vals['end_hour']), ('state', 'not in', ['cancel','done']) ])
        #     start_hour = vals['start_hour']
        #     end_hour = vals['end_hour']
        #     start_hour, start_minute = divmod(start_hour * 60, 60)
        #     end_hour, end_minute = divmod(end_hour * 60, 60)
        #     for app in lah:
        #         hour, minute = app.appointment_sdate.hour, app.appointment_sdate.minute
        #         # c = minute if minute < 60 else minute/60

        #         # if minute > 60:
        #         #     c %= 1
        #         #     c*= 60
        #         #     hour += 1
        #         hour += 7
        #         print('iniiiii dayyy ', app.appointment_sdate.day)
        #         weekday = app.appointment_sdate.weekday()+1 if app.appointment_sdate.weekday()+1 < 7 else 0
                
        #         # print('ini jamnya ', hour, '>=', start_hour, 'and', hour, '<=', end_hour, app.name, self.weekday, '==', weekday)
        #         # print(hour >= start_hour)
        #         # print(hour <= end_hour)
        #         # print(int(self.weekday) == weekday, type(int(self.weekday)), type(weekday))
        #         # if hour >= start_hour and hour <= end_hour and int(self.weekday) == weekday and self.institution_id == app.institution:
        #         if hour >= start_hour and hour <= end_hour and int(self.weekday) == weekday:
        #             print('iiiiiii ', app.appointment_sdate)
        #             app.write({
        #                 'doctor': self.doctor_id.id
        #             })
                    
        #             print('ini jamnya ', hour, '>=', start_hour, 'and', hour, '<=', end_hour, app.name, self.weekday, '==', weekday)
        #             print(hour >= start_hour)
        #             print(hour <= end_hour)
        #             print(int(self.weekday) == weekday, type(int(self.weekday)), type(weekday))
                    
        #             print('========================')

                
        #             print('ahhh ',hour, minute)
                
                
        
        
    
        # print('start hour', vals['start_hour'])
        # print('end hour', vals['end_hour'])
        # print('start hour', self.start_hour)
        # print('end hour', self.end_hour)
        
        
        # cek pergantian jam
        if 'start_hour' in vals and 'end_hour' in vals:
            # cek valid rentang jam
            if vals['start_hour'] >= vals['end_hour']:
                raise UserError('jam akhir tidak bisa lebih kecil sama dengan jam awal')
        
        # cek tipe jadwal
        ganti_jadwal = vals['ganti_jadwal'] if'ganti_jadwal' in vals else self.ganti_jadwal
        if ganti_jadwal:
            dokter_pengganti = vals['doctor_ganti_id'] if 'doctor_ganti_id' in vals else self.doctor_ganti_id
            thn = datetime.today().year
            bln_ganti =  vals['bln_ganti'] if 'bln_ganti' in vals else self.bln_ganti
            tgl_ganti = vals['tgl_ganti'] if 'tgl_ganti' in vals else self.tgl_ganti
            
            start_hour = vals['start_hour'] if 'start_hour' in vals else self.start_hour
            end_hour = vals['end_hour'] if 'end_hour' in vals else self.end_hour
            
            start_thn, start_bln_ganti, start_tgl_ganti, start_jam, start_menit = self.kalkulasi_date(start_hour, thn, bln_ganti, tgl_ganti )
            end_thn, end_bln_ganti, end_tgl_ganti, end_jam, end_menit = self.kalkulasi_date(end_hour, thn, bln_ganti, tgl_ganti )
            print(start_thn, start_bln_ganti, start_tgl_ganti, start_jam, start_menit)
            print(end_thn, end_bln_ganti, end_tgl_ganti, end_jam, end_menit)
            
            start_waktu = datetime.today().replace(start_thn, start_bln_ganti, start_tgl_ganti, start_jam, start_menit)
            end_waktu = datetime.today().replace(end_thn, end_bln_ganti, end_tgl_ganti, end_jam, end_menit)


            data_app = self.env['medical.appointment'].search([ ('state', 'not in', ['cancel','done']), ('doctor', '=', self.doctor_id.id), ('appointment_sdate', '>=', start_waktu), ('appointment_sdate', '<=', end_waktu) ])
            print(data_app)
            for app in data_app:
                    app.write({
                        'doctor': dokter_pengganti
                    })
                        
        
        return super(DoctorSlot, self).write(vals)
    
class InisialSales(models.Model):
    _name = 'inisial.sales'
    _description = 'inisial.sales'
    _rec_name = 'nama'
    
    nama = fields.Char('nama')
    