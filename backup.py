import os
import shutil
import sqlite3
from datetime import datetime, date
import database

BACKUP_DIR = "backups"

def ensure_backup_dir():
    """Crée le dossier de sauvegarde s'il n'existe pas."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def create_backup(force=False):
    """Crée une sauvegarde de la base de données.
    
    Args:
        force: Si True, écrase la sauvegarde existante du jour
    """
    ensure_backup_dir()
    
    today = date.today().strftime("%Y-%m-%d")
    backup_filename = f"{BACKUP_DIR}/challenge_{today}.db"
    
    # Éviter les doublons du même jour (sauf si force=True)
    if os.path.exists(backup_filename) and not force:
        return backup_filename
    
    try:
        # Copie simple du fichier SQLite
        shutil.copy2(database.DB_NAME, backup_filename)
        
        # Nettoyer les anciens backups (garder 30 jours)
        cleanup_old_backups()
        
        return backup_filename
    except Exception as e:
        print(f"Erreur backup: {e}")
        return None

def cleanup_old_backups(keep_days=30):
    """Supprime les backups de plus de keep_days jours."""
    if not os.path.exists(BACKUP_DIR):
        return
    
    cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 3600)
    
    for filename in os.listdir(BACKUP_DIR):
        if filename.startswith("challenge_") and filename.endswith(".db"):
            filepath = os.path.join(BACKUP_DIR, filename)
            if os.path.getmtime(filepath) < cutoff_date:
                try:
                    os.remove(filepath)
                except:
                    pass

def should_backup_today():
    """Vérifie si un backup est nécessaire aujourd'hui."""
    today = date.today().strftime("%Y-%m-%d")
    backup_filename = f"{BACKUP_DIR}/challenge_{today}.db"
    return not os.path.exists(backup_filename)

def get_backup_status():
    """Retourne le statut des sauvegardes."""
    ensure_backup_dir()
    
    backups = []
    if os.path.exists(BACKUP_DIR):
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("challenge_") and filename.endswith(".db"):
                filepath = os.path.join(BACKUP_DIR, filename)
                size = os.path.getsize(filepath)
                
                # Extraire la date du nom de fichier (challenge_YYYY-MM-DD.db)
                try:
                    date_str = filename.replace("challenge_", "").replace(".db", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    date_display = file_date.strftime("%d/%m/%Y")
                except:
                    date_display = "?"
                
                # Heure de modification pour plus de précision
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                time_display = mtime.strftime("%H:%M")
                
                backups.append({
                    "filename": filename,
                    "date": f"{date_display} à {time_display}",
                    "size": f"{size // 1024} Ko"
                })
    
    backups.sort(key=lambda x: x["filename"], reverse=True)
    return backups[:10]  # 10 derniers backups