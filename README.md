# pei-admin-dashboard
PEI - Módulo Admin Dashboard

### Máquina: Testado em Ubuntu 20.04

setup de um virtual environment
https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/development_environment
```
apt install python3-pip
pip3 install virtualenvwrapper
```

```
nano .bashrc
```
```
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV_ARGS=' -p /usr/bin/python3 '
export PROJECT_HOME=$HOME/Devel
export VIRTUALENVWRAPPER_VIRTUALENV=~/.local/bin/virtualenv
source ~/.local/bin/virtualenvwrapper.sh
```

reload da bash
```
source .bashrc
```
criar venv
```
mkvirtualenv myenv
```
listar venvs
```
workon
```
usar myenv
```
workon myenv
```
sair do env (não fazer ainda)
```
deactivate
```

instalar django 3.1 e dependências
```
pip3 install django~=3.1
pip3 install opencv-python~=4.4.0.46
pip3 install cmake
pip3 install dlib~=19.21.1
pip3 install onnxruntime~=1.5.2
pip3 install django-rest-framework
pip3 install jsonfield
pip3 install qrcode
pip3 install pypdf2
pip3 install pafy
pip3 install youtube-dl
pip3 install humanfriendly
```

instalar apache e mod-wsgi (para compatibilidade com django)
https://www.youtube.com/watch?v=q__Nn0RRBvE
```
apt install apache2
apt install libapache2-mod-wsgi-py3
```

```
nano /etc/apache2/apache2.conf
```
```
WSGIPythonHome /home/ubuntu/.virtualenvs/myenv/
WSGIPythonPath /var/www/mainpei-deploy/peidashboard

WSGIPassAuthorization On

WSGIScriptAlias / /var/www/mainpei-deploy/peidashboard/peidashboard/wsgi.py
<Directory /var/www/mainpei-deploy/peidashboard/peidashboard>
        <Files wsgi.py>
                Require all granted
        </Files>
</Directory>

Alias /static/ /var/www/mainpei-deploy/peidashboard/peidashboard/static/
<Directory /var/www/mainpei-deploy/peidashboard/peidashboard/static/>
        Require all granted
</Directory>

XSendFile on
XSendFilePath /var/www/mainpei-deploy/peidashboard/media_cdn/
<Directory /var/www/mainpei-deploy/peidashboard/media_cdn/>
        Order Deny,Allow
        Allow from all
</Directory>
```

Este projeto é um “proof of concept”. Para melhores práticas, nomeadamente na configuração do Apache, recorrer à documentação oficial

módulo xsendfile
```
wget https://tn123.org/mod_xsendfile/mod_xsendfile-0.12.tar.gz
tar xvf mod_xsendfile-0.12.tar.gz
cd mod_xsendfile-0.12/
apxs -cia mod_xsendfile.c
sudo apachectl restart
```

notar que ‘mainpei-deploy’ é o repositório da aplicação de dashboard.
poderá ser 'pei-admin-dashboard'
```
cd /var/www
git clone https://...
```


efetuar após clone do repositório
```
workon myenv
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
```

Comandos Apache
```
apt install apache2-dev
apachectl restart
apachectl stop
apachectl configtest
tail -f /var/log/apache2/error.log
tail -f /var/log/apache2/access.log
```
