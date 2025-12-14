# on teste que nous avons bien les bonnes colonnes numériques et le bon nombre de ces colonnes numériques
from src.def_fonction_a_tester import get_numeric_columns
class TestGetNumericColumns:
    """Tests pour la fonction get_numeric_columns"""
    
    def test_get_numeric_columns_returns_list(self):
        """Teste que la fonction retourne une liste"""
        cols = get_numeric_columns()
        assert isinstance(cols, list)
    
    def test_get_numeric_columns_count(self):
        """Teste que la fonction retourne le bon nombre de colonnes"""
        cols = get_numeric_columns()
        assert len(cols) == 15
    
    def test_get_numeric_columns_content(self):
        """Teste que la fonction retourne les bonnes colonnes"""
        cols = get_numeric_columns()
        
        expected_cols = [
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
        
        assert cols == expected_cols
