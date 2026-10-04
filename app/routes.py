import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from flask import current_app as app # veya direkt app nesnen

# Kendi belirleyeceğin çok gizli ve zor bir şifre olsun
SECRET_KEY = "adsc_creative_cok_gizli_anahtar_2026" 

# 1. TOKEN KONTROL GÜVENLİK KALKANI
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Gelen istekte Authorization başlığı var mı kontrol et
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] 
        
        if not token:
            return jsonify({'hata': 'Bu veriyi görmek için giriş yapmalısınız!'}), 401
        
        try:
            # Token'ın geçerli olup olmadığını bizim gizli şifremizle çözerek anlar
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'hata': 'Geçersiz veya süresi dolmuş oturum!'}), 401
            
        return f(*args, **kwargs)
    return decorated

# 2. GİRİŞ YAPMA VE TOKEN ÜRETME ROTASI
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    veri = request.get_json()
    kullanici = veri.get('kullanici')
    sifre = veri.get('sifre')

    # BURAYA KENDİ ADMİN BİLGİLERİNİ YAZ
    if kullanici == "admin" and sifre == "adsc2026":
        # Şifre doğruysa 24 saat geçerli bir yaka kartı (token) üret
        token = jwt.encode({
            'user': kullanici,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({'basari': True, 'token': token})
    else:
        return jsonify({'basari': False, 'hata': 'Yanlış kullanıcı adı veya şifre!'}), 401

# 3. VERİ ÇEKME ROTASINI (KORUMA ALTINA ALINMIŞ HALİ)
@app.route('/api/leads', methods=['GET', 'POST', 'OPTIONS'])
def leads():
    if request.method == 'OPTIONS':
        return '', 200

    # Ziyaretçi formu doldurduğunda POST ile buraya gelir (Token gerekmez)
    if request.method == 'POST':
        # ... Veritabanına kaydetme kodların (mevcut kodun aynı kalacak) ...
        return jsonify({'basari': True, 'mesaj': 'Kayıt başarılı'})

    # Admin verileri görmek için GET ile buraya gelir (Token ZORUNLUDUR)
    if request.method == 'GET':
        # Burada token'ı manuel kontrol ediyoruz çünkü POST ve GET aynı rotada
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] 
        
        if not token:
            return jsonify({'hata': 'Giriş yapmalısınız!'}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'hata': 'Oturum geçersiz!'}), 401

        # ... Token doğruysa veritabanından müşterileri çekip döndürme kodun ...
        # return jsonify({'leads': cekilen_veriler})