# Türkçe Protokol Dokümanı

**Sunucu - İstemci Haberleşme Protokolü**

---

## 1. Protokolün Genel Tanımı

Bu protokol, istemci (client) ve sunucu (server) arasında dosya paylaşımı, düzenleme ve kullanıcı yönetimi için tasarlanmıştır.
Protokolün amacı, iki tarafın birbirinin kodlamasını bilmeden doğru mesaj alışverişi yapmasını sağlamaktır.
Mesajlar, önceden tanımlanmış sabit mesaj tipleri ve ilgili içerikleriyle iletilir.
Her mesajın, belirli bir anlamı ve karşı tarafın yapması gereken işlem tanımlanmıştır.

---

## 2. Mesaj Türleri ve Anlamları

| Mesaj Tipi                          | Gönderen | Açıklama                                                           |
| ----------------------------------- | -------- | ------------------------------------------------------------------ |
| `MSG_CLIENT_LOGIN`                  | İstemci  | Kullanıcının sisteme giriş yapma isteği                            |
| `MSG_CLIENT_UPDATE_FILE`            | İstemci  | İstemcinin dosya içeriğinde yaptığı güncellemeyi sunucuya iletmesi |
| `MSG_CLIENT_LIST_FILES`             | İstemci  | Paylaşılan dosyaların listesini talep etme                         |
| `MSG_CLIENT_CREATE_FILE`            | İstemci  | Yeni dosya oluşturma talebi                                        |
| `MSG_CLIENT_JOIN_FILE`              | İstemci  | İstemcinin bir dosyaya düzenleme için katılması talebi             |
| `MSG_SERVER_LOAD_FILE`              | Sunucu   | Sunucudan istemciye dosya içeriğinin gönderilmesi                  |
| `MSG_SERVER_CREATE_FILE_FAILURE`    | Sunucu   | Dosya oluşturma sırasında hata bildirimi                           |
| `MSG_SERVER_LOAD_FILE_VIEWER`       | Sunucu   | Dosyanın salt okunur (viewer) modunda istemciye gönderilmesi       |
| `MSG_SERVER_PERMISSION_FAILURE`     | Sunucu   | Yetki hatası bildirimi                                             |
| `MSG_SERVER_LOGIN_FAILURE`          | Sunucu   | Giriş yapma başarısızlık bildirimi                                 |
| `MSG_SERVER_FAILURE`                | Sunucu   | Genel hata bildirimi                                               |
| `MSG_SERVER_SUCCESS`                | Sunucu   | Genel başarılı işlem bildirimi                                     |
| `MSG_SERVER_UPDATE_FILE_SUCCESS`    | Sunucu   | Dosya güncellemesinin başarılı olduğunu bildirme                   |
| `MSG_SERVER_UPDATE_FILE_FAILURE`    | Sunucu   | Dosya güncellemesi sırasında hata bildirimi                        |
| `MSG_SERVER_USER_ACTIVE_SESSION`    | Sunucu   | Aynı kullanıcı adına zaten aktif bir oturum olduğunu bildirme      |
| `MSG_SERVER_REDIRECT_TO_FILES_VIEW` | Sunucu   | İstemcinin dosya listesi ekranına yönlendirilmesi talebi           |
| `MSG_SERVER_UPDATE_LISTED_FILES`    | Sunucu   | Paylaşılan dosyalar listesinin güncellenmesi talebi                |

---

## 3. Protokol İşleyiş Süreci

### 3.1. Kullanıcı Girişi

| Durum                             | İstemci Mesajı     | Sunucu Mesajı                                                       | Açıklama                                              |
| --------------------------------- | ------------------ | ------------------------------------------------------------------- | ----------------------------------------------------- |
| Kullanıcı sisteme giriş yapar     | `MSG_CLIENT_LOGIN` | `MSG_SERVER_REDIRECT_TO_FILES_VIEW` veya `MSG_SERVER_LOGIN_FAILURE` | Kullanıcı adı ve şifre gönderilir, doğrulama yapılır. |
| Kullanıcı mevcut değilse          | `MSG_CLIENT_LOGIN` | `MSG_SERVER_CREATE_USER`                                            | Kullanıcı oluşturulur ve giriş sağlanır.              |
| Şifre hatalı ise                  | `MSG_CLIENT_LOGIN` | `MSG_SERVER_LOGIN_FAILURE`                                          | Giriş reddedilir, hata mesajı gönderilir.             |
| Aktif bir kullanıcı oturumu varsa | `MSG_CLIENT_LOGIN` | `MSG_SERVER_USER_ACTIVE_SESSION`                                    | Giriş reddedilir, hata mesajı gönderilir.             |

