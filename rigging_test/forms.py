from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError

class UmountComponentForm(FlaskForm):
    component_id = HiddenField('Component ID', validators=[DataRequired()])
    current_aad_jumps = IntegerField('Current AAD Jumps', validators=[DataRequired(), NumberRange(min=0)])
    aad_jumps_on_mount = HiddenField('AAD Jumps on Mount', validators=[DataRequired()])
    submit = SubmitField('Remove Component')

    def validate_current_aad_jumps(form, field):
        if field.data < int(form.aad_jumps_on_mount.data):
            raise ValidationError('Current AAD Jumps cannot be less than AAD Jumps on Mount.')