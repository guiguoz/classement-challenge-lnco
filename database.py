import sqlite3
import pandas as pd

DB_NAME = "challenge.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coureurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_complet TEXT UNIQUE NOT NULL,
        genre TEXT,
        categorie_age TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_course TEXT NOT NULL,
        date TEXT,
        circuit TEXT NOT NULL
    )
    """)

    # Ajout de la colonne challenge_id si elle n'existe pas (pour la migration)
    try:
        cursor.execute(
            "ALTER TABLE courses ADD COLUMN challenge_id INTEGER REFERENCES challenges(id)"
        )
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resultats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        coureur_id INTEGER NOT NULL,
        rang INTEGER NOT NULL,
        points INTEGER NOT NULL,
        categorie_course TEXT,
        FOREIGN KEY (course_id) REFERENCES courses (id),
        FOREIGN KEY (coureur_id) REFERENCES coureurs (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT UNIQUE NOT NULL,
        start_year INTEGER,
        end_year INTEGER
    )
    """)

    conn.commit()
    conn.close()


def run_query(query, params=None):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    finally:
        conn.close()


def get_all_coureurs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom_complet FROM coureurs")
    data = cursor.fetchall()
    conn.close()
    return data


def get_courses_by_circuit(circuit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nom_course, date, circuit, challenge_id FROM courses WHERE circuit = ? ORDER BY date ASC",
        (circuit,),
    )
    data = cursor.fetchall()
    conn.close()
    return data


def get_all_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nom_course, date, circuit, challenge_id FROM courses ORDER BY date ASC"
    )
    data = cursor.fetchall()
    conn.close()
    return data


def create_course(nom_course, date, circuit, challenge_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO courses (nom_course, date, circuit, challenge_id) VALUES (?, ?, ?, ?)",
        (nom_course, date, circuit, challenge_id),
    )
    course_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return course_id


def add_coureur(nom_complet, genre, categorie_age):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO coureurs (nom_complet, genre, categorie_age) VALUES (?, ?, ?)",
            (nom_complet, genre, categorie_age),
        )
        new_id = cursor.lastrowid
        conn.commit()
        return new_id
    except sqlite3.IntegrityError:
        cursor.execute("SELECT id FROM coureurs WHERE nom_complet = ?", (nom_complet,))
        return cursor.fetchone()[0]
    finally:
        conn.close()


def update_coureur_name(coureur_id, new_name):
    """Met à jour le nom d'un coureur."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE coureurs SET nom_complet = ? WHERE id = ?", (new_name, coureur_id)
    )
    conn.commit()
    conn.close()


def get_coureur_by_id(coureur_id):
    """Récupère un coureur par son ID avec ses résultats."""
    query = """
    SELECT c.id, c.nom_complet, co.nom_course, r.points, r.rang
    FROM coureurs c
    LEFT JOIN resultats r ON c.id = r.coureur_id
    LEFT JOIN courses co ON r.course_id = co.id
    WHERE c.id = ?
    """
    return run_query(query, (coureur_id,))


def add_result(course_id, coureur_id, rang, points, categorie_course):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resultats (course_id, coureur_id, rang, points, categorie_course) VALUES (?, ?, ?, ?, ?)",
        (course_id, coureur_id, rang, points, categorie_course),
    )
    conn.commit()
    conn.close()


def add_results_batch(results_list):
    """Insert multiple results in one transaction."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO resultats (course_id, coureur_id, rang, points, categorie_course) VALUES (?, ?, ?, ?, ?)",
        results_list,
    )
    conn.commit()
    conn.close()


def get_ranking_data():
    query = """
    SELECT 
        c.nom_complet,
        r.categorie_course as categorie,
        co.circuit,
        co.nom_course,
        co.date as date,
        r.points,
        r.rang,
        co.challenge_id
    FROM resultats r
    JOIN coureurs c ON r.coureur_id = c.id
    JOIN courses co ON r.course_id = co.id
    """
    return run_query(query)


def delete_course(course_id):
    """Delete a raid (course) and its associated results."""
    conn = get_connection()
    cursor = conn.cursor()
    # Remove results linked to this raid
    cursor.execute("DELETE FROM resultats WHERE course_id = ?", (course_id,))
    # Remove the raid itself
    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.commit()
    conn.close()


