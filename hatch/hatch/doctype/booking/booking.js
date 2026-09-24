// Copyright (c) 2026, Monika and contributors
// For license information, please see license.txt

frappe.ui.form.on("Booking", {
    refresh(frm){
        if(frm.doc.status=="Draft"){
             frm.dashboard.add_indicator("Draft", "grey");
        }
       if(frm.doc.status=="Pending Confirmation"){
        frm.dashboard.add_indicator("Pending Confirmation", "orange");
       }
        if(frm.doc.status=="Confirmed"){
        frm.dashboard.add_indicator("Confirmed", "green");
        }
         if(frm.doc.status=="Checked In"){
        frm.dashboard.add_indicator("Checked In", "blue");
         }
         if(frm.doc.status=="Completed"){
        frm.dashboard.add_indicator("Completed", "green");
         }
        if(frm.doc.status=="Cancelled"){
        frm.dashboard.add_indicator("Cancelled", "red");
        }
let today = frappe.datetime.get_today();
        
        if (frm.doc.status === 'Confirmed' && frm.doc.docstatus==1 && frm.doc.booking_date === today) {
            frm.add_custom_button('Check In', function() {
                frm.set_value('status', 'Checked-In');
                frm.save();
            });
        }
    },
});

frappe.ui.form.on("Booking", {

    resource(frm) {
        check_availability(frm);
    },

    booking_date(frm) {
        check_availability(frm);
    },

    start_time(frm) {
        check_availability(frm);
    },

    end_time(frm) {
        check_availability(frm);
    },

    headcount(frm) {
        check_availability(frm);
    }

});


function check_availability(frm) {

    if (
        !frm.doc.resource ||
        !frm.doc.booking_date ||
        !frm.doc.start_time ||
        !frm.doc.end_time
    ) {
        return;
    }

    frappe.call({

        method: "hatch.api.check_availability",

        args: {
            resource: frm.doc.resource,
            booking_date: frm.doc.booking_date,
            start_time: frm.doc.start_time,
            end_time: frm.doc.end_time,
            headcount: frm.doc.headcount || 0,
            booking_name: frm.doc.name
        },

        callback: function(r) {

            if (!r.message) {
                return;
            }

            let data = r.message;

            if (data.can_book) {

                frm.set_intro(
                    `${data.available} of ${data.capacity} seats free in this slot.`,
                    "green"
                );

            } else {

                frm.set_intro(
                    `Only ${data.available} of ${data.capacity} seats free in this slot. ` +
                    `Requested: ${data.requested}.`,
                    "red"
                );

            }
        }
    });
};
frappe.ui.form.on("Booking", {
    refresh(frm){
frm.add_custom_button('Cancel Booking', () => {
    let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
        {
            label: 'Cancellation Reason',
            fieldname: 'cancellation_reason',
            fieldtype: 'Small Text',
            reqd: 1 
        }
        
    ],
    size: 'small', // small, large, extra-large 
    primary_action_label: 'Cancel Booking',
    primary_action(values) {
        frm.save('Cancel');
        d.hide();
    }
});
d.show();

})
    }
})

frappe.ui.form.on("Booking",{
refresh(frm){
    frm.add_custom_button('Reassign to Another Member',()=>{
        frappe.prompt({
    label: 'Member',
    fieldname: 'member',
    fieldtype: 'Link',
    options:'MEMBER'
}, (values) => {
    frappe.confirm('Are you sure you want to proceed?',
    () => {
        frm.set_value("member",values.member)
    
    },)
})

    })
}
})
