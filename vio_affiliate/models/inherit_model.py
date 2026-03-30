from odoo.addons.auth_signup.models.res_partner import SignupError, now
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime,time, timedelta
import logging

_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'
    _description = 'res.partner'
    
    
    kesempatan_reset_pw = fields.Integer('kesempatan_reset_pw', default=0)
    akhir_req_reset_pw = fields.Datetime('akhir_req_reet_pw')
    
    
    
class res_users(models.Model):
    _inherit = 'res.users'
    _description = 'res.users'
    
    
    
    def cron_reset_quota_pw(self):
        dat = self.search('kesempatan_reset_pw', '=', 5)
        for i in dat:
            i.sudo().create({
                'kesempatan_reset_pw': 0
            })
        
    
    # @api.model
    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """    
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(minutes=+5)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)
        
        
        template = self.env.ref('vio_affiliate.templt_reset_pw')
        body = f"""
        <p>Anda Mendapatkan email ini karena anda request reset password</p>
        <p>Jika anda tidak melakukan request, silakan abaikan email ini</p>
        <p><a href="{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}/web/reset_password?db={self.env.cr.dbname}&token={self.signup_token}">klik disini</a> untuk mengganti password</p>
        <br>
        <p>*Request hanya 5 menit sekali dan 3 kali per hari</p>
        """
        
        email_values = {
            'email_cc': False,
            'auto_delete': False,
            'message_type': 'user_notification',
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
            'email_from': f"'VIO - Reset Password' <{self.company_id.email}>",
            'body_html': body
        }
        
        print(self)
        if not self.login: raise UserError(_("Cannot send email: user %s has no email address.", self.name))
        with self.env.cr.savepoint():
            print(f'iniiiiiiii {self.kesempatan_reset_pw+1} {type(self.kesempatan_reset_pw)} {now} {type(now)}')
            kesempatan = self.kesempatan_reset_pw+1
            batas_req_pw = time(0, 5, 0)
            batas_req_pw = timedelta(hours=batas_req_pw.hour, minutes=batas_req_pw.minute, seconds=batas_req_pw.second)
            print(f'pengurangan datetimeeeee {type(datetime.now())} {type(self.akhir_req_reset_pw)} {batas_req_pw} {type(batas_req_pw)}')
            print('aaaa')
            if type(datetime.now()) == type(self.akhir_req_reset_pw):
                if datetime.now() - self.akhir_req_reset_pw >= batas_req_pw and self.kesempatan_reset_pw < 5:
                    self.write({
                        'kesempatan_reset_pw': self.kesempatan_reset_pw+1,
                        'akhir_req_reset_pw': datetime.now()
                    })
                    template.sudo().send_mail(self.id, force_send=True, email_values=email_values)
                    _logger.info("sukses kirim email reset ke user <%s> email <%s>", self.name, self.login)
            else:
                self.write({
                    'kesempatan_reset_pw': self.kesempatan_reset_pw+1,
                    'akhir_req_reset_pw': datetime.now()
                })
                template.sudo().send_mail(self.id, force_send=True, email_values=email_values)
                _logger.info("sukses kirim email reset ke user <%s> email <%s>", self.name, self.login)
        _logger.info("Password reset email sent for user <%s> to <%s>", self.login, self.name)