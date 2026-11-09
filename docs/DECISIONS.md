# THIGA · Registre public des décisions de conception

> **Périmètre.** Ce registre décrit la **livraison corrigée scellée du 9 novembre 2026** ; la V1 et les expérimentations anciennes sont des objets distincts. Les résultats mentionnés sont des preuves historiques bornées : **aucun essai Docker/MCP nouveau n'a été exécuté pour rédiger ce registre**.

## Mode de lecture

L'objectif est de montrer les **arbitrages**, pas de présenter chaque mécanisme comme une invention. Open WebUI, Ollama, MCP et Docker Compose sont imposés ou attendus par l'exercice THIGA. Les choix réellement effectués portent sur leurs modalités d'intégration, le périmètre RH, l'identité, les politiques de sécurité, le modèle, le bootstrap, les preuves et la trajectoire d'industrialisation.

- **Implémenté** : visible dans les sources ou la configuration de la livraison corrigée.
- **Qualifié de façon bornée** : résultat positif sur les scénarios effectivement exécutés ; ce n'est pas une validation générale.
- **Partiel** : couverture incomplète ou incertitude résiduelle importante.
- **Non retenu** : option examinée ou expérimentée, mais absente de la livraison de référence.
- **Cible** : architecture de production proposée, non déployée.

### Carte synthétique des arbitrages

| Décision | Choix retenu | Alternative déterminante | État |
|---|---|---|---|
| D01/D04 · Périmètre métier | Annuaire minimal, soldes, manager, séparation tenant | Mono-utilisateur ou accès manager trop large | Implémenté, cas testés |
| D02 · Transport d'outils | MCP natif Streamable HTTP | Pont `mcpo` / OpenAPI | Implémenté, parcours qualifiés |
| D03 · Identité | Session WebUI + identité backend + secret de service + mapping MCP | En-tête libre, JWT signé, OAuth/OIDC | Implémenté, limites assumées |
| D04 · Habilitations | Autorisation déterministe sur tenant et relation hiérarchique | Décision du LLM, simple rôle WebUI | Implémenté, refus testés |
| D08 · LLM | Qwen3.5 9B Q4_K_M principal | Gemma 4 12B, plus petits modèles | Implémenté ; benchmark borné |
| D05 · Injection indirecte | Défense en profondeur et test adversarial borné | Confiance dans les consignes, filtre automatique de finalité | Partiel ; filtre fort non retenu |
| REG-05/B2 · Continuation | Comportement Qwen/WebUI corrigé de façon bornée, sans B2 | Dispatch/continuation forcés B2 | Partiel ; B2 non promu |
| D06 · État et données | SQLite WebUI, fixtures RH, volumes dédiés | PostgreSQL métier et applicatif | Implémenté ; reprise bornée |
| D07 · Mise en route | Compose et jobs `init`, `seed`, `bootstrap` | Clics administrateur, image de DB préremplie | Démarrage F01 borné |
| E05 · Confinement | Garde `nftables` séparé avec seul `NET_ADMIN` | WebUI privilégié ou réseau Docker seul | Implémenté ; egress PARTIEL |
| Intégrité · Supply chain | Versions et digests épinglés, bases OCI locales, modèle vérifié | Dépendances non épinglées, reconstruction opportuniste | Implémenté ; transfert partiel |
| IAM-03 · Révocation | Logout ciblé, registre SQLite + témoin de génération | Logout HTTP seul, révocation globale du compte | PASS borné |
| D11 · Traçabilité | Journal MCP minimal et corrélation des appels | Logs complets non maîtrisés | Implémenté ; scénarios testés |
| F01 · Qualification Compose | Test d'une commande sur volumes vierges, sans effacer les labos historiques | Deuxième moteur ou clôture PARTIELLE | PASS avec réserve portabilité |
| C01/C07 · Remise | ZIP corrigé scellé et V1 préservée | Modifier la V1 / repackager les octets testés | Exécuté et empreintes vérifiées |
| GitHub · Distribution | Sources publiées, bases OCI distribuées uniquement avec ZIP scellé | Push des binaires OCI publics / clone autonome | GitHub public, clone seul incomplet |
| C08 · Nature de l'agent | Assistant conversationnel outillé par MCP | Revendiquer multiagent ou autonomie de planification | Description de la solution |
| D09/D10 · Cible cloud | Kubernetes managé français à qualifier, OKS candidat, OVHcloud à comparer | Produire directement un cluster ou accepter l'étiquette « souverain » | Proposition, non déployée |
| D12 · Réglementation | Classification par finalité et obligations selon l'usage réel | Déclarer tout usage RH automatiquement « haut risque » | Analyse documentaire, non homologation |

