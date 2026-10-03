import sqlite3
from flask import g


# Veritabanı bağlantı fonksiyonları (mevcut yapı)
# ...existing code...


def yeni_fikir_ekle(
    author_initials, project_title, idea_content, category="Gerilla Hamlesi"
):
  """Yeni bir reklam fikri veya düzeltme metni kaydeder."""
  db = get_db()
  cursor = db.cursor()
  cursor.execute(
      """
        INSERT INTO ad_ideas (author_initials, project_title, idea_content, category)
        VALUES (?, ?, ?, ?)
    """,
      (author_initials, project_title, idea_content, category),
  )
  db.commit()
  return cursor.lastrowid


def tum_fikirleri_getir():
  """Tüm reklam fikirlerini en yeniden eskiye doğru listeler."""
  db = get_db()
  cursor = db.cursor()
  cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS ad_ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_initials TEXT NOT NULL,
            project_title TEXT NOT NULL,
            idea_content TEXT NOT NULL,
            category TEXT DEFAULT 'Gerilla Hamlesi',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
  )
  db.commit()

  cursor.execute(
      "SELECT id, author_initials, project_title, idea_content,"
      " category, created_at FROM ad_ideas ORDER BY id DESC"
  )
  rows = cursor.fetchall()
  return [dict(row) for row in rows]