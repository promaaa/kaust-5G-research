# État de l'Art : Revue de Littérature sur les Stations de Base Aériennes (UAV-BS)

---

## 1. Carte de Littérature : Articles par Matériel et Impact

![Carte des Articles](sota_papers_map.png)

| Article | Matériel | Testé en Vol | Notes |
|---------|----------|--------------|-------|
| **SkyCell** | NUC + USRP B210 | ✅ | Première station BS 5G aérienne |
| **SkyRAN** | NUC + USRP B210 | ✅ | Étude de positionnement LTE |
| **Flying Rebots** | x86 | ❌ | Conceptuel uniquement |
| **Jetson Nano OAI** | Jetson Nano | ❌ | Échec (limites ISA/BW) |
| **5G Edge Vision** | Jetson Nano | ❌ | IA de bord uniquement |

**Résultat Clé :** Les prototypes UAV-BS prouvés utilisent tous **NUC + USRP B210**

---

## 2. Ce Dont Nous Avons Besoin vs. Ce Que la Littérature Fournit

```mermaid
flowchart LR
    subgraph Need["Ce Dont Nous Avons Besoin"]
        gNB["5G gNB\n(OAI + USRP)"]
        Portable["Portable\n(Mini-PC x86)"]
        Security["Analyse\nde Sécurité"]
    end
    
    subgraph Have["Ce Que la Littérature Fournit"]
        SkyCell["SkyCell\nStation BS 5G ✓"]
        SkyRAN["SkyRAN\nStation BS LTE ✓"]
        Position["Concepts de\nPositionnement ✓"]
    end
    
    subgraph Gap["L'ÉCART"]
        Attack["Démo\nd'Attaque ❌"]
        Alert["Alerte d'Urgence\nSécurité ❌"]
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
