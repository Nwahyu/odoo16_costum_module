from odoo import _, api, fields, models


class vio_rme(models.Model):
    _name = 'vio.rme'
    _description = 'vio.rme'
    
    
    appointment_sdate = fields.Datetime('appointment_start')
    name = fields.Char('Traffic ID')
    patient_id = fields.Many2one('medical.patient', string='pasien')
    institution_id = fields.Many2one('res.partner', 'Cabang', domain=[('is_institution', '=', "1")], help="Medical Center")
    no_hp = fields.Char('no hp', related='patient_id.no_hp')
    # no_hp = fields.Char('no hp')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Waiting List'),
         ('still_pending', 'In Progress'),
         ('done', 'Done'),
         ('cancel', 'Cancel'),
         ('reschedule', 'Reschedule')], 'Status Kedatangan', default='confirmed')
    
    status_by = fields.Selection([
        ('app_crs', 'App by CRS'),
        ('app_ces', 'App by CES'),
        ('app_outlet', 'App by OUTLET'),
        ('app_other', 'App by LAINNYA'),
        ('app_vho', 'App by VHO'),
        ('wi', 'Walk In'),
    ], string='Status By')
    race_tipe_id = fields.Many2one('tag.race.tipe', string='Race', domain="[('is_active', '=', '1')]")
    tujuan_id = fields.Many2one('product.product', string='Tujuan Kedatangan', domain=[('type', '=', "service"), ('is_tujuan','=', True)], required=True, tracking=True)
    service_id = fields.Many2one('product.product', 'Result', domain=[('type', '=', "service"), ('is_result', '=', True)],
                                 help="Result", tracking=True)
    resolved = fields.Char('Agent Create APP', tracking=True)
    agent_ids = fields.Many2many('inisial.sales', string='Agent Operation', tracking=True)
    doctor_id = fields.Many2one('medical.physician', 'Dokter', help="Nama Dokter")
    reason = fields.Text('reason')
    remarks = fields.Text('remarks')
    