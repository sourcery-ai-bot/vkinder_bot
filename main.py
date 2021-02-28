from keys import GROUP_TOKEN, PERSONAL_TOKEN, GROUP_ID, APP_ID, DB_NAME, DB_LOGIN, DB_PASSWORD, DB_DRIVER, DB_HOST, \
    DB_PORT
from сlasses.vkinder_bot import VKinderBot

"""
Перед началом использования переименуйте файл "default_keys.py" в "keys.py" и укажите в нем свои токены и данные
доступа к БД. 

Перед первым запуском установите {"rebuild_tables": true} в файле "options.cfg" (регистр букв true имеет значение). 
Когда этот файл установлен, все таблицы в БД будут пересозданы. Все данные в БД будут утеряны. 
После первого запуска этот флаг будет установлен в false автоматически. 
"""
if __name__ == '__main__':
    server = VKinderBot(group_token=GROUP_TOKEN,
                        person_token=PERSONAL_TOKEN,
                        group_id=GROUP_ID,
                        app_id=APP_ID,
                        db_name=DB_NAME,
                        db_login=DB_LOGIN,
                        db_password=DB_PASSWORD,
                        db_driver=DB_DRIVER,
                        db_host=DB_HOST,
                        db_port=DB_PORT,
                        debug_mode=True)
    server.start()
