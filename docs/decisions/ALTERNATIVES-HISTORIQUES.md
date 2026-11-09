# THIGA — Alternatives, essais et décisions historiques

> **Historique, non description du logiciel livré.** Ces entrées préservent les pistes étudiées, les compromis et les non-promotions. Elles ne prouvent ni que chaque proposition ait été ratifiée, ni que les prototypes figurent dans le ZIP corrigé. Pour l'état de livraison, consulter [le registre principal](../DECISIONS.md) et [la qualification](../QUALIFICATION.md).

- **TH-D-018 — Staffing, CV et intercontrat reportés : hors des deux outils en lecture seule retenus.** *Source d'arbitrage : D04 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-025 — Pont mcpo/OpenAPI gardé comme repli si l'intégration MCP native devenait incompatible.** *Source d'arbitrage : D02 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-035 — JWT utilisateur étudié, non assimilé à une délégation OAuth et non retenu dans le PoC.** *Source d'arbitrage : D03 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-039 — Façade d'identité additionnelle évitée tant que le canal backend et le contrôle MCP suffisent aux exigences du PoC.** *Source d'arbitrage : D03 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-047 — Filtre documentaire M08 abandonné après régressions métier, incident mémoire et absence de témoin discriminant.** *Source d'arbitrage : D05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-048 — Contrôle déterministe de finalité pré-appel reporté faute de provenance d'intention fiable.** *Source d'arbitrage : D05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-049 — Socle A et essais B isolés préférés à une défense supplémentaire non qualifiée en routine.** *Source d'arbitrage : D05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-051 — display_file n'est pas une preuve d'exposition du texte au LLM ; attendre un retour lecteur effectif.** *Source d'arbitrage : D05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-052 — Validation humaine systématique par appel RH non retenue pour les lectures simples ; réservée éventuellement aux élargissements sensibles.** *Source d'arbitrage : D05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-053 — Second LLM classificateur de requête non ajouté au PoC.** *Source d'arbitrage : D05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-059 — Gemma 4 12B non promu malgré un cas Claire favorable : preuve ponctuelle, marge GPU moindre, requalification manquante.** *Source d'arbitrage : D08 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-070 — Qwen 4B non retenu comme remplacement automatique du modèle principal 9B ; compromis outil/latence/réglages.** *Source d'arbitrage : D08 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-071 — M10 arrêté au seuil mémoire préétabli plutôt que poursuivre jusqu'à un OOM possible.** *Source d'arbitrage : D08 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-079 — Coffre externe, rotation sophistiquée et état distribué différés à la production.** *Source d'arbitrage : D06 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-105 — Échecs de comparaison nftables/NAT conservés comme incidents de preuve, sans faux PASS.** *Source d'arbitrage : E05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-106 — WebUI non exposé tant que le garde et son état effectif ne satisfont pas les contrôles de démarrage.** *Source d'arbitrage : E05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-117 — Profil de continuation exploré sans changer les droits MCP.** *Source d'arbitrage : REG-05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-118 — B2 expérimenté pour la continuation Claire ; bénéfice confirmé sur un parcours, non-promu.** *Source d'arbitrage : B2 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-120 — Fan-out de tous les outils écarté comme solution générale ; parallélisme sélectif non exclu.** *Source d'arbitrage : B2 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-122 — Investissement supplémentaire B2 non retenu pour la remise : deux P1 dont un pré-dispatch simulé, temps estimé et non-régression incertaine.** *Source d'arbitrage : B2 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-132 — Absence d'egress sans canari positif ne permet pas de conclure à un confinement général.** *Source d'arbitrage : D11 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-136 — Comparaison d'une seconde machine, d'une libération ciblée du seul laboratoire F01 et d'une clôture partielle ; reprise ciblée finalement choisie.** *Source d'arbitrage : F01 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-171 — Frontal expérimental envisagé pour exposer seulement WebUI sans rendre MCP public.** *Source d'arbitrage : E05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-172 — Instrumentation NFLOG du garde M16 envisagée puis distinguée du garde final.** *Source d'arbitrage : E05 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*
- **TH-D-173 — Restitution des paramètres WebUI de l'ancien environnement après essais ponctuels de persistance, sans promotion automatique.** *Source d'arbitrage : D08 ; statut : historique, proposé, expérimenté ou non retenu selon le contexte exact.*

## Enseignements déterminants

**M08** a été abandonné car les témoins n'ont pas permis de démontrer une efficacité anti-injection supplémentaire, tandis que des régressions métier et une pression mémoire ont été observées. **B2** apportait un bénéfice fonctionnel ciblé sur Claire, mais deux défauts P1 ont empêché sa promotion : substitution de réponses explicatives et cohérence de l'identité vérifiée après dispatch dans une simulation. Aucun contournement MCP réel n'a été démontré par cette dernière simulation.

Ne pas requalifier les FAIL, STOP et tests non exécutés en succès après coup. [Catalogue complet](CATALOGUE-COMPLET.md).
