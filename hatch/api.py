from frappe.query_builder import DocType
from frappe.query_builder.functions import Now
from frappe.utils import today
import frappe
@frappe.whitelist(allow_guest=True)
def get_upcoming_bookings():
    BK = DocType("Booking")
    return frappe.qb.from_(BK).select(BK.name,BK.member, BK.resource, BK.booking_date, BK.start_time).where(
        BK.booking_date >= today() and BK.status.isin(["Pending Confirmation", "Confirmed"])).orderby(BK.booking_date).run(as_dict=True)

@frappe.whitelist
def reassign_bookings(from_member, to_member) :
    try:
        frappe.db.sql(
            """
            UPDATE `tabBooking`
            SET member = %(to_member)s
            WHERE member = %(from_member)s
            and status IN ('Pending Confirmation', 'Confirmed')
            """,
            {"from_member": from_member, "to_member": to_member}
        )
    except Exception :
        frappe.rollback()
        frappe.log_error(frappe.traceback())
    raise frappe.ValidationError("Error occurred while reassigning bookings. Please check the error log for details.")

@frappe.whitelist
def share_booking(booking_name, user_email) :

    frappe.share.add({"Booking": booking_name, "User": user_email}, read=1)
    return "Booking shared successfully."

@frappe.whitelist
def after_install():
     settings = frappe.get_doc('Hatch Settings')
     frappe.db.set_value('Hatch Settings', settings.name, 'manager_email','monika@gmail.com')
     frappe.db.set_value('Hatch Settings', settings.name, 'pending_confirmation_expiry_hours',24)
     frappe.db.set_value('Hatch Settings', settings.name, 'cancellation_window_hours',48)
     frappe.db.set_value('Hatch Settings', settings.name, 'waitlist_enabled',1)
     if frappe.db.count('RESOURCE') == 0:
         frappe.get_doc({
             'doctype': 'RESOURCE',
             'resource_name': 'Default Resource1',
             'capacity': 10
         }).insert()
         frappe.get_doc({
             'doctype': 'RESOURCE',
             'resource_name': 'Default Resource2',
             'capacity': 20
         }).insert()
         frappe.get_doc({
             'doctype': 'RESOURCE',
             'resource_name': 'Default Resource3',
             'capacity': 30
         }).insert()
    

def rename_member_in_bookings(old_member, new_member):
	bookings = frappe.get_all("Booking", filters={"member": old_member}, fields=["name"])
	for booking in bookings:
		frappe.rename_doc("MEMBER", old_member, new_member, merge=False)