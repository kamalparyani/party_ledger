frappe.query_reports["Party Ledger"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -2),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "party_type",
            "label": __("Party Type"),
            "fieldtype": "Select",
            "options": "Customer\nSupplier\nEmployee",
            "default": "Customer",
            "reqd": 1
        },
        {
            "fieldname": "party",
            "label": __("Party"),
            "fieldtype": "Dynamic Link",
            "get_options": function() {
                var party_type = frappe.query_report.get_filter_value('party_type');
                if(!party_type) {
                    frappe.throw(__("Please select Party Type first"));
                }
                return party_type;
            },
            "reqd": 1
        },
        {
            "fieldname": "voucher_no",
            "label": __("Voucher No"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "group_items",
            "label": __("Group Items"),
            "fieldtype": "Check",
            "default": 1
        },
        {
            "fieldname": "remove_decimals",
            "label": __("Remove Insignificant Decimals"),
            "fieldtype": "Check",
            "default": 1
        }
    ]
};