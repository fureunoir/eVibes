import json

from django import forms


class JSONTableWidget(forms.Widget):
    template_name = "json_table_widget.html"

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
        json_data = {}

        try:
            keys = data.getlist(f"{name}_key")
            values = data.getlist(f"{name}_value")
            for key, value in zip(keys, values):
                if key.strip():
                    try:
                        json_data[key] = json.loads(value)
                    except (json.JSONDecodeError, ValueError):
                        json_data[key] = value
        except TypeError:
            pass

        return None if not json_data else json.dumps(json_data)
