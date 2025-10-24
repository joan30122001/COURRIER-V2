from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from adminto.forms import *
from datetime import datetime
import random
from .models import Courrier
from django.views import View
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
import json
from django.db.models import Q # new
from django.views.generic import ListView
from django.urls import reverse
import pdfkit
from django.http import HttpResponse
from django.template import loader
import io
from .utils import render_to_pdf
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .filters import CourrierFilter
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.db.models.functions import TruncDate
from openai import OpenAI
import os
from django.conf import settings
# from google import genaiimage_to_pdf_via_gemini
from django.views.decorators.csrf import ensure_csrf_cookie
import mimetypes
from pathlib import Path
# from .tools.tesseract_pdf import image_to_searchable_pdf_bytes

from .tools.gemini_pdf import image_to_pdf_via_gemini
import google.generativeai as genai







from django.forms import modelform_factory
# from .models import Picture

from django.core.files.storage import FileSystemStorage
# from .models import WebcamImage
from django.core.files.base import ContentFile
from django.utils import timezone
import re
from django.http import HttpResponseBadRequest




def chef_service(request):

    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    form = RegistrationForm(request.POST or None)
    chef_service = Courrier()

    if request.method == 'POST':
        # if code_unique:
        #     form = CiviliteForm(request.POST or None, instance=etudiant)
        #     if form.is_valid():
        #         form.save()
        #         messages.add_message(request, messages.SUCCESS, _(f"Informations de civilité modifiées avec succès."))
        #         return redirect('logement:filiation')
        #     else:
        #         messages.add_message(request, messages.ERROR, _('Veuillez vérifier les champs en rouge !!!'))
        #         return render(request, 'logement/civilite.html', {'form': form})
        # else:
        #     form = CiviliteForm(request.POST or None)
        #     etudiant = DemandeChambre()

        # form = RegistrationForm(request.POST or None)
        # chef_service = Courrier()

        if form.is_valid():
            # code_unique = generate_unique_code(str(form.cleaned_data['date_nais']))

            # etudiant.num_ordre = code_unique

            chef_service.transmetteur = form.cleaned_data['transmetteur']                
            chef_service.recepteur = form.cleaned_data['recepteur']                
            chef_service.code = form.cleaned_data['code']                
            chef_service.date = form.cleaned_data['date']                
            chef_service.objet = form.cleaned_data['objet']
            chef_service.structure = form.cleaned_data['structure']                
            chef_service.annee = form.cleaned_data['annee']
            chef_service.types = form.cleaned_data['types']
        
            chef_service.save()
            # request.session['code_logement'] = code_unique

            messages.add_message(request, messages.SUCCESS, (f"Informations du courrier enregistrées avec succès."))
            # return redirect('logement:filiation', request.session['ecole_code'] )
            return redirect('senat:chef_service')
        else:
            messages.add_message(request, messages.ERROR, ('Veuillez vérifier les champs en rouge !!!'))
            return render(request, 'chef_service.html', {'form': form})

    context = {
        'form': form,
        'count_courrier': count_courrier,
    }
    return render(request,'chef_service.html', context)



def chef_depart(request):
    return render(request,'chef_depart.html')



def chef_arrive(request):
    return render(request,'chef_arrive.html')



def bureau_sg(request):
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    type_elt = request.GET.get('types')
    code = request.GET.get('code')

    courrier = Courrier.objects.filter(
        code=code, types=type_elt
    )
    
    sg = get_object_or_404(Courrier, code=code, types=type_elt)
    form = MentionForm(instance=sg)

    if request.method == 'POST':
        form = MentionForm(request.POST or None, instance=sg)
        if form.is_valid():
            sg.service_traitement = form.cleaned_data['service_traitement']
            sg.mention = form.cleaned_data['mention']                
            # sg.service_traitement = form.cleaned_data['service_traitement'] 
            sg.save()
            messages.add_message(request, messages.SUCCESS, (f"Informations du courrier enregistrées avec succès."))
            # return redirect('senat:bureau_sg')

    return render(request,'sg.html', {"courrier": courrier, "form": form, "courrier": courrier, "count_courrier": count_courrier})



def usager(request):
    return render(request,'usager.html')



# def search(request):
#     if request.method == 'POST':
#         query = request.POST.get('code')
#         querys = request.POST.get('types')
        
