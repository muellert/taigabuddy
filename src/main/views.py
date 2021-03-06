from flask import render_template
from flask.views import MethodView


class TemplateFinderViewBase(MethodView):
    """factor common view functionality out"""

    def __init__(self, template_name):
        self.template_name = template_name

    def render_template(self, context):
        return render_template(self.template_name, **context)

