def get_numeric_columns() -> List[str]:
    """
    Retourne la liste des colonnes numériques à normaliser.
    
    Returns:
        Liste des noms de colonnes numériques
    """
    return [
        'satisfaction_employee_environnement',
        'note_evaluation_precedente',
        'satisfaction_employee_nature_travail',
        'satisfaction_employee_equipe',
        'satisfaction_employee_equilibre_pro_perso',
        'note_evaluation_actuelle',
        'age',
        'revenu_mensuel',
        'nombre_experiences_precedentes',
        'annees_dans_l_entreprise',
        'nombre_participation_pee',
        'nb_formations_suivies',
        'distance_domicile_travail',
        'niveau_education',
        'annees_depuis_la_derniere_promotion'
    ]
