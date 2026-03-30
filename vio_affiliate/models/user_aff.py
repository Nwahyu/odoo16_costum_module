from odoo import models, fields, api,_
from odoo.exceptions import UserError
import random
from ast import literal_eval

class aff_user(models.Model):
    _name = 'aff.user'
    _rec_name = 'nama'
    _inherit = ['mail.thread']
    _description = 'Data Affiliate VIO'

    nama = fields.Char(
        string='Nama Lengkap',
        required=True,
        help='Nama lengkap affiliate',
        translate=True
    )
    email = fields.Char(
        string='Email',
        required=True,
        help='Alamat email affiliate untuk login dan komunikasi',
        tracking=True
    )
    phone = fields.Char(
        string='Nomor Telepon',
        required=True,
        help='Nomor telepon/WhatsApp affiliate',
        tracking=True
    )
    sosmed = fields.Char(
        string='Sosial Media',
        help='Username atau link sosial media affiliate',
        tracking=True
    )
    token = fields.Char(
        string='Token Affiliate',
        tracking=True,
        help='Kode unik affiliate untuk tracking referral',
        copy=False
    )
    parent_token = fields.Char(
        string='Token Parent',
        tracking=True,
        help='Token affiliate yang merekrut affiliate ini (upline)',
        readonly=True
    )
    saldo_ready = fields.Integer(
        string='Saldo Ready',
        default=0,
        tracking=True,
        help='Saldo yang tersedia untuk dicairkan'
    )
    jumlah_klik = fields.Integer(
        string='Jumlah Klik',
        default=0,
        help='Total klik yang dihasilkan dari link affiliate'
    )
    point = fields.Integer(
        string='Point',
        default=0,
        tracking=True,
        help='Poin loyalitas yang dikumpulkan affiliate'
    )
    is_pasien = fields.Boolean(
        string='Pasien VIO',
        help='Menandakan apakah affiliate juga merupakan pasien VIO'
    )
    race = fields.Char(
        string='Race',
        help='Race untuk keperluan tracking',
        default='default'
    )

    domisili_kota_id = fields.Many2one(
        comodel_name='domisili.kota',
        string='Kota Domisili',
        help='Pilih kota tempat domisili affiliate',
        tracking=True
    )

    cabang_id = fields.Many2one(
        comodel_name='cabang.cabang',
        string='Cabang VIO',
        required=True,
        help='Pilih cabang VIO tempat affiliate terdaftar',
        tracking=True
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Perusahaan',
        help='Perusahaan yang berafiliasi',
        default=lambda self: self.env.company.id
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        ondelete='cascade',
        help='Partner yang terkait dengan affiliate ini',
        readonly=True
    )
    website_id = fields.Many2one(
        comodel_name='website',
        string='Website',
        help='Website yang digunakan untuk affiliate marketing',
        default=lambda self: self.env['website'].search([], limit=1).id
    )

    # sosmed = fields.Char('Sosial Media', related='partner_id.sosmed')
    medsos_ig = fields.Char(
        string='Instagram',
        related='partner_id.medsos_ig',
        readonly=False,
        help='Username Instagram affiliate'
    )
    medsos_tiktok = fields.Char(
        string='TikTok',
        related='partner_id.medsos_tiktok',
        readonly=False,
        help='Username TikTok affiliate'
    )
    cabang_bank = fields.Char(
        string='Cabang Bank',
        related='partner_id.cabang_bank',
        readonly=False,
        help='Cabang bank untuk rekening affiliate'
    )
    nama_rek = fields.Char(
        string='Nama Rekening',
        related='partner_id.nama_rek',
        readonly=False,
        help='Nama pemilik rekening bank'
    )
    no_rek = fields.Char(
        string='Nomor Rekening',
        related='partner_id.no_rek',
        readonly=False,
        help='Nomor rekening bank untuk pencairan saldo'
    )
    nama_bank = fields.Char(
        string='Nama Bank',
        related='partner_id.nama_bank',
        readonly=False,
        help='Nama bank untuk rekening affiliate'
    )

    state = fields.Selection(
        selection=[
            ('register', 'Mendaftar'),
            ('approve', 'Disetujui'),
            ('reject', 'Ditolak'),
            ('other', 'Lainnya'),
        ],
        string='Status',
        default='register',
        tracking=True,
        help='Status persetujuan affiliate'
    )

    def random_token(self):
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
        token = ""
        while True:
            print('random token affilaite ',token, len(token))
            # cek kepunyaan token
            if self.env['aff.user'].search([('token','=',token)]) or len(token) < 2:
                chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
                token = ''.join(random.SystemRandom().choice(chars) for i in range(5))
                token = 'vhv'+token
            else:
                break
        return token



    # def send_email(self, **kosong):
    #         # db = request.session.get('db')
    #         print('ininini send email dtaa self yaaa', self)
    #         # print('ininini dtaa wk yaaa', wk)
    #         print('ininini send email dtaa kosong yaaa', kosong)
    #         template_id = self.env.ref('vio_affiliate.join_affiliate_email')
    #         user_mail = self.env.user.partner_id.company_id.email or self.env.company.email
    #         # user_mail = self.env.company.email
    #         email_values = {"email_from":user_mail}
    #         print('haursnya ini self id' ,self.id, user_mail)
    #         # email_values = {"email_from":'"ini aku" <akunsimpan25@gmail.com>'}
    #         email_values = {"email_from":f'"ini aku" <{user_mail}>'}
    #         res = template_id.sudo().send_mail(self.id,force_send=True,email_values=email_values)
    #         # res = template_id.sudo().send_mail(self.id,force_send=True)

    def action_aprove(self):
        partner = self.env['res.partner'].create({
            'company_id':1,
            'name':self.nama,
            # 'token':token,
            'phone':self.phone,
            'email':self.email,
            'medsos_ig':self.sosmed
        })

        #cek lead or aff dari parent_token, cari parent, jika ada ditambah saldonya
        # if self.parent_token is not False:
        if self.parent_token:
            parent = self.env['aff.user'].search([('token', '=', self.parent_token)])
            parent.write({
                'saldo_ready':parent.saldo_ready+250
            })

            self.env['aff.trx'].create({
                'nama':self.partner_id.name,
                'user_id':self.id,
                'kategori_trx':'lead',
                'total_trx':0,
                'tipe_komisi':'fixed',
                'komisi':250,
                'status':'approve',
                'input_komisi':1,
                'token_affiliator':self.parent_token,
                'trx_date':fields.Date.today()
            })

            return super(aff_user, self).write({'state':'approve'})

        # bikin aff
        else:
            ini_data = {
                'token': self.random_token(),
                'partner_id':partner.id,
                'state': 'approve'
            }
            super(aff_user, self).write(ini_data)

            # bikin user account
            self.env['res.users'].sudo().with_context(no_reset_password=True).create({
                'partner_id':partner.id,
                'login':self.email,
                'password':'vio_user',
                'partner_id':partner.id,
                'groups_id': [( 4, self.env.ref('base.group_portal').id)]
            })

            template_id = self.env.ref('vio_affiliate.welcome_aff_email')
            user_mail = self.env.user.partner_id.company_id.email or self.env.company.email or self.env.user.partner_id.email
            email_values = {"email_from":f'"VIO - Vision Hero" <{user_mail}>'}
            res = template_id.sudo().send_mail(self.id,force_send=True,email_values=email_values)



        # cek lead atau affiliator
        # if self.parent_token:
        #     pass
        # else:
            # kirim email
            # template_id = self.env.ref('vio_affiliate.welcome_aff_email')
            # user_mail = self.env.user.partner_id.company_id.email or self.env.company.email or self.env.user.partner_id.email
            # email_values = {"email_from":f'"VIO - Vision Hero" <{user_mail}>'}
            # res = template_id.sudo().send_mail(self.id,force_send=True,email_values=email_values)


    def write(self, vals):
        if 'email' in vals:
            data_user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)])
            data_user.write({
                'login': vals['email']
            })
            self.partner_id.write({
                'email': vals['email']
            })
        return super(aff_user, self).write(vals)

        # print(self.partner_id)
        # return self.partner_id




    def action_reject(self):
          self.state = 'reject'
    def action_other(self):
          self.state = 'other'


    def akumulasi_klik(self):
        pass



    def unlink(self):
        data_user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)])
        data_user.unlink()
        self.partner_id.unlink()
        return super(aff_user, self).unlink()


