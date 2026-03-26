import datetime
import os
from fpdf import FPDF


def calculate_points(rank: int) -> int:
    """
    Calcule les points en fonction du rang selon le barème du challenge.
    Barème identique pour Homme, Femme et Mixte :
    1er: 35, 2e: 32, 3e: 29, 4e: 27, 5e: 26, 6e: 25.
    Ensuite -1 point par place jusqu'au 30e (1 pt).
    30e et suivants : 1 pt.
    """
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
        # 7e=24, ... 30e=1 -> Formule : 31 - rang
        return 31 - rank
    else:
        # 31ème et plus
        return 1


class PDF(FPDF):
    def header(self):
        # Logo
        logo_path = "logo_lnco_upscale.jpg"
        has_logo = False
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 25)
            has_logo = True

        self.set_font("Arial", "B", 15)
        base = "Challenge Regional de Raids d'Orientation"
        circuit = getattr(self, "header_circuit", None)
        title = f"{base} - {circuit}" if circuit else base
        header_date = getattr(self, "header_date", None)
        if header_date:
            title = f"{title} - {header_date}"
            
        if has_logo:
            # Titre à droite du logo (aligné verticalement)
            self.set_xy(38, 15)
            self.cell(0, 10, title, 0, 1, "C")
            self.set_y(35)
        else:
            self.cell(0, 10, title, 0, 1, "C")
            self.ln(5)

    def footer(self):
        self.set_y(-22)
        
        # Ligne 1 : Nom de la Ligue (Gras, Gris foncé élégant)
        self.set_font("Arial", "B", 9)
        self.set_text_color(44, 62, 80)
        self.cell(0, 5, "Ligue de Normandie de course d'orientation", 0, 1, "C")
        
        # Ligne 2 : Site Web (Normal, Bleu lien)
        self.set_font("Arial", "", 8)
        self.set_text_color(41, 128, 185)
        self.cell(0, 4, "https://liguenormandiecoursedorientation.fr/", 0, 1, "C", link="https://liguenormandiecoursedorientation.fr/")
        
        # Ligne 3 : Pagination et Date (Italique, Gris clair)
        self.set_font("Arial", "I", 7)
        self.set_text_color(128, 128, 128)
        self.cell(
            0,
            5,
            f"Page {self.page_no()}/{{nb}} - Genere le {datetime.date.today().strftime('%d/%m/%Y')}",
            0,
            0,
            "C",
        )
        # Réinitialiser la couleur en noir pour la suite
        self.set_text_color(0, 0, 0)