---

**Inventaire détaillé :** [catalogue de 173 unités de choix](decisions/CATALOGUE-COMPLET.md) · [expérimentations non promues](decisions/ALTERNATIVES-HISTORIQUES.md) · [cibles Kubernetes et conformité](decisions/CIBLES-NON-DEPLOYEES.md). Les unités historiques et futures ne sont pas des décisions actives.

## I. Cas métier, outils et frontières d'autorisation

### ADR-01 — Un scénario RH suffisamment riche pour éprouver les droits

**Problème.** Le simple affichage d'un solde fictif sous une seule identité aurait satisfait une démonstration fonctionnelle élémentaire, sans tester les frontières essentielles d'un SaaS RH multi-entreprises.

**Options.** (A) Un seul utilisateur et son solde : mise en œuvre minimale, faible pouvoir de preuve. (B) Deux utilisateurs dans deux entreprises : vérifie l'isolement inter-tenant mais pas la hiérarchie interne. (C) Un manager, des salariés de son équipe, un salarié hors équipe et un autre tenant : plus coûteux en identité, tests et fixture, mais discriminant pour les habilitations.

**Décision.** Retenir C avec deux capacités en **lecture seule** : `search_employee` et `get_leave_balance`. L'annuaire ne retourne que des attributs professionnels minimaux ; les soldes exigent une habilitation distincte.

**Constats.** Les données publiées comprennent Marc, Alice, Léa, Claire et Bob. La fonction d'annuaire filtre par tenant ; la consultation de solde accepte son propre solde ou un subordonné direct. Les tests rapportés montrent Marc→Alice = 12 jours, Marc→Claire refusé et une séparation entre entreprises. Un petit corpus synthétique ne démontre pas l'échelle d'une entreprise réelle.

**Contrepartie.** Moins de fonctionnalités RH, mais une démonstration plus convaincante de frontières d'autorisation. Aucun effet d'écriture n'est autorisé ; une lecture RH non autorisée peut malgré tout être un incident grave.

**Traçabilité.** D01/D04 ; [demonstrateur/fixtures.py](../demonstrateur/fixtures.py), [demonstrateur/server.py](../demonstrateur/server.py) ; [`ARCHITECTURE.md`](ARCHITECTURE.md), [`QUALIFICATION.md`](QUALIFICATION.md).

### ADR-02 — MCP natif Streamable HTTP plutôt qu'un pont OpenAPI

**Problème.** Relier Open WebUI aux deux outils Python sans multiplier inutilement les services et les points d'authentification.

**Options.** (A) MCP natif en Streamable HTTP depuis le backend WebUI vers MCP Python. (B) Serveur MCP derrière un pont `mcpo`/OpenAPI : utile si version ou serveur imposent un autre protocole, mais une traduction, un processus et une frontière supplémentaires.

**Décision.** A. Ollama exécute le modèle qui **propose** l'outil ; Open WebUI orchestre l'appel ; MCP exécute la politique métier. MCP est un protocole d'outils, **pas** une garantie d'identité ni de protection contre l'injection.

**Preuve et coût.** Appels natifs observés dans les qualifications sur la pile figée. Le bénéfice de simplicité reste dépendant des capacités précises d'Open WebUI ; si la transmission d'identité était incompatible dans une version future, le pont redeviendrait une alternative à comparer.

**Traçabilité.** D02 ; [demonstrateur/server.py](../demonstrateur/server.py), [demonstrateur/bootstrap.py](../demonstrateur/bootstrap.py), [demonstrateur/compose.yaml](../demonstrateur/compose.yaml).

### ADR-03 — Distinguer identité de service et identité du salarié

**Problème.** Un modèle peut demander l'accès à un autre nom ou inventer un `employee_id`. Le serveur RH ne doit pas interpréter cette cible comme l'identité authentifiée du demandeur.

**Options.** (A) En-tête d'utilisateur transmis par le backend WebUI, **plus** secret Bearer de service et réseau privé. (B) JWT d'utilisateur signé : audience, signature et durée de vie à qualifier. (C) Délégation OAuth/OIDC et identité de workload : meilleure base possible pour plusieurs domaines de confiance, mais hors budget d'un PoC local. (D) Faire confiance aux paramètres de l'outil ou au rôle administratif WebUI : refusé.

**Décision.** A dans une frontière locale maîtrisée. MCP valide le service, associe l'identifiant du compte WebUI à un acteur fictif, puis contrôle séparément sa cible.

