# Évaluation critique de la valeur scientifique et de la publiabilité de votre projet OAI CU/DU F1 PWS

## Résumé exécutif

**Conclusion directe.** Je ne recommande **pas** une soumission immédiate en **full paper académique**. En l’état, le projet paraît **solide en ingénierie**, **prometteur en expérimentation**, mais **insuffisamment verrouillé scientifiquement** pour soutenir une thèse forte et généralisable. Votre dossier montre un banc d’essai OAI 5G NR multi-machines, un split CU/DU opérationnel, plusieurs transports F1, une adaptation PWS/SIB8 côté split, des outillages de déploiement et des mesures radio/réseau déjà non triviales. Mais les résultats restent encore trop hétérogènes, le goulot d’étranglement n’est pas expliqué de façon causale, et la partie PWS doit être normalisée par rapport au chemin 3GPP exact et validée de bout en bout sur UE. fileciteturn0file0 citeturn22academia2turn22academia3turn37academia2turn37academia1

| Verdict | Évaluation |
|---|---|
| Publication recommandée maintenant | **Non** pour un full paper |
| Maturité actuelle | **Moyenne** en expérimentation, **élevée** en intégration, **moyenne-faible** en contribution scientifique |
| Type de publication le plus réaliste | **Workshop**, **démo**, ou **papier orienté reproducibility/open-source testbed** |
| Contribution principale la plus défendable | **Banc d’essai OAI CU/DU reproductible avec transports F1 hétérogènes et instrumentation fine**, éventuellement complété par un **warning path compatible split** si la validation 3GPP/OAI est clarifiée |
| Conditions minimales avant soumission | **A/B contrôlés**, commit OAI figé, répétitions statistiques, captures F1/F1-U/WireGuard, preuve du chemin PWS sur UE, et either **root cause** du bottleneck or **caractérisation robuste** avec limites explicites |

La bonne lecture critique est la suivante. Votre projet **n’est pas “simplement un TP”**. Il dépasse le montage standard par sa reproductibilité, son outillage opérateur, sa séparation accès/backhaul, ses scénarios multi-transport et sa collecte de métriques. En revanche, **ce n’est pas encore une contribution scientifique nette** au sens où les meilleurs papiers OAI récents formulent une revendication précise du type *première implémentation open-source de X*, *première validation over-the-air de Y* ou *méthode généralisable produisant un insight reproductible*, avec validation contrôlée et souvent publication de code ou de dataset. C’est exactement le profil des travaux OAI récents sur l’UL-TDoA, les testbeds de positionnement, le MU-MIMO split, ou encore le testbed d’alertes d’urgence sur OAI. citeturn22academia2turn22academia3turn37academia2turn37academia1turn36academia2

**Ma recommandation ferme** est donc la suivante : **transformer le travail en papier de testbed reproductible / artifact-oriented, avec une soumission workshop ou démo comme cible prioritaire**, et ne viser un article plus ambitieux qu’après une campagne expérimentale courte mais rigoureuse. Le meilleur angle aujourd’hui n’est pas “nous avons branché beaucoup de choses”, mais plutôt “nous avons construit un banc OAI split reproductible qui permet de caractériser l’impact de transports F1 hétérogènes et d’exposer les pièges méthodologiques, tout en montrant la faisabilité d’un chemin d’alerte compatible split”. citeturn39academia0turn39academia2turn39academia3turn40academia0

## Ce que montre l’état de l’art

### CU/DU split et interface F1

La littérature récente traite le CU/DU split comme un composant normal de la désagrégation RAN, particulièrement dans l’écosystème O-RAN et les plateformes ouvertes. Les questions de placement, de capacité de transport, de latence, de virtualisation et de sémantique d’exécution y sont centrales. Les travaux sur le choix dynamique du split et sur les transport networks entre CU et DU montrent bien que le lien CU/DU ne doit pas être vu comme un détail de plumbing, mais comme une variable expérimentale à part entière. Dans le même esprit, des travaux récents sur les plateformes ouvertes soulignent que la fidélité temporelle, le transport, l’I/O et la sémantique d’exécution doivent être documentés comme variables de premier ordre lorsqu’on évalue des systèmes 5G désagrégés. citeturn24academia1turn42academia3turn39academia0turn39academia3

