class Pricluchaysia:
    # Дата-класс приложения
    def __init__(self, app):
        self.app = app
        self.app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
        self.app.config['UPLOAD_FOLDER'] = './static/images/'
        self.maps_server_address = 'https://static-maps.yandex.ru/v1?'
        self.maps_api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.geocoder_api_server = "https://geocode-maps.yandex.ru/1.x/"
        self.geocoder_api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        self.host_name = 'localhost:5000'
        self.protocols = ['http']
        self.mod = 'normal'
        self.first = True