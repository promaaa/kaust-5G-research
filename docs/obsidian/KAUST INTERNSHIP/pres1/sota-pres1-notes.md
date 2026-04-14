# Notes du Présentateur : État de l'Art — Revue de Littérature UAV-BS

## Diapositive 1 : Carte de Littérature

Ce graphique de dispersion montre les articles positionnés par :
- **Axe X :** Adéquation du matériel pour UAV-BS (NUC + USRP = élevé, Jetson = faible)
- **Axe Y :** Impact/relevance de la recherche pour notre projet

Cercles verts (SkyCell, SkyRAN) : Adéquation élevée + impact élevé — ce sont nos conceptions de référence.

Triangle jaune (Flying Rebots) : Travail conceptuel, relevance modérée.

Carrés rouges (articles Jetson Nano) : Adéquation faible — ces articles ont échoué ou sont tangentiels.

**Conclusion clé :** La littérature prouve que NUC + USRP B210 fonctionne pour la station BS aérienne. Jetson Nano ne fonctionne pas.

## Diapositive 2 : Le Diagramme de l'Écart

Le diagramme Mermaid montre :

**Ce que la littérature fournit :**
- SkyCell → Conception de station base 5G ✓
- SkyRAN → Conception de station base LTE ✓
- Positionnement → Idées de portabilité ✓

**Ce dont nous avons besoin que la littérature MANQUE :**
- Démo d'attaque ❌
- Analyse de sécurité des alertes d'urgence ❌

**Notre contribution :** Prendre la plateforme prouvée NUC + USRP et ajouter la dimension sécurité qu'aucun autre article n'a abordée.

C'est pourquoi notre travail est novateur — nous comblons l'écart entre le matériel UAV-BS prouvée et la sécurité broadcast inexaminée.
