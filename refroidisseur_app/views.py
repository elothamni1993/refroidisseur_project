from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64, os
import numpy as np
from datetime import datetime
from django.db.models import Q
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import MesureRefroidisseur, VentilateurMesure, ResultatCalcul, MesureImage

ventilateurs_noms = ["F23", "F23A", "F24", "F24A", "F3", "F4", "F5", "F26", "F28", "F27", "F25"]

infos_chambres = [
    {"grate": "Fixed inlet grate", "fan": "F23+F23A", "area": 3.85},
    {"grate": "Fixed inlet grate", "fan": "F24+F24A", "area": 7.88},
    {"grate": "Polytrack", "fan": "F3", "area": 7.27},
    {"grate": "Polytrack", "fan": "F4", "area": 8.79},
    {"grate": "Fuller grate 1", "fan": "F5", "area": 6.76},
    {"grate": "Fuller grate 1", "fan": "F25", "area": 9.0},
    {"grate": "Fuller grate 2", "fan": "F26", "area": 9.0},
    {"grate": "Fuller grate 2", "fan": "F27", "area": 12.0},
    {"grate": "Fuller grate 2", "fan": "F28", "area": 9.0},
]

repartition = {
    1: [0, 1], 2: [2, 3], 3: [4], 4: [5], 5: [6], 6: [10], 7: [7], 8: [9], 9: [8],
}

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def export_excel(request):
    file_path = os.path.join('media', 'data.xlsx')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="rapport_refroidisseur.xlsx"'
            return response
    return HttpResponse("Aucun fichier à exporter.", status=404)

def export_pdf(request, pk):
    mesure = get_object_or_404(MesureRefroidisseur, pk=pk)

    # Générer tous les graphes
    noms = [v.nom for v in mesure.ventilateurs.all()]
    debits = [v.debit for v in mesure.ventilateurs.all()]
    results = mesure.resultats.all()

    graphs = []

    # Graphique 1 : Débit par ventilateur
    fig, ax = plt.subplots()
    ax.bar(noms, debits, color="#007acc")
    ax.set_title("Débit par ventilateur (Nm³/h)")
    graphs.append(fig_to_base64(fig))

    # Graphiques supplémentaires (Sp. Flow, Sp. Air Load...) si disponibles
    try:
        flow_specifiques = [r.flow_specifique for r in results if r.chambre != '-']
        air_loads = [r.sp_air_load for r in results if r.chambre != '-']
        air_kg = [r.sp_air_load_kg for r in results if r.chambre != '-']

        fig, ax = plt.subplots()
        ax.plot(range(1, 10), flow_specifiques, marker='o', color='#28a745')
        ax.set_title("Sp. Flow (kg/kg clinker)")
        graphs.append(fig_to_base64(fig))

        fig, ax = plt.subplots()
        ax.plot(range(1, 10), air_loads, marker='s', color='#dc3545')
        ax.set_title("Sp. Air Load (Nm³/s/m²)")
        graphs.append(fig_to_base64(fig))

        fig, ax = plt.subplots()
        ax.plot(range(1, 10), air_kg, marker='d', color='#ffc107')
        ax.set_title("Sp. Air Load (kg/min/m²)")
        graphs.append(fig_to_base64(fig))
    except Exception as e:
        print("Erreur lors du rendu des graphes:", e)

    template = get_template('mesure_pdf.html')
    html = template.render({'mesure': mesure, 'graphs': graphs})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=mesure_{pk}.pdf'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur de génération PDF', status=500)
    return response
    mesure = get_object_or_404(MesureRefroidisseur, pk=pk)
    template = get_template('mesure_pdf.html')
    html = template.render({'mesure': mesure})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=mesure_{pk}.pdf'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur de génération PDF', status=500)
    return response

def enregistrer_mesure_bd(date_heure, debit_farine, commentaires, ventilateurs, results, images):
    mesure = MesureRefroidisseur.objects.create(date_heure=date_heure, debit_farine=debit_farine, commentaires=commentaires)
    for nom, val in zip(ventilateurs_noms, ventilateurs):
        VentilateurMesure.objects.create(mesure=mesure, nom=nom, debit=val)
    for r in results:
        ResultatCalcul.objects.create(mesure=mesure, **r)
    for img in images:
        MesureImage.objects.create(mesure=mesure, image=img)

def mesures_list(request):
    query = request.GET.get('q', '')
    mesures = MesureRefroidisseur.objects.all()
    if query:
        mesures = mesures.filter(Q(id__icontains=query) | Q(date_heure__icontains=query) | Q(commentaires__icontains=query))
    mesures = mesures.order_by('-date_heure')
    return render(request, 'mesures_list.html', {'mesures': mesures, 'query': query})

