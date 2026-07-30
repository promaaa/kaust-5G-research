# Évaluation de la valeur scientifique et de la publiabilité du banc d'essai

> **Document de travail.** Cette analyse aide à cadrer une future publication.
> Les affirmations et les sources doivent être vérifiées avant d'être reprises
> dans un manuscrit scientifique.

## **1\. Résumé exécutif**

L'analyse critique approfondie de votre projet expérimental basé sur OpenAirInterface (OAI) révèle une initiative d'ingénierie d'une richesse exceptionnelle. En combinant l'architecture désagrégée (CU/DU split via l'interface F1), l'utilisation de transports hétérogènes non idéaux (Wi-Fi GRE, tunnels WireGuard sur réseaux 5G commerciaux), le portage sur des cibles matérielles limitées (Raspberry Pi 5\) et l'intégration de la diffusion d'alertes publiques (PWS/SIB8), vous avez bâti un écosystème expérimental extrêmement complet. Toutefois, pour déterminer avec votre professeur la stratégie de publication adéquate, une distinction stricte doit être opérée entre l'intégration système réussie (aussi complexe soit-elle) et la production d'une contribution scientifique fondamentale.  
La conclusion directe quant à la publiabilité de ce travail est que la publication est fortement recommandée, mais son format dépendra des validations supplémentaires que vous êtes prêt à mener. Le niveau de maturité actuel de votre projet est très élevé sur le plan logiciel, de l'intégration, et de la reproductibilité (grâce à l'outillage TUI et aux scripts de déploiement). Cependant, sur le plan de la validation scientifique, le projet requiert un contrôle plus strict des variables expérimentales. La variation spectaculaire des débits observés (de 150 Mb/s en monolithique à 12 Mb/s ou 42 Mb/s selon les configurations de *split* et de transport) indique une dégradation majeure des performances qui n'est pas encore mathématiquement ou statistiquement modélisée.  
À ce stade, le type de publication le plus réaliste et immédiat est un "Artifact Paper" ou un article de type "Workshop" orienté vers les réseaux expérimentaux et les bancs d'essai (Testbeds). Une soumission sous forme de "Démo" dans une conférence majeure est également une voie hautement défendable, permettant de valoriser l'interface opérateur (TUI) et la reproductibilité du déploiement. Si l'objectif est de viser un article académique complet (*full paper*) dans une conférence de premier plan, des conditions méthodologiques strictes devront être remplies avant soumission. Il sera impératif de stabiliser l'environnement radio (par exemple via une cage de Faraday ou un câblage coaxial direct) pour isoler les dégradations liées au canal radio de celles induites par le réseau de transport F1.  
La contribution principale la plus défendable, sur le plan strictement scientifique, ne réside pas dans l'empilement des technologies, mais dans l'étude empirique de la dégradation des performances du *split* F1 sur des liaisons asynchrones et non idéales. L'observation du *Modulation and Coding Scheme* (MCS) qui s'effondre et se bloque à 0 constitue un point d'ancrage scientifique majeur. En expliquant la cause racine de ce phénomène de goulot d'étranglement (bottleneck) au niveau du *scheduler* MAC et de sa tolérance à la gigue (jitter) des paquets F1-U, vous transformerez un constat expérimental en une véritable connaissance généralisable pour la communauté des réseaux mobiles.

## **2\. État de l'art structuré**

Pour évaluer la portée de vos travaux, il est indispensable de les confronter à la littérature existante et aux avancées récentes des projets *open-source* dans les domaines de la désagrégation RAN, des transports non idéaux et de la diffusion d'alertes.

### **CU/DU split et interface F1**

L'architecture 5G NR, définie par le 3GPP, introduit plusieurs options de séparation fonctionnelle. L'Option 2, qui sépare la *Central Unit* (CU) de la *Distributed Unit* (DU) via l'interface F1, est aujourd'hui le standard de fait pour centraliser les couches supérieures (RRC, SDAP, PDCP) tout en distribuant les couches temps réel (RLC, MAC, PHY)1. Le plan de contrôle (F1-C) s'appuie sur le protocole F1AP transporté sur SCTP, garantissant une livraison fiable des messages de configuration et de gestion des contextes utilisateurs4. Le plan utilisateur (F1-U) repose quant à lui sur GTP-U/UDP/IP pour l'acheminement des données applicatives4. Bien que la littérature s'accorde à dire que l'interface F1 (souvent qualifiée de *midhaul*) tolère des latences et une gigue plus élevées que le *fronthaul* (Option 7.2x), les contraintes demeurent significatives. Des études industrielles et académiques soulignent que pour maintenir un flux de données ininterrompu et éviter la famine des tampons de la couche MAC de la DU, la latence du *midhaul* doit idéalement rester inférieure à 5 ou 10 millisecondes7. Des recherches ont également exploré l'optimisation des sockets UDP au sein d'OAI pour minimiser la latence de traitement des paquets F1-U8, prouvant que l'implémentation logicielle de cette interface est un sujet d'étude actif.

### **OpenAirInterface et plateformes 5G open-source**

Le paysage des plateformes RAN *open-source* est principalement dominé par OpenAirInterface (OAI) et srsRAN. OAI se distingue par une implémentation exhaustive et standardisée de la pile 3GPP, incluant non seulement le RAN mais également un cœur de réseau complet (OAI-5GC) et des fonctionnalités avancées comme le *split* CU/DU (F1), le *split* CU-CP/CU-UP (E1), et le support O-RAN 7.2x5. Les travaux récents de l'alliance OAI démontrent l'interopérabilité de cette architecture désagrégée avec du matériel commercial6. De son côté, srsRAN, via son projet "srsRAN Project" (ou OCUDU), propose également une architecture SA 5G très performante, reconnue pour sa stabilité et sa facilité de configuration, bien qu'elle s'appuie souvent sur le cœur Open5GS de manière tierce13. Les bancs d'essai basés sur des radios logicielles (SDR) telles que l'USRP B210 sont omniprésents dans la littérature pour caractériser les performances de ces piles logicielles11. Les études comparent fréquemment la consommation de ressources (CPU, RAM) entre les déploiements monolithiques et désagrégés, soulignant que la DU constitue généralement le goulot d'étranglement computationnel en raison des exigences du traitement en bande de base17.

### **Wireless F1, midhaul sans fil et wireless backhaul**