**Limite majeure.** L'identité individuelle n'est pas une délégation cryptographiquement signée de bout en bout : si le secret technique et l'accès interne sont compromis, une usurpation reste envisageable. En production, réexaminer OIDC/OAuth et les identités de service.

**Traçabilité.** D03 ; [demonstrateur/server.py](../demonstrateur/server.py) (`ServiceIdentityGate`), [demonstrateur/bootstrap.py](../demonstrateur/bootstrap.py), [`ARCHITECTURE.md`](ARCHITECTURE.md).

### ADR-04 — Contrôler les permissions dans le serveur RH, pas dans le LLM

**Problème.** La visibilité d'un salarié dans l'annuaire ne donne pas le droit de lire son solde ; un manager ne reçoit pas automatiquement les soldes de toutes les équipes du tenant.

**Options.** (A) Permissions larges par rôle ou trust du LLM : rapides, mais non défendables. (B) Moteur générique d'ABAC externe : extensible, mais surplus technique pour cinq fixtures. (C) Contrôles déterministes **tenant + objet + relation hiérarchique + champs** dans MCP : simples et testables.

**Décision.** C, inspirée de RBAC/ABAC sans prétendre avoir construit un moteur générique. L'annuaire est filtré avant réponse ; le solde est limité à soi ou au subordonné direct. Les refus exposent `unavailable` à l'appelant tout en conservant le motif précis dans l'audit minimal.

**Preuve.** Branches explicites dans `fixtures.py` ; essais directs et intégrés rapportés pour autorisation Alice, refus Claire et inter-tenant Bob. Un refus observé dans le chat ne suffit pas seul : le jugement repose aussi sur le retour MCP et son journal.

**Traçabilité.** D04, ADR-C04 ; [demonstrateur/fixtures.py](../demonstrateur/fixtures.py), [demonstrateur/server.py](../demonstrateur/server.py).

---

## II. Choix du modèle, fiabilité et injection indirecte

### ADR-05 — Qwen3.5 9B comme modèle principal, Gemma comme repli envisagé

**Problème.** Trouver un équilibre entre capacité d'appel d'outils, coût GPU, latence et qualité observée, sur une machine de démonstration limitée en VRAM.

**Options.** Plusieurs candidats ont été présélectionnés ; une comparaison contrôlée s'est concentrée notamment sur Qwen3.5 9B Q4_K_M et Gemma 4 12B. Un modèle plus petit serait moins exigeant, sans supériorité démontrée sur les parcours critiques. Gemma n'a pas été déployée en parallèle ni configurée comme failover automatique.

**Décision.** Qwen3.5 9B principal, quantifié Q4_K_M, avec paramètres d'inférence bornés et digest vérifié. Les scores rapportés dans C1 étaient **10/11** pour les deux modèles sur les cas exécutables ; la petite taille de l'échantillon ne prouve aucune supériorité générale. Qwen utilisait moins de ressources dans ces mesures : pic GPU d'environ **8 249 Mio** contre **10 755 Mio** pour Gemma ; médianes client proches d'environ **1,575–1,576 s**. Ce sont des observations contextuelles, pas des garanties universelles de performance.

**Objection et réponse.** Qwen peut interrompre un parcours après la recherche. Changer automatiquement pour Gemma ne résout pas nécessairement un défaut partagé, ni une lacune d'habilitation ou de finalité. Réouvrir uniquement avec comparaison de non-régression et bénéfice mesuré.

**Traçabilité.** D08 ; [demonstrateur/settings.py](../demonstrateur/settings.py), [demonstrateur/model/](../demonstrateur/model/), [`QUALIFICATION.md`](QUALIFICATION.md).

### ADR-06 — Limiter les conséquences d'une prompt injection sans promettre l'immunité

**Problème.** Une note RH ou une pièce jointe est une **donnée non fiable**. Elle peut contenir une instruction qui incite le modèle à consulter une autre personne ou à inventer un solde.

**Options.** (A) Consignes au seul LLM : utiles pour guider, insuffisantes comme frontière déterministe. (B) ACL métier MCP + réduction des outils/champs + séparation instructions/données : protections complémentaires réellement présentes. (C) Approbation humaine de chaque appel : coût UX, risque d'approbation automatique et couverture à prouver. (D) Périmètre de tâche déterministe pré-dispatch, relié à l'utilisateur et au tour authentifiés : protection potentiellement plus forte, mais exige une identité de tour fiable et une requalification importante.

**Décision de remise.** Socle B, consignes A en complément ; ni C systématique, ni D pleinement implémenté. Ne pas confondre une demande **autorisée par ACL** avec une demande **effectivement sollicitée dans ce tour**.