def mesure_detail(request, pk):
    mesure = get_object_or_404(MesureRefroidisseur, pk=pk)

    noms = [v.nom for v in mesure.ventilateurs.all()]
    debits = [v.debit for v in mesure.ventilateurs.all()]

    # Préparation des données résultats
    resultats = mesure.resultats.exclude(chambre='-').order_by('chambre')
    flow_specifiques = [r.flow_specifique for r in resultats]
    air_loads = [r.sp_air_load for r in resultats]
    air_kg = [r.sp_air_load_kg for r in resultats]

    graphs = []

    # Graphique 1 : Débit par ventilateur
    fig, ax = plt.subplots()
    ax.bar(noms, debits, color="#007acc")
    ax.set_title("Débit par ventilateur (Nm³/h)")
    graphs.append(fig_to_base64(fig))

    # Graphique 2 : Sp. Flow
    fig, ax = plt.subplots()
    ax.plot(range(1, 10), flow_specifiques, marker='o', color='#28a745')
    ax.set_title("Sp. Flow (kg/kg clinker)")
    ax.set_xlabel("Chambre")
    graphs.append(fig_to_base64(fig))

    # Graphique 3 : Sp. Air Load (Nm³/s/m²)
    fig, ax = plt.subplots()
    ax.plot(range(1, 10), air_loads, marker='s', color='#dc3545')
    ax.set_title("Sp. Air Load (Nm³/s/m²)")
    ax.set_xlabel("Chambre")
    graphs.append(fig_to_base64(fig))

    # Graphique 4 : Sp. Air Load (kg/min/m²)
    fig, ax = plt.subplots()
    ax.plot(range(1, 10), air_kg, marker='d', color='#ffc107')
    ax.set_title("Sp. Air Load (kg/min/m²)")
    ax.set_xlabel("Chambre")
    graphs.append(fig_to_base64(fig))

    # Graphique 5 : Heatmap
    heatmap_data = np.array(air_kg).reshape(3, 3)
    fig, ax = plt.subplots()
    c = ax.imshow(heatmap_data, cmap='YlOrRd')
    plt.colorbar(c, ax=ax)
    ax.set_title("Heatmap Sp. Air Load (kg/min/m²)")
    graphs.append(fig_to_base64(fig))

    return render(request, 'mesure_detail.html', {
        'mesure': mesure,
        'graphs': graphs
    })


def mesure_delete(request, pk):
    mesure = get_object_or_404(MesureRefroidisseur, pk=pk)
    if request.method == "POST":
        mesure.delete()
        return redirect('mesures_list')
    return render(request, 'mesure_confirm_delete.html', {'mesure': mesure})

def index(request):
    context = {'ventilateurs_noms': ventilateurs_noms, 'results': [], 'graph_list': [], 'message': '', 'date_heure': datetime.now().strftime('%Y-%m-%dT%H:%M')}
    if request.method == 'POST':
        try:
            ventilateurs = [float(request.POST.get(f'ventilo{i}', 0)) for i in range(len(ventilateurs_noms))]
            debit_farine = float(request.POST.get('debit_farine', 1))
            date_heure = request.POST.get('date_heure', context['date_heure'])
            commentaires = request.POST.get('commentaires', '')
            images = request.FILES.getlist('images')

            results = []
            flow_specifiques = []
            air_loads = []
            air_kg = []
            debit_totaux = []

            for idx, chambre in enumerate(infos_chambres):
                indices = repartition[idx + 1]
                flow = sum(ventilateurs[j] for j in indices)
                area = chambre["area"]
                sp_flow = flow / debit_farine
                sp_air_load = flow / (area * 3600)
                sp_air_load_kg = (flow * 1.2) / (60 * area)

                results.append({
                    'grate': chambre["grate"],
                    'chambre': idx + 1,
                    'fan': chambre["fan"],
                    'flow': round(flow, 2),
                    'flow_specifique': round(sp_flow, 3),
                    'area': area,
                    'sp_air_load': round(sp_air_load, 3),
                    'sp_air_load_kg': round(sp_air_load_kg, 2),
                })

                debit_totaux.append(flow)
                flow_specifiques.append(sp_flow)
                air_loads.append(sp_air_load)
                air_kg.append(sp_air_load_kg)

            results.append({
                'grate': 'Total',
                'chambre': '-',
                'fan': '-',
                'flow': round(sum(debit_totaux), 2),
                'flow_specifique': round(sum(flow_specifiques), 3),
                'area': round(sum(ch["area"] for ch in infos_chambres), 2),
                'sp_air_load': round(np.mean(air_loads), 3),
                'sp_air_load_kg': round(np.mean(air_kg), 2),
            })

            enregistrer_mesure_bd(date_heure, debit_farine, commentaires, ventilateurs, results, images)

            graphs = []

            fig, ax = plt.subplots(figsize=(7, 4))
            ax.bar(ventilateurs_noms, ventilateurs, color='#007acc')
            ax.set_title("Débit par Ventilateur (Nm³/h)")
            graphs.append(fig_to_base64(fig))

            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(range(1, 10), flow_specifiques, marker='o', color='#28a745')
            ax.set_title("Sp. Flow (kg/kg clinker)")
            ax.set_xlabel("Chambre")
            graphs.append(fig_to_base64(fig))

            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(range(1, 10), air_loads, marker='s', color='#dc3545')
            ax.set_title("Sp. Air Load (Nm³/s/m²)")
            ax.set_xlabel("Chambre")
            graphs.append(fig_to_base64(fig))

            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(range(1, 10), air_kg, marker='d', color='#ffc107')
            ax.set_title("Sp. Air Load (kg/min/m²)")
            ax.set_xlabel("Chambre")
            graphs.append(fig_to_base64(fig))

            heatmap_data = np.array(air_kg).reshape(3, 3)
            fig, ax = plt.subplots()
            c = ax.imshow(heatmap_data, cmap='YlOrRd')
            plt.colorbar(c, ax=ax)
            ax.set_title("Heatmap Sp. Air Load (kg/min/m²)")
            graphs.append(fig_to_base64(fig))

            context.update({'results': results, 'graph_list': graphs, 'message': "✅ Données enregistrées avec succès !", 'date_heure': date_heure})
        except Exception as e:
            context['message'] = f"❌ Erreur de traitement: {e}"
    return render(request, 'index.html', context)
