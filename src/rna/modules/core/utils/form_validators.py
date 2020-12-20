from wtforms.validators import Optional, DataRequired


class RequiredIf(DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
        - https://gist.github.com/devxoul/7638142#file-wtf_required_if-py
    """
    field_flags = ('requiredif',)

    def __init__(self, message=None, exclude=None, *args, **kwargs):
        super(RequiredIf).__init__()
        self.message = message
        self.exclude = exclude
        self.conditions = kwargs

    # field is requiring that name field in the form is data value in the form
    def __call__(self, form, field):
        for name, data in self.conditions.items():
            other_field = form[name]
            if other_field is None:
                raise Exception('no field named "%s" in form' % name)
            if self.exclude:
                print(self.exclude(form))
            if self.exclude and self.exclude(form):
                Optional()(form, field)
                continue
            if other_field.data == data and not field.data:
                DataRequired.__call__(self, form, field)
            Optional()(form, field)