#         objects = Courrier.objects.filter(code=query, types=querys, structure="SENAT")
#         if not objects: 
#             messages.error(request, "Le code ou le type fourni n'existe pas")
#             return redirect('senat:search')


#         response = redirect('/bureau_sg/' + f'?code={query}&types={querys}')
#         return response

#     else:
#         return render(request, 'search_sg.html')

def search(request):
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()
    if request.method == 'POST':
        query = request.POST.get('code')
        querys = request.POST.get('types')

        objects = Courrier.objects.filter(code=query, types=querys, structure="SENAT")
        if not objects:
            messages.error(request, "Le code ou le type fourni n'existe pas")
            return redirect('senat:search')

        # ✅ Utiliser reverse avec paramètres GET
        base_url = reverse('senat:bureau_sg')
        redirect_url = f"{base_url}?code={query}&types={querys}"
        return redirect(redirect_url)

    return render(request, 'search_sg.html', {"courrier": courrier, "count_courrier": count_courrier})




def courrier_attente(request):
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    # if request.method == 'POST':
    #     request.is_active = False
    #     request.save()
    #compter le nombre de courrier
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    return render(request, 'courrier_attente.html', {"courrier": courrier, "count_courrier": count_courrier})



def deactivate_record(request, id):
    record = get_object_or_404(Courrier, pk=id)
    if request.method == 'POST':
        record.is_active = False
        record.save()
        return HttpResponseRedirect('/')
    return render(request, 'chef_service.html', {"record": record})



def courrier_attente_detail(request, id):
    obj = get_object_or_404(Courrier, pk=id)

    #compter le nombre de courrier
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    return render(request, 'courrier_detail.html', {"obj": obj, "count_courrier": count_courrier})



# def traited(request):
#     is_active = False
#     request.object.save()
#     return redirect('senat:courrier_attente')



def search_chef(request):

    if request.method == 'POST':
        query = request.POST.get('code')
        querys = request.POST.get('types')
        queryss = request.POST.get('objet')

        base_url = reverse('senat:result_chef')
        redirect_url = f"{base_url}?code={query}&types={querys}&objet={queryss}' or f'?code={query}&types={querys}&objet={queryss}' or f'?objet={queryss}"
        # response = redirect('/result_chef/' + f'?code={query}&types={querys}&objet={queryss}' or f'?code={query}&types={querys}&objet={queryss}' or f'?objet={queryss}')
        # return response
        return redirect(redirect_url)
    else:
        return render(request, 'search_chef.html')



def result_chef(request):
     #compter le nombre de courrier
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    type_elt = request.GET.get('types')
    code = request.GET.get('code')
    objet = request.GET.get('objet')



    courrier = Courrier.objects.filter(
        code=code, types=type_elt
    ) or Courrier.objects.filter(
        code=code, types=type_elt, objet=objet
    )or Courrier.objects.filter(
        objet=objet
    )
    return render(request,'result_chef.html', {"courrier": courrier, "count_courrier": count_courrier})



# def courrier_pdf(request, pk):
#     user_courrier = Courrier.objects.get(pk=pk)

#     context = {
#         "user_courrier": user_courrier,
#     }
    
#     pdf = render_to_pdf('courrier_pdf.html', context)
#     return HttpResponse(pdf, content_type='application/pdf')


def courrier_pdf(request, pk):
    user_courrier = Courrier.objects.get(pk=pk)
    pdf = render_to_pdf('courrier_pdf.html', {"user_courrier": user_courrier})
    return HttpResponse(pdf, content_type='application/pdf')



def list_courrier(request):
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    courriers = Courrier.objects.all()
    # courriers = Courrier.objects.filter(is_active=True).order_by('-created_on')

    #pagination
    # page = request.GET.get('page')
    # num_of_items = 3
    # paginator = Paginator(courriers, num_of_items)

    # try:
    #     courrierss = paginator.page(page)
    # except PageNotAnInteger:
    #     page = 1
    #     courrierss = paginator.page(page)
    # except EmptyPage:
    #     page = paginator.num_pages
    #     courrierss = paginator.page(page)

    #barre de filtre
    courriers_filter = CourrierFilter(request.GET, queryset=courriers)

    return render(request, 'liste_courrier.html', {'courriers': courriers, 
                                                   'count_courrier': count_courrier, 
                                                #    'paginator': paginator,
                                                   'courriers_filter':courriers_filter,
                                                   })



