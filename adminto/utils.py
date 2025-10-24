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



# from django.template.loader import get_template


# def render_to_pdf(template_src, context=None):
#     context = context or {}
#     html = get_template(template_src).render(context)
#     return HTML(string=html, base_url="/").write_pdf(
#         stylesheets=[CSS(string="@page { size: A4; margin: 18mm; }")]
#     )




from django.template.loader import get_template
from django.core.exceptions import ImproperlyConfigured

def render_to_pdf(template_src, context=None, base_url="/"):
    # ⬇️ Import paresseux : WeasyPrint ne se charge que quand on appelle la fonction
    try:
        from weasyprint import HTML, CSS
    except Exception as e:
        raise ImproperlyConfigured(
            "WeasyPrint n'est pas disponible (dépendances système manquantes). "
            "Installe cairo/pango/gdk-pixbuf OU utilise une autre implémentation de render_to_pdf. "
            f"Erreur d'origine : {e}"
        )

    context = context or {}
    html_str = get_template(template_src).render(context)
    return HTML(string=html_str, base_url=base_url).write_pdf(
        stylesheets=[CSS(string="@page { size: A4; margin: 18mm; }")]
    )
