__author__ = 'Daniil Nikulin'
__license__ = "Apache License 2.0"
__email__ = "danil.nikulin@gmail.com"
__date__ = "2018-01-26"
__app__ = "statswebapp"
__status__ = "Development"

from .. import db


class LocationFieldPanel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(6), unique=True)
    number = db.Column(db.String(10), unique=True)


    # @staticmethod
    # def get_editable_html(editor_name):
    #     editable_html_obj = EditableHTML.query.filter_by(
    #         editor_name=editor_name).first()
    #
    #     if editable_html_obj is None:
    #         editable_html_obj = EditableHTML(editor_name=editor_name, value='')
    #     return editable_html_obj
