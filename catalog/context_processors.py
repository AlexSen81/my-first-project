from orders.models import MainSiteSettings

def site_settings_context ( request ) :
    settings = MainSiteSettings.objects.first ()
    if not settings :
        return { 'is_maintenance' : True }
    return { 'is_maintenance' : settings.is_maintenance_mode }
