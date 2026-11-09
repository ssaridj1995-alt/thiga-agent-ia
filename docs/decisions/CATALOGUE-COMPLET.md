# THIGA — Catalogue détaillé des choix et variantes

> **Catalogue public de traçabilité.** Ce catalogue regroupe **173 unités de description**, et non 169 décisions indépendantes ratifiées. Les sources référencées appartiennent à la documentation de travail ; le lecteur public ne doit pas les confondre avec des tests reproduits par lui-même.

Les **20 dossiers narratifs** sont dans [le registre principal](../DECISIONS.md). Ce catalogue ajoute les choix fins, les limites de qualification et les exclusions sans altérer la synthèse principale.

## Métier — 18 unités

- **TH-D-001** · **MAJEURE** · Retenir un assistant RH de consultation plutôt qu'un agent généraliste multi-actions. *Référence : D01.*
- **TH-D-002** · **MAJEURE** · Préférer un scénario manager/équipe à une mono-identité insuffisamment discriminante. *Référence : D01.*
- **TH-D-003** · **MAJEURE** · Comparer séparation intra-entreprise et isolation entre entreprises clientes. *Référence : D01.*
- **TH-D-004** · **SECONDAIRE** · Utiliser uniquement des salariés et soldes synthétiques pour les démonstrations. *Référence : D01.*
- **TH-D-005** · **SECONDAIRE** · Utiliser cinq salariés fictifs répartis entre deux tenants. *Référence : D01.*
- **TH-D-006** · **SECONDAIRE** · Maintenir un rôle manager et plusieurs personnes de son équipe et hors équipe. *Référence : D01.*
- **TH-D-007** · **MAJEURE** · Limiter l'outillage RH à la recherche d'employé et au solde de congés. *Référence : D04.*
- **TH-D-008** · **SECONDAIRE** · Exclure les mutations RH (écriture de congés, approbations, CRUD) du PoC. *Référence : D04.*
- **TH-D-009** · **SECONDAIRE** · Différencier annuaire interne et accès aux soldes, plus sensibles. *Référence : D04.*
- **TH-D-010** · **SECONDAIRE** · Limiter l'annuaire aux champs professionnels minimaux. *Référence : D04.*
- **TH-D-011** · **FINE** · Normaliser les recherches d'annuaire par casse et espaces. *Référence : D04.*
- **TH-D-012** · **FINE** · Retenir la recherche exacte normalisée plutôt que la recherche floue ou libre. *Référence : D04.*
- **TH-D-013** · **FINE** · Limiter les réponses de recherche à cinq résultats. *Référence : D04.*
- **TH-D-014** · **MAJEURE** · Refuser une consultation de solde hors tenant avant retour des données. *Référence : D04.*
- **TH-D-015** · **MAJEURE** · Autoriser le manager uniquement pour les subordonnés directs, pas tous les salariés du tenant. *Référence : D04.*
- **TH-D-016** · **SECONDAIRE** · Autoriser chaque salarié à consulter son propre solde. *Référence : D04.*
- **TH-D-017** · **SECONDAIRE** · Retourner une réponse publique uniforme unavailable pour les refus et cibles inconnues. *Référence : D04.*
- **TH-D-018** · **HISTORIQUE / OPTION ÉTUDIÉE** · Reporter l'extension staffing/CV/intercontrat au lieu de complexifier les habilitations. *Référence : D04.*

## Outils — 9 unités

- **TH-D-019** · **MAJEURE** · Retenir MCP natif Streamable HTTP plutôt que mcpo / proxy OpenAPI. *Référence : D02.*
- **TH-D-020** · **MAJEURE** · Distinguer serveur MCP Python, orchestration WebUI et inférence Ollama. *Référence : D02.*
- **TH-D-021** · **SECONDAIRE** · Exposer les deux outils MCP par un catalogue fixe et versionné. *Référence : D02.*
- **TH-D-022** · **FINE** · Utiliser des contrats d'arguments stricts avec champs supplémentaires interdits. *Référence : D02.*
- **TH-D-023** · **FINE** · Conserver un serveur MCP HTTP stateless pour la démonstration. *Référence : D02.*
- **TH-D-024** · **SECONDAIRE** · Ne pas autoriser des noms d'outils, URL, commandes ou requêtes SQL arbitraires depuis le modèle. *Référence : D02.*
- **TH-D-025** · **HISTORIQUE / OPTION ÉTUDIÉE** · Garder mcpo comme repli conditionnel si le MCP natif se révélait non fiable. *Référence : D02.*
- **TH-D-026** · **SECONDAIRE** · Faire exécuter l'appel RH par WebUI et les autorisations par MCP, non par Ollama. *Référence : D02.*
- **TH-D-027** · **SECONDAIRE** · Corréler les requêtes WebUI et les décisions du serveur pour démontrer un E2E réel. *Référence : D02.*