# def envoi_email(request):
#     courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
#     count_courrier = courrier.count()

#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         message = request.POST.get('message')
#         attachment = request.FILES.get('attachment')
#         form_data = {
#             'name':name,
#             'email':email,
#             # 'phone':phone,
#             'message':message,
#             'attachment':MIMEMultipart(),
#         }
#         recipient_list = email
#         send_mail(name, message, email, [recipient_list], attachment)
        

#     return render(request,'envoi_email.html', {"courrier": courrier, "count_courrier": count_courrier})



from django.core.mail import EmailMessage
from django.shortcuts import render
from .models import Courrier

# def envoi_email(request):
#     courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
#     count_courrier = courrier.count()

#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')  # recipient email
#         message = request.POST.get('message')
#         attachment = request.FILES.get('attachment')

#         email_msg = EmailMessage(
#             subject=name,
#             body=message,
#             from_email=None,  # uses DEFAULT_FROM_EMAIL
#             to=[email],       # dynamic recipient
#         )

#         if attachment:
#             email_msg.attach(attachment.name, attachment.read(), attachment.content_type)

#         email_msg.send()

#     return render(request, 'envoi_email.html', {
#         "courrier": courrier,
#         "count_courrier": count_courrier
#     })








# from django.core.mail import EmailMessage
# from django.shortcuts import render
# from .models import Courrier

# def envoi_email(request):
#     courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
#     count_courrier = courrier.count()

#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         message = request.POST.get('message')
#         attachment = request.FILES.get('attachment')

#         subject = name or "Message sans titre"
#         from_email = None  # uses DEFAULT_FROM_EMAIL
#         to_email = [email]

#         email_msg = EmailMessage(subject, message, from_email, to_email)

#         if attachment:
#             try:
#                 # Read the content ONLY once
#                 file_data = attachment.read()
#                 file_name = attachment.name
#                 content_type = attachment.content_type

#                 email_msg.attach(file_name, file_data, content_type)
#             except Exception as e:
#                 print("Erreur d'attachement:", e)

#         email_msg.send()

#     return render(request, 'envoi_email.html', {
#         "courrier": courrier,
#         "count_courrier": count_courrier
#     })




from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import render
from .models import Courrier

def envoi_email(request):
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        attachment = request.FILES.get('attachment')

        subject = name or "Message sans titre"
        from_email = None  # uses DEFAULT_FROM_EMAIL
        to_email = [email]

        email_msg = EmailMessage(subject, message, from_email, to_email)

        if attachment:
            try:
                file_data = attachment.read()
                file_name = attachment.name
                content_type = attachment.content_type
                email_msg.attach(file_name, file_data, content_type)
            except Exception as e:
                messages.error(request, "Échec de l'ajout du fichier.")
                return render(request, 'envoi_email.html', {
                    "courrier": courrier,
                    "count_courrier": count_courrier
                })

        try:
            email_msg.send()
            messages.success(request, "Message envoyé avec succès.")
        except Exception as e:
            messages.error(request, "Échec de l'envoi du message.")

    return render(request, 'envoi_email.html', {
        "courrier": courrier,
        "count_courrier": count_courrier
    })














import base64
import io
import numpy as np
import cv2
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Capture
from io import BytesIO
from django.utils.encoding import smart_str
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def indexs(request):
    return render(request, 'indexs.html')



# def capture(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         image_data = request.POST.get('image')
#         image_data = image_data.replace('data:image/png;base64,', '')
#         image_data = base64.b64decode(image_data)
#         capture = Capture(name=name)
#         image_file = BytesIO(image_data)
#         capture.image.save(name + '.png', image_file)
#         capture.save()
#         return redirect('senat:captures')
#     return render(request, 'capture.html')



def captures(request):
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    captures = Scan.objects.all()
    return render(request, 'captures.html', {'captures': captures, 'count_courrier':count_courrier})










# def scan(request):

#     courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
#     count_courrier = courrier.count()

#     form = ScanForm(request.POST, request.FILES)
#     scan = Scan()

#     if request.method == 'POST':
#         if form.is_valid():
#             scan.name = form.cleaned_data['name']                
#             scan.file = form.cleaned_data['file']                
        
