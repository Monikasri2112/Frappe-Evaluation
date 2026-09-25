**B2c — Dangerous Patterns:**

using self.save() inside validate() could cause a recursion because validate will trigger an save() and this save() will also performs causing an infinite loop.
def validate(self):
    self.total_amount = sum(r.amount for r in self.addons) + self.base_amount
also we cannot save someother doctype inside validate function of of self doctype so we can use it inside some other function
def save_resource():
    resource = frappe.get_doc("Resource", self.resource)
    resource.times_booked += 1
    resource.save()
  

**B2d — Concurrency, One Question
In README_internals.md: why would two front-desk staff saving the same Booking at once trigger "Document has been modified after you have opened it," and how does Frappe prevent the silent overwrite?**

Frappe checks whether someone else changed the document before we save. If yes, it stops our save instead of overwriting their changes. It tells like Document has modified before you have opened it

**C3-what is the DB table name for Booking Add-on Entry? When you append a row and save, what 4 columns does Frappe set automatically on the child row? If you delete the row at idx=2 and re-save, what happens to the idx values of the remaining rows?**
 Rows that are automatically set are=>name,parenttype,parentfield,idx
 om deleting and resaving the child row the index getting automatically updated if have idx=1,idx=2,idx=3 and we delete idx=2 then indexes get automatically renamed as idx=1,idx=2

**D2-A whitelisted method returning Booking data in two versions — unsafe (all fields to any caller) and safe (frappe.get_list, strips member.email/member.phone for non-staff callers). Explain why frappe.get_all is dangerous here.**
frappe.get_all doesn't check for user permission so all the users can see all the records without any restriction like their email and phone which is not safe so,using frappe.get_list checks for user permissions and restrict their view into other's informations

**E3 — One Performance Judgment Call
In the Resource controller's on_update, which pattern would you use to read a single settings value, and why?
doc = frappe.get_doc("Hatch Settings", "Hatch Settings")
hours = doc.pending_confirmation_expiry_hours
hours = frappe.db.get_value("Hatch Settings", None, "pending_confirmation_expiry_hours")**
hours = frappe.db.get_value("Hatch Settings", None, "pending_confirmation_expiry_hours")
I prefer using this because this only fetches the required field we need rather the frappe.get_doc
fetches the entire document with all the fields that aren't necessary

**H1-why can't that live-availability check be done inside the validate client event via a synchronous-feeling frappe.call, and why does it belong in a field-change handler instead?**

 when we give availability check inside validate that frappe.call method takes time to get the data and it is asynchronous validate function inside js doesn't wait for the output from frappe.call() method it performs the save operation then after when data arrive it is captured. So using this inside field-change handler is efficient.

**I1-f-string version side by side with parameterized, and why the latter always wins.**
F-string puts the value directly into the SQL, which can cause SQL injection.
Parameterized SQL keeps the value separate from the query, so it is safer and preferred.

**N1 — ignore_permissions Audit & JS-Hiding Pitfall
List every place using ignore_permissions=True; one-sentence justification each.
Add a JS field hide for member.phone/member.email on the Booking form for non-staff — then show a direct API call still retrieves them. Explain why hiding a field in JavaScript is not a security measure**
Ignore permission provides access to a particular doctype to the user to even if they aren't given access to that particular doctype. Hiding the data from UI doesn't mean they aren't available in database so to avoid this we have to set perm level for that field and same permission level to the user only then we can prevent the visibility to that field even through API call

**J1-frappe.get_all() called directly inside the Jinja template, versus pre-computed in before_print() and referenced as doc.precomputed_field — explain the difference.**
when frappe.get_all() is called directly inside the Jinja template everytime the whole data is fetched but if it is pre-computed it can be used easily and is optimized.

**E1-Call self.save() inside on_update to "make sure totals are fresh" and observe what breaks. Explain and correct it in README_internals.md.**
Calling self.save() on on_update will cause recursion because both on_update() and salf.save will call save causing an infinite loop

