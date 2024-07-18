from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from collections import defaultdict

def execute(filters=None):
    columns = get_columns()
    data = get_gl_entries(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Voucher No"),
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 180
        },
        {
            "label": _("Detail"),
            "fieldname": "detail",
            "fieldtype": "Small Text",
            "width": 300
        },
        {
            "label": _("Dr"),
            "fieldname": "debit",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Cr"),
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Balance"),
            "fieldname": "balance",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Remarks"),
            "fieldname": "remarks",
            "width": 400
        },
    ]

def get_gl_entries(filters):
    balance_filters = get_balance_filters(filters)
    opening_balance = get_opening_balance(balance_filters)
    
    gl_entries = frappe.db.get_all(
        "GL Entry",
        fields=[
            "posting_date", "account", "party_type", "party", "voucher_type", 
            "voucher_no", "against", "debit", "credit", "remarks"
        ],
        filters=get_filters(filters),
        order_by="posting_date, creation"
    )
    
    data = []
    balance = opening_balance
    
    # Add opening balance row
    opening_row = frappe._dict({
        "posting_date": "",  # No date for opening balance
        "account": filters.get("party") or filters.get("party_type"),
        "party_type": "",
        "party": "",
        "voucher_type": "",
        "voucher_no": "",
        "against": "",
        "debit": format_currency(opening_balance) if opening_balance > 0 else "",
        "credit": format_currency(-opening_balance) if opening_balance < 0 else "",
        "balance": format_currency(opening_balance),
        "detail": "Opening Balance",  # Put "Opening Balance" in the Detail column
        "remarks": ""
    })
    data.append(opening_row)
    
    for entry in gl_entries:
        balance += flt(entry.debit) - flt(entry.credit)
        
        entry.update({
            "balance": format_currency(balance),
            "debit": format_currency(entry.debit),
            "credit": format_currency(entry.credit),
            "detail": get_invoice_items(entry.voucher_type, entry.voucher_no, filters.get("group_items"))
        })
        data.append(entry)
    
    # Add closing balance row
    closing_row = frappe._dict({
        "posting_date": filters.get("to_date"),
        "account": filters.get("party") or filters.get("party_type"),
        "party_type": "",
        "party": "",
        "voucher_type": "",
        "voucher_no": "",
        "against": "",
        "debit": "",
        "credit": "",
        "balance": format_currency(balance),
        "detail": "Closing Balance",  # Put "Closing Balance" in the Detail column
        "remarks": ""
    })
    data.append(closing_row)
    
    return data

def format_currency(value):
    """Format currency value without insignificant decimal points."""
    if isinstance(value, str):
        value = flt(value)
    if value == 0:
        return "0"
    return f"{value:.0f}" if value.is_integer() else f"{value:.2f}".rstrip('0').rstrip('.')

def get_filters(filters):
    filter_dict = {
        "posting_date": ["between", [filters.get("from_date"), filters.get("to_date")]],
        "company": filters.get("company"),
        "party_type": filters.get("party_type"),
        "is_cancelled": 0  # This excludes both cancelled entries and their reversals
    }
    
    if filters.get("party"):
        filter_dict["party"] = filters.get("party")
    
    if filters.get("voucher_no"):
        filter_dict["voucher_no"] = filters.get("voucher_no")
    
    return filter_dict

def get_balance_filters(filters):
    balance_filters = {
        "company": filters.get("company"),
        "party_type": filters.get("party_type"),
        "from_date": filters.get("from_date")
    }
    
    if filters.get("party"):
        balance_filters["party"] = filters.get("party")
    
    return balance_filters

def get_invoice_items(voucher_type, voucher_no, group_items):
    if voucher_type in ["Sales Invoice", "Purchase Invoice"]:
        item_doctype = "Sales Invoice Item" if voucher_type == "Sales Invoice" else "Purchase Invoice Item"
        items = frappe.get_all(item_doctype, 
                               filters={"parent": voucher_no},
                               fields=["item_code", "qty", "uom", "rate"],
                               order_by="idx")
        
        if group_items:
            return get_grouped_items(items)
        else:
            return get_ungrouped_items(items)
    return ""

def get_grouped_items(items):
    grouped_items = defaultdict(lambda: {"qty": 0, "uom": "", "rate": 0})
    for item in items:
        key = (item.item_code, item.uom, item.rate)
        grouped_items[key]["qty"] += item.qty
        grouped_items[key]["uom"] = item.uom
        grouped_items[key]["rate"] = item.rate
    
    detail = []
    for (item_code, uom, rate), data in grouped_items.items():
        qty = format_number(data["qty"])
        rate = format_number(rate)
        detail.append(f"{item_code} {qty} {uom} * {rate}")
    
    return "\n".join(detail)

def get_ungrouped_items(items):
    detail = []
    for item in items:
        qty = format_number(item.qty)
        rate = format_number(item.rate)
        detail.append(f"{item.item_code} {qty} {item.uom} * {rate}")
    
    return "\n".join(detail)

def format_number(value):
    if isinstance(value, str):
        value = flt(value)
    if value == 0:
        return "0"
    return f"{value:.0f}" if value.is_integer() else f"{value:.2f}".rstrip('0').rstrip('.')

def get_opening_balance(filters):
    balance_filters = get_balance_filters(filters)
    balance_filters["is_cancelled"] = 0  # Exclude cancelled entries and their reversals
    opening_balance = frappe.db.sql("""
        SELECT 
            SUM(debit) - SUM(credit) as opening_balance
        FROM 
            `tabGL Entry`
        WHERE 
            posting_date < %(from_date)s
            AND company = %(company)s
            AND party_type = %(party_type)s
            AND is_cancelled = 0
            {party_condition}
    """.format(
        party_condition = "AND party = %(party)s" if balance_filters.get("party") else ""
    ), balance_filters, as_dict=True)
    
    return opening_balance[0].opening_balance if opening_balance and opening_balance[0].opening_balance else 0