#             scan.save()
#             messages.add_message(request, messages.SUCCESS, (f"Informations du courrier enregistrées avec succès."))
#             return redirect('senat:scan')
#         else:
#             messages.add_message(request, messages.ERROR, ('Veuillez vérifier les champs !!!'))
#             return render(request, 'scan.html', {'form': form})
#     context = {
#         'form': form,
#         'count_courrier': count_courrier,
#     }
#     return render(request,'scan.html', context)


def scan(request):
    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    if request.method == 'POST':
        form = ScanForm(request.POST, request.FILES)
        if form.is_valid():
            scan = form.save()
            messages.success(request, "Informations du courrier enregistrées avec succès.")
            return redirect('senat:scan')
        else:
            messages.error(request, "Veuillez vérifier les champs !!!")
    else:
        form = ScanForm()

    context = {
        'form': form,
        'count_courrier': count_courrier,
    }
    return render(request, 'scan.html', context)







def download_capture(request, capture_id):
    capture = get_object_or_404(Scan, id=capture_id)
    response = HttpResponse(capture.file, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename={}'.format(smart_str(capture.name + '.png'))
    return response

# def download_capture_pdf(request, capture_id):
#     capture = get_object_or_404(Scan, id=capture_id)
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename={}'.format(smart_str(capture.name + '.pdf'))
#     buffer = io.BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=letter)
#     img = ImageReader(capture.file.path)
#     pdf.drawImage(img, 0, 0, width=letter[0], height=letter[1])
#     pdf.showPage()
#     pdf.save()
#     pdf_data = buffer.getvalue()
#     buffer.close()
#     response.write(pdf_data)
#     return response


def download_capture_pdf(request, capture_id):
    capture = get_object_or_404(Scan, id=capture_id)
    im = Image.open(capture.file.path).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="PDF")
    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type="application/pdf")
    resp['Content-Disposition'] = 'attachment; filename={}'.format(
        smart_str(f"{capture.name}.pdf")
    )
    return resp










def search_usager(request):
    
    if request.method == 'POST':
        query = request.POST.get('code')
        querys = request.POST.get('types')
        queryss = request.POST.get('objet')


        response = redirect('/result_usager/' + f'?code={query}&types={querys}&objet={queryss}' or f'?code={query}&types={querys}&objet={queryss}' or f'?objet={queryss}')
        return response
    else:
        return render(request, 'search_usager.html')



def result_usager(request):
    #compter le nombre de courrier
    # courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    # count_courrier = courrier.count()

    type_elt = request.GET.get('types')
    code = request.GET.get('code')
    objet = request.GET.get('objet')



    courrier = Courrier.objects.filter(
        code=code, types=type_elt
    ) or Courrier.objects.filter(
        code=code, types=type_elt, objet=objet
    )or Courrier.objects.filter(
        objet=objet
    )
    return render(request,'result_usager.html', {"courrier": courrier})



def terminer_courrier(request, id):
    courrier = get_object_or_404(Courrier, id=id)
    if request.method == 'POST':
        courrier.mention = "AUTRES"
        courrier.save()
        messages.success(request, "Courrier terminé avec succès.")
    return redirect('senat:courrier_attente')





# views.py
import json
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, F
from django.utils import timezone
from django.shortcuts import render

# from .models import Courrier, Scan  # <-- garde tes imports réels

@login_required
# def dashboard(request):
#     courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
#     count_courrier = courrier.count()
#     # Statistiques de base
#     total_courriers = Courrier.objects.count()
#     courriers_entrants = Courrier.objects.filter(types__in=['LETTRE(L)', 'REQUETE(R)', 'NOTE(N)']).count()
#     courriers_sortants = Courrier.objects.filter(types__in=['DECISION(D)', 'PROJET DE LOI(PJL)', 'ARRETE DE BUREAU(AB)']).count()
    
#     # Taux d'archivage (prends l'un des deux selon ta logique)
#     total_archives_courrier = Courrier.objects.filter(is_active=False).count()
#     total_archives_scan = Scan.objects.count()
#     total_archives = total_archives_scan or total_archives_courrier  # priorité au Scan si présent
#     taux_archivage = (total_archives / total_courriers * 100) if total_courriers > 0 else 0

#     # Délai moyen (en jours) entre created_at et date (adaptable à ta logique métier)
#     delai_result = Courrier.objects.filter(is_active=False).aggregate(
#         avg_delai=Avg(F('created_at') - F('date'))
#     )
#     delai_moyen = delai_result['avg_delai']
#     delai_jours = delai_moyen.days if delai_moyen else 0