## Identité — 12 unités

- **TH-D-028** · **MAJEURE** · Ne jamais accepter l'ID employé demandé comme preuve d'identité de l'appelant. *Référence : D03.*
- **TH-D-029** · **MAJEURE** · Transmettre un identifiant de compte provenant du backend WebUI authentifié. *Référence : D03.*
- **TH-D-030** · **MAJEURE** · Exiger séparément une authentification Bearer du service appelant MCP. *Référence : D03.*
- **TH-D-031** · **SECONDAIRE** · Résoudre l'identifiant technique WebUI vers un acteur et son tenant dans l'état MCP. *Référence : D03.*
- **TH-D-032** · **SECONDAIRE** · Rejeter l'absence, duplication ou incohérence du Bearer et de l'identité serveur. *Référence : D03.*
- **TH-D-033** · **SECONDAIRE** · Ne pas publier directement le serveur MCP sur le poste hôte. *Référence : D03.*
- **TH-D-034** · **SECONDAIRE** · Restreindre l'accès réseau au MCP en complément de la protection applicative. *Référence : D03.*
- **TH-D-035** · **HISTORIQUE / OPTION ÉTUDIÉE** · Ne pas considérer un JWT utilisateur signé comme une délégation OAuth équivalente. *Référence : D03.*
- **TH-D-036** · **CIBLE NON DÉPLOYÉE** · Étudier OAuth/OIDC et une identité de workload pour production multi-service. *Référence : D03/D09.*
- **TH-D-037** · **SECONDAIRE** · Utiliser les IDs de message/chat pour corrélation, jamais seuls comme authentification. *Référence : D03.*
- **TH-D-038** · **SECONDAIRE** · Mettre en quarantaine les identités inconnues plutôt que réattribuer silencieusement un utilisateur. *Référence : D03.*
- **TH-D-039** · **HISTORIQUE / OPTION ÉTUDIÉE** · Écarter une façade d'identité supplémentaire au PoC faute de nécessité démontrée. *Référence : D03.*

## Injection — 16 unités

- **TH-D-040** · **MAJEURE** · Séparer autorisation métier, identité et fidélité à l'intention de la demande. *Référence : D05.*
- **TH-D-041** · **MAJEURE** · Traiter toute fiche RH et pièce jointe comme donnée non fiable, non comme instruction. *Référence : D05.*
- **TH-D-042** · **SECONDAIRE** · Maintenir les protections déterministes dans MCP même si le modèle suit une instruction hostile. *Référence : D05.*
- **TH-D-043** · **SECONDAIRE** · Limiter les outils accessibles au modèle pour réduire la surface d'action. *Référence : D05.*
- **TH-D-044** · **SECONDAIRE** · Minimiser les champs de données renvoyés au modèle. *Référence : D05.*
- **TH-D-045** · **SECONDAIRE** · Imposer une provenance MCP du tour pour toute valeur chiffrée de solde déclarée. *Référence : D05.*
- **TH-D-046** · **MAJEURE** · Ne pas déclarer que les ACL empêchent une lecture non sollicitée mais légitimement autorisée. *Référence : D05.*
- **TH-D-047** · **HISTORIQUE / OPTION ÉTUDIÉE** · Écarter le filtre documentaire M08 après régressions métier et stress mémoire. *Référence : D05.*
- **TH-D-048** · **HISTORIQUE / OPTION ÉTUDIÉE** · Différer le contrôle de finalité pré-appel lié au tour faute de garantie fiable de provenance. *Référence : D05.*
- **TH-D-049** · **HISTORIQUE / OPTION ÉTUDIÉE** · Privilégier le socle A et des essais B ciblés plutôt qu'une protection expérimentale non qualifiée en routine. *Référence : D05.*
- **TH-D-050** · **SECONDAIRE** · Distinguer exposition réelle au LLM, affichage navigateur et simple extraction de fichier. *Référence : D05.*
- **TH-D-051** · **HISTORIQUE / OPTION ÉTUDIÉE** · Écarter l'usage de display_file comme preuve d'une lecture effective du contenu. *Référence : D05.*
- **TH-D-052** · **HISTORIQUE / OPTION ÉTUDIÉE** · Ne pas imposer systématiquement une approbation humaine à chaque appel RH. *Référence : D05.*
- **TH-D-053** · **HISTORIQUE / OPTION ÉTUDIÉE** · Ne pas ajouter un second LLM de classification de périmètre au PoC. *Référence : D05.*
- **TH-D-054** · **SECONDAIRE** · Qualifier les documents hostiles avec des témoins bénins et une preuve de lecture avant verdict. *Référence : D05.*
- **TH-D-055** · **SECONDAIRE** · Éviter de généraliser un succès anti-injection obtenu sur un seul scénario documentaire. *Référence : D05.*

