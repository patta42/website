from userinput.models import RUBIONUser
from userdata.models import StaffUser, SafetyInstruction2UserRelation, SafetyInstruction2StaffRelation

for ruser in RUBIONUser.objects.all():
    SafetyInstruction2UserRelation.objects.filter(user = ruser).all().delete()
    for instruction in ruser.needs_safety_instructions.all():
        rel = SafetyInstruction2UserRelation(
            user = ruser,
            instruction = instruction
        ).save()

for staff in StaffUser.objects.all():
    SafetyInstruction2StaffRelation.objects.filter(staff = staff).all().delete()
    for instruction in staff.needs_safety_instructions.all():
        rel = SafetyInstruction2StaffRelation(
            staff = staff,
            instruction = instruction
        ).save()
    

