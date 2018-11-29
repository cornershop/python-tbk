# Ejemplo de Integración con Django

    - Transacción Normal Funcionando
    - OneClick No implementado

## Requisitos Minimos

    - Python 3.6 o Superior.
    - sudo apt-get install python3-pip
    - sudo pip3 install virtualenv

# Instrucciones de Ejemplo

    - Create virtual enviroment
        - virtualenv -p python3 name
        - cd name
        - source bin/activate
    - $ cp ../django_example/ . 
    - $ cd django_example/
    - $ pip install -r requirements.txt
    - $ python manage.py migrate
    - $ python manage.py runserver 0:8080
    - http://localhost:8080/tbk/



## Integration commerces

+---------------+---------------------------+
| Commerce code | Integration               |
+===============+===========================+
| 597020000545  | transacción completa      |
+---------------+---------------------------+
| 597020000546  | captura diferida          |
+---------------+---------------------------+
| 597020000593  | oneclick captura diferida |
+---------------+---------------------------+
| 597020000542  | transacción normal mall   |
+---------------+---------------------------+
| 597020000541  | transacción normal        |
+---------------+---------------------------+
| 597020000547  | oneclick                  |
+---------------+---------------------------+