Point important pour votre projet : vos chiffres historiques — environ 150 Mb/s en monolithique contre environ 19–23 Mb/s en split Ethernet avec SIB8, puis 12 Mb/s en Wi‑Fi GRE, alors que des runs plus récents avec Quectel/WireGuard remontent vers ~42 Mb/s et des MCS parfois élevés — suggèrent fortement que le problème observé n’est **pas** la simple existence du split, mais probablement une combinaison de version logicielle, chemin de transport, scheduler, configuration radio ou instrumentation imparfaite. Autrement dit, votre sujet intéressant n’est pas “le split est lent”, mais “dans quelles conditions le split OAI s’effondre, et pourquoi”. Cette reformulation est beaucoup plus scientifique. fileciteturn0file0 citeturn37academia2turn39academia2turn39academia0

### OpenAirInterface et plateformes 5G open-source

OAI est aujourd’hui une plateforme de recherche large, couvrant RAN, core et outillage OAM, avec une logique CI/CD et des usages de recherche qui vont de la radio expérimentale au positionnement, à l’O-RAN, à la sécurité, jusqu’aux démonstrateurs 6G. Les contributions publiables dans cet écosystème ont un trait commun : elles ne se limitent pas à faire fonctionner OAI, elles **ajoutent une primitive nouvelle** ou **produisent une caractérisation reproductible qui devient réutilisable par d’autres**. C’est le cas de l’implémentation UL‑TDoA dans OAI, du testbed de positionnement qui publie des datasets, du MU‑MIMO downlink en architecture split, ou encore du travail récent sur les alertes d’urgence spoofées dans OAI. Côté srsRAN/O-RAN SC, des testbeds over-the-air avec SDRs et UEs commerciaux sont eux aussi déjà publiés. citeturn36academia2turn22academia2turn22academia3turn37academia2turn37academia1turn42academia0

La conséquence pour votre décision de publication est simple. **Une intégration réussie d’OAI n’est pas, en soi, une contribution scientifique.** Elle devient publiable lorsqu’elle apporte au moins un de ces trois éléments : une nouveauté fonctionnelle bien circonscrite, une méthodologie expérimentale réutilisable, ou un diagnostic causal transférable à d’autres équipes. Votre projet coche déjà partiellement les deux derniers, mais pas encore de manière assez propre pour une soumission ambitieuse. citeturn22academia2turn22academia3turn37academia2turn39academia0

### Wireless F1, midhaul et backhaul hétérogènes

Le corpus consulté montre bien que le transport **sans fil** entre éléments désagrégés est un vrai sujet de recherche. On trouve par exemple un travail OAI sur un **DU aérien** à backhaul radio conforme F1AP, et un travail récent étudiant la faisabilité de l’option 2 sur **liaisons midhaul THz** à 140 GHz. On trouve aussi des évaluations réalistes de **WireGuard** dans des déploiements Open RAN industriels, avec un overhead faible sur débit, latence et CPU lorsque bien configuré. En revanche, dans les sources examinées, je n’ai pas trouvé de papier centré explicitement sur **F1 sur Wi‑Fi GRE** ni sur **F1 sur modem 5G commercial + WireGuard** avec OAI. Cela ne prouve pas une unicité absolue, mais cela suggère que votre combinaison expérimentale est **au moins peu documentée publiquement**. citeturn39academia2turn39academia3turn40academia0turn40academia1

C’est une bonne nouvelle, avec une nuance lourde. La rareté d’un scénario de transport **n’équivaut pas** à une contribution scientifique. Si votre papier dit seulement “nous avons fait passer F1 sur Wi‑Fi et sur modem 5G”, ce sera perçu comme de la bonne intégration. Si au contraire il démontre, par répétitions et captures synchronisées, **comment** la latence, le jitter, la perte, l’encapsulation GRE/WireGuard, le scheduler et le MCS interagissent, alors vous basculez dans la caractérisation expérimentale crédible. Votre idée de **packet placement** et de validation du chemin exact est ici très forte, précisément parce que des travaux récents insistent sur le fait que les “sémantiques de transport” doivent être rapportées explicitement. citeturn39academia0turn40academia0turn39academia2

### PWS, SIB8 et architecture split

