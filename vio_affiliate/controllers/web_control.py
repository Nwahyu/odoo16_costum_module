from odoo import _, api, fields, models,http
from odoo.http import request
import werkzeug, logging
from odoo.addons.portal.controllers.portal import CustomerPortal as custportal
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
# from odoo.addons.auth_signup.
from odoo.exceptions import UserError
from datetime import datetime, timedelta

from odoo.addons.portal.controllers.portal import CustomerPortal
_logger = logging.getLogger(__name__)

from subprocess import Popen, PIPE
import json

class subCustomerPortal(CustomerPortal):
    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        """
        Handle user account data form.
        
        This method displays the personal data form and processes
        form submissions. It passes cabang data for the dropdown.
        
        :param redirect: Redirect URL
        :param post: Form data from POST request
        :return: Rendered form template or redirect
        """
        values = request.env.user
        if request.httprequest.method == 'POST':
            request.env.user.write(post)
            print('ininini dari account form data diri di aff ', post)
            return request.redirect('/my/affiliate')
        print('ininininini daru account detail ', values)

        data = {
            'nik': values.nik,
            'name': values.name,
            'phone': values.phone,
            'email': values.email,
            'city': values.city,
            'ig': values.medsos_ig,
            'tiktok': values.medsos_tiktok,
            'pekerjaan': values.pekerjaan,
            'cabang_id': values.cabang_bank.id if values.cabang_bank else '',
            'nama_bank': values.nama_bank,
            'no_rek': values.no_rek,
            'nama_rek': values.nama_rek,
            'list_cabang': request.env['cabang.cabang'].search([('active', '=', True)]),
        }
        return request.render('vio_affiliate.form_data_diri', data)


