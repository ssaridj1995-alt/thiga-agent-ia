# Architecture du démonstrateur

![Schéma des flux, ports et contrôles](architecture.svg)

## Lecture du schéma — état réellement implémenté

Le dessin représente **la livraison technique corrigée du 9 novembre 2026** (projet Compose `thiga-corrige-20261109`), et non une architecture de production. Le port publié est **`127.0.0.1:3039`** : les anciens ports de laboratoires, notamment `3017`, relèvent de versions historiques distinctes. La représentation regroupe le traitement des messages par fonctions ; les flèches ne sont pas une chronologie exhaustive de tous les allers-retours HTTP.

| Frontière / composant | Situation constatée dans `compose.yaml` | Portée du contrôle |
|---|---|---|
| Poste / navigateur | Chrome hors des conteneurs, accès local `3039:8080` via le namespace du garde | La CSP réduit des surfaces du navigateur ; elle ne confine ni Windows, ni ses extensions, ni Docker Desktop |
| `webui-guard` | Conteneur avec `NET_ADMIN`, réseaux `private` et `frontend`, publication sur loopback | Applique nftables et expose le signal d'état ; ce n'est **pas** un proxy HTTP |
| `webui` | `network_mode: service:webui-guard`, capacités Linux retirées, montages protégés en lecture seule | Le lanceur vérifie le garde et son signal avant/pendant le fonctionnement ; le contrôle n'est pas une garantie face à toutes les voies d'egress |
| `ollama` | Service interne `11434`, GPU, volume `models`, réseau `private` | Inférence locale Qwen3.5 9B ; le modèle peut **proposer** un outil, pas autoriser un accès RH |
| `mcp` | Service Streamable HTTP `8000`, réseau `private`, volume d'identité en lecture seule | Vérifie le Bearer technique et l'en-tête utilisateur ajouté par WebUI côté backend, mappe le compte vers un acteur fictif et applique les droits tenant / relation |
| Trois jobs | `init` (aucun réseau), `seed` (réseau `distribution`), `bootstrap` (réseau `private`) | Préparent respectivement secrets/état, modèle vérifié, puis comptes et connexion d'outils ; leur ordre et leurs dépendances sont définis par Compose |

**Chaîne logique Marc → Alice.** La session Marc est authentifiée dans WebUI. WebUI soumet la demande à Ollama ; Qwen peut proposer `search_employee` et/ou `get_leave_balance`. WebUI transmet l'appel MCP avec ses éléments d'authentification **côté backend** ; MCP établit l'acteur, vérifie l'autorisation et lit la fixture fictive. Le résultat retourne à WebUI et peut être exploité par Ollama pour la formulation. Un texte indiquant « je consulte » sans `tool_call` exécuté ne constitue pas une preuve de consultation.

**Distinction nécessaire : identité ≠ cible ≠ intention.** `employee_id` est un paramètre métier proposé par l'agent, jamais une identité d'appelant ; le principal provient du backend authentifié et du mapping serveur. Le contrôle MCP refuse les objets hors des permissions, mais un appel vers une personne **autorisée sans avoir été demandée** demeure un risque de détournement D05.

**Sept volumes, non sept bases de données :** `admin` (état d'initialisation), `webkeys` (clé WebUI), `mcpstate` (identité et secret de service), `audit` (journal MCP), `webui` (base/état conversationnel et registre IAM), `models` (poids vérifiés), `guard_status` (signal du garde). Leur simple existence ne démontre ni sauvegarde cohérente, ni chiffrement des données au repos, ni haute disponibilité.

**Limites de preuve.** Les protections réseau, D05 et E09 sont qualifiées sur des chemins bornés. Le navigateur/hôte et certaines sorties restent hors couverture E05 exhaustive. Le montage et la distribution exacte des images OCI relèvent du **ZIP de remise scellé** ; le dépôt source GitHub seul n'est pas une distribution autonome des bases binaires. Aucun de ces schémas ne doit être présenté comme une nouvelle exécution Docker.

Chrome ouvre le port `127.0.0.1:3039` sur le poste. Docker le redirige vers `8080` dans le namespace du garde que WebUI partage. Le garde seul reçoit `NET_ADMIN`. WebUI a toutes ses capacités retirées et son accès au volume du signal est en lecture seule. Le signal lie le boot, le namespace, l’identité du garde, la génération noyau et les empreintes du ruleset complet. Un signal absent, ancien ou divergent empêche l’ouverture de WebUI ou met fin à son processus applicatif.

Dans le réseau Docker privé, le backend appelle Ollama en HTTP sur `11434`, puis le serveur RH par MCP natif Streamable HTTP sur `8000`. Ollama propose les appels et produit la réponse. MCP valide le Bearer technique et mappe l’UUID de l’utilisateur WebUI vers l’acteur RH. La cible d’un appel est validée côté serveur. L’annuaire présente des champs professionnels minimaux dans l’entreprise de l’acteur. Le solde est accessible à la personne concernée et à son manager direct. `unavailable` couvre de manière uniforme le refus et la cible inconnue. Le détail de la décision reste dans l’audit.

Le seed seul rejoint le réseau de téléchargement. Il ne monte que le volume modèles et une référence publique du manifeste. Ollama, MCP et le bootstrap restent sur `private`, réseau interne. WebUI rejoint le frontal via le namespace du garde, avec une politique de sortie par défaut `DROP`. Les DNAT DNS conservent `127.0.0.11` avant le filtre et la première règle bloque cette destination. La CSP restreint les ressources et connexions de la page aux origines prévues. Le navigateur, Docker Desktop et le noyau hôte restent des frontières distinctes.

| Volume | Données et lecteurs |
|---|---|
| `admin` | Init et bootstrap, identités et secrets de démonstration. |
| `webkeys` | Init en écriture, WebUI en lecture seule, clé de session et amorçage admin. |
| `mcpstate` | Mapping et secret technique, MCP en lecture seule. |
| `audit` | Audit rotatif des décisions MCP, sans prompt ni mot de passe. |
| `webui` | Configuration, comptes, conversations, registre IAM et son témoin. |
| `models` | Poids vérifiés, utilisés par le seed et Ollama. |
| `guard_status` | Signal transitoire du garde, WebUI en lecture seule. |

Les logs permettent de relier un acteur, un outil, une décision et un identifiant de message. Les preuves de test ont ajouté le résultat fictif de l’outil et le rendu Chrome à cette corrélation. Les volumes locaux restent lisibles par l’administrateur du moteur Docker. En production, cette frontière demande des contrôles d’administration, de rotation, de sauvegarde et d’identité supplémentaires.

Le registre de révocation est validé avant ouverture de WebUI. Le logout retire les sockets du jeton visé. Le filtre, les flux RH et le profil REG-05 restent ceux de la candidate qualifiée. Voir [la portée des preuves](QUALIFICATION.md).
