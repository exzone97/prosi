from openerp.osv import osv, fields
from openerp import tools, api, SUPERUSER_ID
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

# ===============================================================================================================================

class product_template(osv.osv):

	_inherit = 'product.template'

	_columns = {
		'member_point_settings': fields.one2many('product.member.point.setting', 'product_id', 'Member Point Settings'),
	}

class product_member_point_setting(osv.osv):

	_name = 'product.member.point.setting'
	_description = 'Product member point setting'

	_columns = {
		'product_id': fields.many2one('product.template', 'Product'),
		'membership_level_id': fields.many2one('membership.point.level', 'Level', required=True),
		'factor': fields.float('Factor', required=True, digits_compute=dp.get_precision('Membership Factor Decimal')),
		'rounding': fields.integer('Rounding', required=True),
	}

	_sql_constraints = [
		('unique_product_level','UNIQUE(product_id,membership_level_id)',_('Level must be unique per product.'))
	]

# ===============================================================================================================================

class membership_point_member(osv.osv):

	_inherit = 'membership.point.member'

	_columns = {
		'partner_id': fields.many2one('res.partner', string='Related Dentist/Clinic',
			domain=[('customer','=',True)], readonly=True, track_visibility='onchange'),
		'member_type': fields.selection((
			('personal','Individual'),
			('institution','Clinic'),
			), 'Member Type'),
		'password': fields.char('Initial Password', size=255, search=False),
		'birth_date': fields.date('Birth Date'),
	}

	def generate_member_id(self, cr, uid, member):
	# ambil tahun
		year = datetime.now().year
		year_part = str(year)[1:] # tahun yang diambil cuman 3 digit
	# ambil nomor member terakhir
		member_ids = self.search(cr, uid, [
			('id','!=',member.id),
			('register_date','>=','%s-01-01' % year),
			('register_date','<=','%s-12-31' % year),
		], order="member_id DESC")
		if len(member_ids) == 0:
			new_number = 1
		else:
			last_member = None
			for member in self.browse(cr, uid, member_ids):
				if not member.member_id: continue
				last_member = member
				break
			if not last_member:
				new_number = 1
			else:
				new_number = int(last_member.member_id[3:]) + 1
		number_part = str(new_number).zfill(5)
		return "%s%s" % (year_part,number_part)

	def get_member_fullname(self, member):
		return super(membership_point_member, self).get_member_fullname(member).upper()

	def create(self, cr, uid, vals, context={}):
	# capitalize field2 teks
		cap_fields = ['name','last_name','street','street2','city']
		for field in cap_fields:
			if vals.get(field, None) == None: continue
			try:
				vals[field] = vals[field].upper()
			except AttributeError:
				pass
		return super(membership_point_member, self).create(cr, uid, vals)

	def unlink(self, cr, uid, ids, context={}):
	# kalau hapus member, semua MO yang pernah di member ini akan dianggap non-member
	# pengosongan field member_id di MO sudah otomatis via mekanisme ondelete set null
		cr.execute("""
			UPDATE mrp_production SET is_member=False
			WHERE member_id in (%s)
		""" % ",".join([str(i) for i in ids]))
	# non-aktifkan user terkait member ini
		user_obj = self.pool.get('res.users')
		for member_id in ids:
			user_data = self.get_user_by_member_id(cr, uid, member_id)
			if not user_data: continue
			user_obj.write(cr, uid, [user_data.id], {'active': False})
		return super(membership_point_member, self).unlink(cr, uid, ids, context)

	def action_activate(self, cr, uid, ids, context={}):
	# 20171121: ketika activate, bikin data dentist baru
		partner_obj = self.pool.get('res.partner')
		for member in self.browse(cr, uid, ids, context):
			partner_data = {
				'name': self.get_member_fullname(member),
				'street': member.street,
				'street2': member.street2,
				'zip': member.zip,
				'phone': member.phone,
				'city': member.city,
				'mobile': member.mobile,
				'customer': True,
				'is_doctor': (member.member_type == 'personal'),
				'is_company': (member.member_type == 'institution'),
				'email': member.email,
				'member_id': member.member_id,
				'birth_date': member.birth_date,
			}
			partner_id = partner_obj.create(cr, uid, partner_data)
			self.write(cr, uid, [member.id], {'partner_id': partner_id})
		return super(membership_point_member, self).action_activate(cr, uid, ids, context)

# ==========================================================================================================================

class membership_point_institution_member(osv.osv):

	_inherit = 'membership.point.institution.member'

	_columns = {
		'member_id': fields.many2one('membership.point.member', 'Doctor Name'),
	}

# ===============================================================================================================================

class membership_point_log(osv.osv):

	_inherit = 'membership.point.log'

	_columns = {																											#PROSI
		'special_promo_id': fields.many2one('membership.point.special.promo', 'Special Promo ID', ondelete='set null')		#PROSI
	}																														#PROSI

	def _additional_log_detail(self, cr, uid, line, log_data):
		mrp_obj = self.pool.get('mrp.production')
		mo_ids = mrp_obj.search(cr, uid, [('invoice_id','=',log_data.invoice_id.id)])
		if len(mo_ids) > 0:
			mo_data = mrp_obj.browse(cr, uid, mo_ids[0])
			line.update({
				'patient_name': mo_data.patient_name and mo_data.patient_name or '-',
				'mo_description': mo_data.description,
			})
		return line

	@api.model
	def cron_autoexpire_point_log(self):
		now = datetime.now().replace(hour=0, minute=0, second=0) - timedelta(hours=7)
		expire_limit = now - relativedelta(months=3)
		point_logs = self.env['membership.point.log'].search([
			('create_date','<=',expire_limit.strftime('%Y-%m-%d %H:%M:%S')),
			('state','in',['draft']),
		])
		if len(point_logs) == 0: return
		point_logs.write({'state': 'expired'})