**Preuve et limites.** Un essai documenté dans la candidate corrigée a exposé un texte hostile à Qwen sans appel non sollicité observé ; verdict **PASS borné sur ce scénario**, pas résistance générale. Des observations historiques avaient montré qu'un modèle pouvait proposer une lecture de Léa, personne pourtant autorisée à Marc. La finalité du tour demeure donc un risque distinct des droits métier. Ce qui reste non démontré ne doit pas être formulé comme une protection acquise.

**Traçabilité.** D05, ADR-C04 ; [demonstrateur/settings.py](../demonstrateur/settings.py), [demonstrateur/server.py](../demonstrateur/server.py), [`PRODUCTION.md`](PRODUCTION.md).

### ADR-07 — Ne pas promouvoir une continuation forcée qui régressait ailleurs

**Problème.** Certains tours Qwen se terminaient après `search_employee` sans poursuivre jusqu'à `get_leave_balance`. Une continuation déterministe aurait amélioré le cas Claire, mais elle ne devait pas transformer les simples demandes d'explication en requêtes RH.

**Options.** (A) Profil Qwen/WebUI avec correction bornée, sans orchestrateur supplémentaire. (B) Prototype B2 de dispatch/continuation forcée : amélioration ciblée, mais deux anomalies P1 reproduites dans 13 microtests simulés : demande de clarification à la place d'une explication et contrôle tardif d'une identité contradictoire. (C) Nouvelle architecture de vérification pré-appel : perspective à étudier, pas un composant qualifié.

**Décision.** Conserver A pour la remise corrigée. **B2 et Gemma ne sont pas promus**. Un cas multi-outils réussi (recherche Léa puis solde 8 dans une même demande) démontre une capacité, pas une garantie sur toutes les formulations.

**Leçon.** Un gain ciblé n'annule pas une régression sur des cas adjacents, notamment quand elle affecte le moment où un droit est contrôlé. Une correction d'orchestration doit être évaluée sur la complétude, les explications, l'identité et la sécurité **ensemble**.

**Traçabilité.** REG-05, ADR-C03 ; [demonstrateur/settings.py](../demonstrateur/settings.py), [`QUALIFICATION.md`](QUALIFICATION.md).

---

## III. Stockage, démarrage, réseau et sûreté de fonctionnement

### ADR-08 — Privilégier le stockage proportionné et la persistance explicite

**Problème.** Comptes, conversations, modèle et secrets doivent survivre à la recréation des conteneurs, sans introduire une base ou un SI RH inutile pour cinq personnes fictives.

**Options.** (A) SQLite intégrée à WebUI + volumes nommés + fixtures RH versionnées. (B) PostgreSQL WebUI et/ou RH : mieux adapté à certaines architectures distribuées, mais plus de composants, de secrets, de provisioning et de maintenance. (C) Pas de persistance : simple mais ne satisfait pas les scénarios de reprise.

**Décision.** A : SQLite WebUI dans son volume, fixtures Python pour les données RH, volume des modèles, volumes d'initialisation, d'identité et d'audit séparés. Ne pas assimiler volume Docker à sauvegarde ou à réplication multi-hôtes.

**Preuve et limites.** Persistance de comptes, grants, conversations et poids rapportée après reprise bornée ; restauration complexe et haute disponibilité **non démontrées**. En production, externaliser l'état, sauvegarder et tester la restauration.

**Traçabilité.** D06 ; [demonstrateur/compose.yaml](../demonstrateur/compose.yaml), [demonstrateur/fixtures.py](../demonstrateur/fixtures.py), [`ARCHITECTURE.md`](ARCHITECTURE.md).

### ADR-09 — Automatiser l'initialisation plutôt que livrer un état opaque

**Problème.** Réduire au minimum les actions administratives après `docker compose up --build -d`, initialiser comptes, secrets, modèle et outils, et préserver les mêmes identités lors des reprises.

**Options.** (A) Configurer WebUI par clics : lisible, mais non autonome. (B) Distribuer une base préremplie : fragile, opaque, risque de secrets/UUID réutilisés. (C) Variables d'environnement seules : utiles, mais toutes les ressources applicatives ne sont pas couvertes. (D) Outil externe lourd : disproportionné pour le PoC. (E) Paramètres natifs + trois jobs Compose (`init`, `seed`, `bootstrap`) + contrôles d'identité : retenu.

**Décision.** E, avec dépendances de santé et d'achèvement, création des objets absents, refus des divergences d'identité et préservation des volumes.

