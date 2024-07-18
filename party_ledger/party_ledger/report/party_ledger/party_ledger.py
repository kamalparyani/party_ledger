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
    gl_entries = frappe.db.get_all(
        "GL Entry",
        fields=[
            "posting_date", "voucher_type", "voucher_no", "debit", "credit", "remarks", "against", "party", "party_type"
        ],
        filters=get_filters(filters),
        order_by="posting_date, creation"
    )
    
    data = []
    balance = 0
    for entry in gl_entries:
        balance += flt(entry.debit) - flt(entry.credit)
        
        entry.debit = format_currency(entry.debit)
        entry.credit = format_currency(entry.credit)
        formatted_balance = format_currency(balance)
        
        entry.update({
            "balance": formatted_balance,
            "detail": get_invoice_items(entry.voucher_type, entry.voucher_no, filters.get("group_items"))
        })
        data.append(entry)
    
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
        "party_type": filters.get("party_type")
    }
    
    if filters.get("party"):
        filter_dict["party"] = filters.get("party")
    
    if filters.get("voucher_no"):
        filter_dict["voucher_no"] = filters.get("voucher_no")
    
    return filter_dict

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