Sur le plan applicatif, le sujet **n’est pas marginal**. La diffusion cellulaire d’alertes publiques est un service 3GPP bien réel, porté par la logique PWS/Cell Broadcast, et en 5G le chemin implique le core et le gNB ; en France, FR‑Alert est opérationnel sur la base de cette famille de mécanismes. Par ailleurs, un préprint de 2026 montre déjà qu’OAI peut être modifié pour implémenter un **testbed open-source d’alertes d’urgence 5G**, avec étude du comportement des smartphones et proposition de défense. Donc, “PWS sur OAI” n’est plus un angle vierge. citeturn33search1turn35search1turn37academia1

En revanche, dans les sources revues, je n’ai pas trouvé de papier centré explicitement sur **l’acheminement d’un warning path via une architecture OAI CU/DU split avec F1**. C’est un point potentiellement intéressant pour vous. Mais il y a une exigence immédiate : votre papier devra **normaliser précisément la terminologie**. Aujourd’hui, l’étiquette “PWS/SIB8” est trop floue pour un lectorat académique. Il faudra dire exactement quelle primitive 3GPP est visée, comment elle est mappée côté OAI, quel message est préparé par le CU, comment il est transféré au DU, comment il est schedulé, et quel comportement UE est observé. Sans cette cartographie normative, la nouveauté perçue restera fragile. citeturn33search1turn17search1turn37academia1

## Tableau comparatif des travaux proches

Le tableau ci-dessous ne prétend pas être exhaustif. Il synthétise les travaux **les plus proches** du périmètre de votre projet dans le corpus consulté.

| Référence / projet | Année | Plateforme | SDR utilisé | OAI utilisé | CU/DU split réel | F1 étudié explicitement | Transport F1 / midhaul | Wireless F1 ou backhaul testé | PWS / alertes étudié | Débit mesuré | Scheduler / MCS / BLER / SNR | Reproductibilité / code public | Différence principale avec votre projet | Proximité |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Integrated Access and Backhaul in 5G with Aerial Distributed Unit using OAI** citeturn39academia2 | 2023 | OAI + UE commercial | n.c. | Oui | Oui | Oui, F1AP | Backhaul radio pour DU aérien | Oui | Non | Oui | n.c. | n.c. | Très proche sur DU déporté et transport radio, mais pas focalisé sur Wi‑Fi GRE / modem 5G commercial ni sur PWS | Fort |
| **From Concept to Reality: UL‑TDoA in OAI** citeturn22academia2 | 2024 | OAI RAN + CN | O-RAN-based localization testbed | Oui | Oui ou multi-nœuds testbed | Interfaces 3GPP intégrées | n.c. | n.c. | Non | Validation fonctionnelle | n.c. | Oui, implémentation open-source annoncée | Montre le niveau de preuve attendu pour une nouvelle fonction OAI | Moyen |
| **Experimental Insights from OAI 5G Positioning Testbeds** citeturn22academia3 | 2025 | OAI testbeds | O-RAN RUs | Oui | Oui / multi-testbeds | n.c. | n.c. | Oui, environnements indoor/outdoor | Non | non central | Oui | Dataset public | Très proche sur l’esprit “testbed expérimental réutilisable” | Moyen |
| **MU‑MIMO Downlink for O‑RAN 5G NR using OAI** citeturn37academia2 | 2025 | OAI + 5GC + UEs | n.c. | Oui | Oui | Oui, split O‑RAN/CU‑DU | n.c. | n.c. | Non | Oui | BLER et SNR explicitement dans l’abstract | n.c. | Montre qu’un papier split OAI devient fort quand il apporte une primitive nouvelle clairement revendiquée | Fort |
| **Inter‑DU Load Balancing in Experimental O‑RAN** citeturn42academia0 | 2025 | srsRAN + O‑RAN SC + Open5GS | SDRs | Non | Oui | Interfaces O‑RAN/E2 plus que F1 | n.c. | OTA | Non | non central | Métriques réseau / charge | stack open-source | Comparable sur l’angle testbed OTA reproductible, pas sur PWS ni transports F1 hétérogènes | Moyen |
| **Emergency Alerts Spoofing Testbed and Cross-Cell Verification** citeturn37academia1 | 2026 | OAI RAN modifié | SDR | Oui | n.c. | Non indiqué | n.c. | OTA | **Oui** | N/A | Comportement smartphones | Open-source annoncé | Le plus proche de votre thème PWS, mais angle sécurité et non split/F1 | Fort |
| **AtlasRAN** citeturn39academia0 | 2026 | Cadre d’évaluation O‑RAN | n.c. | s’appuie sur plateformes ouvertes | Oui, comme dimension d’évaluation | Non | Transport vu comme variable de premier ordre | Oui, infrastructures ubiquitaires | Non | Goodput étudié | Oui, au moins en partie | cadre méthodologique | Très utile pour justifier votre insistance sur packet placement, timing et artefacts de mesure | Moyen |
| **Preliminary Assessment of Midhaul Links at 140 GHz** citeturn39academia3 | 2026 | Étude ray-tracing | Non | Non | Oui, option 2 | Oui, midhaul CU‑DU | 140 GHz | Oui | Non | Débit supportable estimé | n.c. | non | Proche sur la question “wireless transport for option 2”, mais sans testbed OAI réel | Moyen |

