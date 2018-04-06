{
	'name': 'Ciptadlab',
	'version': '1.0',
	'author': 'Christyan Juniady and Associates',
	'maintainer': 'Christyan Juniady and Associates',
	'category': 'Manufacturing',
	'sequence': 21,
	'website': 'http://www.chjs.biz',
	'summary': '',
	'description': """
		Customized Odoo implementation for Ciptadlab.
	""",
	'author': 'Christyan Juniady and Associates',
	'images': [
	],
	'depends': [
		'base','board','web','report_webkit','account_accountant','stock',
		'membership_point',
	],
	'data': [
		'views/membership_point.xml',
		'views/membership_promo.xml',	#PROSI
	],
	'demo': [
	],
	'test': [
	],
	'installable': True,
	'application': True,
	'auto_install': False,
	'qweb': [
	 ],
}