import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

REPO_URL = 'https://naveen_bollimpalli@bitbucket.org/algovent/petcarehandler.git'
SERVER_CONFIG_URL = ''
env.hosts = ['ec2-13-232-13-243.ap-south-1.compute.amazonaws.com']
env.user = 'ubuntu'
env.key_filename = '~/certs/petcareHandler.pem'

def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        #_update_static_files()
        _update_database()

def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    run(f'git pull')

def _update_virtualenv():
    if not exists('prodenv/bin/pip'):
        run(f'python3 -m venv prodenv')
    run('./prodenv/bin/pip install -r requirements.txt')

def _create_or_update_dotenv():
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')

def _update_static_files():
    run('./prodenv/bin/python manage.py collectstatic --noinput')

def _update_database():
    run('./prodenv/bin/python manage.py migrate --noinput')