L'acheminement de l'interface F1 sur des liaisons sans fil est un domaine de recherche effervescent, particulièrement pour les déploiements nomades ou tactiques. Le 3GPP a formalisé cette approche à travers le standard *Integrated Access and Backhaul* (IAB), qui permet à un nœud de relayer le trafic F1 en utilisant la même interface radio 5G (NR Uu) que l'accès utilisateur, grâce à une couche d'adaptation spécifique (BAP)2. Cependant, au-delà de la norme IAB, de nombreux travaux académiques évaluent des solutions de contournement en utilisant des liaisons IP génériques pour transporter le trafic F1. L'utilisation de liaisons Wi-Fi, de modems cellulaires 4G/5G ou même de constellations satellitaires (Starlink) a été étudiée23. Ces approches dites "transparentes" encapsulent le trafic F1 dans des tunnels (VPN, WireGuard, GRE). La littérature met en garde contre les défis inhérents à ces méthodes, notamment l'impact de la fragmentation IP due à l'accumulation des en-têtes (MTU), l'asymétrie des débits et l'introduction d'une gigue imprévisible qui perturbe les algorithmes d'adaptation de lien et de contrôle de congestion TCP au niveau des applications25.

### **PWS/SIB8 dans OAI et architectures split**

Le système d'alerte public (PWS), incluant des implémentations comme le CMAS américain ou l'EU-Alert européen, repose sur la diffusion de blocs d'informations système spécifiques, en l'occurrence le SIB8 en 5G NR28. Dans une architecture CU/DU, la procédure F1AP Write-Replace Warning est conçue pour permettre à la CU de transmettre le contenu de l'alerte à la DU, qui se charge ensuite de sa planification et de sa diffusion radio4. Historiquement, la prise en charge de ces alertes dans les plateformes *open-source* était inexistante. Très récemment, des chercheurs ont modifié le code d'OAI pour intégrer la génération de SIB8 dans le cadre d'études sur la sécurité et les attaques par usurpation (*spoofing*) d'alertes d'urgence29. Toutefois, ces implémentations pionnières ont été réalisées dans un contexte de gNB monolithique. L'intégration et la validation expérimentale du cheminement complet d'un message PWS à travers une architecture désagrégée CU/DU réelle constituent un terrain très peu exploré.

### **Reproductibilité et testbeds**

La communauté scientifique valorise de plus en plus la reproductibilité des expérimentations réseau. De multiples publications se concentrent exclusivement sur la description de bancs d'essai (*testbeds*), d'outils d'automatisation et de méthodologies de déploiement10. Des frameworks comme SLICES ou Colosseum fournissent des environnements de test à grande échelle, tandis que d'autres travaux se focalisent sur des déploiements hautement portables. Le projet "Pi5G", par exemple, a récemment démontré la viabilité d'un réseau 5G SA complet (srsRAN et Open5GS) sur un Raspberry Pi 535. Bien que ce travail valide l'utilisation de SBC (Single Board Computers) récents pour la 5G, la réalisation d'une DU OAI (réputée plus exigeante en ressources) sur une telle architecture contrainte, couplée à un *midhaul* hétérogène, apporte une dimension supplémentaire aux défis d'intégration à la périphérie du réseau (*edge*).

## **3\. Tableau comparatif des travaux existants**

Le tableau suivant positionne votre projet par rapport aux initiatives académiques et *open-source* les plus pertinentes identifiées dans la littérature.

| Référence / Projet | Année | Plateforme | SDR utilisé | OAI utilisé ? | CU/DU split réel ? | F1 étudié ? | Transport F1 | Wireless F1 testé ? | PWS/SIB8 étudié ? | Mesures de débit ? | Mesures MCS/BLER ? | Reproductibilité | Différence principale avec votre projet | Proximité |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Abou Hasna et al.** (Spoofing)29 | 2026 | PC Standard | USRP B210 | Oui | Non (Monolithique présumé) | Non | N/A | Non | Oui | Non | Non | Code public, NMS | Focalisation exclusive sur la sécurité et le *spoofing* ; architecture monolithique ; pas de *midhaul*. | Moyenne |
| **Pi5G** [35] | 2024 / 2025 | Raspberry Pi 5 | USRP B200mini | Non (srsRAN) | Oui | Partiel | Interne / Ethernet | Non | Non | Oui | Oui | Artifact ouvert | Utilise srsRAN ; environnement local sans transport F1 hétérogène ou de messages SIB8. | Forte |
| **Lisi et al.** (NTN / Starlink)25 | 2024 | Serveurs | RFSimulator | Oui | Oui | Oui (F1-U/C) | Starlink | Oui (Satellite) | Non | Oui (RTT/Jitter) | Non | Faible | Test sur constellation satellitaire entraînant des latences extrêmes (\>50ms) ; usage de simulation RF. | Moyenne |
| **NIST O-RAN Testbed** [34] | 2024 | Serveurs | USRP | Oui | Oui | Oui | Ethernet | Non | Non | Oui | Non | Scripts automatisés | Accent porté sur l'orchestration, les RICs et xApps ; pas d'évaluation de liaisons F1 non idéales. | Faible |
| **Elango et al.** (CPU/GPU)19 | 2024 | Serveurs GPU | Nvidia Aerial | Oui | Oui | Non focalisé | Ethernet | Non | Non | Oui | Non | Partielle | Focalisé sur l'optimisation des ressources matérielles et l'accélération GPU pour la couche PHY. | Faible |
| **Votre Projet** | **2026** | **PC & Pi 5** | **USRP B210** | **Oui** | **Oui** | **Oui** | **Ethernet, Wi-Fi GRE, WG 5G** | **Oui (Wi-Fi, 5G VPN)** | **Oui** | **Oui** | **Oui** | **TUI, Tooling, Dépôts** | **Analyse combinée des goulots MAC sur F1 hétérogène (VPN/GRE) et intégration complète PWS en architecture split.** | **\-** |

L'analyse de ce tableau démontre que votre travail se situe à l'intersection de plusieurs domaines de recherche actifs, mais qu'il propose une combinaison unique. Si l'intégration du Raspberry Pi 5 a été démontrée par Pi5G, et que le SIB8 a été intégré à OAI pour des scénarios de sécurité, aucun travail ne documente les effets profonds d'un *midhaul* de type VPN WireGuard sur réseau cellulaire commercial sur les algorithmes d'ordonnancement (MAC) d'une DU OAI, tout en gérant le cycle de vie complet d'une alerte publique.

