// Copyright (c) 2023, sathya and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Voting Report"] = {
	"filters": [
		{
			'fieldname': 'session',
			'fieldtype': 'Link',
			'label': 'session',
			'options':'Session',
			"reqd": 1
		},
		{
			"fieldname": "registration_no",
			"label": __("Registration No"),
			"fieldtype": "Data",
		},

	],

 
};