**Preuve et réserve importante.** Sur le poste qualifié, une invocation Compose a conduit trois jobs au code 0 et quatre services à l'état sain. Les bases OCI requises sont dans le ZIP technique et les images tierces étaient déjà en cache. **Dans chaque nouvelle conversation WebUI, l'utilisateur doit encore sélectionner Qwen et activer l'outil THIGA RH**, comme le README le précise : ne pas prétendre que l'expérience de chat est entièrement « zéro clic ».

**Traçabilité.** D07, ADR-C06 ; [demonstrateur/compose.yaml](../demonstrateur/compose.yaml), [demonstrateur/init.py](../demonstrateur/init.py), [demonstrateur/bootstrap.py](../demonstrateur/bootstrap.py), [demonstrateur/seed.sh](../demonstrateur/seed.sh).

### ADR-10 — Donner `NET_ADMIN` au garde, pas à WebUI

**Problème.** Une inférence locale ne suffit pas à démontrer que des prompts RH ne peuvent sortir via une application exposant des fonctionnalités réseau. Un réseau Docker interne n'interdit pas à lui seul toute sortie des composants frontaux.

**Options.** (A) Confiance dans les paramètres offline et les seuls réseaux privés : faible garantie. (B) Octroyer des capacités réseau privilégiées au processus WebUI : surface d'attaque excessive. (C) Garde spécialisé, port loopback, règles `nftables` de refus par défaut et WebUI dans le namespace partagé, sans capacités supplémentaires : retenu.

**Décision.** C. Seul le garde dispose de `NET_ADMIN` ; WebUI partage son namespace et attend la validation du ruleset avant ouverture. Le téléchargement des poids est isolé dans un service `seed` et un réseau distinct.

**Preuves et limites.** Six sondes locales de sorties IPv4/HTTP/DNS avec témoins ont été bloquées dans le périmètre testé ; **E05 reste PARTIEL**. IPv6 public routable, DoH, proxies, sorties réelles vers un récepteur contrôlé et navigateur Windows ne sont pas intégralement couverts. La CSP réduit certains chargements du navigateur mais n'en fait pas un namespace protégé par nftables.

**Traçabilité.** E05, ADR-C04 ; [demonstrateur/guard/](../demonstrateur/guard/), [demonstrateur/compose.yaml](../demonstrateur/compose.yaml), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`QUALIFICATION.md`](QUALIFICATION.md).

### ADR-11 — Verrouiller les dépendances et distinguer distribution du modèle et inférence

**Problème.** Une image ou un tag modèle qui change silencieusement peut compromettre la reproductibilité. À l'inverse, livrer tous les poids et toutes les images en Git serait inutilement lourd et poserait des questions de redistribution.

**Options.** (A) Versions flottantes ou tags seuls : simples, identité insuffisante. (B) Versions/digests vérifiés, layouts OCI de deux bases applicatives, SHA des fichiers et manifeste Qwen : retenu. (C) Reconstruction libre des bases depuis recettes : utile à terme, mais non prouvée équivalente aux digests scellés.

**Décision.** B dans le ZIP technique. Le service `seed` télécharge les poids via sa propre frontière réseau ; l'inférence RH reste locale. Un correctif a réconcilié un wrapper Ollama et le manifeste canonique sans affaiblir le contrat de digest.

**Preuve et limites.** Les manifestes et SHA du paquet technique ont été vérifiés ; les images Open WebUI/Ollama externes étaient déjà en cache au test Compose final. Aucune qualification complète de l'acquisition sur un second moteur vierge.

**Traçabilité.** D06/D08, ADR-C06/C07 ; [`BUILD.md`](BUILD.md), [demonstrateur/model/](../demonstrateur/model/), [demonstrateur/compose.yaml](../demonstrateur/compose.yaml).

### ADR-12 — Révoquer une session WebSocket sans interrompre les autres

**Problème.** Un logout HTTP pouvait invalider l'usage futur du jeton tout en laissant une socket déjà connectée recevoir des événements ; une ancienne copie du registre pouvait aussi réadmettre une session.

**Options.** (A) Logout HTTP uniquement : insuffisant pour sockets existantes. (B) Déconnecter toutes les sessions du compte : plus simple, mais perturbe les sessions légitimes. (C) Révocation ciblée avec registre SQLite, témoin de génération, contrôle fail-closed et fermeture des sockets du jeton : retenue. (D) Registre/IdP externe : option plus adaptée au distribué, mais complexe pour le PoC.

**Décision.** C dans la candidate corrigée ; la V1 n'a pas été modifiée silencieusement.

