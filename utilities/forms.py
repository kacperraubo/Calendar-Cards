from django import forms


class StringListField(forms.Field):
    def __init__(self, *args, required=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.required = required

    def clean(self, value):
        if value is None:
            return []

        if isinstance(value, list):
            return value

        return value.split(",")