## **4\. Analyse critique de votre projet**

Afin de structurer le discours face à votre professeur, vos contributions doivent être classées rigoureusement selon leur nature intrinsèque. Il faut éviter l'écueil consistant à présenter une belle réussite technique comme une découverte scientifique.

### **Contribution scientifique potentielle**

Les éléments relevant de cette catégorie doivent produire une connaissance généralisable, indépendante de l'outil OAI, concernant le comportement des réseaux cellulaires désagrégés.

* **Analyse du bottleneck et observation du MCS bloqué à 0 :** C'est l'atout scientifique majeur du projet. La démonstration que l'architecture monolithique atteint un MCS de 18-23 tandis que l'architecture *split* s'effondre à 0 sur un lien asynchrone permet d'étudier la tolérance des algorithmes d'adaptation de lien (*Link Adaptation*). Dans OAI, la fonction de sélection du MCS évalue le taux d'erreur bloc (BLER) généré par les HARQ NACK37. L'identification claire du lien de causalité entre la gigue du trafic GTP-U encapsulé, la famine du *buffer* MAC de la DU, et la dégradation mathématique du MCS constitue une **nouveauté forte**, sous réserve d'être étayée par des mesures statistiques précises et non de simples observations de logs.

### **Contribution expérimentale**

Les éléments expérimentaux relèvent de la métrologie, de la comparaison et de la validation d'hypothèses dans un environnement de test complexe.

* **Caractérisation des transports F1 hétérogènes :** Comparer Ethernet, Wi-Fi GRE et WireGuard sur 5G pour transporter l'interface F1 est une **nouveauté forte**. La littérature théorique postule des latences idéales, mais mesurer les débits réels (12 Mb/s sur Wi-Fi, 42 Mb/s via Quectel) offre un aperçu précieux des réalités du déploiement tactique. Cependant, cette contribution est actuellement **insuffisamment démontrée** car la validation requiert des conditions de canal radio isolées pour garantir que les chutes de débit proviennent du *backhaul/midhaul* et non d'interférences de la liaison d'accès.  
* **Portage de la DU sur Raspberry Pi 5 :** Il s'agit d'une **nouveauté partielle**. L'utilisation du Pi 5 pour la 5G a été documentée35. Toutefois, l'évaluation spécifique du couplage entre l'empreinte logicielle d'une DU OAI et un transport sans fil complexe sur ce matériel restreint apporte une valeur de *benchmark* additionnelle.

### **Contribution d'ingénierie**

Il s'agit ici de la conception, de l'intégration et du développement d'outils facilitant le fonctionnement du réseau.

* **Implémentation de PWS/SIB8 en architecture CU/DU :** L'adaptation du cheminement Write-Replace Warning via F1AP pour la configuration et la diffusion par la DU relève d'une **ingénierie de haut niveau**. Bien que le protocole soit standardisé4, sa réalisation pratique dans la pile OAI désagrégée est originale. Toutefois, ce développement **n'est pas publiable seul** dans un journal scientifique ; il s'apparente plutôt à une "Release Note" ou un correctif ouvert pour la communauté, bien qu'il enrichisse considérablement le récit d'un article de type *Testbed*.  
* **Séparation des chemins de données et validation du packet placement :** La configuration du routage pour s'assurer que le trafic F1 emprunte bien le modem Quectel et non l'accès USRP est un élément de résolution de problèmes (*troubleshooting*) **déjà connu** des ingénieurs réseau. C'est essentiel pour la validité du banc, mais dénué de portée académique.  
* **TUI opérateur et architecture de rollback :** Ce développement offre une **nouveauté forte** dans la sphère de l'outillage expérimental. La communauté peine souvent à reproduire les environnements 5G34 ; un tel outil est l'argument principal pour un *Artifact Paper*.

### **Contribution pédagogique ou de handoff**

* **Documentation technique et repository de déploiement :** Bien qu'indispensables pour la pérennité du projet au sein du laboratoire, ces éléments sont **intéressants mais non publiables** en l'état. Ils constituent cependant la preuve matérielle requise pour l'évaluation par les comités exigeant des badges de reproductibilité (ex. ACM Artifacts Evaluated).

## **5\. Évaluation des plus-values possibles**

Une analyse détaillée de chaque point soulevé par votre requête est nécessaire pour définir la stratégie de publication.

