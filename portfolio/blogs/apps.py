from django.apps import AppConfig

class BlogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfolio.blogs'

    def ready(self):
        print("📣 BlogsConfig.ready() loaded")
        import portfolio.blogs.signals 
 