**Lecture rapide.** Votre projet est **très proche** de trois axes déjà visibles dans la littérature : **testbeds OAI réels**, **DU déporté/backhaul radio**, et **alertes publiques sur OAI**. Sa niche propre n’apparaît pas naturellement comme “faire du split OAI”, car cela existe déjà ; elle apparaît plutôt comme la combinaison **reproductibilité + transports F1 hétérogènes + instrumentation causale + warning path compatible split**. C’est cette combinaison qu’il faut défendre. fileciteturn0file0 citeturn39academia2turn37academia1turn39academia0

## Ce que votre projet apporte réellement

### Classification générale des contributions

| Catégorie | Ce que vous avez | Évaluation |
|---|---|---|
| Contribution scientifique potentielle | Analyse causale d’un effondrement de débit split, interaction transport–scheduler–MCS, éventuelle formalisation d’un warning path compatible split | **Possible**, mais **pas encore démontré** |
| Contribution expérimentale | Comparaison monolithique / split Ethernet / Wi‑Fi GRE / Quectel+WireGuard, métriques radio et réseau, packet placement | **Réelle** et **prometteuse** |
| Contribution d’ingénierie | Déploiement multi-machines OAI, TUI opérateur, rollback, documentation, repo de handoff, séparation accès/backhaul, Pi 5 | **Forte** |
| Contribution pédagogique / handoff | Documentation complète, scénarios reproductibles, outillage d’exploitation | **Très forte**, mais **peu publiable seule** |

Le point décisif est le suivant. **Votre projet a déjà une valeur élevée comme infrastructure de recherche.** Là où il manque encore un cran, c’est dans la transformation de cette infrastructure en **connaissance transférable**. Pour passer le seuil, il faut qu’un lecteur extérieur apprenne quelque chose de général sur OAI split, F1 transporté sur des liens hétérogènes, ou l’intégration d’alertes en architecture split — pas seulement qu’il voie que votre setup fonctionne chez vous. fileciteturn0file0 citeturn22academia2turn37academia2turn39academia0

### Évaluation point par point des plus-values possibles