1. **CU/DU split OAI multi-machines reproductible :** C'est une excellente intégration système, mais ce n'est pas original dans la littérature, l'alliance OAI l'ayant déjà documenté et stabilisé5. Les preuves manquantes pour une publication résident dans l'automatisation stricte et la comparaison métrique.  
2. **Comparaison monolithique vs CU/DU split :** Bien que courant pour l'analyse des ressources CPU17, documenter l'écart massif de débit (150 Mb/s contre 20 Mb/s) est très intrigant. L'originalité viendra de l'explication mathématique de cette chute (overhead d'encapsulation GTP-U, délais de traitement, asynchronisme) plutôt que du simple constat.  
3. **Analyse du bottleneck entre monolithique et split :** C'est ici que réside la plus-value scientifique. Transformer ce point en contribution publiable nécessite de cartographier le temps de traitement d'un paquet depuis son ingestion UDP/SCTP jusqu'à sa soumission à la couche MAC.  
4. **Observation du MCS bloqué à 0 :** C'est l'observation clé. Dans OAI, le *scheduler* dégrade le MCS d'un niveau chaque fois que le taux de NACK (BLER) dépasse un seuil supérieur (généralement 15 %)37. Sur un lien *split*, si le flux F1-U (GTP-U) subit de la gigue, les données arrivent en décalage par rapport à la planification radio, provoquant des erreurs de décodage ou des trames vides, entraînant des NACK de l'UE et la chute irrémédiable du MCS. C'est original expérimentalement, mais les preuves manquent : il faut des captures Wireshark corrélées aux logs MAC (variables dl\_bler\_target\_upper, incréments HARQ).  
5. **Mesures MCS, NPRB, BLER, SNR, scheduler, F1, UPF/SMF :** Outils classiques de validation. La collecte automatisée est une très bonne pratique expérimentale, mais elle sert d'outil probatoire, pas de finalité scientifique.  
6. **Transport F1 via Ethernet :** L'établissement d'une référence (*baseline*) est indispensable à toute démarche expérimentale. Aucune originalité intrinsèque.  
7. **Transport F1 via Wi-Fi GRE :** L'utilisation de tunnels au-dessus du Wi-Fi pour le F1 est originale dans son implémentation OAI, révélant la sensibilité du standard à la gigue des accès déterministes dégradés.  
8. **Transport F1 via Quectel 5G \+ WireGuard :** Extrêmement original dans un contexte de publication expérimentale. L'encapsulation du GTP-U dans de l'UDP, lui-même chiffré dans WireGuard (UDP), transmis sur un réseau 5G public avec sa propre fragmentation (MTU) et ses politiques QoS, crée un environnement de latence hautement instable25. Les preuves manquantes sont des mesures A/B répétées en environnement isolé et une analyse de la fragmentation IP.  
9. **Séparation entre access radio USRP B210 et backhaul Quectel :** Simple condition *sine qua non* du bon fonctionnement du routage. Aucune originalité.  
10. **Validation packet placement :** Indispensable pour la rigueur du papier (prouver qu'on mesure le bon chemin), mais purement intégratif.  
11. **PWS/SIB8 en architecture CU/DU :** Très original dans le contexte de l'architecture désagrégée OAI. La littérature a récemment vu des alertes SIB8 en mode monolithique pour de la cybersécurité29, mais son routage via F1AP apporte une vraie plus-value d'ingénierie.  
12. **TUI opérateur et rollback reproductible :** La nouveauté est méthodologique. Cela transforme un projet technique local en un *testbed* prêt pour la communauté.  
13. **Portage DU vers Raspberry Pi 5 :** Le Pi 5 est populaire, mais la DU OAI étant computationnellement lourde, prouver qu'elle soutient un trafic (même à 12-40 Mb/s) tout en gérant le PWS est un démonstrateur de faisabilité solide, bien qu'empiétant sur le territoire de srsRAN (Pi5G)35.  
14. **Documentation complète de handoff :** Non scientifique, mais augmente considérablement les chances d'acceptation dans les tracks "Artifacts".  
15. **Architecture potentiellement portable ou drone-carried DU :** C'est le cas d'usage (*use-case*) qui englobe et donne un sens au papier. Vendre le projet comme un "nœud d'urgence déployable par drone (UAV)" justifie l'utilisation de liens *midhaul* dégradés et la nécessité du SIB838.

## **6\. Hypothèses de papier possibles**

Le travail peut être orienté selon plusieurs trajectoires de publication, dont deux se démarquent particulièrement.

### **Angle A — Reproducible OAI CU/DU split testbed**

Ce papier se focaliserait sur la méthodologie expérimentale : le banc d'essai, la gestion multi-machines, le TUI de configuration, et les *baselines* établies.

* *Niveau de nouveauté :* Faible d'un point de vue conceptuel 5G, mais modéré à fort en termes d'apport d'infrastructure de recherche.  
* *Contribution principale :* Un outil *open-source* clé en main réduisant la barrière d'entrée pour la recherche sur le *Cloud-RAN*.  
* *Résultats requis :* Preuves de fonctionnement (débits stables, captures d'écrans du TUI, scripts documentés).  
* *Venues possibles :* Pistes "Demos/Artifacts" (INFOCOM, MobiCom), ou journaux spécialisés en expérimentation (Computer Networks).  
* *Probabilité d'acceptation :* Modérée à haute. Les communautés manquent cruellement d'environnements reproductibles.

### **Angle B — Performance characterization of F1 transport over heterogeneous links**

Une analyse comparative rigoureuse des performances du F1 (Ethernet *vs* Wi-Fi GRE *vs* WG sur 5G).

* *Niveau de nouveauté :* Élevé. La caractérisation méticuleuse de la pénalité induite par le *midhaul* non idéal est une question d'actualité pour les déploiements tactiques24.  
* *Analyse à produire :* Corrélations croisées entre la latence, la gigue induite par WireGuard, la taille des paquets et la dégradation finale du débit radio (MCS, BLER).  
* *Limites méthodologiques :* Le risque de l'environnement "bureau" (*Over-The-Air*) faussant les mesures. Une cage de Faraday est impérative.

### **Angle C — Public Warning System / SIB8 over CU/DU split**

Centré sur la diffusion d'alertes via F1AP.

* *Niveau de nouveauté :* Modéré.  
* *Ce qui existe déjà :* Spécifications 3GPP claires4, et récentes implémentations SIB8 monolithiques29.  
* *Preuves nécessaires :* Traces F1AP complètes, validation de la décodabilité sur différents UEs commerciaux.  
* *Avenir de ce papier :* Trop spécifique et descriptif pour constituer un *full paper* de recherche. À fusionner comme cas d'usage applicatif.

### **Angle D — Portable or edge DU with wireless backhaul**

Focus sur le déploiement léger sur Pi 5\.

* *Réalisme :* Prouvé, mais la DU OAI saturera rapidement le processeur ARM, limitant les débits. SrsRAN a déjà établi des références sur cette architecture (Pi5G)35. Cet angle offre un récit attrayant (réseaux d'urgence) mais manque de profondeur fondamentale si présenté seul.

### **Angle E — Debugging and root-cause analysis of OAI CU/DU throughput bottlenecks**

Article d'investigation système sur la chute des performances dans les réseaux logiciels désagrégés.

* *Intérêt scientifique :* Très fort. Expliquer l'effondrement du MCS en décortiquant les interactions entre la pile réseau du système d'exploitation, les tampons UDP/SCTP, et le *scheduler* temps réel de la couche MAC.  
* *Instrumentation nécessaire :* Profiling logiciel (traceurs de noyau, tcpdump synchronisé, analyse du code source OAI de update\_bler\_stats() et nr\_dl\_mcs\_select\_default())37.

**Synthèse stratégique :** L'approche la plus percutante consiste à **fusionner l'Angle B et l'Angle E**. L'article présentera la caractérisation expérimentale des liaisons hétérogènes (Angle B) en révélant une dégradation inattendue, qui sera ensuite expliquée par une analyse de la cause racine au sein de l'architecture OAI (Angle E). L'Angle C (PWS) viendra illustrer la pertinence de ce banc pour les scénarios tactiques (Angle D) et le TUI (Angle A) garantira la validation "Artifact".

## **7\. Méthodologie expérimentale recommandée**

Pour qu'un manuscrit soit qualifié de "publication-grade" (particulièrement en fusionnant les Angles B et E), une rigueur absolue dans l'isolation des variables est exigée. Les observations de "runs historiques" sont insuffisantes.  
**Protocole indispensable :**

1. **Isolation de l'environnement RF :** C'est la condition absolue. Les tests *Over-The-Air* (OTA) en laboratoire sont soumis à des interférences qui influencent le SNR, et donc le BLER et le MCS11. Vous devez relier l'USRP et l'UE par câbles coaxiaux avec des atténuateurs fixes (ex. 60 dB) ou utiliser une cage de Faraday. Cela garantira que toute chute du MCS provient d'un retard de paquet F1-U, et non d'une fluctuation du canal radio.  
2. **Verrouillage logiciel et paramètres :**  
   * Utiliser rigoureusement le même *commit* OAI pour l'ensemble des essais.  
   * Maintenir statiques la bande de fréquence, l'espacement des sous-porteuses (SCS), le nombre de PRB (ex. 106 PRB pour 40 MHz) et la puissance d'émission TX.  
3. **Captures synchronisées et caractérisation du lien de transport :**  
   * Exécuter des sessions de test d'au moins 60 secondes (génération de trafic via iperf UDP saturant pour stresser le *buffer* de la DU).  
   * Capturer simultanément les trames réseau via tcpdump sur les interfaces F1-C (SCTP) et F1-U (UDP port 2152\) du côté CU et DU5.  
   * Mesurer l'impact de la fragmentation IP : les paquets GTP-U encapsulés dans WireGuard risquent de dépasser le MTU cellulaire, provoquant de la fragmentation et de la gigue additionnelle.  
4. **Analyse des logs MAC de la DU :**  
   * Écrire un script pour extraire l'évolution temporelle des variables critiques : dl\_mcs, nombre de NACK HARQ, dl\_bler, et tampons de transmission (NPRB alloués)37.  
5. **Répétabilité statistique :** Minimum 10 passages (runs) par configuration expérimentale pour extraire des médianes et des intervalles de confiance (génération de *boxplots*).  
6. **Cas d'usage SIB8 :** Capturer les traces Wireshark du trafic Paging et SIB1 indiquant la mise à jour des informations système, et documenter la réception effective du SIB8 sur l'UE (idéalement via les outils de diagnostic du modem ou via les messages d'alerte de l'OS du téléphone)29.

**Éléments utiles (mais secondaires) :** Mesures précises de la charge CPU/RAM du Raspberry Pi 5 (htop, sysstat) pour démontrer que la limite ne provient pas d'une saturation processeur, mais bien des délais réseau, ce qui appuiera la thèse de l'Angle E35.

## **8\. Risques et faiblesses**

Tout projet ambitieux comporte des biais qu'un comité de lecture détectera immanquablement. L'anticipation est la clé du succès.

| Risque identifié | Impact sur la publication | Stratégie de mitigation | Bloquant ? |
| :---- | :---- | :---- | :---- |
| **Bruit radio confondu avec le bottleneck réseau** | Critique. Les examinateurs rejetteront l'affirmation que le "midhaul" fait chuter le MCS si des interférences radio ne sont pas mathématiquement exclues. | Isolation totale (câbles coaxiaux, atténuateurs ou cage de Faraday). Preuve que le SNR est constant pendant que le MCS chute. | **OUI** |
| **Erreur de nomenclature (Backhaul vs Midhaul)** | Modéré. Le lien transportant F1 est du *midhaul*, et non du *backhaul* (qui relie le cœur de réseau à internet/autre)7. | Adopter la stricte terminologie 3GPP. Parler de transport F1 ou de *midhaul* hétérogène dans tout le texte. | Non (Sémantique) |
| **Généralisation insuffisante du "MCS \= 0"** | Élevé. Le phénomène peut être perçu comme un simple "bug d'implémentation OAI". | Remonter à l'algorithme générique : prouver que le *scheduler* subit une famine de données due à la gigue asynchrone, ce qui est une limite fondamentale de la désagrégation logicielle. | **OUI** |
| **Débits incohérents entre les runs** | Majeur. La disparité entre 12 Mb/s, 42 Mb/s et 150 Mb/s discrédite le banc s'il n'y a pas d'explication mesurée et répétable. | Fixer les problèmes de MTU du tunnel WireGuard25 et réaliser des moyennes statistiques sur 10 à 20 tests automatisés. | **OUI** |
| **Contribution perçue comme "trop intégrative"** | Élevé. Un empilement de technologies (Pi5 \+ OAI \+ WG \+ SIB8) peut ressembler à un rapport de stage d'ingénieur. | Concentrer l'introduction et la discussion de l'article sur la problématique de recherche (l'impact de la gigue sur la désagrégation RAN), et non sur les étapes d'installation. | **OUI** |
| **PWS/SIB8 jugé "hors sujet"** | Faible. Il risque de distraire du propos principal sur les performances. | Présenter le SIB8 brèvement comme la validation applicative démontrant la viabilité du banc pour des "Réseaux Tactiques Nomades". | Non |

## **9\. Recommandation de venues**

Le choix de la conférence ou du journal dictera le niveau de rigueur formelle à atteindre.

1. **Workshops IEEE/ACM (Hautement recommandé pour un succès rapide) :**  
   * **ACM WiNTECH** (Workshop on Wireless Network Testbeds, Experimental evaluation & CHaracterization) : Conçu spécifiquement pour ce type de travaux, valorisant l'ingénierie des bancs d'essai (TUI, *rollback*, OAI *split*).  
   * **IEEE INFOCOM CNERT** (Computer and Networking Experimental Research using Testbeds) : Venue de choix pour des évaluations de protocoles (WireGuard, GRE) sur des implémentations *open-source*.  
2. **Conférences techniques orientées systèmes et communications :**  
   * **IEEE VTC (Vehicular Technology Conference)** : La session *Radio Access Technology and Heterogeneous Networks* est très réceptive aux études de cas sur les déploiements 5G non idéaux. Le récent article sur le *spoofing* SIB8 y a d'ailleurs été publié45.  
   * **IEEE NFV-SDN :** Une excellente cible pour explorer les limites logicielles de la désagrégation O-RAN (le *bottleneck* MAC)8.  
3. **Demos et Artifact Tracks :**  
   * Si le temps manque pour parfaire la modélisation statistique de la cause racine, soumettez l'environnement (Scripts, TUI, SIB8) à la section **Demo de MobiCom ou MobiSys**.

## **10\. Recommandation finale**

**Ma recommandation ferme est de publier après compléments expérimentaux, en visant un article académique (Workshop ou Conférence type VTC/WiNTECH) combinant la caractérisation du transport et l'analyse de cause racine (Angles B \+ E).**  
Ne publiez pas immédiatement un *full paper* : dans son état actuel, votre travail est une réussite d'ingénierie exceptionnelle, mais les résultats empiriques ("MCS parfois bloqué à 0", "environ 42 Mb/s observés") manquent du blindage méthodologique exigé par l'évaluation par les pairs (isolation RF, répétabilité statistique, traçage logiciel).  
La stratégie optimale consiste à prendre quelques semaines pour asseoir la rigueur expérimentale via des câbles coaxiaux et de l'automatisation. Une fois l'origine du blocage du MCS démontrée formellement (désynchronisation entre les délais de la couche F1-U et la boucle de contrôle HARQ de la couche MAC), votre effort d'intégration basculera en une contribution scientifique inattaquable sur les vulnérabilités de la désagrégation RAN face aux transports "non idéaux". En parallèle, le TUI et l'intégration PWS/SIB8 vous assureront une forte reconnaissance technique pour la mise à disposition de code (Artifacts).

## **11\. Plan d'action sur 2 à 4 semaines**

Ce plan opérationnel est conçu pour structurer votre discussion avec votre professeur et encadrer la finalisation du travail.  
**Titre provisoire :** *Performance Bottlenecks and Root-Cause Analysis in Disaggregated 5G NR Networks over Heterogeneous Non-Ideal Midhaul Links*  
**Abstract provisoire :** L'architecture 5G désagrégée offre une grande flexibilité via l'interface F1, séparant les fonctions centralisées (CU) et distribuées (DU). Néanmoins, le déploiement de nœuds nomades contraints s'appuie fréquemment sur des liaisons de transport (*midhaul*) hétérogènes et non idéales, telles que des tunnels VPN superposés à des réseaux commerciaux. Ce travail présente un banc d'essai expérimental, outillé et reproductible, basé sur OpenAirInterface, pour évaluer l'impact de ces transports (Ethernet, Wi-Fi GRE, WireGuard sur 5G) sur les couches radio. Nos expérimentations révèlent une dégradation sévère et récurrente des débits (effondrement du MCS), indépendante du canal radio. En menant une analyse croisée des traces de trafic F1-U et des journaux d'ordonnancement MAC, nous démontrons comment la gigue asynchrone du transport engendre une famine de données, exacerbant artificiellement le calcul du taux d'erreur (BLER) et forçant l'algorithme d'adaptation de lien à réduire le MCS. Enfin, l'intégration complète du protocole F1AP pour la diffusion d'alertes publiques (PWS/SIB8) confirme l'opérabilité de ce banc pour l'évaluation de réseaux d'urgence tactiques.

### **Semaine 1 : Verrouillage méthodologique et Isolation**

* **Action :** Basculer d'une transmission par antennes à une liaison par câbles coaxiaux équipés d'atténuateurs RF (ou une cage de Faraday) pour figer le SNR/CQI.  
* **Action :** Fixer les paramètres OAI (un seul commit Git, bande passante, PRB, puissance).  
* **Décision :** Valider avec le professeur la disponibilité matérielle pour l'isolation RF.

### **Semaine 2 : Collecte massive et automatisée (Les "Runs")**

* **Action :** Utiliser le TUI pour automatiser des campagnes de 10 à 20 tests iperf de 60 secondes pour chaque topologie (Monolithique, Ethernet *split*, Wi-Fi GRE *split*, Quectel/WireGuard *split*).  
* **Action :** Mettre en place un script exécutant tcpdump sur le trafic UDP 2152 (GTP-U) et extrayant simultanément les compteurs de NACK, le BLER et le dl\_mcs dans les logs de la DU.  
* **Action :** Archiver les PCAPs pour identifier d'éventuelles fragmentations dues au MTU du tunnel WireGuard.

### **Semaine 3 : Traitement des données et Root-Cause Analysis**

* **Action :** Générer les représentations graphiques : diagrammes en boîte (boxplots) de distribution des débits ; graphiques temporels croisant l'évolution de la gigue F1-U (en millisecondes) avec la valeur du MCS et du BLER.  
* **Action :** Isoler le moment exact où le système dégrade le dl\_mcs en dessous d'un seuil critique en raison de l'absence de données prêtes au niveau RLC causée par la gigue du transport.

### **Semaine 4 : Rédaction du manuscrit (Format IEEE 6 pages)**

* **Structure cible :**  
  * *I. Introduction* (Contexte de la désagrégation, nécessité de *midhauls* tactiques et d'alertes PWS).  
  * *II. Architecture Expérimentale* (OAI, Pi 5, TUI, intégration de la signalisation Write-Replace Warning pour le SIB8 via F1AP).  
  * *III. Méthodologie et Métriques* (Détail de l'isolation RF et des scénarios de transport).  
  * *IV. Évaluation des Performances* (Comparaison factuelle des débits Ethernet / GRE / WG).  
  * *V. Analyse des Goulots d'Étranglement* (Explication détaillée de la chute du MCS causée par le *starvation* de la couche MAC).  
  * *VI. Conclusion & Reproductibilité*.  
* **Checklist "Ready to Submit" :** Dépôt GitHub nettoyé contenant les configurations TUI, figures vectorisées, et validation finale par le professeur de la conférence cible (ex. WiNTECH).

#### **Sources des citations**

1. Open Midhaul F1 interface: F1-C and F 1-U | TELCOMA Global, [https://www.telcomaglobal.com/p/open-midhaul-f1-interface](https://www.telcomaglobal.com/p/open-midhaul-f1-interface)  
2. Integrated access and backhaul: new option for 5G \- Ericsson, [https://www.ericsson.com/en/reports-and-papers/ericsson-technology-review/articles/introducing-integrated-access-and-backhaul](https://www.ericsson.com/en/reports-and-papers/ericsson-technology-review/articles/introducing-integrated-access-and-backhaul)  
3. Integrated Access and Backhaul: A New Type of Wireless Backhaul in 5G \- Frontiers, [https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636949/full](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.636949/full)  
4. Open Midhaul F1 Interface F1-C and F1-U \- Techplayon, [https://www.techplayon.com/open-midhaul-f1-interface-f1-u-and-f1-c/](https://www.techplayon.com/open-midhaul-f1-interface-f1-u-and-f1-c/)  
5. openairinterface5g/doc/F1AP/F1-design.md at develop \- GitHub, [https://github.com/OPENAIRINTERFACE/openairinterface5g/blob/develop/doc/F1AP/F1-design.md](https://github.com/OPENAIRINTERFACE/openairinterface5g/blob/develop/doc/F1AP/F1-design.md)  
6. OpenAirInterface RAN Roadmap, [https://openairinterface.org/wp-content/uploads/2022/07/2022-07-12-EURECOM-RAN-SLIDES.pdf](https://openairinterface.org/wp-content/uploads/2022/07/2022-07-12-EURECOM-RAN-SLIDES.pdf)  
7. Spotlight on 5G midhaul networks \- Ciena, [https://www.ciena.com/insights/articles/spotlight-on-5g-midhaul-networks.html](https://www.ciena.com/insights/articles/spotlight-on-5g-midhaul-networks.html)  
8. Ultra-low Latency NFV Services Using DPDK \- Scuola Superiore Sant'Anna, [https://retis.santannapisa.it/\~tommaso/publications/IEEE-NFVSDN-2021.pdf](https://retis.santannapisa.it/~tommaso/publications/IEEE-NFVSDN-2021.pdf)  
9. OAI 5G gNB/DU/CU/CU-CP \- Red Hat Ecosystem Catalog, [https://catalog.redhat.com/en/solutions/detail/6572db16cb83472580a054fce0c26713](https://catalog.redhat.com/en/solutions/detail/6572db16cb83472580a054fce0c26713)  
10. OpenAirInterface (OAI) Framework \- Emergent Mind, [https://www.emergentmind.com/topics/openairinterface-oai](https://www.emergentmind.com/topics/openairinterface-oai)  
11. openairinterface5g/doc/FEATURE\_SET.md at develop \- GitHub, [https://github.com/OPENAIRINTERFACE/openairinterface5g/blob/develop/doc/FEATURE\_SET.md](https://github.com/OPENAIRINTERFACE/openairinterface5g/blob/develop/doc/FEATURE_SET.md)  
12. Overview of F1 and E1 and F1 handover \- Webinar Chapter 12 \- OpenAirInterface, [https://openairinterface.org/wp-content/uploads/2025/10/OAI-Webinar-Series-Chapter-12-slides.pdf](https://openairinterface.org/wp-content/uploads/2025/10/OAI-Webinar-Series-Chapter-12-slides.pdf)  
13. srsRAN Project \- Open Source RAN, [https://www.srslte.com/](https://www.srslte.com/)  
14. srsRAN gNB Handover, [https://docs.srsran.com/projects/project/en/latest/tutorials/source/handover/source/index.html](https://docs.srsran.com/projects/project/en/latest/tutorials/source/handover/source/index.html)  
15. Experimental comparison of 5G SDR platforms: srsRAN x OpenAirInterface \- arXiv, [https://arxiv.org/html/2406.01485v1](https://arxiv.org/html/2406.01485v1)  
16. Performance Analysis and Comparison of Full-Fledged 5G Standalone Experimental TDD Testbeds in Single & Multi-UE Scenarios \- arXiv, [https://arxiv.org/html/2407.02341v1](https://arxiv.org/html/2407.02341v1)  
17. Performance Characterization of dApps in Open Radio Access Networks \- arXiv, [https://arxiv.org/html/2605.05426v1](https://arxiv.org/html/2605.05426v1)  
18. An Open, Programmable, Multi-vendor 5G O-RAN Testbed with NVIDIA ARC and OpenAirInterface \- Electrical and Computer Engineering, [https://ece.northeastern.edu/fac-ece/dkoutsonikolas/publications/ngopera.pdf](https://ece.northeastern.edu/fac-ece/dkoutsonikolas/publications/ngopera.pdf)  
19. Exploratory Study of CPU–GPU Frequency Interactions and Throughput Stability in GPU-Accelerated 5G O-RAN \- Northeastern University, [https://ece.northeastern.edu/fac-ece/dkoutsonikolas/publications/ngopera26.pdf](https://ece.northeastern.edu/fac-ece/dkoutsonikolas/publications/ngopera26.pdf)  
20. Integrated Access and Backhaul \- Samsung, [https://images.samsung.com/is/content/samsung/p5/global/business/networks/insights/white-paper/integrated-access-and-backhaul/200603B\_Intergrated\_Acccess\_and\_Backhaul.pdf](https://images.samsung.com/is/content/samsung/p5/global/business/networks/insights/white-paper/integrated-access-and-backhaul/200603B_Intergrated_Acccess_and_Backhaul.pdf)  
21. A Survey on Integrated Access and Backhaul Networks \- Frontiers, [https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.647284/full](https://www.frontiersin.org/journals/communications-and-networks/articles/10.3389/frcmn.2021.647284/full)  
22. Integrated Access and Backhaul (IAB) in 5G \- NXG Connect, [https://www.nxgconnect.com/post/integrated-access-and-backhaul-iab-in-5g](https://www.nxgconnect.com/post/integrated-access-and-backhaul-iab-in-5g)  
23. Integrated Access and Backhaul in 5G with Aerial Distributed Unit using OpenAirInterface, [https://arxiv.org/html/2305.05983v3](https://arxiv.org/html/2305.05983v3)  
24. On-demand 5G Private Networks using a Mobile Cell \- arXiv, [https://arxiv.org/pdf/2411.06597](https://arxiv.org/pdf/2411.06597)  
25. Exploring the Performance of Transparent 5G NTN Architectures Based on Operational Mega-Constellations \- MDPI, [https://www.mdpi.com/2673-8732/5/3/25](https://www.mdpi.com/2673-8732/5/3/25)  
26. 4G and 5G Radio Access Network (RAN) Security | Fortinet, [https://www.fortinet.com/content/dam/fortinet/assets/white-papers/wp-4g-5g-radio-access-network-security.pdf](https://www.fortinet.com/content/dam/fortinet/assets/white-papers/wp-4g-5g-radio-access-network-security.pdf)  
27. WO2024263321A1 \- Distributed network stack using an overlay network \- Google Patents, [https://patents.google.com/patent/WO2024263321A1/en](https://patents.google.com/patent/WO2024263321A1/en)  
28. 5G NR System Information Block Type 8 \-SIB8 \- RRC Signalling \- Techplayon, [https://www.techplayon.com/5g-nr-system-information-block-type-8-sib8/](https://www.techplayon.com/5g-nr-system-information-block-type-8-sib8/)  
29. From Spoofing to Trust: Emergency Alerts Spoofing Testbed and Cross-Cell Verification \- arXiv, [https://arxiv.org/html/2604.24404v1](https://arxiv.org/html/2604.24404v1)  
30. ETSI TS 138 473 V17.15.0 (2026-04) \- iTeh Standards, [https://cdn.standards.iteh.ai/samples/etsi/etsi-ts-138-473-v17-15-0-2026-04-/a14bd6f7b4724477b2b4862f4653702c/etsi-ts-138-473-v17-15-0-2026-04-.pdf](https://cdn.standards.iteh.ai/samples/etsi/etsi-ts-138-473-v17-15-0-2026-04-/a14bd6f7b4724477b2b4862f4653702c/etsi-ts-138-473-v17-15-0-2026-04-.pdf)  
31. 5G F1AP Messages – Complete CU-DU Message List & Procedures \- 3GLTEInfo, [https://www.3glteinfo.com/messages/5g/f1ap/](https://www.3glteinfo.com/messages/5g/f1ap/)  
32. NMS interface for OAI gNB and SIB8 configuration. \- ResearchGate, [https://www.researchgate.net/figure/NMS-interface-for-OAI-gNB-and-SIB8-configuration\_fig3\_404248677](https://www.researchgate.net/figure/NMS-interface-for-OAI-gNB-and-SIB8-configuration_fig3_404248677)  
33. O-RAN-Testbed-Automation/OpenAirInterface\_Testbed/README.md at main \- GitHub, [https://github.com/usnistgov/O-RAN-Testbed-Automation/blob/main/OpenAirInterface\_Testbed/README.md](https://github.com/usnistgov/O-RAN-Testbed-Automation/blob/main/OpenAirInterface_Testbed/README.md)  
34. Automating the Deployment of 5G Testbeds Across Diverse Open-Source Software Stacks \- National Institute of Standards and Technology, [https://tsapps.nist.gov/publication/get\_pdf.cfm?pub\_id=960654](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=960654)  
35. Pi5G: A lightweight 5G Testbed on a Raspberry Pi5 \- ResearchGate, [https://www.researchgate.net/publication/404659481\_Pi5G\_A\_lightweight\_5G\_Testbed\_on\_a\_Raspberry\_Pi5](https://www.researchgate.net/publication/404659481_Pi5G_A_lightweight_5G_Testbed_on_a_Raspberry_Pi5)  
36. From Spoofing to Trust: Emergency Alerts Spoofing Testbed and Cross-Cell Verification \- ResearchGate, [https://www.researchgate.net/publication/404248677\_From\_Spoofing\_to\_Trust\_Emergency\_Alerts\_Spoofing\_Testbed\_and\_Cross-Cell\_Verification](https://www.researchgate.net/publication/404248677_From_Spoofing_to_Trust_Emergency_Alerts_Spoofing_Testbed_and_Cross-Cell_Verification)  
37. openairinterface5g/doc/MAC/mac-usage.md at develop \- GitHub, [https://github.com/OPENAIRINTERFACE/openairinterface5g/blob/develop/doc/MAC/mac-usage.md](https://github.com/OPENAIRINTERFACE/openairinterface5g/blob/develop/doc/MAC/mac-usage.md)  
38. (PDF) Modular Design and Experimental Evaluation of 5G Mobile Cell Architectures Based on Overlay and Integrated Models \- ResearchGate, [https://www.researchgate.net/publication/394397570\_Modular\_Design\_and\_Experimental\_Evaluation\_of\_5G\_Mobile\_Cell\_Architectures\_Based\_on\_Overlay\_and\_Integrated\_Models](https://www.researchgate.net/publication/394397570_Modular_Design_and_Experimental_Evaluation_of_5G_Mobile_Cell_Architectures_Based_on_Overlay_and_Integrated_Models)  
39. You have been warned: Abusing 5G's Warning and Emergency Systems \- ResearchGate, [https://www.researchgate.net/publication/366017540\_You\_have\_been\_warned\_Abusing\_5G's\_Warning\_and\_Emergency\_Systems](https://www.researchgate.net/publication/366017540_You_have_been_warned_Abusing_5G's_Warning_and_Emergency_Systems)  
40. From Concept to Reality: 5G Positioning with UL-TDoA in OpenAirInterface \- ResearchGate, [https://www.researchgate.net/publication/395633861\_From\_Concept\_to\_Reality\_5G\_Positioning\_with\_UL-TDoA\_in\_OpenAirInterface](https://www.researchgate.net/publication/395633861_From_Concept_to_Reality_5G_Positioning_with_UL-TDoA_in_OpenAirInterface)  
41. OAI RAN \- OpenAirInterface, [https://openairinterface.org/ran/](https://openairinterface.org/ran/)  
42. Exploring the 5G RAN, [https://witestlab.poly.edu/blog/exploring-the-5g-ran/](https://witestlab.poly.edu/blog/exploring-the-5g-ran/)  
43. OpenAirInterface | Request PDF \- ResearchGate, [https://www.researchgate.net/publication/286244586\_OpenAirInterface](https://www.researchgate.net/publication/286244586_OpenAirInterface)  
44. Use Case and Reference Architecture \- Juniper Networks, [https://www.juniper.net/documentation/us/en/software/jvd/jvd-5g-xhaul-sr-01-02/use\_case\_and\_reference\_architecture.html](https://www.juniper.net/documentation/us/en/software/jvd/jvd-5g-xhaul-sr-01-02/use_case_and_reference_architecture.html)  
45. \[2604.24404\] From Spoofing to Trust: Emergency Alerts Spoofing Testbed and Cross-Cell Verification \- arXiv, [https://arxiv.org/abs/2604.24404](https://arxiv.org/abs/2604.24404)
