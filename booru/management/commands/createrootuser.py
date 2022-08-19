from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a new secret key'

    def handle(self, *args, **options):
        User = get_user_model()

        # Check that the 'root' user exists
        if User.objects.filter(username='root').exists():
            raise CommandError('The "root" user already exists')
        
        # Create the 'root' user
        User.objects.create_superuser('root', 'root@localhost', 'root')

        # Say that we're done
        self.stdout.write(self.style.SUCCESS('Successfully created the "root" user'))