from odoo import fields, models


class AssistantDoctorDetails(models.Model):
    _name = 'assistant.doctor.details'
    _description ='Assistant Doctor Details'
    
    appointment_id=fields.Many2one('medical.appointment','Appointment')
    patient_id=fields.Many2one('medical.patient','Patient',related='appointment_id.patient',store=True)
    
    left_distance_id=fields.Many2one('distance','Distance',required=True)
    left_near_id=fields.Many2one('near','Near',required=True)
    left_with_glasses_id=fields.Many2one('with.glasses','With Glasses')
    left_without_glasses_id=fields.Many2one('without.glasses','Without Glasses')
    left_pin_id=fields.Many2one('pin','PIN')
    left_iop_id=fields.Many2one('iop','IOP')
    
    right_distance_id=fields.Many2one('distance','Distance',required=True)
    right_near_id=fields.Many2one('near','Near',required=True)
    right_with_glasses_id=fields.Many2one('with.glasses','With Glasses')
    right_without_glasses_id=fields.Many2one('without.glasses','Without Glasses')
    right_pin_id=fields.Many2one('pin','PIN')
    right_iop_id=fields.Many2one('iop','IOP')    
    
    eye_type=fields.Selection([('right_eye', 'Right Eye'), ('left_eye', 'Left Eye')], 'Eye')
    patient_complaint=fields.Char('Complaint')
    personal_history=fields.Char('Personal Info')
    examination=fields.Char('Examination')
    glass_prescription_line_ids=fields.One2many('glass.prescription.line','ass_dr_detail_id',' ')
    reflectometer=fields.One2many('reflectometer.line','ass_dr_detail_id','Auto Reflectometer')


class Reflectometer(models.Model):
    _name = 'reflectometer.line'
    _description = "Reflectometer Lines"

    spherical=fields.Many2one('spherical','Spherical',required=True)
    cylindrical=fields.Many2one('cylindrical','Cylindrical')
    axis=fields.Many2one('axis','Axis')
    eye_type=fields.Selection([('right_eye', 'Right Eye'), ('left_eye', 'Left Eye')], 'Eye')
    ass_dr_detail_id=fields.Many2one('assistant.doctor.details','Assistance Dr. Details')
    

class GlassPrescription(models.Model):
    _name = 'glass.prescription.line'
    _description ='Glazz RX'
    
    ass_dr_detail_id=fields.Many2one('assistant.doctor.details','Assistance Dr. Details')
    type_of_reading=fields.Selection([('distance', 'Distance'), ('near', 'Near'),('computer', 'Computer')], 'Type')
    eye_type=fields.Selection([('right_eye', 'Right Eye'), ('left_eye', 'Left Eye')], 'Eye')
    quality=fields.Char('quality')
    ipd=fields.Char('IPD')
    
    next_visit_date=fields.Date('Next Visit Date')
    
    
    right_dist_spherical=fields.Many2one('spherical','Spherical', required=True)
    right_near_spherical=fields.Many2one('spherical','Spherical')
    right_comp_spherical=fields.Many2one('spherical','Spherical')
     
    right_dist_cylindrical=fields.Many2one('cylindrical','Cylindrical')
    right_near_cylindrical=fields.Many2one('cylindrical','Cylindrical')
    right_comp_cylindrical=fields.Many2one('cylindrical','Cylindrical')
     
    right_dist_axis=fields.Many2one('axis','Axis')
    right_near_axis=fields.Many2one('axis','Axis')
    right_comp_axis=fields.Many2one('axis','Axis')
     
    right_dist_vision=fields.Many2one('vision','Vision')
    right_near_vision=fields.Many2one('vision','Vision')
    right_comp_vision=fields.Many2one('vision','Vision')
     
    left_dist_spherical=fields.Many2one('spherical','Spherical', required=True)
    left_near_spherical=fields.Many2one('spherical','Spherical')
    left_comp_spherical=fields.Many2one('spherical','Spherical')
     
    left_dist_cylindrical=fields.Many2one('cylindrical','Cylindrical')
    left_near_cylindrical=fields.Many2one('cylindrical','Cylindrical')
    left_comp_cylindrical=fields.Many2one('cylindrical','Cylindrical')
     
    left_dist_axis=fields.Many2one('axis','Axis')
    left_near_axis=fields.Many2one('axis','Axis')
    left_comp_axis=fields.Many2one('axis','Axis')
     
    left_dist_vision=fields.Many2one('vision','Vision')
    left_near_vision=fields.Many2one('vision','Vision')
    left_comp_vision=fields.Many2one('vision','Vision')
     
    right_spherical_reflectometer=fields.Many2one('spherical','Spherical', required=True)
    left_spherical_reflectometer=fields.Many2one('spherical','Spherical', required=True)
     
    right_cylindrical_reflectometer=fields.Many2one('cylindrical','Cylindrical')
    left_cylindrical_reflectometer=fields.Many2one('cylindrical','Cylindrical')
     
    right_axis_reflectometer=fields.Many2one('axis','Axis')
    left_axis_reflectometer=fields.Many2one('axis','Axis')


class Distance(models.Model):
    _name = 'distance'
    _description ='Distance'
    
    name = fields.Char('Name', required=True)


class Near(models.Model):
    _name = 'near'
    _description ='Near Readings'
    
    name = fields.Char('Name', required=True)


class WithGlasses(models.Model):
    _name = 'with.glasses'
    _description ='With Glasses Readings'
    
    name = fields.Char('Name', required=True)


class WithoutGlasses(models.Model):
    _name = 'without.glasses'
    _description ='WithoutGlassesReadings'
    
    name = fields.Char('Name', required=True)


class Pin(models.Model):
    _name = 'pin'
    _description ='PIN'
    
    name = fields.Char('Name', required=True)


class IOP(models.Model):
    _name = 'iop'
    _description ='IOP'
    
    name = fields.Char('Name', required=True)


class Spherical(models.Model):
    _name = 'spherical'
    _description ='Spherical'
    
    name = fields.Char('Name', required=True)


class Cylindrical(models.Model):
    _name = 'cylindrical'
    _description ='Cylindrical'
    
    name = fields.Char('Name', required=True)


class Axis(models.Model):
    _name = 'axis'
    _description ='Axis'
    
    name = fields.Char('Name', required=True)


class Vision(models.Model):
    _name = 'vision'
    _description ='Vision'
    
    name = fields.Char('Name', required=True)
