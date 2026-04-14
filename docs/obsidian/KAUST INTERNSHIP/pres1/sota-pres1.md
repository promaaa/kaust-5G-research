# État de l'Art : Revue de Littérature sur les Stations de Base Aériennes (UAV-BS)

---

## 1. Carte de Littérature : Articles par Matériel et Impact


| Article             | Matériel        | Testé en Vol | Notes                           |
| ------------------- | --------------- | ------------ | ------------------------------- |
| **SkyCell**         | NUC + USRP B210 | oui          | Première station BS 5G aérienne |
| **SkyRAN**          | NUC + USRP B210 | oui          | Étude de positionnement LTE     |
| **Flying Rebots**   | x86             | non          | Conceptuel uniquement           |
| **Jetson Nano OAI** | Jetson Nano     | non          | Échec (limites ISA/BW)          |
| **5G Edge Vision**  | Jetson Nano     | non          | IA de bord uniquement           |

**Résultat Clé :** Les prototypes UAV-BS prouvés utilisent tous **NUC + USRP B210**

---

## 2. Ce Dont Nous Avons Besoin vs. Ce Que la Littérature Fournit

```mermaid
flowchart LR
    subgraph Need["Ce Dont Nous Avons Besoin"]
        gNB["5G gNB (OAI + USRP)"]
        Portable["Portable (Mini-PC x86)"]
        Security["Analyse de Sécurité"]
    end
    
    subgraph Have["Ce Que la Littérature Fournit"]
        SkyCell["SkyCell Station BS 5G ✓"]
        SkyRAN["SkyRAN Station BS LTE ✓"]
        Position["Concepts de Positionnement ✓"]
    end
    
    subgraph Gap["L'ÉCART"]
        Attack["Démo d'Attaque ❌"]
        Alert["Alerte d'Urgence Sécurité ❌"]
    end
    
    SkyCell --> gNB
    SkyRAN --> gNB
    Position --> Portable
    gNB --> Attack
    Attack --> Alert
    
    style Gap fill:#e74c3c,color:#fff
    style Need fill:#f39c12,color:#000
```

**Notre Contribution :** Combler l'écart — analyse de sécurité de la broadcast 5G d'urgence via une station BS aérienne frauduleuse
