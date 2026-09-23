// Copyright (c) 2026, Monika and contributors
// For license information, please see license.txt

frappe.ui.form.on("Booking", {
	
    let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
        {
            label: 'Cancellation Reason',
            fieldname: 'cancellation_reason',
            fieldtype: 'Small Text',
            reqd: 1
        },
    ],
    size: 'small', // small, large, extra-large 
    primary_action_label: 'Cancel Booking',
    primary_action(values) {
        console.log(values);
        d.hide();
    }
})

    d.show()

	
});
