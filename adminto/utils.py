# from io import BytesIO
# from django.http import HttpResponse
# from django.template.loader import get_template

# from xhtml2pdf import pisa

# def render_to_pdf(template_src, context_dict={}):
#     template = get_template(template_src)
#     html  = template.render(context_dict)
#     options = {
#         'footer-right':'[page] of [topage]',
#     }
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
#     # pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result, encoding='UTF-8')
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type='application/pdf')
#     return None



from django.template.loader import get_template
from weasyprint import HTML, CSS

def render_to_pdf(template_src, context=None):
    context = context or {}
    html = get_template(template_src).render(context)
    return HTML(string=html, base_url="/").write_pdf(
        stylesheets=[CSS(string="@page { size: A4; margin: 18mm; }")]
    )