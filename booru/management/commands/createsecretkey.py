from django.core.management.base import BaseCommand, CommandError
import os

class Command(BaseCommand):
    help = 'Creates a new secret key'

    def handle(self, *args, **options):
        # Get the length argument or default to 40
        length = int(options['length']) if options['length'] else 40

        # Make sure that the length is at least 8
        if length < 8:
            raise CommandError('Length must be at least 8')

        # Generate a new secret key
        from django.utils.crypto import get_random_string

        # Generate the key
        key = get_random_string(length)

        # Get the path to the file or default to secret.txt
        path = options['path'] if options['path'] else 'secret.txt'

        # Check if the path already exists
        # Check if the --force flag was passed
        if os.path.exists(path) and not options['force']:
            # Ask the user if they want to overwrite the file
            answer = input('File already exists. Overwrite? [y/N] ')

            # If the user doesn't want to overwrite, exit
            if answer.lower() != 'y':
                return

        # Write the key to the file
        with open(path, 'w') as f:
            f.write(key)

        # Print the key
        self.stdout.write(self.style.SUCCESS('Successfully created secret key: %s' % key))

    def add_arguments(self, parser):
        parser.add_argument('--length', type=int, default=40, help='Length of the key to generate')
        parser.add_argument('--path', type=str, default='secret.txt', help='Path to the file to write the key to')
        parser.add_argument('--force', action='store_true', help='Overwrite the file if it already exists')
        return parser