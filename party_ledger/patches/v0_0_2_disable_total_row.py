import frappe

def execute():
    report = frappe.get_doc("Report", "Party Ledger")
    if report.add_total_row:
        report.add_total_row = 0
        report.save()
        frappe.db.commit()
