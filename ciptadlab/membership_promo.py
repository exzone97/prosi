import datetime
from openerp import models, fields, api
from openerp.exceptions import ValidationError

# ==========================================================================================================================

class membership_point_voucher_setting(models.Model):
	_inherit = 'membership.point.voucher.setting'

	voucher_prefix = fields.Char('Voucher Prefix', size=4, required=True)

	@api.constrains('voucher_prefix')
	def _check_voucher_prefix(self):
		for record in self:
			if not record.voucher_prefix.isdigit():
				raise ValidationError('Voucher prefix must be a number.')
			elif len(record.voucher_prefix) != 4:
				raise ValidationError('Voucher prefix must be 4 digits.')

# ==========================================================================================================================

class membership_point_voucher(models.Model):
	_inherit = 'membership.point.voucher'

	def generate_number(self, vals):
		voucher_prefix = self.env['membership.point.voucher.setting'].browse(vals['setting_id'])[0].voucher_prefix
		year = datetime.datetime.now().strftime("%Y")
		voucher_prefix = ('%s%s' % (voucher_prefix, year))

		latest_voucher = self.search([('name', 'like', voucher_prefix)], order="name DESC", limit=1)
		if len(latest_voucher) == 0:
			new_number = "%s00000001" % voucher_prefix
		else:
			latest_voucher = latest_voucher.name[8:]
			new_number = "%s%08d" % (voucher_prefix, int(latest_voucher)+1)

		return new_number
		
# ==========================================================================================================================

class membership_point_special_promo(models.Model):
	_name = 'membership.point.special.promo'
	_inherit = 'chjs.dated.setting'
	_description = 'Membership point special promo'

	invoice_paid_before = fields.Integer('Invoice Paid Before', required=True)
	multipliers_ids = fields.One2many('membership.point.special.promo.multiplier','header_id', 'Multiplier Id')

# ==========================================================================================================================

class membership_point_special_promo_multiplier(models.Model):
	_name = 'membership.point.special.promo.multiplier'
	_description = 'Multiplier for membership point special promo'

	header_id = fields.Many2one('membership.point.special.promo', 'Header ID' , ondelete='cascade')
	level_id = fields.Many2one('membership.point.level', 'Level', required=True, ondelete='restrict')
	multiplier = fields.Float(string='Multiplier', required=True)