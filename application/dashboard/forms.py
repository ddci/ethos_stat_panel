from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextField
from wtforms.validators import InputRequired, Length

__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-26"
__app__ = "statswebapp"
__status__ = "Development"


class ManagementRigsForm(FlaskForm):
    username = StringField(
        'Username', validators=[InputRequired(), Length(4, 64)])
    password = PasswordField(
        'Password', validators=[InputRequired()])
    ssh_username = StringField(
        'SHH Username', validators=[InputRequired(), Length(2, 64)])
    ssh_password = PasswordField(
        'SHH Password', validators=[InputRequired(), Length(2, 64)])

    put_conf = BooleanField("Putconf + Reboot")
    clear_thermals = BooleanField("Clear thermals + Reboot")
    reboot_task = BooleanField("Reboot")
    update_miners = BooleanField("Update Miners")
    allow_command = BooleanField("Allow")

    update_miner_with_name = BooleanField("Update specific miner", id="minerNameCheckbox")

    miner_name = StringField("Miner name: ", id="minerNameField")

    change_password = BooleanField("Change ethOS password", id="passwordCheckbox")

    new_password = StringField("New ethos password: ", id="passwordField")

    execute_custom_command = BooleanField("Execute custom command", id="CustomCommandCheckbox")

    custom_command = StringField("Custom command: ", id="customCommand")

    submit = SubmitField('Execute commands', id="submitManagementRigsForm")