**Preuve.** Dans les essais rapportés avant correction, 365 événements étaient encore reçus après logout. Après correction, zéro contenu après acquittement sur la socket révoquée pendant que la session témoin recevait 406 événements ; HTTP 401 sur jetons révoqués. **IAM-03 PASS borné**.

**Limites.** Hypothèses mono-worker et stockage local ; un rollback **cohérent simultané** du registre et du témoin avec la même clé, ainsi que des ordonnancements distribués, ne sont pas éliminés par ces essais.

**Traçabilité.** ADR-C02 ; [demonstrateur/webui_patch/auth.py](../demonstrateur/webui_patch/auth.py), [demonstrateur/webui_patch/socket_main.py](../demonstrateur/webui_patch/socket_main.py), [demonstrateur/webui_patch/thiga_revocation.py](../demonstrateur/webui_patch/thiga_revocation.py), [`QUALIFICATION.md`](QUALIFICATION.md).

### ADR-13 — Conserver des traces suffisantes sans reproduire les données RH

**Problème.** Le jury doit pouvoir attribuer une décision à une identité, un outil et un résultat, sans exposer prompts, jetons, mots de passe ou dossiers RH dans les journaux.

**Options.** (A) Journaux verbeux de toutes les entrées/sorties : audit apparent, risque de fuite élevé. (B) Aucun audit : impossible d'expliquer un refus. (C) Événements MCP avec date, acteur, outil, motif et identifiant de corrélation, rotation et volume dédié : retenu.

**Décision.** C. Les résultats d'essais sont croisés avec les journaux d'appels et les observations de la conversation ; les motifs `relationship_denied` et `tenant_denied` ne sont pas présentés à l'utilisateur comme explication détaillée de ses permissions.

**Limites.** La corrélation n'est pas un mécanisme d'authentification. La politique de rétention, l'export centralisé et la résistance aux falsifications demanderaient une solution de production.

**Traçabilité.** D11/ADR-C04 ; [demonstrateur/server.py](../demonstrateur/server.py), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`QUALIFICATION.md`](QUALIFICATION.md).

---

## IV. Stratégie de qualification, version et distribution

### ADR-14 — Réparer le candidat corrigé sans effacer la baseline V1

**Problème.** Une amélioration ponctuelle n'autorise pas à remplacer une version de remise par une variante insuffisamment testée. À l'inverse, conserver une version dont des défauts importants sont connus n'est plus optimal après correction et requalification.

**Options.** (A) Livrer V1 historique : identité préservée, mais défauts IAM-03/REG-05 précédemment observés. (B) Livrer la candidate corrigée séparément, après contrôles ciblés et reprise des parcours Docker : retenue après les preuves du 9 novembre. (C) Promouvoir B2/Gemma : bénéfices expérimentaux ciblés mais non-régression et requalification incomplètes.

**Décision et évolution.** **Le 8 novembre : V1 recommandée. Le 9 novembre : candidate corrigée retenue.** Changement déterminant : remédiations IAM-03/REG-05 et qualification Compose/F01 sur les octets corrigés. La V1 demeure inchangée et archivée ; B2 demeure non promu.

**Limites.** Cette décision vaut pour les scénarios et le poste testés ; le statut global est **GO sous réserves**, non certification de sécurité/production.

**Traçabilité.** ADR-C01/C03 ; [`QUALIFICATION.md`](QUALIFICATION.md).

### ADR-15 — Tester une commande Compose réelle, sans masquer ses conditions

**Problème.** Pour un exercice notant Docker à 25 %, une succession de commandes manuelles ne prouverait pas une mise en route initiale en une commande.

**Options.** (A) Deuxième moteur Docker isolé : test potentiellement plus fort pour l'absence de cache, mais coûts GPU/WSL et comparabilité incertains. (B) Restaurer proprement le laboratoire temporaire sur le moteur connu, après contrôle de ses ressources et consentement ciblé : retenu. (C) Clore un F01 partiel : protège l'existant mais laisse l'objectif insuffisamment démontré.

**Décision et preuve.** Une invocation naturelle `docker compose up --build -d` sur **sept volumes vierges** a terminé code 0 en **167,266 s**, avec trois jobs réussis et quatre services sains. Le vérificateur d'ordre a rencontré une fenêtre de journaux incomplète ; les mêmes IDs et journaux ont été réconciliés, sans prétendre à un second démarrage caché. Verdict **F01 PASS avec réserve de portabilité**.

**Limites.** Images tierces déjà en cache ; installation sur autre PC, autre daemon, matériel ou réseau non démontrée. L'état du cache et les prérequis GPU/CIDR sont des conditions explicites, pas des détails facultatifs.