## Modèle — 17 unités

- **TH-D-056** · **MAJEURE** · Construire une longue liste multi-familles plutôt que choisir automatiquement Qwen. *Référence : D08.*
- **TH-D-057** · **MAJEURE** · Comparer localement quatre modèles sur le même jeu RH et le GPU réel. *Référence : D08.*
- **TH-D-058** · **MAJEURE** · Retenir Qwen3.5 9B Q4_K_M comme principal. *Référence : D08.*
- **TH-D-059** · **HISTORIQUE / OPTION ÉTUDIÉE** · Ne pas promouvoir Gemma 4 12B malgré certains succès ponctuels sur Claire. *Référence : D08.*
- **TH-D-060** · **SECONDAIRE** · Prévoir Gemma comme repli manuel conditionnel, sans failover automatique. *Référence : D08.*
- **TH-D-061** · **SECONDAIRE** · Ne charger qu'un modèle à la fois pour maîtriser VRAM et causalité des tests. *Référence : D08.*
- **TH-D-062** · **SECONDAIRE** · Évaluer tool calling, fidélité MCP, mémoire, latence, sûreté et français. *Référence : D08.*
- **TH-D-063** · **SECONDAIRE** · Ne pas déduire d'un benchmark externe des performances dans WebUI. *Référence : D08.*
- **TH-D-064** · **SECONDAIRE** · Écarter RH09 de la comparaison stricte faute de six correspondances possibles. *Référence : D08.*
- **TH-D-065** · **SECONDAIRE** · Conserver les écarts de mémoire/VRAM et les appels superflus comme critères déterminants. *Référence : D08.*
- **TH-D-066** · **SECONDAIRE** · Fixer le tag ET le digest du manifeste Ollama, et refuser un tag incorrect. *Référence : D08.*
- **TH-D-067** · **SECONDAIRE** · Borner think=false, num_ctx 8192, num_predict 1024, température 0 et seed42. *Référence : D08.*
- **TH-D-068** · **FINE** · Borner top_k=64 et top_p=0.95 dans le profil Qwen final. *Référence : D08.*
- **TH-D-069** · **SECONDAIRE** · Privilégier le bon service utile et la marge matériel à la taille brute du modèle. *Référence : D08.*
- **TH-D-070** · **HISTORIQUE / OPTION ÉTUDIÉE** · Ne pas retenir le 4B comme substitut automatique du 9B contraint. *Référence : D08.*
- **TH-D-071** · **HISTORIQUE / OPTION ÉTUDIÉE** · Interrompre M10 au seuil RAM prédéfini plutôt que poursuivre vers un OOM. *Référence : D08.*
- **TH-D-173** · **HISTORIQUE / OPTION ÉTUDIÉE** · Restaurer les paramètres antérieurs du profil C0 après une vérification ponctuelle de leur persistance dans WebUI. *Référence : D08.*

## Stockage — 11 unités