class res_partner(models.Model):
    _inherit = 'res.partner'

    is_affiliate = fields.Boolean('is_affiliate')
    token = fields.Char(string='token')
    parent_token = fields.Char('parent_token')

    nik = fields.Char('nik', tracking=True)
    pekerjaan = fields.Char('pekerjaan', tracking=True)
    sosmed = fields.Char('Sosial Media')
    medsos_ig = fields.Char('medsos_ig', tracking=True)
    medsos_tiktok = fields.Char('medsos_tiktok', tracking=True)
    nama_bank = fields.Char('nama_bank', tracking=True)
    no_rek = fields.Char('no_rek', tracking=True)
    nama_rek = fields.Char('nama_rek', tracking=True)
    cabang_bank = fields.Char('cabang_bank', tracking=True)

    pw = fields.Char('pw', tracking=1)


class inherit_user(models.Model):
    _inherit = 'res.users'


    def write(self, vals):
        # print('iniiii valss ',vals)
        # aff = self.env['aff.user'].search([('partner_id', '=', self.partner_id.id)])
        if 'password' in vals:
            self.partner_id.write({
                'pw': vals['password']
            })

        return super(inherit_user, self).write(vals)


class domisili(models.Model):
    _name = 'domisili.kota'
    _description = 'domisili'
    _rec_name = 'domisili'


    domisili = fields.Char('nama kota')
