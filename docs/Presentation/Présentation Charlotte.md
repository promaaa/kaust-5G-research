# De la station au sol au relais 5G volant
### Progrès d'un banc d'essai 5G/UAV

Récapitulatif de la recherche


---

## Concept principal

```mermaid
graph TD
    subgraph Ground["Station au sol"]
        A["Réseau cœur + CU<br>(Calcul lourd)"]
    end
    subgraph Air["Relais drone"]
        B["DU + radio USRP B210<br>(Charge utile RF légère)"]
    end
    subgraph User["Zone d'urgence"]
        C["Utilisateur Nothing Phone<br>(Alerte d'urgence PWS)"]
    end
    A -->|Backhaul 5G C/U| B
    B -.->|Backhaul 5G| C
    style Ground fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc
    style Air fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style User fill:#1e293b,stroke:#f43f5e,stroke-width:2px,color:#f8fafc
```

---

## Contexte et intérêt

### Rétablissement d'urgence

```mermaid
flowchart TD
    Disaster["Catastrophe<br>(Inondations, incendies, pannes)"] --> Outage["Pylônes au sol hors service<br>(Aucun signal mobile)"]
    Outage --> Rescue["Relais 5G sur drone<br>(Déploiement en minutes)"]
    Rescue --> Recovery["Couverture d'urgence rétablie<br>(Alerte PWS envoyée)"]
    style Disaster fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#f8fafc
    style Outage fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#f8fafc
    style Rescue fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style Recovery fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
```

---

## Le concept de séparation CU/DU

<grid cols="2" gap="10">

![Target airborne CU/DU architecture](img/diagram-of-setup.png)

![Physical testbed in the laboratory](img/IMG_4346.jpg)

</grid>

---

## Le banc d'essai physique

![Annotated physical testbed](img/Pasted%20image%2020260604093732.png)

---

## Chronologie des développements

```mermaid
flowchart LR
    A["Simulation"] --> B["Radio réelle"] --> C["Nothing Phone"] --> D["PWS d'urgence"] --> E["Séparation Ethernet"] --> F["DU sur Pi 5"] --> G["GRE sur Wi-Fi"] --> H["Quectel 5G"] --> I["Setup cible"]
    style A fill:#1e293b,stroke:#3b82f6,color:#f8fafc
    style B fill:#1e293b,stroke:#3b82f6,color:#f8fafc
    style C fill:#1e293b,stroke:#10b981,color:#f8fafc
    style D fill:#1e293b,stroke:#10b981,color:#f8fafc
    style E fill:#1e293b,stroke:#10b981,color:#f8fafc
    style F fill:#1e293b,stroke:#10b981,color:#f8fafc
    style G fill:#1e293b,stroke:#f59e0b,color:#f8fafc
    style H fill:#1e293b,stroke:#f59e0b,color:#f8fafc
    style I fill:#1e293b,stroke:#f59e0b,color:#f8fafc
```

---

## Choix techniques et pivots d'ingénierie

<grid cols="2" gap="10">

<div style="font-size: 26px; text-align: left; line-height: 1.5; color: #94a3b8;">

### Résolution des verrous

1. **Jetson (Tegra)** : Noyau SCTP recompilé, puis profil CPU/USB stabilisé.
2. **RF** : Une seule radio sature en accès et transport. Séparation des rôles (USRP et Quectel).
3. **Débit** : Analyse conjointe MTU/MSS, BLER et planificateur OAI.

</div>

<div style="font-size: 20px; line-height: 1.4;">

<div style="background: rgba(30, 41, 59, 0.3); border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid #ef4444; border-radius: 8px; padding: 10px 15px; margin-bottom: 10px;">
  <strong style="color: #f8fafc;">Noyau SCTP</strong><br>
  Un noyau SCTP adapté et un profil CPU/USB ont rendu le DU Jetson opérationnel.
</div>

<div style="background: rgba(30, 41, 59, 0.3); border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid #f59e0b; border-radius: 8px; padding: 10px 15px; margin-bottom: 10px;">
  <strong style="color: #f8fafc;">Ressources RF</strong><br>
  L'USRP B210 gère l'accès du téléphone, et le modem Quectel gère la liaison de transport.
</div>

<div style="background: rgba(30, 41, 59, 0.3); border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid #38bdf8; border-radius: 8px; padding: 10px 15px; margin-bottom: 10px;">
  <strong style="color: #f8fafc;">Planificateur</strong><br>
  Le réglage MTU/MSS et l'adaptation des seuils BLER ont permis au MCS de remonter.
</div>

</div>

</grid>

---

## Résultats validés à ce jour

<grid cols="2" gap="10">

<div style="font-size: 26px; text-align: left; line-height: 1.5; color: #94a3b8;">

### État de validation

* Connexions et alertes PWS stabilisées.
* Ethernet séparé réglé jusqu'à 100 Mbps en pointe.
* Jetson avec backhaul Quectel validé autour de 40–44 Mbps.

</div>

<div style="font-size: 18px; line-height: 1.4; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; color: #cbd5e1;">