- **TH-D-072** · **MAJEURE** · Garder SQLite intégré à WebUI plutôt que PostgreSQL dédié pour un PoC mono-instance. *Référence : D06.*
- **TH-D-073** · **SECONDAIRE** · Conserver la configuration, les comptes et les chats WebUI dans un volume nommé. *Référence : D06.*
- **TH-D-074** · **SECONDAIRE** · Conserver les poids Ollama dans un volume modèle distinct. *Référence : D06.*
- **TH-D-075** · **SECONDAIRE** · Utiliser des fixtures RH en lecture seule plutôt qu'une base métier additionnelle. *Référence : D06.*
- **TH-D-076** · **SECONDAIRE** · Générer localement les secrets et les maintenir stables aux redémarrages. *Référence : D06.*
- **TH-D-077** · **SECONDAIRE** · Séparer volumes d'administration, clés WebUI, état MCP, audit, modèles et signal du garde. *Référence : D06.*
- **TH-D-078** · **SECONDAIRE** · Ne pas considérer un volume nommé comme une sauvegarde ni une preuve de portabilité. *Référence : D06.*
- **TH-D-079** · **HISTORIQUE / OPTION ÉTUDIÉE** · Reporter Vault/coffre externe et rotation sophistiquée au contexte production. *Référence : D06.*
- **TH-D-080** · **FINE** · Restreindre les accès lecture/écriture aux volumes et secrets selon les services. *Référence : D06.*
- **TH-D-081** · **FINE** · Séparer et limiter les journaux MCP, sans prompts ni secrets bruts. *Référence : D06.*
- **TH-D-082** · **FINE** · Utiliser une rotation bornée des fichiers d'audit serveur. *Référence : D06.*

## Démarrage — 10 unités

- **TH-D-083** · **MAJEURE** · Automatiser l'installation avec Compose en une commande et des jobs séparés. *Référence : D07.*
- **TH-D-084** · **SECONDAIRE** · Créer les comptes, grants et connexion MCP par API WebUI plutôt que clics administrateur. *Référence : D07.*
- **TH-D-085** · **SECONDAIRE** · Éviter une base WebUI préconfigurée transplantée depuis une autre machine. *Référence : D07.*
- **TH-D-086** · **SECONDAIRE** · Préférer primitives déclaratives et bootstrap léger à un orchestrateur externe lourd. *Référence : D07.*
- **TH-D-087** · **SECONDAIRE** · Différencier service healthy et fonction RH réellement accessible. *Référence : D07.*
- **TH-D-088** · **SECONDAIRE** · Ordonner init, seed, Ollama, garde, WebUI, bootstrap et MCP par prérequis. *Référence : D07.*
- **TH-D-089** · **SECONDAIRE** · Rendre le bootstrap idempotent et refusant les divergences d'UUID/grants. *Référence : D07.*
- **TH-D-090** · **FINE** · Séparer téléchargement de poids initial et runtime d'inférence local. *Référence : D07.*
- **TH-D-091** · **FINE** · Reconnaître l'activation d'outil par utilisateur dans le chat comme étape opérateur distincte. *Référence : D07.*
- **TH-D-092** · **SECONDAIRE** · Ne pas rouvrir les secrets ou les privilèges en cas d'échec de bootstrap. *Référence : D07.*

## Réseau — 19 unités

