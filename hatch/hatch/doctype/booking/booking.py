# Copyright (c) 2026, Monika and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime

class Booking(Document):
	def validate(self):
		if self.start_time and self.end_time:
			if get_datetime(self.end_time) < get_datetime(self.start_time):
				frappe.throw("End Time must be greater than Start Time")
		
		hr = frappe.db.get_value("RESOURCE", self.resource, 'hourly_rate')
		
		start = get_datetime(self.start_time)
		end = get_datetime(self.end_time)
		duration_seconds = (end - start).total_seconds()
		duration_in_hours = duration_seconds / 3600.0
		
		self.base_amount = hr * duration_in_hours
		
		addons_total = 0
		for row in self.addons:
			row.amount = row.rate * row.quantity
			addons_total += row.amount
			
		self.addons_total = addons_total
		self.total_amount = self.base_amount + self.addons_total
		self.check_capacity()

	def before_submit(self):
		if self.status != "Pending Confirmation":
			frappe.throw("Booking can only be submitted if status is 'Pending Confirmation'")
		
		self.status = "Confirmed"

	def on_submit(self):
		frappe.enqueue(
			send_booking_email, 
			booking_name=self.name,
			queue="default",
			is_async=True,
			enqueue_after_commit=True,
		)

	def on_cancel(self):
		self.status = "Cancelled"

	def on_trash(self):
		if self.status not in ["Cancelled", "Draft"]:
			frappe.throw("Booking can only be deleted if status is 'Cancelled' or 'Draft'")

	def check_capacity(self):
		if not self.resource or not self.start_time or not self.end_time:
			return

		resource_capacity = frappe.db.get_value(
			"RESOURCE",
			self.resource,
			"capacity"
		)

		if not resource_capacity:
			return

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
				self.resource,
				self.name or "",
				self.end_time,
				self.start_time,
				self.booking_date
			)
		)

		existing_headcount = result[0][0] or 0
		total_headcount = existing_headcount + (self.headcount or 0)

		if total_headcount > resource_capacity:
			available = resource_capacity - existing_headcount
			frappe.throw(
				f"Booking cannot be created. "
				f"Only {max(available, 0)} seat(s) are available."
			)

def send_booking_email(booking_name):
	doc = frappe.get_doc("Booking", booking_name)

	member_email = frappe.db.get_value(
		"MEMBER",
		doc.member,
		"email"
	)

	if not member_email:
		frappe.log_error(
			f"No email found for Member {doc.member}",
			"Booking Confirmation Email"
		)
		return

	frappe.sendmail(
		recipients=[member_email],
		subject="Booking Confirmation",
		message=f"""
			<p>Dear {doc.member},</p>
			<p>Your booking has been confirmed.</p>
			<p>
				<b>Resource:</b> {doc.resource}<br>
				<b>Start Time:</b> {doc.start_time}<br>
				<b>End Time:</b> {doc.end_time}<br>
				<b>Total Amount:</b> {doc.total_amount}
			</p>
			<p>Thank you for choosing our services.</p>
		"""
	)

def before_print(doc, method=None,print_settings=None):
	doc.print_summary = f"{doc.member} - {doc.resource}"