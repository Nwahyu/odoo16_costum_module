from odoo import _, api, fields, models
from datetime import timedelta, datetime
import requests, json
from pprint import pprint
# from tiga import body_rme_kunjungan_baru as kun

class satset_icd10(models.Model):
    _name = 'satset.icd10'
    _description = 'satset.icd10'
    
    
    id_icd10 = fields.Char('id icd10')
    name = fields.Char('name')

class satset_appointment(models.Model):
    _name = 'satset.appointment'
    _description = 'satset.appointment'
    
    # def _attrs_group(self):
    #     return (
    #         self.user.has_group('v_satset.group_satset_dokter')
    #     )
    name = fields.Char('name', related='appointment_id.name')
    status_kirim_data = fields.Boolean('status_kirim')
    # status_kirim_data = fields.Boolean('status_kirim', readonly=_attrs_group)
    nik = fields.Char('nik', related='appointment_id.patient.nik')
    # nama = fields.Char('pasien', related='appointment_id.patient.nama')
    nama = fields.Many2one('medical.patient', string='pasien', related="appointment_id.patient")
    doctor_id = fields.Many2one('medical.physician', string='doctor', related="appointment_id.doctor")
    id_satset_awal = fields.Char('id_satset')
    id_satset_ruangan = fields.Char('id_satset_ruangan')
    id_satset_pulang = fields.Char('id_satset_pulang')
    # health_record = fields.Binary('health record', readonly=_attrs_group)
    health_record = fields.Binary('health record')
    # appointment_id = fields.Many2one('medical.appointment', string='appointment', readonly=_attrs_group)
    appointment_id = fields.Many2one('medical.appointment', string='appointment')
            
    def get_id_satset_pasien_v2(self, nik):
        base_url = self.env['ir.default'].sudo().get('res.config.settings', 'base_url')
        token = self.env['ir.default'].sudo().get('res.config.settings', 'token')
        
        header = {'Authorization':f'Bearer {token}'}
        res = requests.get(f'{base_url}/Patient?identifier=https://fhir.kemkes.go.id/id/nik|{nik}', headers=header)
        return res.json()['entry'][0]['resource']['id']
    
    def get_id_satset_dokter(self, nik):
        base_url = self.env['ir.default'].sudo().get('res.config.settings', 'base_url')
        token = self.env['ir.default'].sudo().get('res.config.settings', 'token')
        header = {'Authorization':f'Bearer {token}'}
        
        res = requests.get(f"{base_url}/Practitioner?identifier=https://fhir.kemkes.go.id/id/nik|{nik}", headers=header)
        return res.json()['entry'][0]['resource']['id']
        
    def get_detail_org(self):
        print('run get detail org')
        token = self.env['ir.default'].sudo().get('res.config.settings', 'token')
        org_ID = self.env['ir.default'].sudo().get('res.config.settings', 'org_ID')
        header = {'Authorization':f'Bearer {token}'}
        # print('org tes')
        # print(org_ID, header)
        uh = requests.get(f'https://api-satusehat-stg.dto.kemkes.go.id/fhir-r4/v1/Organization/{org_ID}',headers=header)
        return uh.status_code
        
    def kirim_data(self):
        print('kirim data v2')
        if self.get_detail_org() != 200:
            # self.env['res.config.settings'].set_values()
            self.env['res.config.settings'].get_access_token()
        # if self.appointment_id.icd10_id:
        a = self.search([('appointment_id.appointment_sdate', '>', datetime.today().date()-timedelta(days=3)), ('status_kirim_data', '=', False)])
        for data in a:
            if data.appointment_id.icd10_id.id_icd10:
                print(f'iniii icd10 {data.appointment_id.icd10_id} {data.appointment_id.icd10_id.id_icd10} {type(data.appointment_id.icd10_id.id_icd10)}')
                if data.appointment_id.icd10_id.id_icd10:
                    print('masuk icd10')
                    if data.appointment_id.patient.id_satset:
                        # self.kirim_encounter(data)
                        data.write({
                            'status_kirim_data': True,
                            'id_satset_awal': self.kirim_encounter(data),
                            'id_satset_ruangan': self.update_encounter(data),
                        })
                        data.appointment_id.write({
                            'id_satset_icd10': self.kirim_diagnosis(data)
                        })
                        data.write({
                            'id_satset_pulang': self.update_encounter_pulang(data)
                        })
                        
                    else:
                        if data.nik:
                            id_satset = self.get_id_satset_pasien_v2(data.appointment_id.patient.nik)
                            pasiennya = data.appointment_id.patient
                            # print(pasiennya)
                            pasiennya.write({
                                'id_satset':id_satset
                            })
                            data.write({
                                'status_kirim_data': True,
                                'id_satset_awal': self.kirim_encounter(data),
                                'id_satset_ruangan': self.update_encounter(data),
                                # 'id_satset_pulang' : '0'
                            })
                            data.appointment_id.write({
                                'id_satset_icd10': self.kirim_diagnosis(data)
                            })
                            data.write({
                                'id_satset_pulang': self.update_encounter_pulang(data)
                            })
                    
                    
                
    def kirim_encounter(self, data):
        # print(f'body {body_rme_kunjungan_baru}')
        print(f'sukses kirim encounter {data}')
        irDefault = self.env['ir.default'].sudo()
        org_id = irDefault.get('res.config.settings', 'org_ID')
        base_url = irDefault.get('res.config.settings', 'base_url')
        id_traffic = data.appointment_id.name
        token = irDefault.get('res.config.settings', 'token')
        header = {'Authorization':f'Bearer {token}'}
        
        
        body = {
                "resourceType": "Encounter",
                "identifier": [
                    {
                        "system": f"http://sys-ids.kemkes.go.id/encounter/{org_id}",
                        "value": f"{data.name}"
                    }
                ],
                "status": "arrived",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory"
                },
                "subject": {
                    "reference": f"Patient/{data.appointment_id.patient.id_satset}",
                    "display": f"{data.appointment_id.patient.nama}"
                },
                "participant": [
                    {
                        "type": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                        "code": "ATND",
                                        "display": "attender"
                                    }
                                ]
                            }
                        ],
                        "individual": {
                            "reference": f"Practitioner/{data.appointment_id.doctor.id_satset}",
                            "display": f"{data.appointment_id.doctor.res_partner_physician_id.name}"
                        }
                    }
                ],
                "period": {
                    "start": "2023-08-31T00:00:00+00:00"
                },
                "location": [
                    {
                        "location": {
                            "reference": f"Location/29125048-8d6b-4c79-b724-992fd7d5dd28",
                            "display": f"poli vhi"
                        },
                        "period": {
                            "start": "2023-08-31T03:00:00+00:00"
                        },
                        "extension": [
                            {
                                "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/ServiceClass",
                                "extension": [
                                    {
                                        "url": "value",
                                        "valueCodeableConcept": {
                                            "coding": [
                                                {
                                                    "system": "http://terminology.kemkes.go.id/CodeSystem/locationServiceClass-Outpatient",
                                                    "code": "reguler",
                                                    "display": "Kelas Reguler"
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "url": "upgradeClassIndicator",
                                        "valueCodeableConcept": {
                                            "coding": [
                                                {
                                                    "system": "http://terminology.kemkes.go.id/CodeSystem/locationUpgradeClass",
                                                    "code": "kelas-tetap",
                                                    "display": "Kelas Tetap Perawatan"
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "statusHistory": [
                    {
                        "status": "arrived",
                        "period": {
                            "start": "2023-08-31T03:00:00+00:00"
                        }
                    }
                ],
                "serviceProvider": {
                    "reference": f"Organization/{org_id}"
                }
            }
        
        # print(f'inin json before {type(body)} {body}')
        res = requests.post(f"{base_url}/Encounter", json.dumps(body), headers=header)
        # print(f'inin jsonnn kriim counte')
        print(res.json())
        return res.json()['id']
        # print(f'inini {res.json()['id']}')
        # print(f"inin id json kiriim {res.json()['class']['id']}")
        
        
    def update_encounter(self, data):
        print('update encounterrrrr')
        irDefault = self.env['ir.default'].sudo()
        org_id = irDefault.get('res.config.settings', 'org_ID')
        base_url = irDefault.get('res.config.settings', 'base_url')
        token = irDefault.get('res.config.settings', 'token')
        header = {'Authorization':f'Bearer {token}'}
        
        body = \
            {
                "resourceType": "Encounter",
                "id": f"{data.id_satset_awal}",
                "identifier": [
                    {
                        "system": f"http://sys-ids.kemkes.go.id/encounter/{org_id}",
                        "value": f"{data.name}"
                    }
                ],
                "status": "in-progress",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory"
                },
                "subject": {
                    "reference": f"Patient/{data.appointment_id.patient.id_satset}",
                    "display": f"{data.appointment_id.patient.nama}"
                },
                "participant": [
                    {
                        "type": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                        "code": "ATND",
                                        "display": "attender"
                                    }
                                ]
                            }
                        ],
                        "individual": {
                            "reference": f"Practitioner/{data.appointment_id.doctor.id_satset}",
                            "display": f"{data.appointment_id.doctor.id_satset}"
                        }
                    }
                ],
                "period": {
                    "start": "2023-08-31T01:00:00+00:00"
                },
                "location": [
                    {
                        "location": {
                            "reference": f"Location/29125048-8d6b-4c79-b724-992fd7d5dd28",
                            "display": "poli vhi"
                        },
                        "period": {
                            "start": "2023-08-31T03:00:00+00:00"
                        },
                        "extension": [
                            {
                                "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/ServiceClass",
                                "extension": [
                                    {
                                        "url": "value",
                                        "valueCodeableConcept": {
                                            "coding": [
                                                {
                                                    "system": "http://terminology.kemkes.go.id/CodeSystem/locationServiceClass-Outpatient",
                                                    "code": "reguler",
                                                    "display": "Kelas Reguler"
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "url": "upgradeClassIndicator",
                                        "valueCodeableConcept": {
                                            "coding": [
                                                {
                                                    "system": "http://terminology.kemkes.go.id/CodeSystem/locationUpgradeClass",
                                                    "code": "kelas-tetap",
                                                    "display": "Kelas Tetap Perawatan"
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "statusHistory": [
                    {
                        "status": "arrived",
                        "period": {
                            "start": "2023-08-31T03:00:00+00:00",
                            "end": "2023-08-31T03:00:00+00:00"
                        }
                    },
                    {
                        "status": "in-progress",
                        "period": {
                            "start": "2023-08-31T03:00:00+00:00"
                        }
                    }
                ],
                "serviceProvider": {
                    "reference": f"Organization/{org_id}"
                }
            }
        
        res = requests.put(f'{base_url}/Encounter/{data.id_satset_awal}', headers=header, data=json.dumps(body))
        print(res.json())
        return res.json()['id']
        # pprint(res.json())
        # print(f'iiiiiiiiiiiiii {data.id_satset_awal}')


    def kirim_diagnosis(self, data):
        print('kirim diagnosis')
        print(data.id_satset_ruangan)
        print(data.id_satset_awal)
        irDefault = self.env['ir.default'].sudo()
        org_id = irDefault.get('res.config.settings', 'org_ID')
        base_url = irDefault.get('res.config.settings', 'base_url')
        token = irDefault.get('res.config.settings', 'token')
        header = {'Authorization':f'Bearer {token}'}
        
        body = \
            {
                "resourceType": "Condition",
                "clinicalStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active",
                            "display": "Active"
                        }
                    ]
                },
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                                "code": "encounter-diagnosis",
                                "display": "Encounter Diagnosis"
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/sid/icd-10",
                            "code": "A15.0",
                            "display": "Tuberculosis of lung, confirmed by sputum microscopy with or without culture"
                        }
                    ]
                },
                "subject": {
                    "reference": f"Patient/{data.appointment_id.patient.id_satset}",
                    "display": f"{data.appointment_id.patient.nama}"
                },
                "encounter": {
                    "reference": f"Encounter/{data.id_satset_ruangan}"
                },
                "onsetDateTime": "2023-08-31T04:10:00+00:00",
                "recordedDate": "2023-08-31T04:10:00+00:00"
            }
        res = requests.post(f'{base_url}/Condition', json.dumps(body), headers=header)
        # print('masukaannnn diagnosis')
        print(res.json())
        return res.json()['id']

    def update_encounter_pulang(self, data):
        print('update encounter pulang')
        irDefault = self.env['ir.default'].sudo()
        org_id = irDefault.get('res.config.settings', 'org_ID')
        base_url = irDefault.get('res.config.settings', 'base_url')
        token = irDefault.get('res.config.settings', 'token')
        header = {'Authorization':f'Bearer {token}'}
    
    
        body = \
            {
                "resourceType": "Encounter",
                "id": "",
                "identifier": [
                    {
                        "system": f"http://sys-ids.kemkes.go.id/encounter/{org_id}",
                        "value": f"{data.id_satset_awal}"
                    }
                ],
                "status": "finished",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory"
                },
                "subject": {
                    "reference": f"Patient/{data.nama.id_satset}",
                    "display": f"{data.nama.nama}"
                },
                "participant": [
                    {
                        "type": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                        "code": "ATND",
                                        "display": "attender"
                                    }
                                ]
                            }
                        ],
                        "individual": {
                            "reference": f"Practitioner/{data.doctor_id.id_satset}",
                            "display": f"{data.doctor_id.res_partner_physician_id.name}"
                        }
                    }
                ],
                "period": {
                    "start": "2023-08-31T00:00:00+00:00",
                    "end": "2023-08-31T04:10:00+00:00"
                },
                "location": [
                    {
                        "location": {
                            "reference": "Location/29125048-8d6b-4c79-b724-992fd7d5dd28",
                            "display": "poli vhi"
                        },
                        "period": {
                            "start": "2023-08-31T00:00:00+00:00"
                        },
                        "extension": [
                            {
                                "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/ServiceClass",
                                "extension": [
                                    {
                                        "url": "value",
                                        "valueCodeableConcept": {
                                            "coding": [
                                                {
                                                    "system": "http://terminology.kemkes.go.id/CodeSystem/locationServiceClass-Outpatient",
                                                    "code": "reguler",
                                                    "display": "Kelas Reguler"
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "url": "upgradeClassIndicator",
                                        "valueCodeableConcept": {
                                            "coding": [
                                                {
                                                    "system": "http://terminology.kemkes.go.id/CodeSystem/locationUpgradeClass",
                                                    "code": "kelas-tetap",
                                                    "display": "Kelas Tetap Perawatan"
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "diagnosis": [
                    {
                        "condition": {
                            "reference": f"Condition/{data.appointment_id.id_satset_icd10}",
                            "display": f"{data.appointment_id.icd10_id.name}"
                        },
                        "use": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                                    "code": "DD",
                                    "display": "Discharge diagnosis"
                                }
                            ]
                        },
                        "rank": 1
                    },
                    {
                        "condition": {
                            "reference": "",
                            "display": ""
                        },
                        "use": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                                    "code": "DD",
                                    "display": "Discharge diagnosis"
                                }
                            ]
                        },
                        "rank": 2
                    }
                ],
                "statusHistory": [
                    {
                        "status": "arrived",
                        "period": {
                            "start": "2023-08-31T03:00:00+00:00",
                            "end": "2023-08-31T03:00:00+00:00"
                        }
                    },
                    {
                        "status": "in-progress",
                        "period": {
                            "start": "2023-08-31T03:00:00+00:00",
                            "end": "2023-08-31T03:00:00+00:00"
                        }
                    },
                    {
                        "status": "finished",
                        "period": {
                            "start": "2023-08-31T03:00:00+00:00",
                            "end": "2023-08-31T03:15:00+00:00"
                        }
                    }
                ],
                "hospitalization": {
                    "dischargeDisposition": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/discharge-disposition",
                                "code": "home",
                                "display": "Home"
                            }
                        ],
                        # "text": "Anjuran dokter untuk pulang dan kontrol kembali 1 bulan setelah minum obat"
                        "text": ""
                    }
                },
                "serviceProvider": {
                    "reference": f"Organization/{org_id}"
                }
            }
            
            
        res = requests.put(f'{base_url}/Encounter/{data.id_satset_awal}', headers=header, data=json.dumps(body))
        # requests.put(f'{base_url}/Encounter/{data.id_satset_awal}', json.dumps(body), headers=header)
        print(res.json())
        return res.json()['id']