**Traçabilité.** ADR-C05/C06 ; [demonstrateur/compose.yaml](../demonstrateur/compose.yaml), [`QUALIFICATION.md`](QUALIFICATION.md).

### ADR-16 — Ne jamais convertir une matrice de tests en un score global trompeur

**Problème.** Un nombre de contrôles planifiés ou examinés ne signifie pas qu'ils ont tous réussi.

**Décision.** Maintenir les états testés séparément, et publier seulement la portée adéquate. La qualification finale de la candidate corrigée couvre **106 identifiants**, mais aboutit à **46 PASS exécutés, 4 PASS historiques, 45 PARTIEL, 8 BLOQUÉS_PRÉREQUIS, 2 BLOQUÉS_PLATEFORME et 1 NON EXÉCUTÉ**. L'absence de FAIL dans la matrice finale ne transforme pas les contrôles bloqués en PASS. Des changements de statut reflètent aussi l'évolution des oracles, pas nécessairement des régressions produit.

**Exemples de limites visibles.** E05 confinement partiel ; E09 disponibilité/reprise partielle ; D05 scénario hostile borné ; APP-01 et SECX-04 non qualifiés à cause de restrictions de plateforme ; portabilité sur autre machine non prouvée.

**Pourquoi.** Les preuves sont un actif du projet à condition de ne pas les surinterpréter. Voir la description concise dans [`QUALIFICATION.md`](QUALIFICATION.md) ; les pièces brutes et historiques ne sont pas publiées ici.

**Traçabilité.** D11, ADR-C06 ; matrice interne de qualification 106 contrôles ; [`QUALIFICATION.md`](QUALIFICATION.md).

### ADR-17 — Conserver une remise scellée et publier le code séparément

**Problème.** Modifier les octets de la livraison après les tests invaliderait le lien direct entre artefact et preuve. Publier publiquement toutes les couches tierces pourrait aussi exiger des vérifications de redistribution distinctes.

**Options.** (A) Retoucher le ZIP qualifié pour aligner toutes les notes : rompt l'identité déjà testée. (B) Préserver le ZIP scellé, ajouter une enveloppe documentaire, publier sur GitHub les sources et notices, distribuer les bases OCI avec le ZIP par le canal de remise : retenu. (C) Publier les OCI via une Release publique : non validé en raison des obligations de redistribution non entièrement établies.

**Décision.** Paquet technique identique aux sources qualifiées ; V1 préservée ; dépôt GitHub public séparé. Le clone **seul** n'est pas autonome : `tools/restaurer-oci.py` restaure les deux bases OCI **à partir du ZIP remis**, après contrôle des empreintes. La restauration a été vérifiée hors Docker ; un démarrage complet depuis cette copie GitHub n'a pas été rejoué.

**Conséquence pour le jury.** Le lien GitHub sert à consulter le code ; le ZIP complet est indispensable pour reproduire la candidate testée. Ne pas promettre un clone autonome.

**Traçabilité.** ADR-C07 ; [`BUILD.md`](BUILD.md), [`../README.md`](../README.md), `../tools/restaurer-oci.py`.

---

## V. Limites de l'agent et trajectoire de production

### ADR-18 — Nommer exactement le niveau d'agentivité

**Problème.** L'appellation « agent IA » peut laisser supposer une planification autonome, plusieurs agents spécialisés ou une capacité de décision métier indépendante.

**Décision.** Présenter l'artefact comme un **assistant RH conversationnel outillé** : Qwen sélectionne des appels aux outils, WebUI les orchestre, MCP exécute les validations et les lectures. Il ne s'agit pas d'une architecture multiagent propriétaire ni d'un moteur de workflow RH autonome. Ce bornage est volontaire pour réduire les effets et démontrer les autorisations.

**Compromis.** Moins de fonctionnalités autonomes, mais un comportement plus intelligible et un meilleur contrôle des données sensibles. La fiabilité conversationnelle reste probabiliste : des parcours multi-outils peuvent être incomplets.

**Traçabilité.** ADR-C08 ; [`ARCHITECTURE.md`](ARCHITECTURE.md), [`QUALIFICATION.md`](QUALIFICATION.md).

### ADR-19 — Kubernetes managé comme trajectoire, pas comme composant livré

**Problème.** L'exercice demande d'envisager l'industrialisation d'une plateforme multi-entreprises, alors que le PoC est mono-poste, local et non conçu pour 500 000 utilisateurs simultanés.

**Options.** (A) Développer un cluster complet pour l'exercice : effort disproportionné et nouvelles exigences de sécurité. (B) Documenter une trajectoire progressive de Kubernetes managé, avec validations avant données réelles : retenu. (C) Affirmer qu'un simple `docker compose` réplique la production : non retenu.

