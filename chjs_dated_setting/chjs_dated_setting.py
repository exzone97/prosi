from datetime import datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

# ===============================================================================================================================

class chjs_dated_setting(osv.osv):
	
	_name = 'chjs.dated.setting'
	_description = 'Base model for settings with valid-from and valid-through date.'
	
# COLUMNS -----------------------------------------------------------------------------------------------------------------------

	_columns = {
		'name': fields.char('Description', size=500, required=True),
		'valid_from': fields.date('Valid From', required=True),
		'valid_through': fields.date('Valid Through'),
	}
	
# DEFAULTS ----------------------------------------------------------------------------------------------------------------------
	
	_defaults = {
		'valid_from': lambda *a: datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
	}
	
# CUSTOM METHODS ----------------------------------------------------------------------------------------------------------------
	
	def get_current(self, cr, uid, current_date=None, domain=[], context={}):
	# gaya browse. menggantikan versi 2015 di bawahnya
		current_date = current_date and current_date or datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
		domain.append(('valid_from','<=',current_date))
		setting_ids = self.search(cr, uid, domain, order="valid_from DESC", limit=1)
		if len(setting_ids) == 0:
			raise osv.except_osv(_('Setting Error'),_('It appears that no one creates any setting that is valid for this date.'))
		current_setting = self.browse(cr, uid, setting_ids[0])
		if current_setting.valid_through and current_setting.valid_through < current_date:
			raise osv.except_osv(_('Setting Error'),_('It appears that no one creates any setting that is valid for this date.'))
		return current_setting
	# di bawah ini versi 2015. jaman kegelapan XD
	# siapkan query. query adalah join antara tabel ini dengan seluruh tabel "anak", yaitu tabel ke mana model ini o2m	
		tables = []
		wheres = []
		table_name = self._table
		for field_name, field_def in self.fields_get(cr, uid).iteritems():
			if field_def['type'] == 'one2many':
				relation_name = field_def['relation'].replace('.','_')
				tables.append(relation_name)
				wheres.append("%s.%s = %s.id" % (relation_name,field_def['relation_field'],table_name)) 
		tables.append(table_name)
	# gabungkan domain ke wheres
		for dom in domain:
			wheres.append("%s %s '%s'" % (dom[0],dom[1],dom[2]))
	# ini query lengkapnya 
		current_date = current_date and current_date or datetime.today()
		query = """
			SELECT * FROM %s WHERE %s AND valid_from <= '%s' AND (valid_through IS NULL OR valid_through > '%s')
		""" % (",".join(tables)," AND ".join(wheres),current_date.strftime('%Y-%m-%d'),current_date.strftime('%Y-%m-%d'))
		cr.execute(query)
		row = cr.dictfetchone()
		return row or {}