| Élément | Originalité dans la littérature | Originalité dans OAI | Verdict critique | Preuves manquantes | Comment le rendre publiable |
|---|---|---|---|---|---|
| CU/DU split OAI multi-machines reproductible | Faible à moyenne | Moyenne | **Bonne intégration**, forte valeur artifact | script clean-room, manifest matériel, versions figées, replay complet | En faire un **testbed paper** ou annexe artifact |
| Comparaison monolithique vs split | Faible | Faible à moyenne | **Baseline nécessaire**, pas un papier à elle seule | A/B strictement contrôlé | L’utiliser comme figure de référence, pas comme claim principal |
| Analyse du bottleneck monolithique vs split | Moyenne à forte | Moyenne à forte | **Le point le plus publiable** si causal | root cause robuste, runs répétés, traces corrélées | Faire un papier “performance pathology” |
| MCS bloqué à 0 dans certains runs | Faible seule | Moyenne si bug OAI spécifique | Intéressant, mais **non publiable seul** | explication précise du bug/config | L’insérer comme symptôme d’un diagnostic causal |
| Mesures MCS/NPRB/BLER/SNR/scheduler/F1/UPF | Faible | Faible | **Nécessaire**, pas novateur | synchronisation et nettoyage | Soutien méthodologique essentiel |
| F1 via Ethernet | Faible | Faible | Baseline | stabilité des runs | Référence uniquement |
| F1 via Wi‑Fi GRE | Moyenne dans le corpus consulté | Moyenne | **Expérimentalement intéressant** | latence/jitter/perte + répétitions | Angle workshop possible si comparaison propre |
| F1 via Quectel 5G + WireGuard | Moyenne à forte dans le corpus consulté | Moyenne à forte | **Point distinctif réel** | validation A/B publication-grade | Très bon angle expérimental si vous verrouillez la méthode |
| Séparation radio d’accès / backhaul | Moyenne | Moyenne | Bonne architecture expérimentale | schéma clair + captures prouvant les flux | Excellent élément de crédibilité |
| Packet placement / preuve du bon chemin | Faible en nouveauté, forte en valeur méthodo | Moyenne | **Très bon point** | traces horodatées CU/DU/WG/UE | À mettre en avant comme exigence méthodologique citeturn39academia0 |
| PWS/SIB8 en architecture CU/DU | Moyenne à potentiellement forte | Potentiellement forte | **Le point fonctionnel le plus original**, mais fragile | mapping 3GPP précis, test UE, comparaison monolithique/split | Très bon angle secondaire ; angle principal seulement si validation impeccable |
| TUI opérateur et rollback | Faible scientifiquement | Moyenne ingénierie | Forte valeur pratique | démonstration de reproductibilité inter-opérateurs | À valoriser comme artifact/tooling |
| Portage DU sur Raspberry Pi 5 | Faible à moyenne | Moyenne | Intéressant, encore trop léger | CPU/RAM/température/stabilité | Peut devenir un papier edge seulement avec mesures de contraintes |
| Documentation de handoff | Faible | Faible | Très utile, non publiable seule | n/a | À joindre au dépôt |
| Architecture portable / drone-carried DU | Faible en preuve actuelle | Moyenne conceptuelle | **Spéculatif** pour l’instant | démo terrain ou emulation argumentée | Mention “future work”, pas contribution actuelle |

Le cœur du diagnostic est net. **Vos points forts publiables aujourd’hui sont les points 3, 7, 8, 10 et 11.** Le reste sert à construire la crédibilité du banc d’essai, pas à porter la contribution principale. Le Pi 5, le TUI, la documentation et le handoff renforcent la valeur de l’artefact, mais ne sauveront pas un papier si la thèse scientifique reste floue. fileciteturn0file0 citeturn39academia0turn39academia2turn40academia0turn37academia1

## Scénarios de publication réalistes

### Évaluation des angles possibles

| Angle | Thèse possible | Niveau de nouveauté | Ce qu’il faut encore | Venue la plus réaliste | Probabilité relative |
|---|---|---|---|---|---|
| **Reproducible OAI CU/DU split testbed** | Banc d’essai stable, multi-scenarios, scripts, captures, rollback, traces | Moyenne | dépôt propre, protocole d’évaluation, instructions clean-room, figures comparatives | **Workshop**, **papier testbed**, **rapport technique public** | **Élevée** |
| **Performance characterization of F1 transport over heterogeneous links** | Ethernet vs Wi‑Fi GRE vs Quectel/WG, avec impact sur MCS/BLER/throughput | Moyenne à forte | A/B strict, statistiques, métriques réseau complètes, contrôle radio | **Workshop** ou **conférence télécom intermédiaire** | **Moyenne** |
| **PWS / SIB8 over CU/DU split** | Faisabilité et chemin split-compatible d’un warning path sur OAI | Potentiellement forte mais niche | normalisation 3GPP, validation UE, démonstration monolithique/split, comparaison avec OAI existant | **Workshop**, **démo**, éventuellement **papier court** | **Moyenne** |
| **Portable / edge DU with wireless backhaul** | DU contraint, portable, Pi 5, backhaul sans fil | Faible à moyenne aujourd’hui | CPU/RAM/thermals/stabilité, terrain ou campagne edge | **Démo** plutôt que full paper | **Faible à moyenne** |
| **Debugging and root-cause analysis of OAI CU/DU bottlenecks** | Diagnostic causal d’un pathologie de débit split | Moyenne à forte | root cause reproductible, isolation des variables, correctif ou mitigation | **Workshop solide**, voire meilleure ambition si diagnostic très net | **Moyenne à élevée** |

