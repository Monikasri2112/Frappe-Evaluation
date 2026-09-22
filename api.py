def todo_query(user):
    if not user:
        user = frappe.session.user
    # todos that belong to user or assigned by user
    return "(`tabToDo`.owner = {user} or `tabToDo`.assigned_by = {user})".format(user=frappe.db.escape(user))
