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

from frappe.utils import now

def log_change(doc,method):
    log= frappe.get_doc({
          'doctype':"Audit Log",
          'doctype_name':doc.doctype,
          'document_name':doc.name,
          'action':method,
          'user':frappe.session.user,
          'timestamp':now()
     })
    log.insert()


# def check_availability(doc):
#             if not doc.resource or not doc.start_time or not doc.end_time:
#                 return
     
#             resource_capacity = frappe.db.get_value(
#                 "RESOURCE",
#                 doc.resource,
#                 "capacity"
#             )
     
#             if not resource_capacity:
#                 return
     
#             result = frappe.db.sql(
#                 """
#                 SELECT COALESCE(SUM(headcount), 0) 
#                 FROM `tabBooking`
#                 WHERE resource = %s
#                 AND name != %s
#                 AND status IN (
#                     'Pending Confirmation',
#                     'Confirmed',
#                     'Checked-In'
#                 )
#                 AND start_time < %s
#                 AND end_time > %s
#                 AND booking_date = %s
#                 """,
#                 (
#                     doc.resource,
#                     doc.name or "",
#                     doc.end_time,
#                     doc.start_time,
#                     doc.booking_date
#                 )
#             )
     
#             existing_headcount = result[0][0] or 0
#             total_headcount = existing_headcount + (doc.headcount or 0)
     
#             if total_headcount > resource_capacity:
#                 available = resource_capacity - existing_headcount
#                 frappe.throw(
#                     f"Booking cannot be created. "
#                     f"Only {max(available, 0)} seat(s) are available."
#                 )





@frappe.whitelist()
def check_availability(resource, booking_date, start_time, end_time, headcount=0, booking_name=None):

    if not resource or not booking_date or not start_time or not end_time:
        return None

    resource_capacity = frappe.db.get_value(
        "RESOURCE",
        resource,
        "capacity"
    )

    if not resource_capacity:
        return None

    result = frappe.db.sql(
        """
        SELECT COALESCE(SUM(headcount), 0)
        FROM `tabBooking`
        WHERE resource = %s
        AND name != %s
        AND status IN (
            'Pending Confirmation',
            'Confirmed',
            'Checked-In'
        )
        AND start_time < %s
        AND end_time > %s
        AND booking_date = %s
        """,
        (
            resource,
            booking_name or "",
            end_time,
            start_time,
            booking_date
        )
    )

    existing_headcount = result[0][0] or 0

    available = resource_capacity - existing_headcount

    requested_headcount = int(headcount or 0)

    return {
        "capacity": resource_capacity,
        "booked": existing_headcount,
        "available": max(available, 0),
        "requested": requested_headcount,
        "can_book": requested_headcount <= available
    }