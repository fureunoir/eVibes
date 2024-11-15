from django import forms
import json

class JSONTableWidget(forms.Widget):
    template_name = 'json_table_widget.html'

    def format_value(self, value):
        if isinstance(value, dict):
            return value
        try:
            if isinstance(value, str):
                value = json.loads(value)
        except json.JSONDecodeError:
            value = {}
        return value

    def render(self, name, value, attrs=None, renderer=None):
        value = self.format_value(value)
        return super().render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        keys = data.getlist(f'{name}_key')
        values = data.getlist(f'{name}_value')

        json_data = {}
        for key, value in zip(keys, values):
            if key:
                try:
                    json_data[key] = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    json_data[key] = value

        return json_data
