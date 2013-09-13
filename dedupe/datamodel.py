try:
    from collections import OrderedDict
except ImportError :
    from backport import OrderedDict

from dedupe.distance.affinegap import normalizedAffineGapDistance
from dedupe.distance.haversine import compareLatLong
from dedupe.distance.jaccard import compareJaccard


class DataModel(dict) :
    def __init__(self, fields):
        self['bias'] = 0

        self['fields'] = OrderedDict()

        interaction_terms = {}

        for k, v in fields.items():
            self.checkFieldDefinition(v)

            if v['type'] == 'LatLong' :
                v['comparator'] = compareLatLong
            elif v['type'] == 'Set' :
                v['comparator'] = compareJaccard
            elif v['type'] == 'String' :
                v['comparator'] = normalizedAffineGapDistance

            if v['type'] != 'Interaction' :
                self['fields'][k] = v

            else :
                
                if any(fields[field]['Has Missing']
                       for field in v['Interaction Fields'] if 
                       'Has Missing' in fields[field]) :
                    v.update({'Has Missing' : True})

                interaction_terms[k] = v

        self['fields'].update(interaction_terms)
        
        self.missingData()

    def missingData(self) :
        for k, v in self['fields'].items() :
           if 'Has Missing' in v :
               if v['Has Missing'] :
                   self['fields'][k + ': not_missing'] = {'type'   : 'Missing Data'}
           else :
               self['fields'][k].update({'Has Missing' : False})

        

    def checkFieldDefinition(self, definition) :
        assert definition.__class__ is dict, \
            "Incorrect field specification: field " \
            "specifications are dictionaries that must " \
            "include a type definition, ex. " \
            "{'Phone': {type: 'String'}}"

        assert 'type' in definition, \
            "Missing field type: field " \
            "specifications are dictionaries that must " \
            "include a type definition, ex. " \
            "{'Phone': {type: 'String'}}"

        assert definition['type'] in ['String', 'LatLong', 'Set',
                                      'Custom', 'Interaction'], \
            "Invalid field type: field " \
            "specifications are dictionaries that must " \
            "include a type definition, ex. " \
            "{'Phone': {type: 'String'}}"

        if definition['type'] == 'Custom' :
            assert 'comparator' in v, \
                "For 'Custom' field types you must define " \
                "a 'comparator' function in the field "\
                "definition. "
        else :
            assert 'comparator' not in definition, \
                "Custom comparators can only be " \
                "defined for fields of type 'Custom'"

        if definition['type'] == 'Interaction' :
            assert 'Interaction Fields' in definition, \
                'No "Interaction Fields" defined'