- **TH-D-093** · **MAJEURE** · Privilégier un garde réseau dédié avec NET_ADMIN plutôt que privilégier WebUI. *Référence : E05.*
- **TH-D-094** · **MAJEURE** · Définir une politique de sortie nftables restrictive vérifiée avant lancement WebUI. *Référence : E05.*
- **TH-D-095** · **SECONDAIRE** · Écarter docker internal:true seul comme confinement effectif de tous les flux. *Référence : E05.*
- **TH-D-096** · **SECONDAIRE** · Isoler le téléchargement du seed sur un réseau distribution distinct. *Référence : E05.*
- **TH-D-097** · **SECONDAIRE** · Garder Ollama et MCP sur un réseau interne non publié. *Référence : E05.*
- **TH-D-098** · **SECONDAIRE** · Limiter l'accès hôte de WebUI au loopback 127.0.0.1:3039. *Référence : E05.*
- **TH-D-099** · **SECONDAIRE** · Faire partager le namespace réseau du garde à WebUI. *Référence : E05.*
- **TH-D-100** · **SECONDAIRE** · Retirer toutes les capacités Linux à WebUI, limiter celle du garde. *Référence : E05.*
- **TH-D-101** · **FINE** · Vérifier règles, identité de namespace et témoin de génération avant ouverture de WebUI. *Référence : E05.*
- **TH-D-102** · **FINE** · Bloquer le résolveur DNS Docker dans la politique de garde en tenant compte du NAT. *Référence : E05.*
- **TH-D-103** · **SECONDAIRE** · Ajouter une CSP restrictive pour limiter les ressources/connexions de la page. *Référence : E05.*
- **TH-D-104** · **MAJEURE** · Ne pas assimiler egress WebUI bloqué localement et protection du navigateur Windows hôte. *Référence : E05.*
- **TH-D-105** · **HISTORIQUE / OPTION ÉTUDIÉE** · Traiter échecs comparateur nftables NAT/conntrack comme incidents de preuve, sans promotion silencieuse. *Référence : E05.*
- **TH-D-106** · **HISTORIQUE / OPTION ÉTUDIÉE** · Garder WebUI fermé tant que les règles du garde ne sont pas démontrées conformes. *Référence : E05.*
- **TH-D-107** · **SECONDAIRE** · Ne pas prétendre un confinement Internet universel depuis les six sondes locales. *Référence : E05.*
- **TH-D-108** · **SECONDAIRE** · Épingler politique, digests d'images et contrôles des dépendances OCI. *Référence : E05.*
- **TH-D-170** · **SECONDAIRE** · Désactiver les intégrations externes facultatives de WebUI (API OpenAI, recherche web, interpréteur, images, OTEL, mises à jour), activer les modes hors ligne. *Référence : E05.*
- **TH-D-171** · **HISTORIQUE / OPTION ÉTUDIÉE** · Étudier un frontal pour joindre WebUI localement sans publier le serveur MCP. *Référence : E05.*
- **TH-D-172** · **HISTORIQUE / OPTION ÉTUDIÉE** · Arbitrer la conservation ou dissociation de l’instrumentation NFLOG du garde M16. *Référence : E05.*

## Révocation — 7 unités

- **TH-D-109** · **MAJEURE** · Révoquer la session ciblée, y compris ses WebSockets, plutôt que uniquement le cookie HTTP. *Référence : IAM-03.*
- **TH-D-110** · **MAJEURE** · Éviter la révocation de toutes les sessions du compte si une seule doit être coupée. *Référence : IAM-03.*
- **TH-D-111** · **SECONDAIRE** · Utiliser registre SQLite local et témoin de génération synchronisés. *Référence : IAM-03.*
- **TH-D-112** · **SECONDAIRE** · Refuser l'ouverture si registre et témoin absents ou désynchronisés. *Référence : IAM-03.*
- **TH-D-113** · **FINE** · Hacher les identifiants de jeton au lieu de les stocker directement. *Référence : IAM-03.*
- **TH-D-114** · **FINE** · Sérialiser localement la révocation et les subscriptions avant acquittement. *Référence : IAM-03.*
- **TH-D-115** · **CIBLE NON DÉPLOYÉE** · Requalifier rollback simultané registre/témoin/clé pour toute production distribuée. *Référence : IAM-03.*

## Continuité — 7 unités

- **TH-D-116** · **MAJEURE** · Reconnaître que Qwen peut s'arrêter après search_employee sans appeler le solde. *Référence : REG-05.*
- **TH-D-117** · **HISTORIQUE / OPTION ÉTUDIÉE** · Tester un profil de continuation borné sans changer les droits MCP. *Référence : REG-05.*
- **TH-D-118** · **HISTORIQUE / OPTION ÉTUDIÉE** · Tester B2 comme mécanisme de reprise automatique pour le cas Claire. *Référence : B2.*
- **TH-D-119** · **MAJEURE** · Rejeter B2 pour la remise après deux régressions P1 reproductibles. *Référence : B2.*
- **TH-D-120** · **HISTORIQUE / OPTION ÉTUDIÉE** · Écarter le fan-out aveugle de tous les outils comme solution scalable. *Référence : B2.*
- **TH-D-121** · **SECONDAIRE** · Préserver les réponses explicatives sans outil malgré le défaut de complétude. *Référence : REG-05.*
- **TH-D-122** · **HISTORIQUE / OPTION ÉTUDIÉE** · Ne pas investir 17–27 h estimées dans B2 pour la remise sans identité fiable pré-dispatch. *Référence : B2.*

