import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run

CONFIGS = [{'REPO_URL': 'git@bitbucket.org:algovent/algovent_website.git', 'APP_NAME': 'algovent'},{'REPO_URL' : 'git@bitbucket.org:algovent/petcarehandler.git', 'APP_NAME' : 'petcareHandler'},{'REPO_URL' : 'git@bitbucket.org:algovent/eventico.git', 'APP_NAME' : 'eventico'}]
env.hosts = ['ec2-13-232-13-243.ap-south-1.compute.amazonaws.com']
env.user = 'ubuntu'
env.key_filename = '~/certs/petcareHandler.pem'

def deploy():
    for config in CONFIGS:
        app_name = config['APP_NAME']
        repo_url = config['REPO_URL']
        site_folder = f'/home/{env.user}/sites/{app_name}'
        run(f'mkdir -p {site_folder}')
        with cd(site_folder):
            _get_latest_source(repo_url)
            _update_virtualenv()
            _create_or_update_dotenv()
            _update_database()
    _restart_server()

def _get_latest_source(repo_url):
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {repo_url} .')
    run(f'git pull')

def _update_virtualenv():
    if not exists('prodenv/bin/pip'):
        run(f'python3 -m venv prodenv')
    if not exists('prodenv/bin/wheel'):
        run('./prodenv/bin/pip install wheel')
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

def _update_database():
    run('./prodenv/bin/python manage.py migrate --noinput')

def _restart_server():
    run('sudo service nginx stop')
    run('sudo systemctl stop gunicorn')
    run('sudo systemctl stop gunicorn_al')
    run('sudo systemctl stop gunicorn_ev')
    run('sudo systemctl start gunicorn')
    run('sudo systemctl start gunicorn_al')
    run('sudo systemctl start gunicorn_ev')
    run('sudo service nginx start')