def rename_course(course_id, new_name):
    """Rename a raid (course)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE courses SET nom_course = ? WHERE id = ?", (new_name, course_id)
    )
    conn.commit()
    conn.close()


def change_course_date(course_id, new_date):
    """Change the date of a raid (course)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE courses SET date = ? WHERE id = ?", (new_date, course_id))
    conn.commit()
    conn.close()


def update_course_challenge(course_id, challenge_id):
    """Change le challenge associé à un raid."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE courses SET challenge_id = ? WHERE id = ?", (challenge_id, course_id)
    )
    conn.commit()
    conn.close()


def get_challenges():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nom, start_year, end_year FROM challenges ORDER BY start_year DESC"
    )
    data = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "range": r[1], "start": r[2], "end": r[3]} for r in data]


def create_challenge(nom, start, end):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO challenges (nom, start_year, end_year) VALUES (?, ?, ?)",
            (nom, start, end),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Le challenge existe déjà
    conn.close()


def update_result_points(course_id, coureur_id, new_points):
    """Met à jour les points d'un résultat spécifique."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE resultats SET points = ? WHERE course_id = ? AND coureur_id = ?",
        (new_points, course_id, coureur_id),
    )
    conn.commit()
    conn.close()


def update_result_points_by_id(result_id, new_points):
    """Met à jour les points d'un résultat par son ID."""
    # Récupérer les anciennes valeurs pour l'audit
    old_data = run_query("SELECT points FROM resultats WHERE id = ?", (result_id,))
    old_points = old_data.iloc[0]["points"] if not old_data.empty else None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE resultats SET points = ? WHERE id = ?", (new_points, result_id)
    )
    conn.commit()
    conn.close()

    # Log de la modification
    import audit

    audit.log_modification(
        "UPDATE", "resultats", result_id, {"points": old_points}, {"points": new_points}
    )


def delete_result_by_id(result_id):
    """Supprime un résultat par son ID."""
    import audit

    # Récupérer les données pour l'audit
    old_data = run_query(
        "SELECT coureur_id, course_id, points, rang FROM resultats WHERE id = ?",
        (result_id,),
    )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resultats WHERE id = ?", (int(result_id),))
    conn.commit()
    conn.close()

    # Log de la suppression
    if not old_data.empty:
        audit.log_modification(
            "DELETE", "resultats", result_id, old_data.iloc[0].to_dict(), None
        )


def get_coureur_id_by_name(nom_complet):
    """Récupère l'ID d'un coureur par son nom."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM coureurs WHERE nom_complet = ?", (nom_complet,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None


def get_coureur_results_for_challenge(
    coureur_name, challenge_id, circuit, category=None
):
    """Récupère tous les résultats d'un coureur pour un challenge/circuit donné,
    incluant les courses où il n'a pas participé."""
    if category:
        query = """
        SELECT 
            r.id, 
            co.id as course_id, 
            co.nom_course, 
            COALESCE(r.points, 0) as points, 
            r.rang, 
            COALESCE(r.categorie_course, ?) as categorie_course
        FROM courses co
        LEFT JOIN (
            SELECT res.* 
            FROM resultats res
            JOIN coureurs cou ON res.coureur_id = cou.id
            WHERE cou.nom_complet = ? AND res.categorie_course = ?
        ) r ON co.id = r.course_id
        WHERE co.challenge_id = ? AND co.circuit = ?
        ORDER BY co.date
        """
        return run_query(
            query, (category, coureur_name, category, challenge_id, circuit)
        )
    else:
        query = """
        SELECT 
            r.id, 
            co.id as course_id, 
            co.nom_course, 
            COALESCE(r.points, 0) as points, 
            r.rang, 
            r.categorie_course
        FROM courses co
        LEFT JOIN (
            SELECT res.* 
            FROM resultats res
            JOIN coureurs cou ON res.coureur_id = cou.id
            WHERE cou.nom_complet = ?
        ) r ON co.id = r.course_id
        WHERE co.challenge_id = ? AND co.circuit = ?
        ORDER BY co.date
        """
        return run_query(query, (coureur_name, challenge_id, circuit))


