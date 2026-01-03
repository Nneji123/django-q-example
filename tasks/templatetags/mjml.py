from django import template
from io import BytesIO
from mjml import mjml_to_html

register = template.Library()


@register.tag(name="mjml")
def do_mjml(parser, token):
    nodelist = parser.parse(("endmjml",))
    parser.delete_first_token()
    return MjmlNode(nodelist)


class MjmlNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        mjml_content = self.nodelist.render(context)
        mjml_bytes = BytesIO(mjml_content.encode("utf-8"))
        result = mjml_to_html(mjml_bytes)
        if result.errors:
            return f"<!-- MJML Errors: {result.errors} -->\n{mjml_content}"
        return result.html