**Mon classement opérationnel** est simple.  
Le meilleur angle **maintenant** est **A**, avec **B** comme cœur expérimental, et **C** comme bonus fonctionnel si vous clarifiez la cartographie normative.  
Le meilleur angle **ambitieux** serait **E**, mais seulement si vous arrivez à démontrer un mécanisme causal clair et réutilisable. citeturn22academia2turn22academia3turn37academia2turn39academia0turn37academia1

### Venues réalistes

Je privilégie ici des **familles de venues existantes** et cohérentes avec l’état actuel du projet, pas des cibles artificiellement flatteuses.

| Venue | Type de papier attendu | Adéquation avec votre projet | Exigence relative | Avis |
|---|---|---|---|---|
| **EuCNC & 6G Summit** | télécoms appliquées, testbeds, démos, plateformes | Bonne pour un papier orienté testbed, transport radio, OAI, emergency networking | Moyenne | **Bonne cible** pour version propre et appliquée citeturn27news0 |
| **IEEE ICC workshops** | travaux en télécoms, souvent plus ciblés et plus souples que le main track | Bonne pour transport hétérogène, split, edge DU, O-RAN appliqué | Moyenne à élevée | **Bonne cible workshop** citeturn46search1 |
| **IEEE GLOBECOM workshops** | proche d’ICC, bonne place pour travaux expérimentaux ciblés | Bonne | Moyenne à élevée | **Bonne cible workshop** citeturn46search0 |
| **IEEE NetSoft** | softwarization, virtualisation, orchestration, tooling, plateformes | Bonne si vous accentuez la reproductibilité, l’automatisation et l’intégration système | Moyenne à élevée | **Très cohérent** si l’angle “testbed/automation/softwarization” domine citeturn45academia6 |
| **ACM MobiCom demos/posters** | démos percutantes, systèmes mobiles convaincants, forte sélectivité | Bon pour une **démo** PWS split ou DU portable, moins réaliste pour un full paper à ce stade | Très élevée | **Démo ambitieuse**, pas pari principal citeturn28search0 |
| **Rapport technique public + dépôt artifact** | valeur d’usage plus que prestige | Excellente si vous voulez d’abord figer et transmettre | Faible à moyenne | **À faire dans tous les cas** |

Je déconseille en revanche de viser directement un full paper de rang très élevé type MobiCom/NSDI/INFOCOM avec les preuves actuelles. Non pas parce que le sujet serait faible, mais parce que le **message n’est pas encore cristallisé** et que vos résultats ne sont pas encore assez propres pour survivre à une review agressive. Les venues hautement sélectives récompensent une revendication simple, dure et parfaitement démontrée. Aujourd’hui, vous avez surtout un **excellent terrain d’essai**. citeturn28search0turn45search0turn29search1

## Validations indispensables et risques

### Protocole expérimental recommandé

| Élément | Priorité | Pourquoi |
|---|---|---|
| Commit OAI unique pour toute la campagne | **Indispensable** | Sans cela, vous mélangez science et archéologie logicielle |
| Même bande, PRB, SCS, fréquence, puissance, UE, position, environnement radio | **Indispensable** | Sinon les comparaisons de débit et MCS ne veulent pas dire grand-chose |
| Même application et même durée de run | **Indispensable** | Évite les biais d’application et de warm-up |
| Minimum 10 répétitions par scénario | **Indispensable** | Nécessaire pour sortir des anecdotes |
| Logs CU/DU/5GC synchronisés temporellement | **Indispensable** | Condition de toute analyse causale |
| Captures réseau sur chaque segment important | **Indispensable** | Pour prouver le chemin réel F1/F1-U/WG |
| Débit DL/UL côté UE et côté backhaul brut | **Indispensable** | Distingue limite radio et limite transport |
| RTT, jitter, perte | **Indispensable** | Le transport F1 ne se résume pas au débit citeturn31academia2turn39academia3turn40academia1 |
| CPU/RAM par nœud | **Indispensable** | Surtout pour expliquer le split et le Pi 5 |
| MCS, BLER, SNR/CQI, NPRB, HARQ | **Indispensable** | Nécessaire pour relier réseau et radio |
| SCTP F1-C, GTP-U/UDP 2153 pour F1-U, trafic WireGuard outer | **Indispensable** | Prouve que vous mesurez le bon plan et le bon tunnel |
| iperf sur backhaul brut indépendamment d’OAI | **Indispensable** | Sinon vous ne savez pas qui est coupable |
| Validation smartphone du PWS | **Indispensable** si angle C | Un patch non visible par le téléphone reste une demi-validation |
| Mesures thermiques et charge sur Raspberry Pi 5 | **Utile, quasi indispensable** si angle D | Pour passer de “ça tourne” à “c’est portable” |
| fast.com / application commerciale en complément d’iperf | **Utile** | Cela parle à un lecteur non spécialiste, mais ne remplace pas l’iperf |
| Cage ou environnement RF vraiment stable | **Très utile** | Réduit le bruit expérimental |