---

### 3.2. Dosya Listeleme ve Yönetim

| Durum                 | İstemci Mesajı           | Sunucu Mesajı                                                                                | Açıklama                                                   |
| --------------------- | ------------------------ | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Dosya listesi istenir | `MSG_CLIENT_LIST_FILES`  | `MSG_SERVER_UPDATE_LISTED_FILES`                                                             | Sunucu, kullanıcı yetkisine göre dosya listesini gönderir. |
| Yeni dosya oluşturma  | `MSG_CLIENT_CREATE_FILE` | `MSG_SERVER_SUCCESS`, `MSG_SERVER_UPDATE_LISTED_FILES` veya `MSG_SERVER_CREATE_FILE_FAILURE` | Dosya oluşturulur. Yeni liste veya hata döner.             |

---

### 3.3. Dosya Düzenleme

| Durum                           | İstemci Mesajı           | Sunucu Mesajı                                                          | Açıklama                                                          |
| ------------------------------- | ------------------------ | ---------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Dosya açılır ve içerik yüklenir | `MSG_CLIENT_JOIN_FILE`   | `MSG_SERVER_LOAD_FILE` veya `MSG_SERVER_LOAD_FILE_VIEWER`              | Dosya içeriği, düzenlenebilir ya da salt okunur şekilde iletilir. |
| Dosya güncelleme yapılır        | `MSG_CLIENT_UPDATE_FILE` | `MSG_SERVER_UPDATE_FILE_SUCCESS` veya `MSG_SERVER_UPDATE_FILE_FAILURE` | Güncelleme başarılı veya hata bilgisi döner.                      |

---

## 4. Mesajların İçeriği ve Yapısı

Her mesaj, JSON formatında gönderilir. Mesajlar aşağıdaki yapıyı içerir:

```json
{
  "cmd": "<MESAJ_TIPI>",
  "payload": {
    // Mesaj tipine göre değişen içerik
  }
}
```

### Örnek:

- `MSG_CLIENT_LOGIN` mesajı için:

```json
{
  "cmd": "MSG_CLIENT_LOGIN",
  "payload": {
    "username": "user1",
    "password": "hashed_password"
  }
}
```

- `MSG_SERVER_LOAD_FILE` mesajı için:

```json
{
  "cmd": "MSG_SERVER_LOAD_FILE",
  "payload": {
    "filename": "document.txt",
    "content": "Dosya içeriği buraya gelecek"
  }
}
```

---

## 5. Sonlu Durum Makinası (FSM) / Durum Diyagramı

1. **Başlangıç Durumu:** Kullanıcı giriş ekranı açık.
2. **Login Başarılı:** Dosya listesi ekranına geçilir.
3. **Dosya Seçimi:** Dosya içeriği yüklenir ve EditorView açılır.
4. **Dosya Düzenleme:** Dosya üzerinde gerçek zamanlı değişiklikler gönderilir ve alınır.
5. **Dosya Oluşturma:** Kullanıcı yeni dosya oluşturabilir, başarılıysa dosya listesine eklenir.
6. **Hatalar:** Yetki, giriş veya işlem hatalarında uygun hata mesajları gösterilir.

---

## 6. Hata Yönetimi

| Hata Mesajı                      | Anlamı                     | İstemci Tepkisi                        |
| -------------------------------- | -------------------------- | -------------------------------------- |
| `MSG_SERVER_LOGIN_FAILURE`       | Giriş başarısız            | Kullanıcı uyarılır, tekrar deneyebilir |
| `MSG_SERVER_PERMISSION_FAILURE`  | Yetki yok                  | Erişim reddedilir, uyarı gösterilir    |
| `MSG_SERVER_CREATE_FILE_FAILURE` | Dosya oluşturulamadı       | Hata mesajı gösterilir                 |
| `MSG_SERVER_UPDATE_FILE_FAILURE` | Dosya güncelleme başarısız | Hata mesajı gösterilir                 |
| `MSG_SERVER_FAILURE`             | Genel hata                 | Genel hata bildirimi yapılır           |

---

## 7. Özet

- Protokol, istemci ve sunucu arasında net, anlaşılır mesajlar ile gerçek zamanlı dosya paylaşımı ve kullanıcı yönetimini sağlar.
- Tüm mesajlar JSON formatında iletilir.
- Her mesaj tipinin ne anlama geldiği ve alındığında yapılacak işlemler tablo ile belirtilmiştir.
- Protokol dil bağımsızdır ve farklı platformlarda uygulanabilir.