class affiliate(AuthSignupHome):
    
    @http.route("/daftar", auth="public", website=True, type="http")
    def daftar(self, **kw):
        """
        Render the affiliate registration form.
        
        This method prepares the domisili and cabang data
        and passes them to the registration form template.
        
        :param kw: URL parameters
        :return: Rendered form template
        """
        kw['domisili'] = request.env['domisili.kota'].search([])
        kw['cabang'] = request.env['cabang.cabang'].search([('active', '=', True)])
        return request.render('vio_affiliate.aff_form_aff', kw)
    
    @http.route("/affiliate/join", auth="public", website=True, type="http", methods=["POST","GET"])
    def joinan(self, **kw):
        """
        Handle affiliate registration form submission.
        
        This method processes the registration form data,
        creates a new affiliate user record, and handles
        duplicate email validation.
        
        :param kw: Form data from POST request
        :return: Rendered thank you page or redirect
        """
        if request.httprequest.method == 'POST':
            data = request.env['aff.user'].search([('email', '=', kw['email'])], limit=1)
            if data:
                value = {
                    'headline': 'EMAIL SUDAH TERDAFTAR PADA AKUN LAIN',
                    'p_head': 'Email anda sudah terdaftar, Jika ada pertanyaan silahkan untuk menghubungi kami.',
                    'btn': {
                        'cond':True,
                        'href':'/',
                        'txt':'Home'
                    },
                    'penjelasan': ''
                }
                return request.render('vio_affiliate.thx_page', value)
            else:
                print('inini data ',kw)
                data = request.env['aff.user'].create({
                    'nama': kw['name'],
                    'email': kw['email'].lower(),
                    'phone': kw['phone'],
                    'sosmed': 'instagram.com/'+kw['sosmed'],
                    'is_pasien': kw['is_pasien'] if 'is_pasien' in kw else '',
                    'race': kw['race'],
                    'domisili_kota_id': kw['domisili_id'],
                    'cabang_id': kw['cabang_id']
                })
                # print('terima kasih sudah daftar')
                
                value = {
                    'headline': 'TERIMA KASIH SUDAH MENDAFTAR, CEK EMAIL MAKSIMAL 2x24 JAM',
                    'p_head': 'Terima kasih telah mendaftar, kami akan meninjau pendaftaran anda dan akan memberikan informasi selanjutnya melalui email. Mohon cek email anda secara berskala.',
                    'btn': {
                        'cond':True,
                        'href':'/',
                        'txt':'Home'
                    },
                    'penjelasan': ''
                }
                return request.render('vio_affiliate.thx_page', value)
                # data.send_email()
                # return werkzeug.utils.redirect(f"https://wa.me/62811244839?text=hallo%20saya%20{kw['name']}%20dan%20ingin%20bertanya%20tentang%20mata%20saya.%0A%23ViRo")

                
        else:
            # werkzeug.utils.redirect('/register%s' % qcontext)
            return werkzeug.utils.redirect('/')
            

    @http.route(["/my/affiliate"], auth="user", website=True, type="http", methods=["GET"])
    def affiliate_home(self):
        """
        Display affiliate dashboard home page.
        
        This method gathers affiliate statistics and data
        to display on the dashboard including saldo, leads,
        and klik count.
        
        :return: Rendered affiliate home template
        """
        data_user = request.env['aff.user'].search([('partner_id', '=', request.env.user.partner_id.id)])
        data_payout = request.env['payout.trx'].search([('user_id', '=', data_user.id)])
        saldo = data_user.saldo_ready
        if data_payout:
            for _ in data_payout:
                saldo -= _.jumlah_payout
                
        token = data_user.token
        lead = request.env['aff.user'].search_count([('parent_token','=',data_user.token)])
        base_url = request.website.domain

        if request.env.user.has_group('base.group_user'):
            klik_admina = sum(request.env['aff.user'].search([('parent_token', '=', False)]).mapped('jumlah_klik'))
        else:
            klik_admina = data_user.jumlah_klik
                
        values = {
            'token': str(token),
            'data_user': data_user,
            'url': str(base_url[8:] if base_url else 'Error_url_not_found') + '/VocP?token=' + str(token),
            "affiliate_key": token,
            "refferal": lead,
            'klik': klik_admina,
            'point': data_user.point,
            'saldo': saldo,
            'page_name': 'Vio | Vision Hero',
            'list_cabang': request.env['cabang.cabang'].search([('active', '=', True)]),
        }
        return request.render('vio_affiliate.portal_my_affiliate_home', values)
    
    
    # redirect if user internal
    @http.route(["/web/login", "/*/web/login"], type='http', auth="public", website=True)
    # @http.route(["/*/web/login"], type='http', auth="public", website=True)
    def web_login(self, redirect=None, **kw):
        response = super().web_login(redirect='/my/affiliate', **kw)
        if request.env.user.has_group('base.group_user'):
            return super().web_login(**kw)
        return response
    
    
    # @http.route(['/VocP'], type='http', auth='public', website=True)
    def lead_daftar_homepage(self, **kw):
        # if request.env['ir.http'].session_info()['uid'] is None and not request.env['ir.http'].is_a_bot():
        if request.httprequest.environ['REMOTE_ADDR'] not in [ i.ip for i in request.env['aff.ip.record'].search([('token', '=', kw['token'] )]) ]:
                request.env['aff.user'].search([('token', '=', kw['token'])]).jumlah_klik += 1
                request.env['aff.ip.record'].create({
                    'ip': request.httprequest.environ['REMOTE_ADDR'],
                    'token': kw['token']
                })
        
        if 'token' in kw:
            value ={
                    'token':kw['token']
                }
            return request.render('vio_affiliate.web_form_satu', value)
        else:
            return werkzeug.utils.redirect('/daftar')
    
    
    @http.route(['/VocP'], type='http', auth='public', website=True)
    def daftar_lead(self, **kw):
        # if request.env['ir.http'].session_info()['uid'] is None and not request.env['ir.http'].is_a_bot():
        if request.env['ir.http'].session_info()['uid'] is None:
            if request.httprequest.environ['REMOTE_ADDR'] not in [ i.ip for i in request.env['aff.ip.record'].search([('token', '=', kw['token'] )]) ]:
                    request.env['aff.user'].search([('token', '=', kw['token'])]).jumlah_klik += 1
                    request.env['aff.ip.record'].create({
                        'ip': request.httprequest.environ['REMOTE_ADDR'],
                        'token': kw['token']
                    })
        return werkzeug.utils.redirect(f"https://wa.me/6281717111172?text=hallo%20saya%20ingin%20bertanya%20tentang%20penglihatan%20saya.%0A%23{kw['token']}")
    
    @http.route(['/lead-daftar'], type='http', auth='public')
    def print_data(self, **kw):
        _logger.info(f'ini daftar lead {kw}')
        if request.httprequest.method == 'POST':
            data = request.env['aff.user'].search([('phone', '=', kw['number'])])
            if data :
                value = {
                    'headline': 'anda sudah terdaftar',
                    'p_head': 'email anda sudah terdaftar',
                    'btn': {
                        'cond':True,
                        'href':'/',
                        'txt':'Home'
                    },
                    'penjelasan': 'ini penjelasan'
                }
                return request.render('vio_affiliate.thx_page', value)
            else:
                data = request.env['aff.user'].create({
                    'nama': kw['nama'],
                    'email': kw['email'],
                    'parent_token': kw['token'] if kw['token'] else '',
                    'phone': kw['number']
                })
                return werkzeug.utils.redirect(f"https://wa.me/6281717111172?text=hallo%20saya%20{kw['nama']}%20dan%20saya%20ingin%20bertanya%20tentang%20penglihatan%20saya.%0A%23{kw['token']}")
                
        else:
            return werkzeug.utils.redirect('/')
            
    @http.route(['/my/referrals'], type='http', auth='user', methods=["GET"], website=True)            
    def list_reff(self, **kw):
        print('ini dari my reff ',kw)
        print('ini dari my reff ', request.env.user)
        
        affnya_user = request.env['aff.user'].search([('partner_id','=',request.env.user.partner_id.id)])
        print('aff ',affnya_user, affnya_user.token)
        # lead= request.env['aff.user'].search([('parent_token','=',affnya_user.token)])
        value = {
            'lead': request.env['aff.user'].search([('parent_token','=',affnya_user.token)], limit=25),
        }
        print('ini vaue coy ',value)
        return request.render('vio_affiliate.web_list_lead', value)
    
    @http.route(['/my/saldo'], type='http', auth='user', methods=["GET"], website=True)
    def list_saldo(self, **kw):
        data_user = request.env['aff.user'].search([('partner_id', '=', request.env.user.partner_id.id)])
        trx = request.env['aff.trx'].search([('token_affiliator', '=', data_user.token)], limit=200)
        value = {
            'trx':trx
        }
        return request.render('vio_affiliate.web_list_trx', value)


    