from django.shortcuts import render


def commands_page(request):
    return render(request, "entities/entities.html", {'base_page': 'new_base_page.html'})
