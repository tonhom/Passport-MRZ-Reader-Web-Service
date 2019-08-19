from flask import json

class PersonalData():
    surname: str
    given_names: str
    country_code: str
    passport_number: str
    nationality: str
    birth_date: str
    sex: str
    expiry_date: str

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
