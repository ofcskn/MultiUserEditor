import os

# Mesaj türleri
MSG_LOGIN = "LOGIN"         # Kullanıcı sisteme giriş yaptı ya da kaydolu 
MSG_FILE_UPDATE = "FILE_UPDATE"           # Dosya güncellemesi
MSG_FILE_LIST = "FILES"     # Paylaşılan dosyalar listesi
MSG_CREATE_FILE = "CREATE_FILE" # Yeni dosya oluşturma isteği
MSG_FILE_LOAD = "LOAD"   # Dosya yükleme 
MSG_FILE_LOAD_VIEWER = "LOAD_VIEWER" # Dosyayı sadece görüntüle 
MSG_JOIN_FILE="JOIN_FILE"   # Kullanıcı dosyaya katıldı
MSG_ERROR= "ERROR" # Herhangi bir hata
MSG_PERMISSION_ERROR = "PERMISSON_ERROR" # İzin hatası
MSG_LOGIN_ERROR = "LOGIN_ERROR" # Giriş yaparken alınan hata
MSG_SUCCESS = "SUCCESS" # Başarılı bir aksiyon

# Paket ayırıcı (protokol için)
DELIMITER = "|"

# Kullanıcı adı maksimum uzunluğu
MAX_USERNAME_LEN = 16

HOST = '127.0.0.1'
PORT = 65433

SAVE_INTERVAL = 5  # seconds

DATA_FOLDER = 'data'
SAVE_FOLDER = 'www/files'

USERS_JSON = os.path.join(DATA_FOLDER, 'users.json')
FILES_JSON = os.path.join(DATA_FOLDER, 'files.json')