def generate_pdf(dfs_dict, is_final: bool = False):
    """
    Génère un PDF mis en page proprement (paysage si nécessaire), avec:
    - en-têtes de tableau grisés
    - colonnes à largeur dynamique (nom plus large)
    - zébrage des lignes
    - troncature élégante du texte pour éviter les débordements
    dfs_dict = { "Titre de la section": dataframe }
    is_final: si True, affiche la mention "Classement Final - 4 meilleurs resultats"
    """
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=25)

    def fit_text(txt: str, width: float) -> str:
        """Tronque avec ellipsis si le texte dépasse la largeur."""
        s = str(txt)
        s = s.encode("latin-1", "replace").decode("latin-1")
        if pdf.get_string_width(s) <= width - 2:
            return s
        ell = "..."
        while s and pdf.get_string_width(s + ell) > width - 2:
            s = s[:-1]
        return (s + ell) if s else ""

    for title, df_item in dfs_dict.items():
        header_date = None
        df = df_item
        if isinstance(df_item, tuple) and len(df_item) == 2:
            df, header_date = df_item
        cols = df.columns.tolist()
        # Orientation paysage si beaucoup de colonnes
        orientation = "L" if len(cols) > 6 else "P"
        # Injecter le circuit dans l'en-tête
        pdf.header_circuit = title
        pdf.header_date = header_date
        pdf.add_page(orientation=orientation)

        # Titre de section
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, title, 0, 1, "L")
        if is_final:
            pdf.set_font("Arial", "I", 9)
            pdf.set_text_color(0, 128, 0)
            pdf.cell(0, 5, "Classement Final - 4 meilleurs resultats retenus", 0, 1, "L")
            pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

        # Calcul des largeurs de colonnes
        page_w = pdf.w - pdf.l_margin - pdf.r_margin
        num_cols = len(cols)
        # Largeurs dédiées pour Rang et Nom, le reste partagé
        has_rang = "Classement" in cols
        has_nom = "Nom Prénom" in cols
        w_rang = 14 if has_rang else 0
        w_nom = 80 if has_nom else 0
        rem_w = page_w - w_rang - w_nom if (has_rang or has_nom) else page_w
        num_other = num_cols - (1 if has_rang else 0) - (1 if has_nom else 0)
        w_other = max(12, rem_w / num_other) if num_other > 0 else 0
        # Ajustement si dépassement
        total_w = (
            (w_rang if has_rang else 0)
            + (w_nom if has_nom else 0)
            + w_other * num_other
        )
        if total_w > page_w and has_nom:
            over = total_w - page_w
            w_nom = max(45, w_nom - over)
            rem_w = page_w - w_rang - w_nom
            w_other = max(16, rem_w / num_other) if num_other > 0 else 0

        # Liste des largeurs dans l'ordre des colonnes
        widths = []
        for c in cols:
            if c == "Classement":
                widths.append(w_rang)
            elif c == "Nom Prénom":
                widths.append(w_nom)
            else:
                widths.append(w_other if num_other > 0 else page_w / num_cols)

        # Dessin de l'en-tête de tableau
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 9)
        header_h = 12  # Hauteur augmentée pour les dates
        for i, c in enumerate(cols):
            display_header = c
            # Gérer les retours à la ligne dans les en-têtes
            if "\n" in display_header:
                lines = display_header.split("\n")
                pdf.cell(widths[i], header_h, "", border=1, ln=0, align="C", fill=True)
                # Revenir en arrière pour écrire le texte
                x_pos = pdf.get_x() - widths[i]
                y_pos = pdf.get_y()
                pdf.set_xy(x_pos, y_pos + 1)
                pdf.cell(widths[i], 5, fit_text(lines[0], widths[i]), ln=0, align="C")
                pdf.set_xy(x_pos, y_pos + 6)
                pdf.cell(widths[i], 5, fit_text(lines[1], widths[i]), ln=0, align="C")
                pdf.set_xy(x_pos + widths[i], y_pos)
            else:
                pdf.cell(
                    widths[i],
                    header_h,
                    fit_text(display_header, widths[i]),
                    border=1,
                    ln=0,
                    align="C",
                    fill=True,
                )
        pdf.ln(header_h)

        # Lignes du tableau (zébrage)
        pdf.set_font("Arial", "", 9)
        row_h = 7
        fill_toggle = False

        def maybe_new_page():
            nonlocal fill_toggle
            if pdf.get_y() > pdf.h - pdf.b_margin - row_h:
                pdf.add_page(orientation=orientation)
                # Répéter l'en-tête
                pdf.set_font("Arial", "B", 9)
                pdf.set_fill_color(230, 230, 230)
                for i, c in enumerate(cols):
                    if "\n" in c:
                        lines = c.split("\n")
                        pdf.cell(widths[i], header_h, "", border=1, ln=0, align="C", fill=True)
                        x_pos = pdf.get_x() - widths[i]
                        y_pos = pdf.get_y()
                        pdf.set_xy(x_pos, y_pos + 1)
                        pdf.cell(widths[i], 5, fit_text(lines[0], widths[i]), ln=0, align="C")
                        pdf.set_xy(x_pos, y_pos + 6)
                        pdf.cell(widths[i], 5, fit_text(lines[1], widths[i]), ln=0, align="C")
                        pdf.set_xy(x_pos + widths[i], y_pos)
                    else:
                        pdf.cell(
                            widths[i],
                            header_h,
                            fit_text(c, widths[i]),
                            border=1,
                            ln=0,
                            align="C",
                            fill=True,
                        )
                pdf.ln(header_h)
                pdf.set_font("Arial", "", 9)
                fill_toggle = False

        for _, row in df.iterrows():
            maybe_new_page()
            fill_toggle = not fill_toggle
            if fill_toggle:
                pdf.set_fill_color(248, 248, 248)
            else:
                pdf.set_fill_color(255, 255, 255)
            for i, c in enumerate(cols):
                val = row[c]
                align = "L" if c == "Nom Prénom" else "C"
                if isinstance(val, (int, float)) and c != "Nom Prénom":
                    txt = str(int(val)) if float(val).is_integer() else f"{val:.2f}"
                else:
                    txt = str(val)
                txt = fit_text(txt, widths[i])
                pdf.cell(widths[i], row_h, txt, border=1, ln=0, align=align, fill=True)
            pdf.ln(row_h)

    return bytes(pdf.output())


