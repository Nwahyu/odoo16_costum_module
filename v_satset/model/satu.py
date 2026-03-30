from odoo import _, api, fields, models
from odoo.exceptions import UserError
import requests

class vio_satset_configuration(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'vio.satset'
    
    
    auth_url = fields.Char('auth_url', default="https://api-satusehat-stg.dto.kemkes.go.id/oauth2/v1")
    base_url = fields.Char('base_url', default="https://api-satusehat-stg.dto.kemkes.go.id/fhir-r4/v1")
    consent_url = fields.Char('consent_url', default="https://api-satusehat-stg.dto.kemkes.go.id/consent/v1")
    org_ID = fields.Char('org_ID', default="816f5a6d-01c4-4b7c-a419-9d22ab72d8f3")
    client_id = fields.Char('client_id', default="SmCXGcsD9Gl14N2YNVuFIMZmUj1MHp4KlBjeAwWZA5mXezjh")
    client_secret = fields.Char('client_secret', default="lTTuQoeBCUs2Oh59I1bzAXgpXpfUwLSZlaBrifZTFP4008gPir8WvKEKxDAHOMRI")
    token = fields.Char('token', default="not_token")
    
    
    def get_access_token(self, **args):
        irDefault = self.env['ir.default'].sudo()
        
        print('run akses token')
        client_id = self.env['ir.default'].sudo().get('res.config.settings', 'client_id')
        client_secret = self.env['ir.default'].sudo().get('res.config.settings', 'client_secret')
        auth_url = self.env['ir.default'].sudo().get('res.config.settings', 'auth_url') or False
        token = self.env['ir.default'].sudo().get('res.config.settings', 'token')
        # print(auth_url, type(auth_url))
        if auth_url is False:
            print('masuk ke update value')
            self.set_values()
            auth_url = self.env['ir.default'].sudo().get('res.config.settings', 'auth_url')
            client_id = self.env['ir.default'].sudo().get('res.config.settings', 'client_id')
            client_secret = self.env['ir.default'].sudo().get('res.config.settings', 'client_secret')
        body = {
            'client_id': client_id,
            'client_secret': client_secret
        }
        print('client id')
        print(client_id, client_secret, auth_url)
        param = {'grant_type':'client_credentials'}
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        
        res = requests.post(f"{auth_url}/accesstoken", body, params=param, headers=header)
        print(res)
        print(res.json())
        irDefault.set('res.config.settings', 'token', res.json()['access_token'])
        # print(f"token {res.json()['access_token']}")
        # print(token)
        # self.env['satset.appointment'].kirim_data()
        return True
            
        
        
    def set_values(self):
        print('run set value')
        irDefault = self.env['ir.default'].sudo()
        irDefault.set('res.config.settings', 'auth_url', 'https://api-satusehat-stg.dto.kemkes.go.id/oauth2/v1')
        irDefault.set('res.config.settings', 'base_url', 'https://api-satusehat-stg.dto.kemkes.go.id/fhir-r4/v1')
        # # irDefault.set('res.config.settings', 'consent_url', )
        irDefault.set('res.config.settings', 'token', 'no_token')
        irDefault.set('res.config.settings', 'org_ID', '816f5a6d-01c4-4b7c-a419-9d22ab72d8f3')
        irDefault.set('res.config.settings', 'client_id', 'SmCXGcsD9Gl14N2YNVuFIMZmUj1MHp4KlBjeAwWZA5mXezjh')
        # irDefault.set('res.config.settings', 'client_id', 'SmCXGcsD9Gl14N2YNVuFIMZmUj1MHp4KlBjeAwWZA5mXezjh')
        irDefault.set('res.config.settings', 'client_secret', 'lTTuQoeBCUs2Oh59I1bzAXgpXpfUwLSZlaBrifZTFP4008gPir8WvKEKxDAHOMRI')
        # irDefault.set('res.config.settings', 'client_secret', 'lTTuQoeBCUs2Oh59I1bzAXgpXpfUwLSZlaBrifZTFP4008gPir8WvKEKxDAHOMRI')
        
        # irDefault.set('res.config.settings', 'auth_url', self.auth_url)
        # irDefault.set('res.config.settings', 'base_url', self.base_url)
        # irDefault.set('res.config.settings', 'consent_url', )
        # irDefault.set('res.config.settings', 'org_ID', self.org_ID)
        # irDefault.set('res.config.settings', 'client_id', self.client_id)
        # irDefault.set('res.config.settings', 'client_secret', self.client_secret)
        return True
        
    
    
class vio_satset_pasien(models.Model):
    # ketika result is mecu, data kirim ke satset.appointment untuk dikirm ke satu sehat pd mlm hari
    _inherit = 'medical.appointment'
    _description = 'inherit medical appointment'
    
    
    # icd10_ids = fields.One2many('satset.icd10', 'appointment_id', string='Diagnosa')
    # icd10_ids = fields.Many2many('satset.icd10', string='icd10')
    icd10_id = fields.Many2one('satset.icd10', string='icd10')
    id_satset_icd10 = fields.Char('id_satset_icd10')
    id_satset = fields.Char('id_satset')
    
    def write(self, vals):
        # self.env['res.config.settings'].get_access_token()
        
        mecunya: bool = False
        icd10nya: bool = False
        # print(f"aa {self.env['satset.appointment'].search([('appointment_id.id', '=', self.id)])}")
        # print(f"aa {self.env['satset.appointment'].search([('appointment_id', '=', self.id)])}")
        if len(self.env['satset.appointment'].search([('appointment_id', '=', self.id)])) < 1:
            if self.doctor.doctor_satset:
                print('iiiiiiiiiiiii write on sateset by qapp')
                print(self.doctor.doctor_satset)
                print(vals)
                if 'state' in vals:
                    if vals['state'] == 'done':
                        if 'service_id' in vals:
                            if 'MECU' in vals['service_id']:
                                mecunya = True
                        else:
                            if 'MECU' in self.service_id.name or 'ORTHO' in self.service_id.name or 'FEE JASA' in self.service_id.name: mecunya = True
                            
                        if self.patient.nik:pass
                        else: raise UserError('nik pasien masih kosong')
                        
                        
                        if 'icd10_id' in vals:
                            if vals['icd10_id']:icd10nya = True
                        else:
                            if self.icd10_id: icd10nya = True
            
            print(mecunya, icd10nya)
            if mecunya and icd10nya:
                self.env['satset.appointment'].create({
                    'name' : self.name,
                    'status_kirim_data': False,
                    'appointment_id': self.id
                })
                    
        
        
        return super(vio_satset_pasien, self).write(vals)
    
    
    
# class res_users(models.Model):
#     _name = 'res.users'
#     _description = 'res.users'
    
#     data_dokter_id = fields.Many2one('medical.physician', string='data dokter')
    
class medical_physician(models.Model):
    _inherit = 'medical.physician'
    _description = 'medical.physician'
    
    
    doctor_satset = fields.Boolean('dokter satu sehat')
    id_satset = fields.Char('id_satset')
    
class medical_patient(models.Model):
    _inherit = 'medical.patient'
    _description = 'medical.patient'
    
    id_satset = fields.Char('id_satset')
    
    
class medical_ukp(models.Model):
    _inherit = 'medical.hospital.building'
    _description = 'medical location ukp ( cabang )'
    
    status_kirim_data = fields.Boolean('status_kirim_data')
    
    no_hp = fields.Char('nomor hp')
    email = fields.Char('email')
    url = fields.Char('link web')
    address = fields.Char('address')
    city = fields.Char('city')
    post_code = fields.Char('post code')
    
    cd_province = fields.Char('code_province')
    cd_city = fields.Char('code_city')
    cd_district = fields.Char('code_district')
    cd_village = fields.Char('code_village')
    
    
    
    def kirim_data_baru(self):
    # dari action server
        pass
        if self.status_kirim_data == False:
            # kirim data ke satu sehat n get id from response
            # sekalian kirim data poli room n gedung
            pass
            
    
    
class medical_hospital_unit(models.Model):
    _inherit = 'medical.hospital.unit'
    _description = 'medical.hospital.unit ( nama poli )'
    
    
    longtitude = fields.Char('logtitude')
    latitude = fields.Char('latitude')
    altitude = fields.Char('altitude')