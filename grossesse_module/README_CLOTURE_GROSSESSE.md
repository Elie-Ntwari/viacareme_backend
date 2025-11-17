# Documentation - Clôture de Grossesse

## Modification de l'endpoint `grossesses/<int:id>/set-state/`

L'endpoint pour changer le statut d'une grossesse a été modifié pour permettre la saisie d'informations détaillées lors de la clôture d'une grossesse (statut "TERMINEE").

## Nouveau Modèle: ClotureGrossesse

Le modèle `ClotureGrossesse` stocke les informations détaillées de l'accouchement:

### Champs disponibles:
- `date_accouchement`: Date de l'accouchement (obligatoire)
- `nombre_enfants`: Nombre d'enfants nés (défaut: 1)
- `genre_enfant`: Genre de l'enfant (MASCULIN, FEMININ, INDETERMINE)
- `poids_naissance`: Poids à la naissance en kg (0.5 - 10 kg)
- `taille_naissance`: Taille à la naissance en cm (20 - 70 cm)
- `type_accouchement`: Type d'accouchement (VAGINAL, CESARIENNE, FORCEPS, VENTOUSE)
- `issue_grossesse`: Issue de la grossesse (VIVANT, MORT_NE, FAUSSE_COUCHE, INTERRUPTION)
- `complications`: Complications éventuelles (texte libre)
- `observations`: Observations médicales (texte libre)
- `duree_travail`: Durée du travail (format durée Django)

## Utilisation de l'endpoint

### URL
```
POST /grossesses/<int:id>/set-state/
```

### Changement de statut simple (EN_COURS, PERDUE)
```json
{
    "statut": "PERDUE"
}
```

### Clôture de grossesse avec informations détaillées
```json
{
    "statut": "TERMINEE",
    "cloture_info": {
        "date_accouchement": "2024-01-15",
        "nombre_enfants": 1,
        "genre_enfant": "MASCULIN",
        "poids_naissance": 3.2,
        "taille_naissance": 48,
        "type_accouchement": "VAGINAL",
        "issue_grossesse": "VIVANT",
        "complications": "Aucune complication majeure",
        "observations": "Accouchement normal, mère et enfant en bonne santé",
        "duree_travail": "08:30:00"
    }
}
```

### Réponse en cas de succès
```json
{
    "id": 1,
    "date_debut": "2023-04-20",
    "dpa": "2024-01-15",
    "statut": "TERMINEE",
    "cloture": {
        "id": 1,
        "date_accouchement": "2024-01-15",
        "nombre_enfants": 1,
        "genre_enfant": "MASCULIN",
        "poids_naissance": "3.20",
        "taille_naissance": 48,
        "type_accouchement": "VAGINAL",
        "issue_grossesse": "VIVANT",
        "complications": "Aucune complication majeure",
        "observations": "Accouchement normal, mère et enfant en bonne santé",
        "duree_travail": "08:30:00",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

## Validations

### Champs obligatoires pour la clôture:
- `date_accouchement`
- `type_accouchement`
- `issue_grossesse`

### Validations automatiques:
- `nombre_enfants`: Minimum 1
- `poids_naissance`: Entre 0.5 et 10 kg
- `taille_naissance`: Entre 20 et 70 cm
- Les informations de clôture sont obligatoires si le statut est "TERMINEE"
- Une grossesse ne peut être clôturée qu'une seule fois

## Erreurs possibles

### Clôture sans informations
```json
{
    "error": "Les informations de clôture sont obligatoires pour terminer une grossesse"
}
```

### Grossesse déjà clôturée
```json
{
    "error": "Cette grossesse a déjà été clôturée"
}
```

### Données invalides
```json
{
    "cloture_info": {
        "poids_naissance": ["Le poids doit être entre 0.5 et 10 kg"]
    }
}
```

## Audit

Toutes les clôtures de grossesse sont enregistrées dans le système d'audit avec l'action `CLOTURE_GROSSESSE`.

## Migration

Pour appliquer les changements en base de données:
```bash
python manage.py migrate grossesse_module