## Qualification — 11 unités

- **TH-D-123** · **MAJEURE** · Distinguer exécution directe, logs de Codex, relecture critique et test indépendant. *Référence : D11.*
- **TH-D-124** · **MAJEURE** · Définir critères de PASS/FAIL/STOP avant les tests, pas après lecture des résultats. *Référence : D11.*
- **TH-D-125** · **SECONDAIRE** · Exiger un cas autorisé et un refus négatif pour l'identité et les droits. *Référence : D11.*
- **TH-D-126** · **SECONDAIRE** · Séparer validation de l'appel MCP, réponse de l'agent et rendu Chrome. *Référence : D11.*
- **TH-D-127** · **SECONDAIRE** · Distinguer données jointes lues, affichées et effectivement exposées au LLM. *Référence : D11.*
- **TH-D-128** · **SECONDAIRE** · Ne jamais déclarer 106 PASS : les deux matrices comportent des verdicts mixtes. *Référence : D11.*
- **TH-D-129** · **SECONDAIRE** · Conserver les 41 transitions de statut et les six PASS devenus PARTIEL. *Référence : D11.*
- **TH-D-130** · **SECONDAIRE** · Maintenir APP-01/SECX-04 BLOQUÉS PLATEFORME, non qualifiés. *Référence : D11.*
- **TH-D-131** · **SECONDAIRE** · Distinguer persistance F06 bornée et reprise générale E09 PARTIELLE. *Référence : E09.*
- **TH-D-132** · **HISTORIQUE / OPTION ÉTUDIÉE** · Stopper une campagne sans témoin positif/canari de confiance plutôt que conclure sur une absence d'egress. *Référence : D11.*
- **TH-D-133** · **SECONDAIRE** · Exclure RH09 du benchmark si précondition absente, sans l'attribuer à un échec de modèle. *Référence : D11.*

## Docker — 10 unités

- **TH-D-134** · **MAJEURE** · Exiger un démarrage naturel avec une seule invocation Compose sur volumes vierges. *Référence : F01.*
- **TH-D-135** · **SECONDAIRE** · Distinguer un harnais incorrect et un défaut réel du produit au premier essai. *Référence : F01.*
- **TH-D-136** · **HISTORIQUE / OPTION ÉTUDIÉE** · Comparer deuxième moteur Docker, libération ciblée laboratoire et clôture partielle. *Référence : F01.*
- **TH-D-137** · **MAJEURE** · Privilégier le nettoyage ciblé du seul laboratoire temporaire après preuve et consentement. *Référence : F01.*
- **TH-D-138** · **MAJEURE** · Ne pas effacer les laboratoires historiques ni les sources scellées pour obtenir un PASS. *Référence : F01.*
- **TH-D-139** · **SECONDAIRE** · Garder le PASS 167,266 s borné par caches tiers et environnement GPU/WSL spécifique. *Référence : F01.*
- **TH-D-140** · **SECONDAIRE** · Ne pas surqualifier l'accès HTTP 200 attesté indirectement par le harnais. *Référence : F01.*
- **TH-D-141** · **SECONDAIRE** · Préserver le ZIP technique qualifié et séparer le paquet documentaire externe. *Référence : F01.*
- **TH-D-142** · **SECONDAIRE** · Ne pas déclarer un clonage autonome lorsque les bases OCI sont absentes du GitHub. *Référence : F01.*
- **TH-D-143** · **SECONDAIRE** · Geler l'identité des bases OCI et contrôler les SHA avant toute restauration. *Référence : F01.*

## Production — 12 unités