Ce protocole est exigeant, mais il ne demande pas de nouvelle théorie. Il demande surtout de **transformer un bon projet d’intégration en expérience contrôlée**. C’est le passage obligé. Les travaux de testbed récents dans l’écosystème OAI vont exactement dans ce sens : instrumentation, variables explicites, validation terrain, et parfois publication de données. citeturn22academia3turn39academia0turn36academia2

### Risques principaux

| Risque | Impact | Mitigation | Bloquant pour publier |
|---|---|---|---|
| Contribution trop intégrative | Élevé | recentrer la thèse sur un problème causal ou une méthodologie réutilisable | **Oui**, pour full paper |
| Résultats de débit non comparables entre runs | Élevé | commit figé, mêmes paramètres, répétitions | **Oui** |
| Bottleneck MCS=0 non expliqué | Élevé | corrélation radio/logs réseau/CPU + séparation des causes | **Oui** pour angle E, **non** pour simple testbed paper |
| Quectel/WireGuard encore peu validé | Élevé | A/B propres + mesures de base du lien brut | **Oui** si angle B principal |
| Confusion backhaul / midhaul / fronthaul / F1 | Moyen à élevé | terminologie stricte dès l’introduction | **Oui** pour crédibilité |
| PWS/SIB8 trop spécifique ou terminologie floue | Moyen à élevé | cartographie 3GPP/OAI/UE très explicite | **Oui** si angle C |
| TUI et rollback survalorisés | Moyen | les présenter comme artifact, pas comme contribution scientifique | Non |
| Raspberry Pi 5 insuffisamment caractérisé | Moyen | mesures de ressources et limites | Non, sauf si angle D |
| Dépendance forte à votre setup local | Élevé | documentation clean-room + scripts + BOM + traces | **Oui** pour tout papier de testbed |

Le risque majeur est simple. Si vous ne verrouillez pas la méthodologie, un reviewer conclura : **“beau système, mais impossible de savoir si les effets observés viennent du split, du lien, du scheduler, du commit, de l’UE ou de l’environnement radio.”** C’est la phrase à éviter. citeturn39academia0turn40academia1turn31academia2

## Recommandation finale et plan sur quatre semaines

### Recommandation finale

**Je recommande l’option 4 : transformer le travail en artifact paper / open-source testbed paper, avec une cible workshop ou démo en accompagnement.**

Si vous obtenez, dans les deux à quatre semaines, une campagne propre montrant l’effet différentiel de **Ethernet vs Wi‑Fi GRE vs Quectel/WireGuard** sur **throughput, RTT, jitter, perte, MCS, BLER et CPU**, alors l’option 2 — *publier après compléments expérimentaux* — devient réaliste aussi. Mais **pas comme full paper maintenant**. La priorité est de sortir un message unique, propre, défendable. fileciteturn0file0 citeturn39academia0turn39academia2turn40academia0turn37academia1

**Contribution principale à défendre en réunion avec votre professeur :**  
*“Nous avons construit un banc d’essai OAI 5G NR CU/DU reproductible, multi-machines, instrumenté de bout en bout, permettant de caractériser l’impact de transports F1 hétérogènes sur les performances radio et réseau, et nous montrons la faisabilité d’un chemin d’alerte compatible split sous réserve d’une validation normative et UE complète.”*