def get_aberrant_points():
    """Récupère les résultats avec des points aberrants (> 35)."""
    query = """
    SELECT r.id, c.nom_complet, co.nom_course, r.points, r.rang, r.categorie_course
    FROM resultats r
    JOIN coureurs c ON r.coureur_id = c.id
    JOIN courses co ON r.course_id = co.id
    WHERE r.points > 35
    ORDER BY r.points DESC
    """
    return run_query(query)


def get_duplicate_results():
    """Détecte les doublons (même coureur inscrit plusieurs fois sur la même course)."""
    query = """
    SELECT r.id, c.nom_complet, co.nom_course, r.points, r.rang, r.categorie_course, co.id as course_id
    FROM resultats r
    JOIN coureurs c ON r.coureur_id = c.id
    JOIN courses co ON r.course_id = co.id
    WHERE (r.coureur_id, r.course_id) IN (
        SELECT coureur_id, course_id
        FROM resultats
        GROUP BY coureur_id, course_id
        HAVING COUNT(*) > 1
    )
    ORDER BY c.nom_complet, co.nom_course, r.id
    """
    return run_query(query)


def fix_aberrant_points():
    """Corrige automatiquement les points aberrants en les recalculant selon le rang."""
    conn = get_connection()
    cursor = conn.cursor()

    # Récupérer tous les résultats avec points > 35
    cursor.execute("""
        SELECT id, rang FROM resultats WHERE points > 35
    """)
    aberrant_results = cursor.fetchall()

    # Corriger chaque résultat
    for result_id, rang in aberrant_results:
        # Recalculer les points selon le rang (max 35)
        correct_points = min(35, calculate_points_from_rank(rang))
        cursor.execute(
            "UPDATE resultats SET points = ? WHERE id = ?", (correct_points, result_id)
        )

    conn.commit()
    fixed_count = len(aberrant_results)
    conn.close()
    return fixed_count


def calculate_points_from_rank(rank):
    """Calcule les points selon le rang (copie de utils.calculate_points)."""
    if rank < 1:
        return 0
    if rank == 1:
        return 35
    elif rank == 2:
        return 32
    elif rank == 3:
        return 29
    elif rank == 4:
        return 27
    elif rank == 5:
        return 26
    elif rank == 6:
        return 25
    elif 7 <= rank <= 30:
        return 31 - rank
    else:
        return 1


def get_invalid_coureurs():
    """Récupère les coureurs avec des noms invalides."""
    query = """
    SELECT c.id, c.nom_complet, COUNT(r.id) as nb_resultats
    FROM coureurs c
    LEFT JOIN resultats r ON c.id = r.coureur_id
    WHERE c.nom_complet IS NULL OR 
          c.nom_complet = '' OR 
          LOWER(TRIM(c.nom_complet)) = 'nan' OR 
          LOWER(TRIM(c.nom_complet)) = 'nan nan' OR
          LOWER(c.nom_complet) LIKE 'nan %' OR
          LOWER(c.nom_complet) LIKE '% nan' OR
          LOWER(c.nom_complet) LIKE '% nan %'
    GROUP BY c.id, c.nom_complet
    """
    return run_query(query)


def clean_invalid_coureurs():
    """Supprime les coureurs avec des noms invalides (nan, vides, etc.)."""
    conn = get_connection()
    cursor = conn.cursor()

    # Supprimer les résultats des coureurs invalides d'abord
    cursor.execute("""
        DELETE FROM resultats WHERE coureur_id IN (
            SELECT id FROM coureurs WHERE 
            nom_complet IS NULL OR 
            nom_complet = '' OR 
            nom_complet = 'nan' OR 
            nom_complet = 'nan nan' OR
            nom_complet LIKE '%nan%'
        )
    """)

    # Puis supprimer les coureurs invalides
    cursor.execute("""
        DELETE FROM coureurs WHERE 
        nom_complet IS NULL OR 
        nom_complet = '' OR 
        nom_complet = 'nan' OR 
        nom_complet = 'nan nan' OR
        nom_complet LIKE '%nan%'
    """)

    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def delete_challenge(challenge_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM resultats WHERE course_id IN (SELECT id FROM courses WHERE challenge_id = ?)",
        (challenge_id,),
    )
    cursor.execute("DELETE FROM courses WHERE challenge_id = ?", (challenge_id,))
    cursor.execute("DELETE FROM challenges WHERE id = ?", (challenge_id,))
    conn.commit()
    conn.close()
