from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime, re, time

class aff_transaksi(models.Model):
    _name = 'aff.trx'
    _description = 'Transaksi Afiliasi'
    
    input_komisi = fields.Boolean(
        string='Komisi Sudah Dihitung',
        default=False,
        help='Menandakan apakah komisi untuk transaksi ini sudah dihitung atau belum'
    )

    id_trx = fields.Char(
        string='ID Transaksi',
        help='Identifikasi unik untuk transaksi afiliasi'
    )
    nama = fields.Char(
        string='Nama',
        help='Nama afiliator yang melakukan transaksi'
    )
    total_trx = fields.Integer(
        string='Total Transaksi',
        help='Total nilai transaksi dalam rupiah'
    )
    token_affiliator = fields.Char(
        string='Token Afiliator',
        help='Kode token unik untuk mengidentifikasi afiliator'
    )
    user_id = fields.Many2one(
        'aff.user',
        string='User Transaksi',
        help='Referensi ke user afiliator yang melakukan transaksi'
    )
    kategori_trx = fields.Char(
        string='Kategori Transaksi',
        help='Kategori atau jenis transaksi afiliasi'
    )
    
    persen_komisi = fields.Float(
        string='Persentase Komisi',
        help='Besaran persentase komisi yang didapatkan dari transaksi'
    )
    komisi = fields.Integer(
        string='Nominal Komisi',
        help='Nilai komisi dalam rupiah yang didapatkan dari transaksi'
    )
    tipe_komisi = fields.Selection([
        ('fixed', 'Nominal Tetap'),
        ('persen', 'Persentase'),
    ],
        string='Tipe Komisi',
        required=True,
        default='fixed',
        help='Menentukan apakah komisi dihitung dengan nominal tetap atau persentase'
    )
    
    status = fields.Selection([
        ('waiting', 'Menunggu'),
        ('approve', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ],
        string='Status',
        default='waiting',
        help='Status persetujuan untuk transaksi afiliasi'
    )
    
    trx_date = fields.Date(
        string='Tanggal Transaksi',
        help='Tanggal transaksi afiliasi dilakukan'
    )
    
    
    def approve(self):
        self.status = 'approve'
        
    def reject(self):
        self.status = 'rejected'

    def itung_komisi(self):
        # first_time = datetime.datetime.now()
        
        # cek batas bawah
        batas_bawah = datetime.datetime.today()-datetime.timedelta(days=60)
        data = self.env['aff.trx'].search(['&',('create_date','>', batas_bawah.strftime('%Y-%m-%d %H:%M:%S')), ('create_date','<',datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))])
        
        if data:
            for _ in data:
                if _.input_komisi == 0:
                    if _.tipe_komisi == 'persen':
                        _.komisi = _.total_trx * (_.persen_komisi / 100)
                
                # cek pernah diitung atau belum
                    # itung dan input
                    affiliatornya = self.env['aff.user'].search([ ('token', '=', _.token_affiliator) ], limit=1)
                    print('niini isaldo affiloator ', affiliatornya)
                    # saldo_affiliatornya += _.komisi
                    affiliatornya.write({
                        'saldo_ready': affiliatornya.saldo_ready + _.komisi
                    })
                    _.input_komisi = 1
                    
                    # assign yg trx
                    _.user_id = self.env['aff.user'].search([('nama','=', _.nama)], limit=1)
                    _.trx_date = fields.Date.today()
                    
        
        

class payout_trx(models.Model):
    _name = 'payout.trx'
    _description = 'Transaksi Payout Afiliasi'
    _rec_name = 'nama'
    
    input_komisi = fields.Boolean(
        string='Komisi Sudah Dihitung',
        default=False,
        help='Menandakan apakah komisi untuk transaksi payout ini sudah dihitung atau belum'
    )
    
    nama = fields.Char(
        string='Nama',
        help='Nama untuk transaksi payout'
    )
    user_id = fields.Many2one(
        'aff.user',
        string='User',
        help='Referensi ke user afiliator yang melakukan transaksi payout'
    )
    token_affiliator = fields.Char(
        string='Token Afiliator',
        help='Kode token unik untuk mengidentifikasi afiliator dalam transaksi payout'
    )
    jumlah_payout = fields.Integer(
        string='Jumlah Payout',
        help='Besaran nilai payout dalam rupiah yang akan dikirimkan'
    )
    
    trx_date = fields.Date(
        string='Tanggal Kirim',
        help='Tanggal pengiriman transaksi payout dilakukan'
    )
    
    
    @api.model
    def create(self, vals):
        print('inin vals ', vals)
        print('inin vals ', self)
            # pass
        # vals['input_komisi'] = 1
        # create trx
        vals['nama'] = 'payout'
        self.env['aff.trx'].create({
            'nama':'payout',
            'kategori_trx': 'payout',
            'total_trx': 0,
            'input_komisi': 0,
            'tipe_komisi': 'fixed',
            'token_affiliator': vals['token_affiliator'],
            'komisi': int(vals['jumlah_payout']) * -1,
            'status': 'approve',
            'trx_date': vals['trx_date']
        })
        return super(payout_trx, self).create(vals)
    