import jwt
import datetime
from functools import wraps
from flask import Blueprint, render_template, request, jsonify

from app.database import lead_ekle, tum_leadler
from app.services.ai_service import ai_service, AIServiceError

main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__)

# Güvenlik şifremiz
SECRET_KEY = "adsc_creative_cok_gizli_anahtar_2026"

# --- TOKEN KONTROL GÜVENLİK KALKANI ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Wix'in gönderdiği öncü güvenlik isteklerine (OPTIONS) izin ver
        if request.method == 'OPTIONS':
            return '', 200
            
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] 
        
        if not token:
            return jsonify({'hata': 'Bu veriyi görmek için giriş yapmalısınız!'}), 401
        
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'hata': 'Geçersiz veya süresi dolmuş oturum!'}), 401
            
        return f(*args, **kwargs)
    return decorated

# --- SAĞLIK KONTROLÜ (HEALTH) ---
@main_bp.route("/health")
def health():
    return jsonify({"durum": "aktif", "mesaj": "SmartLead AI servisi sorunsuz çalışıyor."}), 200

# --- SAYFA ROTALARI ---
@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/dashboard")
def dashboard():
    leads = tum_leadler()
    return render_template("dashboard.html", leads=leads)

# --- API ROTALARI ---

# 1. WIX ADMİN GİRİŞ ROTASI
@api_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json() or {}
    kullanici = data.get('kullanici')
    sifre = data.get('sifre')

    if kullanici == "admin" and sifre == "adsc2026":
        token = jwt.encode({
            'user': kullanici,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'basari': True, 'token': token})
    else:
        return jsonify({'basari': False, 'hata': 'Yanlış kullanıcı adı veya şifre!'}), 401


@api_bp.route("/sohbet", methods=["POST", "OPTIONS"])
def sohbet():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json() or {}
    mesaj = data.get("mesaj", "").strip()
    gecmis = data.get("gecmis", [])

    if not mesaj:
        return jsonify({"basari": False, "hata": "Mesaj alanı zorunludur."}), 400

    try:
        cevap = ai_service.yanit_uret(mesaj, gecmis)
        return jsonify({"basari": True, "cevap": cevap}), 200
    except AIServiceError as e:
        return jsonify({"basari": False, "hata": str(e)}), 503

# 2. YENİ MÜŞTERİ KAYDETME (Wix Formundan Gelen)
@api_bp.route("/leads", methods=["POST", "OPTIONS"])
def yeni_lead():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json() or {}
    isim = data.get("isim", "").strip()
    email = data.get("email", "").strip() 
    mesaj = data.get("mesaj", "").strip()

    if not isim or not email:
        return jsonify({"basari": False, "hata": "İsim ve email alanları zorunludur."}), 400

    try:
        lead_id = lead_ekle(isim, email, mesaj)
        return jsonify({"basari": True, "id": lead_id, "mesaj": "Lead başarıyla kaydedildi."}), 201
    except Exception as e:
        return jsonify({"basari": False, "hata": "Veritabanı kaydı sırasında hata oluştu."}), 500

# 3. MÜŞTERİLERİ LİSTELEME (Güvenlik Kalkanı Eklendi)
@api_bp.route("/leads", methods=["GET", "OPTIONS"])
@token_required 
def lead_listesi():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        leads = tum_leadler()
        return jsonify({"basari": True, "leads": leads}), 200
    except Exception as e:
        return jsonify({"basari": False, "hata": "Kayıtlar çekilemedi."}), 500