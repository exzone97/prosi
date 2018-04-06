{
	'name': 'CHJS Dated Setting',
	'version': '1.0',
	'category': 'Utilities',
	'description': """
		Base model for settings with valid dates. This implements capability to get current setting based on certain date (or now) 
		and valid date of available settings. Settings have valid-from and valid-through date; if valid-through is empty it is assumed 
		that the setting is always valid except there is another setting with more recent valid-from date.
	""",
	'author': 'Christyan Juniady and Associates',
	'maintainer': 'Christyan Juniady and Associates',
	'website': 'http://www.chjs.biz',
	'depends': ["base"],
	'data': [
	],
	'demo': [
	],
	'test': [
	],
	'installable': True,
	'auto_install': False,
}