def generate_stats_pdf(circuits_stats: dict, challenge_name: str) -> bytes:
    """
    Génère un PDF de statistiques pour tous les circuits du challenge.
    circuits_stats = {
        "trotteur": {
            "global": {"Total": int, "Hommes": int, "Femmes": int, "Mixtes": int},
            "courses": [(nom, date, total, hommes, femmes, mixtes), ...]
        },
        ...
    }
    """
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=25)

    def fit_text(txt: str, width: float) -> str:
        s = str(txt)
        s = s.encode("latin-1", "replace").decode("latin-1")
        if pdf.get_string_width(s) <= width - 2:
            return s
        ell = "..."
        while s and pdf.get_string_width(s + ell) > width - 2:
            s = s[:-1]
        return (s + ell) if s else ""

    def draw_table(headers: list, rows: list, col_widths: list):
        """Dessine un tableau avec en-têtes grisés et zébrage des lignes."""
        row_h = 7
        header_h = 8

        # En-tête
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 9)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], header_h, fit_text(h, col_widths[i]), border=1, ln=0, align="C", fill=True)
        pdf.ln(header_h)

        # Lignes
        pdf.set_font("Arial", "", 9)
        fill_toggle = False
        for row in rows:
            if pdf.get_y() > pdf.h - pdf.b_margin - row_h:
                pdf.add_page(orientation="P")
                pdf.set_fill_color(230, 230, 230)
                pdf.set_font("Arial", "B", 9)
                for i, h in enumerate(headers):
                    pdf.cell(col_widths[i], header_h, fit_text(h, col_widths[i]), border=1, ln=0, align="C", fill=True)
                pdf.ln(header_h)
                pdf.set_font("Arial", "", 9)
                fill_toggle = False
            fill_toggle = not fill_toggle
            pdf.set_fill_color(248, 248, 248) if fill_toggle else pdf.set_fill_color(255, 255, 255)
            for i, val in enumerate(row):
                align = "L" if i == 0 and len(headers) > 2 else "C"
                pdf.cell(col_widths[i], row_h, fit_text(str(val), col_widths[i]), border=1, ln=0, align=align, fill=True)
            pdf.ln(row_h)

    circuit_labels = {"trotteur": "Trotteur", "orienteur": "Orienteur", "raideur": "Raideur"}

    for circuit, data in circuits_stats.items():
        pdf.header_circuit = circuit_labels.get(circuit, circuit.capitalize())
        pdf.header_date = challenge_name
        pdf.add_page(orientation="P")

        page_w = pdf.w - pdf.l_margin - pdf.r_margin

        # Titre de section
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 9, f"Statistiques - {circuit_labels.get(circuit, circuit.capitalize())}", 0, 1, "L")
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Challenge {challenge_name}", 0, 1, "L")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

        # --- Tableau statistiques globales ---
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 7, "Statistiques globales", 0, 1, "L")
        pdf.ln(1)

        g = data["global"]
        glob_headers = ["Total Circuit", "Hommes", "Femmes", "Mixtes"]
        glob_rows = [[g["Total"], g["Hommes"], g["Femmes"], g["Mixtes"]]]
        w_col = page_w / 4
        draw_table(glob_headers, glob_rows, [w_col] * 4)
        pdf.ln(6)

        # --- Tableau participants par course ---
        if data["courses"]:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 7, "Participants par course", 0, 1, "L")
            pdf.ln(1)

            course_headers = ["Course", "Date", "Total", "Hommes", "Femmes", "Mixtes"]
            w_course = page_w * 0.38
            w_date = page_w * 0.14
            w_stat = (page_w - w_course - w_date) / 4
            course_widths = [w_course, w_date, w_stat, w_stat, w_stat, w_stat]

            course_rows = [
                [nom, date, total, hommes, femmes, mixtes]
                for nom, date, total, hommes, femmes, mixtes in data["courses"]
            ]
            draw_table(course_headers, course_rows, course_widths)

    return bytes(pdf.output())
