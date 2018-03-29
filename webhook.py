# -*- coding: utf-8 -*-
import webapp2
import json
import pandas as pd
import numpy


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        speech = 'Hello!!!!'
        res = {"speech": speech, "displayText": speech, "source": "webhookdata"}
        self.response.write(json.dumps(res, indent=4))

    def __init__(self, *args, **kwargs):
        super(MainPage, self).__init__(*args, **kwargs)
        self.parameters = ['Address', 'ReadyStatus', 'BuildingType']
        self.parameter_values = {p: '' for p in self.parameters}
        self.parameter_events = {p: p + 'Event' for p in self.parameters}

    def get_parameter_values(self, obj):
        for parameter in self.parameters:
            contexts = obj['result']['contexts']
            input_parameters = obj['result']['parameters']
            for context in contexts:
                if parameter in context['parameters'] and len(context['parameters'][parameter]) > 0:
                    self.parameter_values[parameter] = context['parameters'][parameter]
            if parameter in input_parameters and len(input_parameters[parameter]) > 0:
                self.parameter_values[parameter] = input_parameters[parameter]

    def get_result(self, obj):
        result = {}
        action_name = str(obj['result']['action'])
        if action_name == 'search':
            self.get_parameter_values(obj)
            for parameter in self.parameters:
                if self.parameter_values[parameter] == '':
                    event = {
                        'name': self.parameter_events[parameter],
                        'data': {
                            p: self.parameter_values[p] for p in self.parameters
                        }
                    }
                    result = {'followupEvent': event, 'source': 'webhookdata'}
                    return result
            search_table = pd.read_csv('kvartiru.csv')
            for parameter in self.parameters:
                if self.parameter_values[parameter] != 'None':
                    search_table = search_table.loc[search_table[parameter] == self.parameter_values[parameter]]
            if search_table.size > 0:
                data = {
                    'telegram':
                        {
                            'text': 'Результаты поиска: ',
                            'reply_markup': {
                                'inline_keyboard': [
                                    [{'text': n, 'url': u}] for n, u in zip(search_table['Name'], search_table['URL'])
                                ]
                            }
                        }
                }
            else:
                data = {
                    'telegram':
                        {
                            'text': 'По запросу ничего не найдено...'
                        }
                }
            result = {'source': 'webhookdata', 'data': data}
        return result

    def post(self):
        json_data = self.request.body
        obj = json.loads(json_data)
        try:
            result = self.get_result(obj)
        except Exception as e:
            result = {'speech': str(e), 'displayText': str(e), 'source': 'webhookdata'}
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(json.dumps(result, indent=4))


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

