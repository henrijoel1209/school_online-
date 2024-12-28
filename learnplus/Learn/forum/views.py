from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Sujet, Reponse
from .forms import SujetForm, ReponseForm
from school.models import Cours

@login_required
def liste_sujets(request, cours_id=None):
    """Liste tous les sujets du forum, filtrés par cours si spécifié"""
    if cours_id:
        cours = get_object_or_404(Cours, id=cours_id)
        sujets = Sujet.objects.filter(cours=cours, status=True).order_by('-date_add')
        context = {'sujets': sujets, 'cours': cours}
    else:
        sujets = Sujet.objects.filter(status=True).order_by('-date_add')
        context = {'sujets': sujets}
    
    paginator = Paginator(sujets, 10)  # 10 sujets par page
    page = request.GET.get('page')
    sujets_page = paginator.get_page(page)
    context['sujets_page'] = sujets_page
    
    return render(request, 'forum/liste_sujets.html', context)

@login_required
def nouveau_sujet(request, cours_id=None):
    """Crée un nouveau sujet"""
    if cours_id:
        cours = get_object_or_404(Cours, id=cours_id)
    else:
        cours = None

    if request.method == 'POST':
        form = SujetForm(request.POST)
        if form.is_valid():
            sujet = form.save(commit=False)
            sujet.user = request.user
            if cours:
                sujet.cours = cours
            sujet.save()
            messages.success(request, "Votre sujet a été créé avec succès.")
            return redirect('forum:detail_sujet', slug=sujet.slug)
    else:
        initial = {}
        if cours:
            initial['cours'] = cours
        form = SujetForm(initial=initial)

    context = {
        'form': form,
        'cours': cours,
    }
    return render(request, 'forum/nouveau_sujet.html', context)

@login_required
def detail_sujet(request, slug):
    """Affiche les détails d'un sujet et ses réponses"""
    sujet = get_object_or_404(Sujet, slug=slug, status=True)
    reponses = sujet.sujet_reponse.filter(status=True).order_by('date_add')
    
    if request.method == 'POST':
        form = ReponseForm(request.POST)
        if form.is_valid():
            reponse = form.save(commit=False)
            reponse.user = request.user
            reponse.sujet = sujet
            reponse.save()
            messages.success(request, "Votre réponse a été ajoutée avec succès.")
            return redirect('forum:detail_sujet', slug=slug)
    else:
        form = ReponseForm()
    
    context = {
        'sujet': sujet,
        'reponses': reponses,
        'form': form,
    }
    return render(request, 'forum/detail_sujet.html', context)

@login_required
def modifier_sujet(request, slug):
    """Modifie un sujet existant"""
    sujet = get_object_or_404(Sujet, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = SujetForm(request.POST, instance=sujet)
        if form.is_valid():
            form.save()
            messages.success(request, "Le sujet a été modifié avec succès.")
            return redirect('forum:detail_sujet', slug=sujet.slug)
    else:
        form = SujetForm(instance=sujet)
    
    context = {
        'form': form,
        'sujet': sujet,
    }
    return render(request, 'forum/modifier_sujet.html', context)

@login_required
def supprimer_sujet(request, slug):
    """Supprime un sujet (soft delete)"""
    sujet = get_object_or_404(Sujet, slug=slug, user=request.user)
    sujet.status = False
    sujet.save()
    messages.success(request, "Le sujet a été supprimé avec succès.")
    return redirect('forum:liste_sujets')

@login_required
def modifier_reponse(request, id):
    """Modifie une réponse existante"""
    reponse = get_object_or_404(Reponse, id=id, user=request.user)
    
    if request.method == 'POST':
        form = ReponseForm(request.POST, instance=reponse)
        if form.is_valid():
            form.save()
            messages.success(request, "La réponse a été modifiée avec succès.")
            return redirect('forum:detail_sujet', slug=reponse.sujet.slug)
    else:
        form = ReponseForm(instance=reponse)
    
    context = {
        'form': form,
        'reponse': reponse,
    }
    return render(request, 'forum/modifier_reponse.html', context)

@login_required
def supprimer_reponse(request, id):
    """Supprime une réponse (soft delete)"""
    reponse = get_object_or_404(Reponse, id=id, user=request.user)
    reponse.status = False
    reponse.save()
    messages.success(request, "La réponse a été supprimée avec succès.")
    return redirect('forum:detail_sujet', slug=reponse.sujet.slug)