**Cible proposée, non déployée.** Ingress privé TLS/SSO, workloads séparés, MCP et Ollama en `ClusterIP`, identités de workload et assertions utilisateur vérifiables, politiques ingress/egress via CNI, pool GPU NVIDIA dédié, volumes et secrets administrés, base persistante externalisée, sauvegardes et audit par tenant, monitoring et pilotes de charge. La séparation de ressources de production ne reprend pas mécaniquement les sept conteneurs du PoC.

**Fournisseurs.** 3DS OUTSCALE OKS est un **candidat conditionnel de pilote en France** ; OVHcloud Managed Kubernetes une alternative à comparer. Ni disponibilité GPU, ni périmètre de qualification de toutes les briques, ni conditions contractuelles, ni prix n'ont été qualifiés en exploitation réelle. Si un managé ne satisfait pas les exigences de souveraineté, explorer une infrastructure qualifiée avec plus de charge d'exploitation. Aucune homologation ou installation Kubernetes n'est revendiquée.

**Traçabilité.** D09/D10, ADR-C08 ; [`PRODUCTION.md`](PRODUCTION.md).

### ADR-20 — Classifier le risque réglementaire par usage et non par étiquette « RH »

**Problème.** Une simple consultation d'annuaire ou de solde n'a pas la même finalité ni les mêmes effets qu'une sélection de candidats, une évaluation de salariés ou une recommandation de licenciement.

**Décision méthodologique.** Documenter la finalité effectivement implémentée et **réévaluer la classification** si des fonctions influant sur des décisions de personnel sont ajoutées. Distinguer rôles fournisseur/déployeur, transparence du chatbot, obligations RGPD (base légale, minimisation, accès, conservation, transferts, AIPD éventuelle) et obligations AI Act applicables selon l'usage. Une localisation française n'est pas, à elle seule, une preuve de conformité ou de souveraineté.

**Limite.** Analyse d'orientation pour un cas fictif ; pas une analyse d'impact juridique validée, pas de déploiement de données RH réelles. Les dates de mise en application et les contrats doivent être revalidés à la date d'un projet opérationnel.

**Traçabilité.** D12, ADR-C08 ; [`PRODUCTION.md`](PRODUCTION.md).

---

## Points de vérification et limites transversales

1. **Lecture autorisée ≠ lecture demandée.** Les ACL MCP protègent l'habilitation métier ; une injection peut viser un collègue effectivement autorisé à Marc mais absent de la demande du tour. La restriction déterministe de finalité n'est **pas** une fonctionnalité qualifiée de la livraison.
2. **Local ≠ étanche.** Une inférence locale évite un fournisseur de génération externe pendant le traitement, mais n'établit pas l'absence de tous les chemins de sortie : navigateur, proxy, DoH, IPv6 et chaîne de téléchargement sont des frontières distinctes.
3. **Healthy ≠ métier validé.** Les états Docker et les essais navigateur/MCP doivent être lus ensemble ; les résultats sont limités aux configurations et scénarios rapportés.
4. **Volume ≠ sauvegarde ; copie de code ≠ exécutable autonome.** Les poids et images nécessaires ne sont pas dans le dépôt GitHub public.
5. **Nombre de contrôles ≠ nombre de PASS.** La matrice de 106 identifiants conserve volontairement ses PARTIEL et blocages.
6. **Proposition Kubernetes ≠ production déployée.** La cible est conditionnelle à une étude de sécurité, d'exploitation, de résidence, de disponibilité GPU et de conformité.

## Index de lecture

- [Vue rapide et instructions](../README.md)
- [Architecture réelle et frontières de confiance](ARCHITECTURE.md)
- [Construction, dépendances et digests](BUILD.md)
- [Résultats et limites de qualification](QUALIFICATION.md)
- [Production, Kubernetes, souveraineté et AI Act](PRODUCTION.md)
- [Schéma de l'architecture cible Kubernetes (proposition non déployée)](ARCHITECTURE-CIBLE-KUBERNETES.md)
- [Composants tiers et attributions](../THIRD-PARTY-NOTICES.md)

> **Portée des sources :** cette synthèse réconcilie les choix D01–D12 et ADR-C01–C08 avec le code/configuration du commit public `6d8471a` et les rapports documentaires de la livraison corrigée. Les sources historiques privées contiennent davantage d'incidents, de versions expérimentales et de propositions non retenues. Il ne s'agit ni de leur publication intégrale, ni d'une certification d'exhaustivité absolue sur toutes les conversations et archives du projet.