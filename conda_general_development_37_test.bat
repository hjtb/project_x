rem This automates the creation of general_development_37 with as many of the packages coming from conda as possible 
rem Depending on the installation of your conda, it may need to be run with administrator privileges
rem To do that, find the anaconda prompt in the start menu and right click, then select "run as administrator"
rem Then navigate to the folder where this file is stored and execute it by typing its name

rem I had a problem recereating the environment on threadripper 
rem complained abourt vs2015_runtime
rem I did:
rem    conda clean --all
rem    conda install -c anaconda vs2015_runtime
rem That seemed to fix it 

rem You can remove this virtual environment by typing the following command
rem To move to a different envirnment
rem conda remove --name general_development_37 --all

rem You can check your environments by typing
rem conda info --envs

rem First change to the disk and directory where this bat file is
cd /D "%~dp0"

rem The following packages are all in the default channel 
call conda create --name general_development_37 python=3.7 ^
flask=1.1.2 ^
SQLAlchemy=1.3.17 ^
flask-SQLAlchemy=2.4.1 ^
alembic=1.4.2 ^
Flask-WTF=0.14.3 ^
WTForms=2.2.1 ^
requests=2.23.0 ^
bokeh=2.2.3 ^
pyserial=3.5 ^


rem Occasionally, this process has failed with a file contention error 
rem To try and fix that, I am putting a sleep statement in between the steps
call timeout /t 10 /nobreak

rem The following packages are only in the conda-forge channel
call conda install  --name general_development_37 -c conda-forge ^
Flask-Migrate=2.4.0 ^
python-dotenv=0.13.0 ^
opencv=4.5.0 ^
scapy ^
libpcap

rem Occasionally, this process has failed with a file contention error 
rem To try and fix that, I am putting a sleep statement in between the steps
call timeout /t 10 /nobreak

rem Finally, we need to install some packages with pip
rem So first activate the environment and then pip install them all in 
call activate general_development_37
pip install mysql-connector-python==8.0.19
pip install black==20.8b1
pip install Flask-Session==0.3.2
pip install waitress==1.4.4
