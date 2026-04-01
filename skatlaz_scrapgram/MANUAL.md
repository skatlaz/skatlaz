# 📡 API - Skatlaz Scrapgram

## 🔐 Auth

### Admin Login

POST /admin/login

```json
{ 
"password": "admin123"
}
```

Response:

```json
{ 
"token": "JWT_TOKEN"
}
```

---

## 📊 Admin

### Stats

GET /admin/stats
Header:

```
Authorization: TOKEN
```

---

###Users

GET /admin/users

---

### Messages

GET /admin/messages

---

## 💬Chat

### To send

POST /chat/send

```json
{
"room":"global",

"msg":"Hello"

}
```

---

## 📁 Upload

POST /files/upload

---

## 😂 Giphy

GET /giphy/cats

---

## 📡 WebSocket

Events:

* join
* send
* alert

---

🔥 API ready for app integration