C’est honnête. C’est défendable. Et cela ne survalorise pas le projet.  

### Titre provisoire

**A Reproducible OpenAirInterface 5G NR CU/DU Testbed for Characterizing Heterogeneous F1 Transport and Split-Compatible Public Warning Delivery**

### Abstract provisoire

*Open RAN research increasingly relies on disaggregated yet reproducible 5G experimental platforms. We present a multi-machine OpenAirInterface 5G NR testbed supporting monolithic and CU/DU-split deployments, heterogeneous F1 transport paths, and operator-oriented automation for deployment, validation, and rollback. Our platform integrates Ethernet, Wi-Fi with GRE encapsulation, and a commercial 5G modem with WireGuard as candidate transport substrates, while exposing synchronized traces from the CU, DU, core, and transport network. We use this testbed to compare monolithic and split deployments under controlled conditions and to analyze performance pathologies observed in historical runs, including severe throughput degradation and abnormal MCS behavior. In addition, we prototype a split-compatible warning-message delivery path and discuss the requirements for end-to-end validation on commercial UEs. Our results show that reproducibility, transport semantics, and packet-path verification are first-class variables when evaluating disaggregated 5G systems. The artifact, scripts, and measurement methodology are released to support repeatable experimentation on open 5G platforms.* citeturn39academia0turn39academia2turn40academia0turn37academia1

### Structure de papier recommandée

1. Motivation et question expérimentale  
2. Architecture du banc d’essai  
3. Scénarios de transport F1 et instrumentation  
4. Protocole expérimental  
5. Résultats comparatifs  
6. Analyse du bottleneck et limites  
7. Extension warning path compatible split  
8. Reproductibilité et artefacts  

### Plan d’action concret

| Semaine | Actions |
|---|---|
| Semaine 1 | Geler le commit OAI, figer la config radio, nettoyer le dépôt, écrire le manifest matériel/logiciel, définir les scénarios exacts |
| Semaine 2 | Refaire les baselines monolithique et split Ethernet avec répétitions, captures synchronisées, CPU/RAM, MCS/BLER/SNR |
| Semaine 3 | Refaire Wi‑Fi GRE puis Quectel/WireGuard avec le même protocole, mesurer aussi le backhaul brut sans OAI, produire les figures principales |
| Semaine 4 | Valider le chemin PWS sur UE, écrire le papier court, décider avec le professeur entre workshop/démo/rapport technique public |

### Figures à produire

- Schéma d’architecture complet avec chemins F1/F1-U/WireGuard  
- Boxplots débit DL/UL par scénario  
- Série temporelle MCS/BLER/SNR pour monolithique vs split  
- Corrélation débit ↔ MCS ↔ RTT ↔ jitter  
- Tableau packet placement prouvant le chemin exact des flux  
- Figure CPU/RAM par nœud et par scénario  
- Figure PWS : chaîne logique CU → F1 → DU → UE  

### Checklist ready to submit

- [ ] Commit OAI unique pour tous les résultats  
- [ ] Dépôt propre, installable, documenté  
- [ ] BOM matériel et topologie réseau  
- [ ] Scripts de run et de collecte automatisés  
- [ ] 10 répétitions par scénario minimum  
- [ ] Captures synchronisées CU/DU/5GC/WG  
- [ ] Figures débit, RTT, jitter, perte, MCS, BLER, CPU  
- [ ] Explication causale ou au minimum limites clairement formulées  
- [ ] Cartographie normative précise de la partie PWS  
- [ ] Validation UE visible et documentée  
- [ ] Section limites et menaces à la validité  
- [ ] README artifact et guide clean-room  

**En une phrase pour votre réunion.**  
Votre travail est **assez fort pour justifier une publication ciblée**, mais **pas assez mûr pour prétendre tout de suite à un full paper généraliste**. Sa meilleure valeur, aujourd’hui, est celle d’un **testbed reproductible et instrumenté**, avec un **angle expérimental net sur les transports F1 hétérogènes** et un **bonus fonctionnel PWS split** si vous le verrouillez correctement. fileciteturn0file0 citeturn22academia2turn22academia3turn37academia2turn39academia0turn40academia0