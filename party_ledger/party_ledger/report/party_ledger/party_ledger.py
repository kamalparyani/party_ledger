from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from collections import defaultdict

def execute(filters=None):
    columns = get_columns()
    data = get_gl_entries(filters)
    return columns, data

def get_data():
    return [
        {
            "label": _("Accounting"),
            "items": [
                {
                    "type": "report",
                    "name": "Party Ledger",
                    "doctype": "GL Entry",
                    "is_query_report": True
                },
            ]
        },
    ]

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
            "width": 400  # Increased width to accommodate remarks
        },
        {
            "label": _("Debit"),
            "fieldname": "debit",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Credit"),
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Balance"),
            "fieldname": "balance",
            "fieldtype": "Currency",
            "width": 100
        }
    ]

def get_gl_entries(filters):
    balance_filters = get_balance_filters(filters)
    opening_balance = get_opening_balance(balance_filters)
    
    conditions = """
        gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        AND gle.company = %(company)s
        AND gle.party_type = %(party_type)s
        AND gle.is_cancelled = 0
    """
    
    if filters.get("party"):
        conditions += " AND gle.party = %(party)s"
    
    if filters.get("voucher_no"):
        conditions += " AND gle.voucher_no = %(voucher_no)s"
    
    if filters.get("exclude_system_generated"):
        conditions += " AND (je.is_system_generated IS NULL OR je.is_system_generated = 0)"
    
    gl_entries = frappe.db.sql("""
        SELECT 
            gle.posting_date, gle.account, gle.party_type, gle.party, 
            gle.voucher_type, gle.voucher_no, gle.against, gle.debit, 
            gle.credit, gle.remarks
        FROM 
            `tabGL Entry` gle
        LEFT JOIN 
            `tabJournal Entry` je ON gle.voucher_no = je.name AND gle.voucher_type = 'Journal Entry'
        WHERE 
            {conditions}
        ORDER BY 
            gle.posting_date, gle.creation
    """.format(conditions=conditions), filters, as_dict=True)
    
    payment_entries_with_custom_remarks = get_payment_entries_with_custom_remarks([entry.voucher_no for entry in gl_entries if entry.voucher_type == "Payment Entry"])
    
    data = []
    balance = opening_balance
    
    # Add opening balance row
    opening_row = frappe._dict({
        "posting_date": "",
        "account": filters.get("party") or filters.get("party_type"),
        "party_type": "",
        "party": "",
        "voucher_type": "",
        "voucher_no": "",
        "against": "",
        "debit": format_currency(opening_balance) if opening_balance > 0 else "",
        "credit": format_currency(-opening_balance) if opening_balance < 0 else "",
        "balance": format_currency(opening_balance),
        "detail": "Opening Balance"
    })
    data.append(opening_row)
    
    for entry in gl_entries:
        balance += flt(entry.debit) - flt(entry.credit)
        
        remarks = get_remarks(entry, payment_entries_with_custom_remarks)
        detail = get_invoice_items(entry.voucher_type, entry.voucher_no, filters.get("group_items"))
        
        if filters.get("show_against_account") and entry.voucher_type == "Journal Entry" and entry.against and entry.against != entry.account:
            detail = f"Against: {entry.against}\n" + (detail if detail else "")
        
        if entry.voucher_type == "Sales Invoice" and remarks:
            detail += "\n- - - - - -\n" + remarks
        elif remarks:
            detail = remarks + "\n" + detail if detail else remarks
        
        entry.update({
            "balance": format_currency(balance),
            "debit": format_currency(entry.debit),
            "credit": format_currency(entry.credit),
            "detail": detail
        })
        data.append(entry)
    
    # Add closing balance row
    closing_row = frappe._dict({
        "posting_date": "",
        "account": filters.get("party") or filters.get("party_type"),
        "party_type": "",
        "party": "",
        "voucher_type": "",
        "voucher_no": "",
        "against": "",
        "debit": "",
        "credit": "",
        "balance": format_currency(balance),
        "detail": "Closing Balance"
    })
    data.append(closing_row)
    
    return data

def get_payment_entries_with_custom_remarks(voucher_nos):
    return frappe.get_all(
        "Payment Entry",
        filters={
            "name": ["in", voucher_nos],
            "custom_remarks": 1
        },
        pluck="name"
    )

def get_remarks(entry, payment_entries_with_custom_remarks):
    if entry.voucher_type == "Payment Entry":
        return entry.remarks if entry.voucher_no in payment_entries_with_custom_remarks else ""
    elif entry.voucher_type == "Sales Invoice":
        return "" if entry.remarks.lower() == "no remarks" else entry.remarks
    else:
        return entry.remarks

def format_currency(value):
    if isinstance(value, str):
        value = flt(value)
    if value == 0:
        return "0"
    return f"{value:.0f}" if value.is_integer() else f"{value:.2f}".rstrip('0').rstrip('.')

def get_balance_filters(filters):
    balance_filters = {
        "company": filters.get("company"),
        "party_type": filters.get("party_type"),
        "from_date": filters.get("from_date"),
        "exclude_system_generated": filters.get("exclude_system_generated")
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
    conditions = """
        gle.posting_date < %(from_date)s
        AND gle.company = %(company)s
        AND gle.party_type = %(party_type)s
        AND gle.is_cancelled = 0
    """
    
    if filters.get("party"):
        conditions += " AND gle.party = %(party)s"
    
    if filters.get("exclude_system_generated"):
        conditions += " AND (je.is_system_generated IS NULL OR je.is_system_generated = 0)"
    
    opening_balance = frappe.db.sql("""
        SELECT 
            SUM(gle.debit) - SUM(gle.credit) as opening_balance
        FROM 
            `tabGL Entry` gle
        LEFT JOIN
            `tabJournal Entry` je ON gle.voucher_no = je.name AND gle.voucher_type = 'Journal Entry'
        WHERE 
            {conditions}
    """.format(conditions=conditions), filters, as_dict=True)
    
    return opening_balance[0].opening_balance if opening_balance and opening_balance[0].opening_balance else 0