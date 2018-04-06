from openerp import http
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta, date
import re
import  werkzeug
import json as json

class web(http.Controller):

# ==========================================================================================================================

	@http.route('/home', auth='user', type="http", website=True)
	def home(self, **kw):
		return http.request.render('membership_point.home', {})

# ==========================================================================================================================

	@http.route('/vouchers', auth='user', type='http', website=True)
	def vouchers(self, **kw):

		uid = http.request.env['membership.point.member'].get_member_by_uid
		mode = http.request.env['membership.point.voucher.setting']
		vouc = mode.search([['is_purchaseable', '=', 'True'],['voucher_type','=','member']],order="write_date desc")

		return http.request.render('membership_point.vouchers', {
			'ids' : uid,
			'vouchers' : vouc,
		})

# ==========================================================================================================================

	@http.route('/vouchers/detail/<int:id>', auth='user', type='http', website=True)
	def detail(self, id):

		model_user = http.request.env['res.users']
		id_user =	model_user._uid
		model_member = http.request.env['membership.point.member']
		member_id = model_member.env['membership.point.member'].get_member_by_uid(id_user)
		member = model_member.search([['id','=',member_id.id]])
		mode = http.request.env['membership.point.voucher.setting']
		vouc = mode.search([['is_purchaseable', '=', 'True'],['voucher_type','=','member']])

		return http.request.render('membership_point.detail', {
			'member' : member,
			'id' : id,
			'vouchers' : vouc,
		})

# ==========================================================================================================================

	@http.route('/vouchers/purchase', auth='user', type='http', website=True)
	def purchase(self, **kw):


		model_user = http.request.env['res.users']
		id_user =	model_user._uid
		model_member = http.request.env['membership.point.member']
		member_id = model_member.env['membership.point.member'].get_member_by_uid(id_user)
		member = model_member.search([['id','=',member_id.id]])
		model_voucher_setting = http.request.env['membership.point.voucher.setting']
		vouc = model_voucher_setting.search([['id', '=', int(kw['voucher_id']) ]])
		vouc.purchase_member_voucher(member_id, int(kw['qty']))

		return werkzeug.utils.redirect('/mypurchases')

# ==========================================================================================================================

	@http.route('/mypurchases', auth='user', type='http', website=True)
	def mypurchases(self, **kw):

		fmt = '%Y-%m-%d'
		model_user = http.request.env['res.users']
		id_user =	model_user._uid
		model_member = http.request.env['membership.point.member']
		member_id = model_member.env['membership.point.member'].get_member_by_uid(id_user)
		model_voucher = http.request.env['membership.point.voucher']
		vouc = model_voucher.search([['member_id','=', member_id.id]], order="expired_date asc")
		# d1 = []

		return http.request.render('membership_point.mypurchases', {
			'vouchers' : vouc,
		})

# ==========================================================================================================================

	@http.route('/mypurchases/generated',  auth="public", website=True, type='http')
	def mypurchases_generated(self, **kw):

		fmt = '%Y-%m-%d'
		model_user = http.request.env['res.users']
		id_user =	model_user._uid
		model_member = http.request.env['membership.point.member']
		member_id = model_member.env['membership.point.member'].get_member_by_uid(id_user)
		model_voucher = http.request.env['membership.point.voucher']
		vouchers = model_voucher.search([['member_id','=', member_id.id],['state','=', 'generated']], order="expired_date asc")
		today_date = datetime.now()
		result = {}
		result['state'] = 'berhasil'
		result['res'] = []
		

		for voucher in vouchers:
			temp = int((today_date-datetime.strptime(voucher.expired_date, fmt)).days)
			result['res'].append({"name":voucher.setting_id.name,
					 "img":voucher.setting_id.thumbnail,
					 "number":voucher.name,
					 "description":voucher.setting_id.description,
					 "tnc":voucher.setting_id.terms_and_conditions,
					 "expired_date":voucher.expired_date,
					 "today_date": temp
					 })


		return  json.dumps(result)

		
# ==========================================================================================================================

	@http.route('/mypurchases/used',  auth="public", website=True, type='http' )
	def mypurchases_used(self, **kw):


		model_user = http.request.env['res.users']
		id_user =	model_user._uid
		model_member = http.request.env['membership.point.member']
		member_id = model_member.env['membership.point.member'].get_member_by_uid(id_user)
		model_voucher = http.request.env['membership.point.voucher']
		vouchers = model_voucher.search([['member_id','=', member_id.id],['state','=', 'used']], order="expired_date asc")
		result = {}
		result['state'] = 'berhasil'
		result['res'] = []


		for voucher in vouchers:
			result['res'].append({"name":voucher.setting_id.name,
					 "img":voucher.setting_id.thumbnail,
					 "number":voucher.name,
					 "description":voucher.setting_id.description,
					 "tnc":voucher.setting_id.terms_and_conditions,
					 "expired_date":voucher.expired_date,
					 "usage_date":voucher.usage_date
					 })

		return json.dumps(result)


# ==========================================================================================================================

	@http.route('/mypurchases/expired',  auth="public", website=True, type='http')
	def mypurchases_expired(self, **kw):


		model_user = http.request.env['res.users']
		id_user =	model_user._uid
		model_member = http.request.env['membership.point.member']
		member_id = model_member.env['membership.point.member'].get_member_by_uid(id_user)
		model_voucher = http.request.env['membership.point.voucher']
		vouchers = model_voucher.search([['member_id','=', member_id.id],['state','=', 'expired']], order="expired_date asc")
		result = {}
		result['state'] = 'berhasil'
		result['res'] = []

		for voucher in vouchers:
			result['res'].append({"name":voucher.setting_id.name,
					 "img":voucher.setting_id.thumbnail,
					 "number":voucher.name,
					 "description":voucher.setting_id.description,
					 "tnc":voucher.setting_id.terms_and_conditions,
					 "expired_date":voucher.expired_date
					 })

		
		return json.dumps(result)



