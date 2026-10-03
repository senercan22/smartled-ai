from flask import Blueprint, render_template, request, jsonify
from app.database import lead_ekle, tum_leadler
from app.services.ai_service import ai_service, AIServiceError

main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__)

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

@api_bp.route("/sohbet", methods=["POST"])
def sohbet():
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

@api_bp.route("/leads", methods=["POST"])
def yeni_lead():
    data = request.get_json() or {}
    isim = data.get("isim", "").strip()
    telefon = data.get("telefon", "").strip()
    mesaj = data.get("mesaj", "").strip()

    if not isim or not telefon:
        return jsonify({"basari": False, "hata": "İsim ve telefon alanları zorunludur."}), 400

    try:
        lead_id = lead_ekle(isim, telefon, mesaj)
        return jsonify({"basari": True, "id": lead_id, "mesaj": "Lead başarıyla kaydedildi."}), 201
    except Exception as e:
        return jsonify({"basari": False, "hata": "Veritabanı kaydı sırasında hata oluştu."}), 500

@api_bp.route("/leads", methods=["GET"])
def lead_listesi():
    try:
        leads = tum_leadler()
        return jsonify({"basari": True, "leads": leads}), 200
    except Exception as e:
        return jsonify({"basari": False, "hata": "Kayıtlar çekilemedi."}), 500