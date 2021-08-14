from customize.models import Customize

def footer(request):
    footer = Customize.objects.get(title='Footer')
    return {'footer': footer}
