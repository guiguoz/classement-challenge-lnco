import streamlit as st
import pandas as pd
import database
import audit
from datetime import datetime, timedelta
import backup

def show_dashboard():
    st.title("📊 Tableau de Bord")
    
    # Résumé simple
    show_simple_summary()
    
    st.divider()
    
    # Classements actuels
    show_current_rankings()
    
    st.divider()
    
    # Historique des modifications
    show_modification_history()
    
    st.divider()
    
    # Maintenance
    show_maintenance()

def show_simple_summary():
    st.subheader("📋 Résumé")
    
    # Compter les raids et participants
    total_raids = database.run_query("SELECT COUNT(*) as count FROM courses").iloc[0]['count']
    total_participants = database.run_query("SELECT COUNT(DISTINCT coureur_id) as count FROM resultats").iloc[0]['count']
    
    # Dernier raid ajouté
    last_raid = database.run_query("""
        SELECT nom_course, date, circuit 
        FROM courses 
        ORDER BY date DESC 
        LIMIT 1
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏁 Nombre de raids", total_raids)
    
    with col2:
        st.metric("👥 Nombre de participants", total_participants)
    
    with col3:
        if not last_raid.empty:
            last_name = last_raid.iloc[0]['nom_course']
            last_date = last_raid.iloc[0]['date']
            st.metric("📅 Dernier raid", f"{last_name}")
            st.caption(f"Le {last_date}")
        else:
            st.metric("📅 Dernier raid", "Aucun")

def show_current_rankings():
    st.subheader("🏆 Classements actuels")
    
    # Sélection du circuit
    circuits = database.run_query("SELECT DISTINCT circuit FROM courses ORDER BY circuit")['circuit'].tolist()
    
    if not circuits:
        st.info("Aucun raid enregistré")
        return
    
    selected_circuit = st.selectbox("Choisir un circuit :", circuits, key="dashboard_circuit")
    
    # Classement général pour ce circuit
    ranking = database.run_query(f"""
        SELECT 
            c.nom_complet as "Nom",
            r.categorie_course as "Catégorie",
            SUM(r.points) as "Total Points",
            COUNT(*) as "Nb Raids",
            ROUND(AVG(r.points), 1) as "Moyenne"
        FROM coureurs c
        JOIN resultats r ON c.id = r.coureur_id
        JOIN courses co ON r.course_id = co.id
        WHERE co.circuit = '{selected_circuit}'
        GROUP BY c.id, r.categorie_course
        ORDER BY "Total Points" DESC
        LIMIT 20
    """)
    
    if not ranking.empty:
        st.dataframe(ranking, use_container_width=True, hide_index=True)
    else:
        st.info(f"Aucun résultat pour le circuit {selected_circuit}")
    
    # Liste des raids de ce circuit
    st.subheader(f"📅 Raids du circuit {selected_circuit}")
    raids_list = database.run_query(f"""
        SELECT 
            nom_course as "Nom du raid",
            date as "Date",
            COUNT(r.id) as "Participants"
        FROM courses c
        LEFT JOIN resultats r ON c.id = r.course_id
        WHERE c.circuit = '{selected_circuit}'
        GROUP BY c.id
        ORDER BY c.date DESC
    """)
    
    if not raids_list.empty:
        st.dataframe(raids_list, use_container_width=True, hide_index=True)
    else:
        st.info(f"Aucun raid pour le circuit {selected_circuit}")

def show_modification_history():
    st.subheader("📝 Historique des modifications")
    
    # Initialiser l'audit log si nécessaire
    audit.init_audit_log()
    
    tab1, tab2 = st.tabs(["Modifications récentes", "Changements de points"])
    
    with tab1:
        recent_mods = audit.get_recent_modifications()
        
        if not recent_mods.empty:
            # Formatage pour affichage
            display_mods = recent_mods.copy()
            display_mods['timestamp'] = pd.to_datetime(display_mods['timestamp']).dt.strftime('%d/%m/%Y %H:%M')
            st.dataframe(display_mods[['timestamp', 'action', 'table_name']], use_container_width=True)
        else:
            st.info("Aucune modification enregistrée")
    
    with tab2:
        point_mods = audit.get_point_modifications()
        
        if not point_mods.empty:
            st.markdown("**Dernières modifications de points :**")
            for _, mod in point_mods.iterrows():
                timestamp = pd.to_datetime(mod['timestamp']).strftime('%d/%m/%Y %H:%M')
                st.text(f"• {timestamp} - Résultat ID {mod['record_id']} modifié")
        else:
            st.info("Aucune modification de points enregistrée")
        
def show_maintenance():
    st.subheader("🔧 Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Créer sauvegarde maintenant", key="dashboard_backup_now"):
            try:
                backup_file = backup.create_backup()
                st.success(f"Sauvegarde créée : {backup_file}")
            except Exception as e:
                st.error(f"Erreur lors de la sauvegarde : {e}")
    
    with col2:
        if st.button("🗑️ Nettoyer anciennes sauvegardes", key="dashboard_cleanup_backups"):
            try:
                cleaned = backup.cleanup_old_backups()
                st.success(f"{cleaned} anciennes sauvegardes supprimées")
            except Exception as e:
                st.error(f"Erreur lors du nettoyage : {e}")
    
    # Afficher les sauvegardes existantes
    backups = backup.get_backup_status()
    if backups:
        st.write("**Sauvegardes disponibles :**")
        for backup_info in backups[:5]:  # 5 plus récentes
            st.text(f"• {backup_info['filename']} - {backup_info['date']} ({backup_info['size']})")
    else:
        st.info("Aucune sauvegarde trouvée")