from flask import url_for


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    # @app.template_global(name='zip')
    # def _zip(*args, **kwargs):  # to not overwrite builtin zip in globals
    #     return __builtins__.zip(*args, **kwargs)

    app.add_template_global(index_for_role)

    # @app.template_global()
    #     def what_color()


def index_for_role(role):
    return url_for(role.index)