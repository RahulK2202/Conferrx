# Copyright (c) 2023, sathya and contributors
# For license information, please see license.txt

import json
import frappe
import io
from frappe.model.document import Document
from pyqrcode import create as qr_create
# import png
import os
from frappe.model.naming import parse_naming_series
from e_desk.e_desk.utils.role import update_event_participant_role

class RegistrationDesk(Document):
    @classmethod
    def create_qr_participant(self, pr_doc):
        qr_image = io.BytesIO()
        data={"name":pr_doc.name}
        data=json.dumps(data,indent=4,sort_keys=True,default=str)
        data_ = qr_create(data, error='L')
        data_.png(qr_image, scale=4, quiet_zone=1)
        name = frappe.generate_hash('', 5)
        filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
        _file = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "is_private": 0,
        "content": qr_image.getvalue(),
        "attached_to_doctype":  pr_doc.doctype,
        "attached_to_name": pr_doc.name,
        "attached_to_field":"qr"
        })
        for i in frappe.get_all("File", {
        "attached_to_doctype":  pr_doc.doctype,
        "attached_to_name": pr_doc.name,
        "attached_to_field":"qr"}):
            frappe.delete_doc("File", i.name)

        _file.save(ignore_permissions=True)
        frappe.db.set_value(pr_doc.doctype, pr_doc.name, 'qr', _file.file_url, update_modified=False)
        pr_doc.reload()
        return _file.file_url
    
    # Registration completed -> converting the participant status as registered
    # def on_update(self):
    #     for row in self.participant:
    #         if not row.profile_img:
    #             frappe.throw(f"Profile picture mandatory in {row.idx}")


        #     doc = frappe.get_doc("Participant", row.participant_id)
        #     # qr=self.create_qr_participant( doc)
        #     doc.status = "Registered"
        #     doc.save()
        #     # frappe.db.set_value(row.doctype, row.name, 'qr_img', qr, update_modified=False)
        # self.reload()


    # Registration canceled -> moving the particioant to old status


    def on_trash(self):
        for row in self.participant:
            event_participant = frappe.get_doc(
            "Event Participant",
            {
                "name": row.participant_id,
            }
            )
          
            event_participant.is_paid = False
            event_participant.reg_status = "Pending"
            event_participant.status = "Open"

            # Save the changes
            event_participant.save()
            
   


    # def autoname(self):
    #     if self.participant:
    #         first_item =self.participant[0]
    #         first_item_name=first_item.participant_name
    #         self.name = parse_naming_series(f"{first_item_name}-.#")

    def before_save(self):
        for row in self.participant:
            profile_id = frappe.get_value("Event Participant", row.participant_id, "participant")
            participant_qr = frappe.get_value("Participant", profile_id, "qr")
            print(participant_qr,"this is rowWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
            row.qr_img=participant_qr

    def on_submit(self):

        for row in self.participant:
            
            profile_id = frappe.get_value("Event Participant", row.participant_id, "participant")
            # participant_qr = frappe.get_value("Participant", profile_id, "qr")
            # print(participant_qr,"this is rowWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
            # row.qr_img=participant_qr
    
            event_participant = frappe.get_doc(
                "Event Participant",
                {
                    "participant": profile_id,
                    "event": self.confer
                }
            )

            is_paid = False  
            if self.mode_of_payment:
                for payment in self.mode_of_payment:
                    amount = frappe.get_value("Mode of payment", payment, "amount")
                    if float(amount) > 0:
                        is_paid = True
                        break 
            # Update the Event Participant table with payment and registration status
            event_participant.is_paid = is_paid
            event_participant.reg_status = "Approved"
            event_participant.status = "Registered"
            event_participant.custom_kit_provided=self.kit_provided_

            # Save the changes for each participant
            event_participant.save()
            print("NEXT ID COMING..............")

        # Optionally, show a confirmation message after processing all participants
        frappe.msgprint("All participants' registration and payment status have been updated successfully.")



    # def on_submit(doc):
    #     participant= doc.participant[0].participant_id
    #     new_row = frappe.get_doc({
    #         'doctype': 'Event Participant',
    #         'event': doc.confer,
    #         'participant': participant,
    #         'event_role' : "Participant"
    #     })

 
    #     new_row.insert(ignore_permissions=True)
    #     frappe.db.commit()
    #     # if user.role_profile_name not in ["Participant", "E-Desk Admin"]:
    #     update_event_participant_role(participant,doc.confer, "Participant")
            
    #     frappe.msgprint('Conference updated successfully.')



# @frappe.whitelist()
# def event_participant_filter(doctype, txt, searchfield, start, page_len, filters):
#     conference = filters.get('conference')

#     # filtering  participant which are not registered in this perticular event
#     participants = frappe.db.sql("""
#         SELECT p.name,p.full_name
#         FROM `tabParticipant` p
#         WHERE p.name  IN (
#             SELECT ep.participant
#             FROM `tabEvent Participant` ep
#             WHERE ep.event = %(conference)s
#         )
#         AND p.name LIKE %(txt)s
        
#         LIMIT %(start)s, %(page_len)s
        
#     """, {
#         'conference': conference,
#         'txt': "%" + txt + "%",
#         'start': start,
#         'page_len': page_len
#     })

#     # registered_participants=

 
#     return participants



# @frappe.whitelist()
# def event_participant_filter(doctype, txt, searchfield, start, page_len, filters):
#     conference = filters.get('conference')

#     # Filtering participants who are not registered in the Registration Desk for this particular event
#     participants = frappe.db.sql("""
#         SELECT p.name, p.full_name
#         FROM `tabParticipant` p
#         WHERE p.name IN (
#             SELECT ep.participant
#             FROM `tabEvent Participant` ep
#             WHERE ep.event = %(conference)s
#         )
#         AND p.name NOT IN (
#             SELECT pt.participant_id
#             FROM `tabRegistration Desk` rd
#             JOIN `tabParticipant Table` pt ON pt.parent = rd.name
#             WHERE rd.confer = %(conference)s
#         )
#         AND p.name LIKE %(txt)s
#         LIMIT %(start)s, %(page_len)s
#     """, {
#         'conference': conference,
#         'txt': "%" + txt + "%",
#         'start': start,
#         'page_len': page_len
#     })

#     return participants


@frappe.whitelist()
def event_participant_filter(doctype, txt, searchfield, start, page_len, filters):
    conference = filters.get('conference')
    print(conference, "confere.....")
    

    participants = frappe.db.sql("""
        SELECT p.name, p.full_name 
        FROM `tabEvent Participant` p
        WHERE p.event = %(conference)s
        AND p.status = 'Approved'                        
        AND p.name NOT IN (
            SELECT pt.participant_id 
            FROM `tabRegistration Desk` rd
            JOIN `tabParticipant Table` pt ON pt.parent = rd.name 
            WHERE rd.confer = %(conference)s
        )
        AND p.name LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
    """, {
        'conference': conference,
        'txt': "%" + txt + "%",
        'start': start,
        'page_len': page_len
    })

    return participants





