# -*- coding: utf-8 -*-

SCHEMA_SQL = """
-- =====================================================
-- CREATION DES TABLES METIER
-- =====================================================
-- avec horodatage des lignes pour tracabilite
CREATE TABLE IF NOT EXISTS extrait_sirh (
    id_employee INTEGER PRIMARY KEY,
    age INTEGER,
    genre VARCHAR(20),
    revenu_mensuel INTEGER,
    statut_marital VARCHAR(30),
    departement VARCHAR(50),
    poste VARCHAR(50),
    nombre_experiences_precedentes INTEGER,
    annees_dans_l_entreprise INTEGER,
    annees_dans_le_poste_actuel INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS extrait_eval (
    eval_number VARCHAR(50) PRIMARY KEY,
    id_employee INTEGER NOT NULL,
    augmentation_salaire_precedente VARCHAR(20),
    heure_supplementaires VARCHAR(20),
    satisfaction_employee_environnement INTEGER,
    note_evaluation_precedente INTEGER,
    satisfaction_employee_nature_travail INTEGER,
    satisfaction_employee_equipe INTEGER,
    satisfaction_employee_equilibre_pro_perso INTEGER,
    note_evaluation_actuelle INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (id_employee) REFERENCES extrait_sirh(id_employee) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS extrait_sondage (
    code_sondage VARCHAR(50) PRIMARY KEY,
    id_employee INTEGER NOT NULL,
    a_quitte_l_entreprise VARCHAR(10),
    frequence_deplacement VARCHAR(30),
    domaine_etude VARCHAR(50),
    nombre_participation_pee INTEGER,
    nb_formations_suivies INTEGER,
    distance_domicile_travail INTEGER,
    niveau_education INTEGER,
    annees_depuis_la_derniere_promotion INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (id_employee) REFERENCES extrait_sirh(id_employee) ON DELETE CASCADE
);

-- =====================================================
-- VUE FUSIONNEE (INNER JOIN)
-- =====================================================

CREATE OR REPLACE VIEW donnees_fusionnees AS
SELECT
    s.id_employee,
    s.age,
    s.genre,
    s.revenu_mensuel,
    s.statut_marital,
    s.departement,
    s.poste,
    s.nombre_experiences_precedentes,
    s.annees_dans_l_entreprise,
    s.annees_dans_le_poste_actuel,
    
    e.eval_number,
    e.augmentation_salaire_precedente,
    e.heure_supplementaires,
    e.satisfaction_employee_environnement,
    e.note_evaluation_precedente,
    e.satisfaction_employee_nature_travail,
    e.satisfaction_employee_equipe,
    e.satisfaction_employee_equilibre_pro_perso,
    e.note_evaluation_actuelle,
    
    so.code_sondage,
    so.a_quitte_l_entreprise,
    so.frequence_deplacement,
    so.domaine_etude,
    so.nombre_participation_pee,
    so.nb_formations_suivies,
    so.distance_domicile_travail,
    so.niveau_education,
    so.annees_depuis_la_derniere_promotion
FROM extrait_sirh s
INNER JOIN extrait_eval e ON s.id_employee = e.id_employee
INNER JOIN extrait_sondage so ON s.id_employee = so.id_employee;

-- tracabilite du modele et enregistrement des predictions
-- pour chaque employe, on stocke les donnees d_entree, la prediction et un horodatage
CREATE TABLE IF NOT EXISTS model_logs ( 
    id SERIAL PRIMARY KEY,
    id_employee INTEGER, 
    input_json JSONB, 
    output_json JSONB, 
    created_at TIMESTAMP DEFAULT NOW() 
);
"""