<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 8px 12px;"><span style="color: #10b981; font-weight: bold; margin-right: 8px;">✓</span>Téléphone connecté en mode séparé</div>
<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 8px 12px;"><span style="color: #10b981; font-weight: bold; margin-right: 8px;">✓</span>Diffusion d'alerte SIB8 (PWS)</div>
<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 8px 12px;"><span style="color: #10b981; font-weight: bold; margin-right: 8px;">✓</span>Fonctionnement séparé CU/DU</div>
<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 8px 12px;"><span style="color: #10b981; font-weight: bold; margin-right: 8px;">✓</span>Transport F1 sur canal sans fil</div>
<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 8px 12px;"><span style="color: #10b981; font-weight: bold; margin-right: 8px;">✓</span>Liaison de transport via Quectel</div>
<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 8px 12px;"><span style="color: #10b981; font-weight: bold; margin-right: 8px;">✓</span>Thread pinning validé sur Pi 5</div>
<div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 8px; padding: 8px 12px; grid-column: span 2;"><span style="color: #f59e0b; font-weight: bold; margin-right: 8px;">⚠</span>En cours : répétitions contrôlées et publication des preuves expérimentales</div>

</div>

</grid>

---

## Architecture cible unifiée

<grid cols="2" gap="10">

<div style="font-size: 26px; text-align: left; line-height: 1.5; color: #94a3b8;">

### Implantation finale

Le trafic utilisateur traverse le DU distant, s'encapsule dans le tunnel WireGuard chiffré établi sur le lien 5G du Quectel, puis atteint le cœur au sol.

</div>

<div>

```mermaid
graph TD
    subgraph Ground["Station au sol (serber-firecell)"]
        Core["Cœur 5G OAI"]
        CU["Central Unit OAI (CU)"]
        Donor["Cellule donneuse OAI (gNB)<br>(PCI 1, TAC 2)"]
        Core --- CU
        Core --- Donor
    end
    subgraph Remote["Unité distante (serber-minipc)"]
        Quectel["Modem 5G Quectel<br>(IP 10.0.0.6)"]
        DU["Distributed Unit OAI (DU)<br>(PCI 0, TAC 1)"]
        B210["Radio d'accès USRP B210"]
        DU --- B210
    end
    subgraph UE["Terminal utilisateur"]
        Phone["Nothing Phone"]
    end
    
    Donor -.->|Liaison RF 5G| Quectel
    Quectel ==>|Liaison F1 WireGuard| CU
    B210 -.->|Accès RF 5G| Phone
    
    style Ground fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#f8fafc
    style Remote fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#f8fafc
    style UE fill:#1e293b,stroke:#f43f5e,stroke-width:2px,color:#f8fafc
```

</div>

</grid>

---

## Analyse du débit et goulot d'étranglement

<grid cols="2" gap="10">

<div style="font-size: 26px; text-align: left; line-height: 1.5; color: #94a3b8;">

### Goulot d'étranglement

Les essais tardifs ont invalidé le plafond initial de 23 Mbps. Le split Ethernet réglé a atteint 100 Mbps en pointe; le chemin Wi-Fi/GRE 52 Mbps et le chemin Quectel/WireGuard 78 Mbps.

Ces valeurs sont des meilleurs résultats observés, pas des moyennes contrôlées.

</div>

<div>

![Best-observed throughput comparison](img/throughput_chart_best.png)

</div>

</grid>

---

## Perspectives et étapes futures

<grid cols="2" gap="10">

<div style="font-size: 26px; text-align: left; line-height: 1.5; color: #94a3b8;">

### Travaux futurs

La suite transforme les démonstrations en artefact reproductible et prépare une intégration drone sûre.

</div>

<div style="font-size: 18px; line-height: 1.4; display: flex; flex-direction: column; gap: 8px;">

<div style="background: rgba(30, 41, 59, 0.3); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 12px; border: 1px solid rgba(255,255,255,0.03);">
  <span style="background: #3b82f6; color: #0b0f19; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800;">1</span>
  <span style="color: #cbd5e1;"><strong>Geler le logiciel</strong> : publier le commit OAI, les patchs et configurations exacts.</span>
</div>
<div style="background: rgba(30, 41, 59, 0.3); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 12px; border: 1px solid rgba(255,255,255,0.03);">
  <span style="background: #3b82f6; color: #0b0f19; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800;">2</span>
  <span style="color: #cbd5e1;"><strong>Répéter les mesures</strong> : campagnes contrôlées avec métriques synchronisées.</span>
</div>
<div style="background: rgba(30, 41, 59, 0.3); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 12px; border: 1px solid rgba(255,255,255,0.03);">
  <span style="background: #3b82f6; color: #0b0f19; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800;">3</span>
  <span style="color: #cbd5e1;"><strong>Publier les preuves</strong> : données anonymisées et validation du chemin des paquets.</span>
</div>
<div style="background: rgba(30, 41, 59, 0.3); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 12px; border: 1px solid rgba(255,255,255,0.03);">
  <span style="background: #3b82f6; color: #0b0f19; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800;">4</span>
  <span style="color: #cbd5e1;"><strong>Radio légère</strong> : valider le B205mini-i avant le choix d'un petit drone.</span>
</div>
<div style="background: rgba(30, 41, 59, 0.3); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 12px; border: 1px solid rgba(255,255,255,0.03);">
  <span style="background: #3b82f6; color: #0b0f19; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800;">5</span>
  <span style="color: #cbd5e1;"><strong>Châssis drone</strong> : alimentation, refroidissement, RF, fixation et sécurités.</span>
</div>

</div>

</grid>