- **TH-D-144** · **CIBLE NON DÉPLOYÉE** · Choisir un pilote Kubernetes managé français seulement après revue de toutes les frontières de souveraineté. *Référence : D09.*
- **TH-D-145** · **CIBLE NON DÉPLOYÉE** · Étudier 3DS OUTSCALE OKS sous réserve GPU, région et périmètre contractuel. *Référence : D09.*
- **TH-D-146** · **CIBLE NON DÉPLOYÉE** · Comparer OVHcloud Kubernetes et une IaaS qualifiée si le managé requis n'est pas couvert. *Référence : D09.*
- **TH-D-147** · **CIBLE NON DÉPLOYÉE** · Prévoir ingress TLS privé et SSO/OIDC pour les utilisateurs de production. *Référence : D10.*
- **TH-D-148** · **CIBLE NON DÉPLOYÉE** · Remplacer Bearer+UUID local par identité workload et assertion à audience/durée bornées. *Référence : D10.*
- **TH-D-149** · **CIBLE NON DÉPLOYÉE** · Déployer CNI/NetworkPolicies default-deny, DNS et egress internes contrôlés. *Référence : D10.*
- **TH-D-150** · **CIBLE NON DÉPLOYÉE** · Déployer pool GPU dédié, quotas, files, métriques et latence p95. *Référence : D10.*
- **TH-D-151** · **CIBLE NON DÉPLOYÉE** · Externaliser base et secrets, sauvegardes et audit avant réplication WebUI. *Référence : D10.*
- **TH-D-152** · **CIBLE NON DÉPLOYÉE** · Dimensionner sur concurrence réellement mesurée, pas sur 500 000 comptes déclarés. *Référence : D10.*
- **TH-D-153** · **CIBLE NON DÉPLOYÉE** · Classifier l'usage AI Act par finalité, pas par étiquette générale RH. *Référence : D12.*
- **TH-D-154** · **CIBLE NON DÉPLOYÉE** · Distinguer consultation de congés et décision sur embauche/performance. *Référence : D12.*
- **TH-D-155** · **CIBLE NON DÉPLOYÉE** · Associer DPO et juridique aux vérifications de base légale, minimisation et AIPD. *Référence : D12.*

## Gouvernance — 14 unités

- **TH-D-156** · **MAJEURE** · Passer de V1 à la livraison corrigée seulement après IAM-03/REG-05 et requalification. *Référence : C01.*
- **TH-D-157** · **MAJEURE** · Conserver V1 historique inchangée sans promotion physique de la candidate. *Référence : C01.*
- **TH-D-158** · **SECONDAIRE** · Sceller la version technique et contrôler ses empreintes à la remise. *Référence : C07.*
- **TH-D-159** · **SECONDAIRE** · Présenter le système comme agent conversationnel outillé, non multiagent autonome. *Référence : C08.*
- **TH-D-160** · **SECONDAIRE** · Séparer sources GitHub publiques et dépendances OCI conservées avec ZIP autorisé. *Référence : C07.*
- **TH-D-161** · **SECONDAIRE** · Éviter de publier les poids Qwen et les archives brutes sans droits/contrôles de secrets. *Référence : C07.*
- **TH-D-162** · **MAJEURE** · Conserver ADR, mémoire, carnet, START HERE et guide avec responsabilités documentaires distinctes. *Référence : METH.*
- **TH-D-163** · **MAJEURE** · Conserver l'historique append-only et qualifier les passages obsolètes par date. *Référence : METH.*
- **TH-D-164** · **MAJEURE** · Ne pas traiter les recommandations Work ou Codex comme des arbitrages de l'utilisateur. *Référence : METH.*
- **TH-D-165** · **SECONDAIRE** · Exiger des ZIP légers autonomes de preuves, sans couches OCI dupliquées. *Référence : METH.*
- **TH-D-166** · **SECONDAIRE** · Distinguer candidate, source GitHub, ZIP scellé et tests de portabilité. *Référence : METH.*
- **TH-D-167** · **SECONDAIRE** · Ne pas inférer exhaustivité historique des 174 jalons numérotés. *Référence : METH.*
- **TH-D-168** · **SECONDAIRE** · Documenter FAIL/NO-GO et pourquoi l'arbitrage a changé, sans effacer l'état antérieur. *Référence : METH.*
- **TH-D-169** · **SECONDAIRE** · Créer une documentation GitHub navigable sans recopier la mémoire maître privée. *Référence : METH.*

---

**Limite de lecture :** un paramètre observé dans le code n’est pas nécessairement une décision explicitement prise par le candidat. Les 22 paramètres sans justification précise retrouvée sont conservés dans l’annexe de réconciliation privée, et ne sont pas présentés comme des arbitrages validés.
