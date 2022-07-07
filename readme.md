## Windows Development Environment Setup

#### Requirements

- Windows 10 Pro
- Hyper-V feature enabled

#### Software Installation

Before we start, install these software. All 64Bit versions:

- [Python 3.6.8](https://www.python.org/downloads/windows/)
    + Default installation
- [Visual Studio 2017 - C++ Compiler](https://docs.microsoft.com/pt-br/cpp/build/vscpp-step-0-installation?view=vs-2017)
    + Community version. Install only C++ Compilers, around 3Gb.
- [PyCharm (Python IDE)](https://www.jetbrains.com/pycharm/download/#section=windows)
    + Default installation
- [Docker - Container System](https://docs.docker.com/docker-for-windows/install/)
    + Default installation
- [GIT - Version Control](https://git-scm.com/download/win):
    + Commit files as Linux and checkout as Is option. Put GIT on PATH.
- [OSGeos4W - GIS libraries](https://trac.osgeo.org/osgeo4w/)
    + Default installation

#### GIT Clone
1. Clone the project
    ```
    git clone <repository_url> <local_project_folder>
    ```

#### PyCharm Setup
Setup the IDE to work on the project
    
1. Open the Project Folder in **PyCharm**

1. Go to _"Settings"_ on _"File"_ menu and got to `Project > Project Interpreter`

1. Click on the gear on the top right, and choose `Add` to create a new Virtual Environment
 
1. Go to _"Settings"_ on _"File"_ menu and got to `Build, Execution, Deployment > Console > Python Console`

1. Paste the following code on `Starting script`:
    ```
    import sys, os, django
    print('Python %s on %s' % (sys.version, sys.platform))
    sys.path.extend([WORKING_DIR_AND_PYTHON_PATHS])
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")
    django.setup()
    ```
    
1. Mark the `code` folder as `Sources Root`
 
#### Project Setup
1.  Copy some template files to their locations:
    - Copy `file-templates/code/proj/settings_dev.py` to `code/proj/`
    - Copy `file-templates/docker-dev.yml` to the project root
    
1. At the Terminal, install the dependencies libraries
    ```
    cd code
    pip install -r requirements_dev.txt
    ```
    
1. Update the file `code/proj/settings_dev.py` setting your local path for `GDAL_LIBRARY_PATH` and `OSGEO4W`:
    ```
    GDAL_LIBRARY_PATH = r'<python_virtualenv_path>/Lib/site-packages/osgeo/gdal202.dll'
    OSGEO4W = r'<python_virtualenv_path>/Lib/site-packages/osgeo/'
    ```
    
1. Build the Docker Images
    Ensure Docker is running and you have free access to the internet before running this step
    ```
    docker-compose -f docker_dev.yml up -d
    ```
    
1. Create an empty file at `code/` called `__dev__.py` to declare the Development running environment
    
1. Run Django Migrations
    ```
    python manage.py migrate
    ```
    
1. Create the project super-user
    ```
    cd code
    python manage.py createsuperuser
    ```
    
#### Running the Project
1. To run the Project for development, start the Django Development Server
    ```
    cd code
    python manage.py runserver
    ```

2. Test on any browser (Chrome preferred) [http://localhost:8000](http://localhost:8000)

3. During development, the Django Development Server reacts to code changes and restart automatically.

## TO DO: Improve, Translate

### Implantação
1. Clone este repositório e acesse ele.
    ```
    git clone <url_do_repositorio>
    cd <repositorio>
    ```
   
2. Instale docker e docker-compose no servidor
    ```
    chmod a+x install-docker.sh
    sudo ./install-docker.sh

3. Inicie o stack docker
    ```
    docker-compose up -d
    ```

4. Acompanhe pelos logs para verificar se tudo correu bem.
    ```
    docker-compose logs -ft
    ```

5. Faça a instalação do certificado, de acordo com o domínio desejado.
    ```
    certbot certonly --webroot -w var/letsencrypt/ -d <url_do_dominio>
    ```

6. Após a geração do certificado, copie o conteúdo do arquivo `files-templates/etc/nginx/default.conf.https` para o arquivo `/etc/nginx/default.conf`, altere os caminhos e nomes do domínio e suba para o repositório. No servidor dê um pull novamente e reinicie os containers, acompanhando pelos logs se for necessário.
    ```
    docker-compose down
    git pull
    docker-compose up -d
    docker-compose logs -ft
    ```

### Deploy
1. Pare os containers
    ```
    cd cidc-sys
    docker-compose down
    ```

1. Faça o pull do repositório
    ```     
    git pull
    ```

3. Inicie o stack docker
    ```
    docker-compose up -d
    ```
    
    Se houver alteração no requirements.txt, faça o build das imagens novamente:
    ```
    docker-compose up -d --build
    ```

### Utilidades
- Verificar logs: `docker-compose logs -ft`
- Verificar log de um container específico: `docker-compose logs -ft django-server`
- Executar terminal de um container específico: `docker exec -it django-server sh`

### Subir o docker 
- docker-compose -f docker_dev.yml up
