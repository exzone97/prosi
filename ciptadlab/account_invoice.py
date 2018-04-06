from openerp import models, fields, api, _
from openerp.osv import osv, fields
import re
from datetime import datetime, timedelta, date
from openerp import tools, SUPERUSER_ID
import base64, csv, StringIO

class account_invoice(osv.osv):

	_inherit = 'account.invoice'

	@api.multi
	def confirm_paid(self):
		super(account_invoice, self).confirm_paid()
	# ketika invoice dibayar, set tanggal bayarnya yaitu tanggal payment pertama
		payment_date = date.today()
		for payment in self.payment_ids:
			if payment.date:
				payment_date = payment.date
			elif payment.date_created:
				payment_date = payment.date_created
			break # ambil payment yang pertama aja. asumsi tidak ada backdate payment sedemikian sehingga tanggal payument yang kedua lebih dulu dari yang pertama

		promo_obj = self.pool.get('membership.point.special.promo')																	#PROSI
		point_obj = self.pool.get('membership.point.log')																			#PROSI
		member_obj = self.pool.get('membership.point.member')																		#PROSI
		for invoice in self:																										#PROSI
			member_id = invoice.member_id.id																						#PROSI
			member = member_obj.browse(self.env.cr, self.env.uid, member_id)														#PROSI
			current_member_level = member.current_level																				#PROSI
			point_ids = point_obj.search(self.env.cr, self.env.uid, [('invoice_id','=',invoice.id)])								#PROSI
			current_promo = promo_obj.get_current(self.env.cr, self.env.uid, payment_date)											#PROSI
			if (current_promo):																										#PROSI
				multiply = 0																										#PROSI
				fmt = '%Y-%m-%d'																									#PROSI
				temp_invoice_pay_before = current_promo.invoice_paid_before															#PROSI
				temp_invoice_generate_date = invoice.date_invoice																	#PROSI
				temp_invoice_payment_date = payment_date																			#PROSI
				d1 = datetime.strptime(temp_invoice_generate_date, fmt)																#PROSI
				d2 = datetime.strptime(temp_invoice_payment_date, fmt)																#PROSI
				dayDiff = int((d2-d1).days)																							#PROSI
				for multiplier in current_promo.multipliers_ids:																	#PROSI
					if multiplier.level_id.id == current_member_level.id:															#PROSI
						multiply = multiplier.multiplier																			#PROSI
						break																										#PROSI
				if multiply > 0 and dayDiff <= temp_invoice_pay_before:																#PROSI
						point_log = point_obj.browse(self.env.cr, self.env.uid, point_ids[0])										#PROSI
						point_obj.write(self.env.cr, self.env.uid, [point_log.id],{'point_in':point_log.point_in * multiply})		#PROSI
		super(account_invoice, self).confirm_paid()																					#PROSI

		return self.write({'payment_date': payment_date})

	@api.model
	def calculate_invoice_point(self, member, invoice_line):
	# ambil nilai uang dari mo ini
		amount = invoice_line.price_subtotal
	# ambil settingan terakhir. kalau productnya ngga ada setting, ya udah
		setting = invoice_line.product_id.member_point_settings
		if not setting: return 0
	# dapatkan setting line berdasarkan level member saat ini
		used_setting_line = None
		for setting_line in setting:
			if setting_line.membership_level_id.id == member.current_level.id:
				used_setting_line = setting_line
				break
		if not used_setting_line: return 0
	# hitung poin beserta pembulatannya
		point = used_setting_line.factor * amount / 1000
		point = point - (point % used_setting_line.rounding)
		return point