#     # Répartition par service / type / mention
#     courriers_par_service = list(
#         Courrier.objects.values('service_traitement')
#         .annotate(count=Count('id'))
#         .order_by('-count')[:10]
#     )
#     courriers_par_type = list(
#         Courrier.objects.values('types')
#         .annotate(count=Count('id'))
#         .order_by('-count')
#     )
#     courriers_par_mention = list(
#         Courrier.objects.values('mention')
#         .annotate(count=Count('id'))
#         .order_by('-count')
#     )

#     # Série temporelle sur 30 jours (groupée par date)
#     date_limite = timezone.now() - timedelta(days=30)
#     courriers_30_jours_qs = (
#         Courrier.objects.filter(created_at__gte=date_limite)
#         .annotate(date_created=TruncDate('created_at'))
#         .values('date_created')
#         .annotate(count=Count('id'))
#         .order_by('date_created')
#     )
#     dates = [item['date_created'].strftime('%Y-%m-%d') for item in courriers_30_jours_qs]
#     # dates = [item['date_created'] if isinstance(item['date_created'], str) else item['date_created'].strftime('%Y-%m-%d') for item in courriers_30_jours_qs]
#     counts = [item['count'] for item in courriers_30_jours_qs]

#     # Courriers récents
#     courriers_recents = Courrier.objects.all().order_by('-created_at')[:10]

#     context = {
#         'count_courrier': count_courrier,
#         'total_courriers': total_courriers,
#         'courriers_entrants': courriers_entrants,
#         'courriers_sortants': courriers_sortants,
#         'taux_archivage': round(taux_archivage, 2),
#         'delai_moyen': delai_jours,

#         'courriers_par_service': courriers_par_service,
#         'courriers_par_type': courriers_par_type,
#         'courriers_par_mention': courriers_par_mention,

#         'courriers_30_jours': courriers_30_jours_qs,
#         'courriers_recents': courriers_recents,

#         # JSON pour Chart.js (on sérialise ici)
#         'dates_json': json.dumps(dates),
#         'counts_json': json.dumps(counts),
#         'courriers_par_type_json': json.dumps(courriers_par_type),
#         'courriers_par_service_json': json.dumps(courriers_par_service),
#         'courriers_par_mention_json': json.dumps(courriers_par_mention),
#     }
#     return render(request, 'dashboard.html', context)



