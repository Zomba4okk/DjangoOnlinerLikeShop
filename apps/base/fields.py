from django.forms.fields import MultipleChoiceField


class MultipleField(MultipleChoiceField):
    def valid_value(self, value):
        return True
