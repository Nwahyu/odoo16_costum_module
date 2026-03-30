from odoo import _, api, fields, models
import requests, time, re, threading
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError, RedirectWarning
import logging, time
import multiprocessing
import itertools
# from pprint import pprint
from timeit import default_timer as timer
_logger = logging.getLogger(__name__)

from functools import wraps
import time

def timing_val(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        elapsed_time = t2 - t1
        print(f"{func.__name__} took {elapsed_time:.3f}s.")
        return result

    return wrapper

class kriteria(models.Model):
    _name = 'tag.kriteria'
    _description = 'tag.kriteria'
    _rec_name = 'nama'
    
    
    nama = fields.Char('nama')
    stage_id = fields.Many2one('crm.stage', string='stage')
    
    
    
class solusi(models.Model):
    _name = 'tag.solusi'
    _description = 'tag.solusi'
    _rec_name = 'nama'
    
    nama = fields.Char('nama')
    
class race(models.Model):
    _name = 'tag.race'
    _description = 'race'
    _rec_name = 'nama'
    
    nama = fields.Char('nama')
    race_id = fields.Many2one('tag.race.tipe', string='race')
    
class tag_race_tipe(models.Model):
    _name = 'tag.race.tipe'
    _description = 'tag.race.tipe'
    _rec_name = 'nama'
    
    nama = fields.Char('nama')
    is_reff = fields.Boolean('is refferal')
    race_ids = fields.One2many('tag.race', 'race_id', string='race')
    is_active = fields.Boolean('is active')
    
    
    
    
class chat(models.Model):
    _name = 'qontak.chat'
    _description = 'qontak.chat'
    
    def reparse_note(self, data):
        if data is None:
            gender = 'm'
            start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            end = datetime.now()+timedelta(minutes=15)
            end = end.strftime('%Y-%m-%d %H:%M:%S')
            # end+=timedelta(minutes=15)
            cabang = self.env['res.partner'].search([('is_institution', '=', '1'),('name', 'ilike', 'VHO')])
            reschedule = False
            jam_awal = 0
            weekday = 1
            no_hp = ''
            
            return gender, start, end, cabang, reschedule, jam_awal, weekday, no_hp
        else:
            data = data['text']
            print(data)
            bb = [z for z in data[:]]
            
            cabang = ""
            gender = ""
            start = ""
            end = ""
            no_hp = ''
            tujuan = ''
            reschedule = False
            cdone = False
            gdone = False
            sdone = False
            
            jam_awal = 0
            weekday = 0
            
            a = -1
            for _ in bb:
                a += 1
                
                if _ == 'g' and "".join(bb[a-2:a]) == '--':
                    # pasin = "".join(bb[a-2:a])
                    ii = {'f', 'm'}
                    gender = "".join(bb[a+2:a+3])
                    if gender not in ii:
                        gender = 'm'
                    gdone = True
                    
                if _ == 'c' and "".join(bb[a-2:a]) == '--':
                    # fin =
                    # print(f'ini akses cabang', re.findall("\S", "".join(bb[a+2:a+5])))
                    # cabang = "".join(bb[a+2:a+5])
                    if len(re.findall("\S", "".join(bb[a+2:a+5]))) == 3:
                        print("ini masuk cabang")
                        hc_cabang = self.env['res.partner'].search([('is_institution', '=', '1')])
                        for u in hc_cabang:
                            pattern = re.compile(re.escape("".join(bb[a+2:a+5])), re.IGNORECASE)
                            hasil = re.search(pattern, u.name)
                            if hasil:
                                cabang = self.env['res.partner'].search([('is_institution', '=', '1'),('id', '=', u.id)])
                        # print('note cabang ', cabang)
                        cdone = True
                            
                if _ == 's' and "".join(bb[a-2:a]) == '--':
                    sdone = True
                    # print('ini s masuk ',bb[a+2:a+19])
                    if len(bb[a+2:a+19]) > 15:
                        # print('tag_info line 133')
                        jam = int("".join(bb[a+13:a+15]))
                        menit = int("".join(bb[a+16:a+19]))
                        hari = int("".join(bb[a+10:a+12]))
                        bulan = int("".join(bb[a+7:a+9]))
                        tahun = int("".join(bb[a+2:a+6]))
                        # print('ekkk point sdate')
                        start = time.strftime(f'{tahun:04}-{bulan:02}-{hari:02} {jam-7:02}:{menit:02}:00')
                        # print(f"ini len {len(start)} {jam}:{menit}")
                        # break
                        jam_awal = jam
                        weekday = datetime(tahun, bulan, hari, jam, menit, 00).weekday()
                        
                        menit+=15
                        if menit >59:
                            menit = menit-60
                            jam += 1
                        elif menit < 0:
                            menit += 60
                            jam -=1
                        end = time.strftime(f'{tahun:04}-{bulan:02}-{hari:02} {jam-7:02}:{menit:02}:00')
                        
                # if _ == 't' and "".join(bb[a-2:a]) == '--':
                #     pass
                    
                        
                if _ == 'n' and "".join(bb[a-2:a]) == '--':
                    no_hp = "".join(bb[a+2: a+18])
                        
                # if _ == 'r' and "".join(bb[a-2:a]) == '--':
                #     reschedule = True
                
            # jika value tidak ada       
            if gdone == False:
                gender = 'm'
            if cdone == False:
                cabang = self.env['res.partner'].search([('is_institution', '=', '1'),('name', 'ilike', 'VHO')])
                print('else cabang', cabang)
                # if cabang == False:
                #     cabang = ''
            if sdone == False:
                start = time.strftime('%Y-%m-%d %H:%M:%S')
                end = time.strftime('%Y-%m-%d %H:%M:%S')
            
            
            # return gender, start, end, cabang, reschedule, jam_awal, weekday, no_hp, tujuan
            return gender, start, end, cabang, reschedule, jam_awal, weekday, no_hp

        
    # def get_chat(self):
    #     awal = time.time()
    #     won_stage = self.env['crm.stage'].search([('is_won', '=', True)]).id
    #     solusi = [z.nama for z in self.env['tag.solusi'].search([])]
    #     race = [z.nama for z in self.env['tag.race'].search([])]
    #     kriteria = [z.nama for z in self.env['tag.kriteria'].search([])]
    #     tujuan_kedatangan = [z.name for z in self.env['product.product'].search([])]
        
    #     self.get_lead()
        
        
    #     data_leads = self.env['crm.lead'].search([('create_date', '>', datetime.now()-timedelta(25)), ('stage_id.is_won', '=', False)])
        
    #     self.update_leads(data_leads, solusi, race, tujuan_kedatangan, kriteria, won_stage)
        
    #     print('waktu lama ', time.time() - awal)
        

    def get_lead(self):
        _logger.info('='*20+ 'run get lead' + '='*20)
        url = "https://service-chat.qontak.com/api/open/v1/rooms"
        querystring = {}
        headers = {"Authorization": "Bearer qdAg6K2pVA10nNBMNdTUAsWs0KeoGuFOgk6qM16fZ6U"}
        response = requests.get(url, headers=headers, params=querystring)
        val = response.json()['data']
        
        
        for _ in val:
            #(future) cek leadnya udah punya app atau belum, if sudah maka update saja else bikin baru
            data_res = self.env['res.partner'].search([('mobile', '=', _['account_uniq_id'])])
            if len(data_res) < 1 :
                res_part = self.env['res.partner'].create({
                    'name': _['name'],
                    # 'phone': 
                    'mobile': _['account_uniq_id'],
                })
                self.env['crm.lead'].create({
                    'name': f"{_['name']} opp",
                    'partner_id': res_part.id,
                    'room_id': _.get('last_message').get('room_id')
                })
                
            else:
                try:
                    # ambil leadnya
                    leadnya = self.env['crm.lead'].search([('partner_id', '=', data_res.id)])
                    print('data ressssssss', data_res.name, leadnya.name, _.get('id'), data_res.mobile)
                    if leadnya.name is False:
                        data_res.unlink()
                    leadnya.write({
                        'room_id': _.get('id')
                    })
                    self.env.cr.commit()
                except: pass
            #     self.env['crm.lead'].create({
            #         'name': f"{_['name']} opp",
            #         'partner_id': data_res.id,
            #         'room_id': _.get('last_message').get('room_id')
            #     })
            #     print('data leaddddddddd', data_res)
                # create lead dup
        
    # def tes_fungsi_jalan(self, data_leads, data_solusi, data_race, data_tujuan_kedatangan, data_kriteria, won_stage):
    #     for data_lead in data_leads:
    #         print(data_lead.name, data_lead.room_id)
    
    
    def periperal_chat(self):
        won_stage = self.env['crm.stage'].search([('is_won', '=', True)]).id
        solusi = [z.nama for z in self.env['tag.solusi'].search([])]
        race = [z.nama for z in self.env['tag.race'].search([])]
        kriteria = [z.nama for z in self.env['tag.kriteria'].search([])]
        tujuan_kedatangan = [z.name for z in self.env['product.product'].search([])]
        data_leads = self.env['crm.lead'].search([('create_date', '>', datetime.now()-timedelta(25)), ('stage_id.is_won', '=', False)])
        
        return won_stage, solusi, race, kriteria, tujuan_kedatangan, data_leads

    @timing_val            
    def up_lead_1(self):
        # a = time.time()
        print('='*7, 'ini up lead 1', '='*7)
        won_stage, solusi, race, kriteria, tujuan_kedatangan, data_leads = self.periperal_chat()
        # print('ini ahuau ',len(data_leads))
        
        data_leads = data_leads[:len(data_leads)//7]
        self.update_leads(data_leads, solusi, race, tujuan_kedatangan, kriteria, won_stage)
        print(len(data_leads))
        # print('time up lead 1 ', time.time() - a)
            
    @timing_val
    def up_lead_2(self):
        # a = time.time()
        print('='*7, 'ini up lead 2', '='*7)
        won_stage, solusi, race, kriteria, tujuan_kedatangan, data_leads = self.periperal_chat()
        if len(data_leads) >= 30:
        
            data_leads = data_leads[len(data_leads)//7:len(data_leads)//7*2]
            self.update_leads(data_leads, solusi, race, tujuan_kedatangan, kriteria, won_stage)
        print(len(data_leads))
        # print('time up lead 1 ', time.time() - a)
            
    @timing_val
    def up_lead_3(self):
        # a = time.time()
        print('='*7, 'ini up lead 3', '='*7)
        won_stage, solusi, race, kriteria, tujuan_kedatangan, data_leads = self.periperal_chat()
        
        if len(data_leads) >= 30:
            
            data_leads = data_leads[len(data_leads)//7*2:len(data_leads)//7*3]
            self.update_leads(data_leads, solusi, race, tujuan_kedatangan, kriteria, won_stage)
        print(len(data_leads))
        # print('time up lead 1 ', time.time() - a)
            
    @timing_val
    def up_lead_4(self):
        # a = time.time()
        print('='*7, 'ini up lead 3', '='*7)
        won_stage, solusi, race, kriteria, tujuan_kedatangan, data_leads = self.periperal_chat()
        
        if len(data_leads) >= 30:
            
            data_leads = data_leads[len(data_leads)//7*3:len(data_leads)//7*4]
            self.update_leads(data_leads, solusi, race, tujuan_kedatangan, kriteria, won_stage)
        print(len(data_leads))
        # print('time up lead 1 ', time.time() - a)
            
    @timing_val
    def up_lead_5(self):
        # a = time.time()
        print('='*7, 'ini up lead 3', '='*7)
        won_stage, solusi, race, kriteria, tujuan_kedatangan, data_leads = self.periperal_chat()
        
        if len(data_leads) >= 30:
            
            data_leads = data_leads[len(data_leads)//7*4:len(data_leads)//7*5]
            self.update_leads(data_leads, solusi, race, tujuan_kedatangan, kriteria, won_stage)
        print(len(data_leads))
        # print('time up lead 1 ', time.time() - a)
        
    @timing_val
    def up_lead_6(self):
        # a = time.time()
        print('='*7, 'ini up lead 3', '='*7)
        won_stage, solusi, race, kriteria, tujuan_kedatangan, data_leads = self.periperal_chat()
        
        if len(data_leads) >= 30:
            
            data_leads = data_leads[len(data_leads)//7*5:len(data_leads)//7*6]
            self.update_leads(data_leads, solusi, race, tujuan_kedatangan, kriteria, won_stage)
        print(len(data_leads))
        # print('time up lead 1 ', time.time() - a)
        
    @timing_val
    def up_lead_7(self):
        # a = time.time()
        print('='*7, 'ini up lead 3', '='*7)
        won_stage, solusi, race, kriteria, tujuan_kedatangan, data_leads = self.periperal_chat()
        
        if len(data_leads) >= 30:
            
            data_leads = data_leads[len(data_leads)//7*6:]
            self.update_leads(data_leads, solusi, race, tujuan_kedatangan, kriteria, won_stage)
        print(len(data_leads))
        # print('time up lead 1 ', time.time() - a)
            
            
            
            
            
    def update_leads(self, data_leads, data_solusi, data_race, data_tujuan_kedatangan, data_kriteria, won_stage):
        _logger.info('='*20 + 'run update leads' + '='*20)
        for data_lead in data_leads:
            try:
                url = f"https://service-chat.qontak.com/api/open/v1/rooms/{data_lead.room_id}"

                headers = {"Authorization": "Bearer qdAg6K2pVA10nNBMNdTUAsWs0KeoGuFOgk6qM16fZ6U"}
                # headers = {"Authorization": "Bearer qdAg6K2pVA10nNBMNdTUAsWs0KeoGuFOgk6qM16fZ6U"}

                response = requests.get(url, headers=headers)

            # with api.Environment.manage():
            #     new_cr = self.pool.cursor()
            #     self = self.with_env(self.env(cr=new_cr))
            # if True:
                # print(data_lead.room_id)
                # print('='*20)
                if response.json()['status'] != 'error':
                    data_lead_qontak = response.json()['data']
                    

                # update tag_race_tipe
                    if 'app' in data_lead_qontak['tags'] and data_lead.tujuan_id and data_lead.race_id:
                        cek_app = self.env['medical.appointment'].search_count([('room_id', '=', data_lead_qontak.get('last_message').get('room_id') )]) < 1
                        print('inini bukan sih? ', data_lead_qontak.get('last_message').get('room_id'))
                        if cek_app:
                        # bikin .app
                        # pass
                            gender, start, end, cabang, reschedule, jam_awal, weekday, no_hp = self.reparse_note(data_lead_qontak['note'])
                            print('ininiii??? ',gender, start, end, cabang, reschedule, jam_awal, weekday, no_hp)
                            agents = self.get_agent_des(data_lead_qontak['id'])
                            
                            
                            dokter_pilihan = ''
                            # self.env['res.partner'].search([('name', '=', str(cabang).upper() )]).id
                                                            
                            slot_jadwal = self.env['doctor.slot'].search([('institution_id','=', self.env['res.partner'].search([('id', '=', cabang.id )]).id )])
                            for _ in slot_jadwal:
                                # print('iniiiiiiii hari dokter ',_.weekday)
                                # print('iiiiiiiiiiiiiiiiiiiiiii jjjjjjjjjjjjjjjjj',_.weekday, weekday)
                                if int(_.weekday) == weekday+1 :
                                    dokter_pilihan = _.doctor_id.id
                                    break
                                else:
                                    dokter_pilihan = self.env['medical.physician'].search([('name', '=', 'Eye Care Profesional')]).id
                                
                                
                            data_lead.write({
                                'stage_id': won_stage,
                                'resolved': agents
                            })
                            data_pat = self.env['medical.patient'].create({
                                'partner_id': data_lead.partner_id.id,
                                'sex': gender,
                                'no_hp': no_hp,
                                'mobile': data_lead.partner_id.mobile if data_lead.partner_id.mobile[:3] == '62' else no_hp,
                                'race_id': data_lead.race_id.race_id.id,
                            })
                            data_lead.partner_id.write({
                                'is_patient': True,
                                'is_person': True,
                                'name': data_lead_qontak['name']
                            })
                            
                            self.env['medical.appointment'].create({
                                'patient': data_pat.id,
                                'appointment_sdate': start,
                                'appointment_edate': end,
                                'doctor': dokter_pilihan,
                                'race_tipe_id': data_lead.race_id.race_id.id,
                                # 'race_tipe_id': data_pat.race_id.id,
                                'tujuan_id': data_lead.tujuan_id.id if data_lead.tujuan_id else self.env['product.product'].search([('name', '=', 'FEE JASA')]).id,
                                'resolved': agents,
                                'institution': cabang.id,
                                'status': 'app_crs',
                                'room_id': data_lead.room_id,
                                'company_id': cabang.company_id.id,
                                'is_buatan_qontak': True
                            })
                            # self.env.cr.commit()
                    else:
                        for tag in data_lead_qontak['tags']:
                            tag = tag.upper()
                            if tag in data_kriteria :
                                data_lead.write({
                                    'kriteria_id': self.env['tag.kriteria'].search([('nama', '=', tag)]).id,
                                    'stage_id': self.env['tag.kriteria'].search([('nama','=', tag)]).stage_id.id
                                })
                            
                            if tag in data_race :
                                data_lead.write({
                                    'race_id': self.env['tag.race'].search([('nama', '=', tag)]).id
                                })
                            
                            if tag in data_tujuan_kedatangan :
                                data_lead.write({
                                    'tujuan_id': self.env['product.product'].search([('name', '=', tag)]).id
                                })
                                
                            if data_lead_qontak['name'] != data_lead.partner_id.name :
                                data_lead.partner_id.write({
                                    'name': data_lead_qontak['name']
                                })
                                
                        self.env.cr.commit()
            except:
                pass
            
            
    # def bikin_appointment(self, **data):
    #     print('ini start app', data['start'])
    #     print('ini end app', data['end'])
    #     dokter_pilihan = ''
        
    #     slot_jadwal = self.env['doctor.slot'].search([('institution_id','=', data['cabang'])])
    #     for _ in slot_jadwal:
    #         # print('iniiiiiiii hari dokter ',_.weekday)
    #         # print('iiiiiiiiiiiiiiiiiiiiiii jjjjjjjjjjjjjjjjj',_.weekday, data['weekday'])
    #         if int(_.weekday) == data['weekday'] :
    #             dokter_pilihan = _.doctor_id.id
    #             break
    #     else:
    #         dokter_pilihan = self.env['medical.physician'].search([('name', '=', 'Eye Care Profesional')]).id
        
    #     # slot_jadwal = self.env['doctor.slot'].search([('institution_id','=', data['cabang'])])
    #     # for _ in slot_jadwal:
    #         # print(int(_.weekday) ,'==', data['weekday'] ,'and', data['jam'] ,'>=', _.start_hour and data['jam'] ,'=', _.end_hour)
    #         # print(int(_.weekday) ,'==', data['weekday'] ,'and', data['jam'] ,'>=', _.start_hour ,'and', data['jam'] ,'<', _.end_hour)
    #         # if int(_.weekday) == data['weekday'] and data['jam'] >= _.start_hour and data['jam'] < _.end_hour:
    #         #     dokter_pilihan = _.doctor_id.id
    #         #     break
    #         # else:
    #         #     dokternya = self.env['res.partner'].search([('name', '=', 'Eye Care Profesional')]).id
    #         #     dokter_pilihan = self.env['medical.physician'].search([('res_partner_physician_id.name', '=', 'Eye Care Profesional')]).id
    #         #     print('inin print dokternyayaaa ',dokternya, dokter_pilihan)
    #         #     break
            
        
    #     self.env['medical.appointment'].sudo().create({
    #         'patient': self.env['medical.patient'].search([('partner_id', '=', data['partner_user'].id)], limit=1).id,
    #         'appointment_sdate': data['start'],
    #         'appointment_edate': data['end'],
    #         'doctor': dokter_pilihan,
    #         'race_tipe_id' : data['ini_crm']['race_id'].race_id.id,
    #         'tujuan_id': data['tujuan_kedatangan'].id if data['tujuan_kedatangan'].id else self.env['product.product'].search([('type','=','service')])[0].id,
    #         # 'service_id': self.env['product.product'].search([('type','=','service')])[0].id,
    #         'resolved': data['agents'],
    #         'institution': data['cabang'],
    #         'status': 'app_crs',
    #         'room_id': data['room_id'],
    #         # 'company_id': data['cabang'].company_id.id,
    #         'company_id': self.env['res.partner'].search([('id', '=', data['cabang'])]).company_id.id
    #     })
        
        
    #     lines = []
        
    #     crm = self.env['crm.lead'].search([( 'room_id','=',data['room_id'] )])
    #     is_app = self.env['medical.appointment'].search([( 'room_id','=',data['room_id'] )]).id
    #     # print('ininiiiiiiii app create', is_app, type(is_app))
    #     # if len(is_app) > 1:
    #     #     for _ in is_app:
    #     #         lines.append( (1,_,{'lead_id':crm.id}) )
    #     #     crm.write({
    #     #         'appointment_ids': lines
    #     #     })
    #     # else:
    #     crm.write({
    #         'appointment_ids': [(1,is_app,{'lead_id':crm.id})]
    #     })
        
    def get_agent_des(self, room):
        url = f"https://service-chat.qontak.com/api/open/v1/rooms/{room}/participants"

        querystring = {"type":"all", "limit":"1"}

        headers = {"Authorization": "Bearer qdAg6K2pVA10nNBMNdTUAsWs0KeoGuFOgk6qM16fZ6U"}

        response = requests.get(url, headers=headers, params=querystring)

        a = response.json()['data']

        lahah = []
        for _ in a:
            if _['type'] == 'Models::AgentParticipant':
                lahah.append(_['profile']['name'])
                # print('-'*20)
                
        return ",".join(lahah)
    
    
    def edit_appointment(self, **data):
        ini_partner = self.env['res.partner'].search([('mobile', '=', data['mobile']), ('name', '=', data['name'])]).id
        # pasien = 
        ini_app = self.env['medical.appointment'].search([('patient', '=', self.env['medical.patient'].search([('partner_id', '=', ini_partner)]).id)])
        date = ini_app.appointment_sdate
        print('iiiiiiiiiiiiiii in func edit app ',date,type(date), data['start'][:-3], type(data['start'][:-3])) #iliangin detik
        print('booooooooooooooollllllll', type(date))
        if type(date) != bool:
            print('printaannnnn date ', date.strftime('%Y-%m-%d %H:%M') , data['start'][:-3])
            if date.strftime('%Y-%m-%d %H:%M') != data['start'][:-3]:
                print('aaaaaaaaaaaa ok schedule')
                ini_app.write({
                    'appointment_sdate': data['start'],
                    'appointment_edate': data['end'],
                })
                
                
        # slot_jadwal = self.env['doctor.slot'].search([('institution_id','=', data['cabang'])])
        # for _ in slot_jadwal:
        #     print('iniiiiiiii hari dokter ',_.weekday)
        #     print('iiiiiiiiiiiiiiiiiiiiiii jjjjjjjjjjjjjjjjj',_.weekday, data['weekday'])
        #     if int(_.weekday) == data['weekday'] :
        #         ini_app.write({
        #             'doctor': _.doctor_id.id
        #         })    