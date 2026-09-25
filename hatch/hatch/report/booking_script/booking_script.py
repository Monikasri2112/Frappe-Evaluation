# Copyright (c) 2026, Monika and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import frappe

def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()

	return columns, data

	"""Return columns and data for the report.

	This is the main entry point for snapshot report. When 'Synced
	Report' is enabled in report, framework will call this method
	every time the report is refreshed or a filter is updated. It
	accepts the same filters as normal execute. But a utility method -
	get_latest_sync, is also imported.

	"""
	from frappe.database.duckdb.database import get_latest_sync

	columns = get_columns()
	data = get_data()

	return columns, data

def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Resource"),
			"fieldname": "resource",
			"fieldtype": "Link",
			"options": "RESOURCE"
		},
		{
			"label": _("Total Bookings"),
			"fieldname": "total_bookings",
			"fieldtype": "Int",
		},
		{
			"label": _("Total Hours Booked"),
			"fieldname": "total_hours_booked",
			"fieldtype": "Int",
		},
		{
			"label": _("Utilization Percentage"),
			"fieldname": "utilization_percentage",
			"fieldtype": "Percent",
		},
		{
			"label": _("Revenue Generated"),
			"fieldname": "revenue_generated",
			"fieldtype": "Currency",
		}
	]


def get_data() -> list[list]:
	data = frappe.db.sql(
		"""
		SELECT resource,
			COUNT(*) AS total_bookings,
			SUM(TIMESTAMPDIFF(HOUR, start_time, end_time)) AS total_hours_booked,
			(SUM(TIMESTAMPDIFF(HOUR, start_time, end_time))/ (COUNT(*) * 24)) * 100 AS utilization_percentage,
			SUM(total_amount) AS revenue_generated
		FROM `tabBooking`
		GROUP BY resource
	""",
		as_dict=True,
	)

	return data
