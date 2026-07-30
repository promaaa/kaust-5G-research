---
theme: white
transition: slide
center: false
highlightTheme: github
width: 1920
height: 1080
margin: 0.08
---

<style>
.reveal section { text-align: left; }
.reveal h1, .reveal h2, .reveal h3 { color: #111827; }
.reveal p, .reveal li { color: #374151; line-height: 1.25; }
.reveal img { max-height: 560px; object-fit: contain; }
.small { font-size: 0.72em; color: #6b7280; }
.note-box { border-left: 6px solid #2563eb; padding-left: 24px; color: #374151; }
</style>

# Presentation Charlotte V2
### Stage 5G OAI CU/DU

**Du banc d'essai radio au backhaul 5G**

<img src="img/Pasted%20image%2020260604093732.png" alt="Annotated physical 5G testbed" width="1100">

Note:
Presentation courte, environ 10 minutes. L'objectif est de donner une vue globale: ce qui etait prevu, ce qui a ete fait, les resultats, le banc d'essai et les prochaines etapes.

---

## Idee generale

Construire un reseau 5G experimental capable de separer:

- le calcul lourd au sol: **5GC + CU**;
- la radio proche de l'utilisateur: **DU + USRP B210**;
- le transport entre les deux: **F1 sur Ethernet, Wi-Fi, puis 5G Quectel**.

```mermaid
flowchart LR
    Ground["Station au sol<br>5GC + CU"]
    Link["Backhaul F1<br>Ethernet / Wi-Fi / Quectel"]
    Remote["DU distant<br>USRP B210"]
    User["Nothing Phone<br>PWS / donnees"]

    Ground --> Link --> Remote --> User
```

Note:
Le fil rouge est un relais 5G deployable: garder le coeur et le CU au sol, et rapprocher seulement la radio des utilisateurs.

---

## Ce qui etait prevu

```mermaid
flowchart LR
    A["1. Reference<br>OAI monolithique"]
    B["2. Alertes<br>PWS / SIB8"]
    C["3. Split<br>CU / DU"]
    D["4. Backhaul<br>sans fil"]
    E["5. Banc<br>reproductible"]

    A --> B --> C --> D --> E
```

<div class="note-box">
La logique du stage: avancer par baselines, valider chaque etape, et garder un rollback propre.
</div>

Note:
Cette slide explique le plan initial. On ne cherchait pas seulement une demo finale, mais une progression controlee.

---

## Le banc d'essai


<img src="img/picture-of-setup.png" alt="Physical testbed with compute nodes labeled" width="950">

---

## Architecture cible

```mermaid
graph TD
    subgraph Firecell["serber-firecell"]
        Core["OAI 5GC"]
        CU["OAI CU"]
        Donor["gNB donneur<br>pour le modem Quectel"]
        Core --- CU
        Core --- Donor
    end

    subgraph MiniPC["serber-minipc"]
        Quectel["Quectel RM500Q-GL"]
        WG["WireGuard<br>wg-quectel-f1"]
        DU["OAI DU d'acces"]
        B210["USRP B210"]
        Quectel --- WG --- DU --- B210
    end

    Phone["Nothing Phone"]

    Donor -. "RF 5G donneur" .-> Quectel
    WG == "F1-C / F1-U" ==> CU
    B210 -. "cellule 5G d'acces" .-> Phone
```

<span class="small">Image future possible: `target-quectel-f1-architecture.png`.</span>

Note:
Point cle: le Quectel doit utiliser une cellule donneuse separee, pas la cellule d'acces qu'il backhaul.

---

## Ce qui a ete realise

- Reference OAI monolithique fonctionnelle.
- Split **CU/DU Ethernet** avec SIB8/PWS.
- Alertes **PWS** observees sur telephone.
- Backhaul **Wi-Fi GRE** valide.
- Plan **Quectel + WireGuard** implemente.
- TUI et scripts pour lancer, valider et rollback.

<img src="img/diagram-of-setup.png" alt="Target airborne CU/DU testbed architecture" width="850">

Note:
Le resultat n'est pas seulement radio: c'est aussi un banc que l'on peut relancer et documenter.

---

## Resultats principaux

| Configuration | Etat | Resultat observe |
|---|---:|---:|
| Monolithique OAI | reference | ~150 Mb/s |
| CU/DU Ethernet + SIB8 | rollback stable | ~19-23 Mb/s |
| CU/DU Wi-Fi GRE | backhaul sans fil valide | ~12 Mb/s |
| Quectel / WireGuard | en validation | F1-C et tunnel prouves, F1-U final ouvert |

<img src="img/throughput_chart%201.png" alt="Observed throughput by configuration" width="900">

Note:
Ne pas survendre Quectel. Les resultats solides sont monolithique, Ethernet split avec SIB8, et Wi-Fi GRE. Quectel est avance, mais la preuve utilisateur finale reste a fermer.

---

## Points difficiles

- Compatibilite **SCTP** selon les machines et noyaux.
- Separation necessaire entre **radio d'acces** et **radio/backhaul**.
- Routes residuelles pouvant casser le transport F1.
- Debit split limite, avec investigation autour de **MCS / CQI / HARQ**.
- Attribution du trafic telephone: besoin de captures synchronisees.

```mermaid
flowchart TD
    Problem["Debit ou validation incomplete"]
    Transport["Transport F1"]
    Core["PDU session coeur"]
    Scheduler["Planificateur radio"]
    Evidence["Preuves synchronisees"]

    Problem --> Transport
    Problem --> Core
    Problem --> Scheduler
    Transport --> Evidence
    Core --> Evidence
    Scheduler --> Evidence
```

Note:
Cette slide montre les verrous d'ingenierie. Les problemes ont ete transformes en gates de validation.

---

## Ce que le banc permet maintenant

Comparer proprement plusieurs transports F1:

- **Ethernet**: baseline de rollback.
- **Wi-Fi GRE**: backhaul sans fil valide.
- **Quectel 5G**: cible principale en validation.
- **DU portable**: direction suivante.

<img src="img/Pasted%20image%2020260616095439.png" alt="Deployment tooling interface" width="950">

<span class="small">Image future possible: `validation-workflow-screenshot.png`.</span>

Note:
Le banc devient un outil pour faire des campagnes experimentales, pas seulement une installation ponctuelle.

---

## Suite du travail

1. Fermer la validation Quectel avec F1-U pendant trafic telephone.
2. Instrumenter le MCS split et comparer au monolithique.
3. Produire une matrice de performance Ethernet / Wi-Fi / Quectel.
4. Stabiliser le profil DU portable.

<img src="img/IMG_4346.jpg" alt="Physical testbed in the laboratory" width="760">

<span class="small">Image future possible: `portable-du-drone-concept.jpg`.</span>

Note:
Terminer sur la trajectoire: du banc de laboratoire vers un relais 5G deployable.

---

# Conclusion

Le stage a transforme une idee de relais 5G en un banc d'essai structure:

- radio reelle;
- split CU/DU;
- alertes PWS/SIB8;
- backhauls compares;
- validation outillee.

**Prochaine marche:** fermer la preuve de bout en bout sur Quectel, puis optimiser le debit et la portabilite.

Note:
Phrase de fin possible: "Le plus important n'est pas seulement d'avoir fait fonctionner une configuration, mais d'avoir construit une methode pour prouver ce qui fonctionne, identifier ce qui bloque, et continuer sans perdre les baselines."