def dashboard(request):
    # helper local pour normaliser les valeurs vides → "Non défini"
    from collections import defaultdict
    def normalize_group(qs, key, label_fallback="Non défini"):
        acc = defaultdict(int)
        for row in qs:
            label = row.get(key)
            label = label if (label is not None and str(label).strip() != "") else label_fallback
            acc[label] += row["count"]
        return [{key: k, "count": v} for k, v in acc.items()]

    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()
    # Statistiques de base
    total_courriers = Courrier.objects.count()
    courriers_entrants = Courrier.objects.filter(types__in=['LETTRE(L)', 'REQUETE(R)', 'NOTE(N)']).count()
    courriers_sortants = Courrier.objects.filter(types__in=['DECISION(D)', 'PROJET DE LOI(PJL)', 'ARRETE DE BUREAU(AB)']).count()
    
    # Taux d'archivage (prends l'un des deux selon ta logique)
    total_archives_courrier = Courrier.objects.filter(is_active=False).count()
    total_archives_scan = Scan.objects.count()
    total_archives = total_archives_scan or total_archives_courrier  # priorité au Scan si présent
    taux_archivage = (total_archives / total_courriers * 100) if total_courriers > 0 else 0

    # Délai moyen (en jours) entre created_at et date (adaptable à ta logique métier)
    delai_result = Courrier.objects.filter(is_active=False).aggregate(
        avg_delai=Avg(F('created_at') - F('date'))
    )
    delai_moyen = delai_result['avg_delai']
    delai_jours = delai_moyen.days if delai_moyen else 0

    # Répartition par service / type / mention
    # (1) service_traitement avec fallback "Non défini"
    raw_service = (
        Courrier.objects.values('service_traitement')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    courriers_par_service = normalize_group(raw_service, 'service_traitement')[:10]

    # (2) types (inchangé)
    courriers_par_type = list(
        Courrier.objects.values('types')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # (3) mention avec fallback "Non défini"
    raw_mention = (
        Courrier.objects.values('mention')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    courriers_par_mention = normalize_group(raw_mention, 'mention')

    # Série temporelle sur 30 jours (groupée par date)
    date_limite = timezone.now() - timedelta(days=30)
    courriers_30_jours_qs = (
        Courrier.objects.filter(created_at__gte=date_limite)
        .annotate(date_created=TruncDate('created_at'))
        .values('date_created')
        .annotate(count=Count('id'))
        .order_by('date_created')
    )
    dates = [item['date_created'].strftime('%Y-%m-%d') for item in courriers_30_jours_qs]
    counts = [item['count'] for item in courriers_30_jours_qs]

    # Courriers récents
    courriers_recents = Courrier.objects.all().order_by('-created_at')[:10]

    context = {
        'count_courrier': count_courrier,
        'total_courriers': total_courriers,
        'courriers_entrants': courriers_entrants,
        'courriers_sortants': courriers_sortants,
        'taux_archivage': round(taux_archivage, 2),
        'delai_moyen': delai_jours,

        'courriers_par_service': courriers_par_service,
        'courriers_par_type': courriers_par_type,
        'courriers_par_mention': courriers_par_mention,

        'courriers_30_jours': courriers_30_jours_qs,
        'courriers_recents': courriers_recents,

        # JSON pour Chart.js (on sérialise ici)
        'dates_json': json.dumps(dates),
        'counts_json': json.dumps(counts),
        'courriers_par_type_json': json.dumps(courriers_par_type),
        'courriers_par_service_json': json.dumps(courriers_par_service),
        'courriers_par_mention_json': json.dumps(courriers_par_mention),
    }
    return render(request, 'dashboard.html', context)







# @ensure_csrf_cookie
# @login_required
# def chatbot_page(request):
#     return render(request, "chat.html")


# client = genai.Client(api_key=settings.GEMINI_API_KEY)

# @login_required
# def chatbot_ask(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "POST only"}, status=405)

#     try:
#         payload = json.loads(request.body.decode("utf-8"))
#     except Exception:
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     user_msg = (payload.get("message") or "").strip()
#     if not user_msg:
#         return JsonResponse({"error": "Message manquant"}, status=400)

#     # —— Recherche rapide côté DB (tes champs) ——
#     qs = (
#         Courrier.objects.filter(
#             Q(code__icontains=user_msg)
#             | Q(objet__icontains=user_msg)
#             | Q(types__icontains=user_msg)
#             | Q(service_traitement__icontains=user_msg)
#             | Q(mention__icontains=user_msg)
#             | Q(transmetteur__icontains=user_msg)
#             | Q(recepteur__icontains=user_msg)
#         )
#         .order_by("-created_at")[:10]
#         .values(
#             "code","types","objet","service_traitement","mention",
#             "date","created_at","transmetteur","recepteur"
#         )
#     )
#     snippets = list(qs)

#     # —— Contexte envoyé au modèle ——
#     today = timezone.now().strftime("%Y-%m-%d %H:%M")
#     context_doc = {
#         "generated_at": today,
#         "count": len(snippets),
#         "examples": snippets,
#         "policy": {
#             "privacy": "Ne jamais divulguer des données sensibles hors besoin légitime.",
#             "scope": "Répondre UNIQUEMENT à propos des courriers et des stats du système.",
#         },
#     }
#     system_prompt = (
#         "Tu es un assistant interne du Sénat du Cameroun pour l'application de gestion du courrier. "
#         "Réponds en français, de manière concise, en citant les champs utiles (code, date, type, service, mention). "
#         "Si la question sort du périmètre (courriers, stats, procédures), dis-le poliment."
#     )

#     # —— Appel Gemini (free: modèle rapide conseillé) ——
#     try:
#         # gemini-1.5-flash est bien adapté au free tier (rapide, peu coûteux)
#         result = client.models.generate_content(
#             model="gemini-1.5-flash",
#             contents=[
#                 {"role": "user", "parts": [
#                     system_prompt +
#                     "\n\nVoici un extrait JSON de données internes (à utiliser si pertinent):\n" +
#                     json.dumps(context_doc, ensure_ascii=False) +
#                     "\n\nQuestion de l'utilisateur:\n" + user_msg
#                 ]}
#             ],
#             config={
#                 "temperature": 0.2,
#                 "max_output_tokens": 600,
#             },
#         )

#         ai_text = ""
#         # Le SDK renvoie généralement `result.text` (ou `candidates` selon version)
#         if hasattr(result, "text") and result.text:
#             ai_text = result.text.strip()
#         elif hasattr(result, "candidates") and result.candidates:
#             # compat: certaines versions renvoient candidates[0].content.parts[0].text
#             try:
#                 ai_text = result.candidates[0].content.parts[0].text.strip()
#             except Exception:
#                 ai_text = ""

#         if not ai_text:
#             ai_text = "Je n'ai pas pu générer de réponse pour le moment."

#         return JsonResponse({"ok": True, "answer": ai_text, "matched": snippets})
#     except Exception as e:
#         return JsonResponse({"error": f"Gemini API error: {e}"}, status=500)










# def scan_list(request):
#     qs = Scan.objects.select_related("courrier").order_by("-created_at")
#     # (optionnel) petite recherche par code ou nom
#     q = request.GET.get("q", "").strip()
#     if q:
#         qs = qs.filter(courrier__code__icontains=q) | qs.filter(name__icontains=q)

#     paginator = Paginator(qs, 12)
#     page = request.GET.get("page")
#     scans = paginator.get_page(page)
#     return render(request, "scans_list.html", {"scans": scans, "q": q})

# def scan_download(request, pk: int):
#     scan = get_object_or_404(Scan, pk=pk)
#     if not scan.file:
#         raise Http404("Fichier introuvable.")
#     # Téléchargement forcé
#     return FileResponse(
#         scan.file.open("rb"),
#         as_attachment=True,
#         filename=scan.file.name.split("/")[-1],
#     )








def scan_list(request):
    """
    Liste paginée des scans avec petite recherche sur le code du courrier ou le titre du scan.
    """

    courrier = Courrier.objects.filter(mention="ETUDE ET COMPTE RENDU", is_active=True)
    count_courrier = courrier.count()

    qs = Scan.objects.select_related("courrier").order_by("-created_at")

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(courrier__code__icontains=q) | Q(name__icontains=q))

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    scans = paginator.get_page(page_number)

    return render(request, "scans_list.html", {"scans": scans, "q": q, "count_courrier": count_courrier})


def scan_preview(request, pk: int):
    """
    Renvoie le fichier inline (image/pdf) pour pouvoir l'afficher en <embed>/<img>.
    Fonctionne même si X-Frame-Options serait bloquant en externe.
    """
    scan = get_object_or_404(Scan, pk=pk)
    if not scan.file:
        raise Http404("Fichier introuvable.")

    ctype = mimetypes.guess_type(scan.file.name)[0] or "application/octet-stream"
    resp = FileResponse(scan.file.open("rb"), content_type=ctype)
    # 'inline' pour dire au navigateur d'afficher si possible
    resp["Content-Disposition"] = f'inline; filename="{Path(scan.file.name).name}"'
    return resp


def scan_download(request, pk: int):
    """
    Forcer le téléchargement du fichier.
    """
    scan = get_object_or_404(Scan, pk=pk)
    if not scan.file:
        raise Http404("Fichier introuvable.")
    return FileResponse(
        scan.file.open("rb"),
        as_attachment=True,
        filename=Path(scan.file.name).name,
    )


def scan_download_gemini(request, pk: int):
    """
    Forcer le téléchargement du fichier.
    - Si c'est une IMAGE, on passe par Gemini pour produire un PDF NATIF (texte copiable).
    - Sinon, on renvoie le fichier tel quel.
    """
    scan = get_object_or_404(Scan, pk=pk)
    if not scan.file:
        raise Http404("Fichier introuvable.")

    name_lower = scan.file.name.lower()
    is_image = name_lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff'))

    if is_image:
        try:
            pdf_bytes = image_to_pdf_via_gemini(scan.file.path)  # <-- Gemini + WeasyPrint
            filename = Path(scan.file.name).with_suffix(".pdf").name
            resp = HttpResponse(pdf_bytes, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="{filename}"'
            return resp
        except Exception as e:
            # En cas d'échec Gemini, on retombe sur le fichier brut (pour ne pas bloquer l'utilisateur)
            # Tu peux aussi "messages.error" + redirect si tu préfères
            print("Gemini PDF error:", repr(e))

    # Fallback: fichier tel quel (PDF original, etc.)
    return FileResponse(
        scan.file.open("rb"),
        as_attachment=True,
        filename=Path(scan.file.name).name,
    )