# THIGA — Cibles de production et évolutions NON déployées

> **Attention : aucune de ces propositions ne décrit un composant Kubernetes exécuté par le démonstrateur local.** L'as-built utilise Docker Compose. Le choix d'un hébergeur, d'un produit de stockage ou d'un pool GPU n'est pas ratifié par cette page.

- **TH-D-036** (D03/D09) — OIDC/OAuth et identité de workload pour un environnement multi-service. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-115** (IAM-03) — Requalifier le rollback simultané du registre de révocation, de son témoin et de la clé. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-144** (D09) — Sélection d'un pilote Kubernetes managé français uniquement après revue des frontières de souveraineté. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-145** (D09) — 3DS OUTSCALE OKS : candidat à étudier sous réserve de la disponibilité GPU, région, contrats et périmètre précis de qualification. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-146** (D09) — OVHcloud Managed Kubernetes ou cluster administré sur IaaS qualifiée : alternatives à comparer si l'offre managée choisie ne couvre pas les exigences. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-147** (D10) — Ingress TLS privé et SSO OIDC ; aucune exposition directe de MCP/Ollama. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-148** (D10) — Remplacer Bearer de service + UUID local par identité de workload et assertion utilisateur d'audience/durée bornées. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-149** (D10) — CNI appliquant NetworkPolicies ingress/egress default-deny, DNS et egress autorisés précisément. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-150** (D10) — Pool GPU dédié, quotas, files, métrologie VRAM et latence p95. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-151** (D10) — État WebUI externalisé, base et secrets chiffrés, audit et sauvegardes avec restauration testée avant réplication. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-152** (D10) — Dimensionnement sur concurrence mesurée, non sur le seul nombre de 500 000 comptes évoqués. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-153** (D12) — Qualification de l'usage AI Act d'après les finalités et effets réels, non l'étiquette générique RH. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-154** (D12) — Différencier consultation de congés et décisions d'emploi, d'évaluation ou de recrutement. **Statut : proposé / à qualifier, non déployé.**
- **TH-D-155** (D12) — DPO et juridique : base légale, minimisation, AIPD éventuelle, droits et flux transfrontaliers. **Statut : proposé / à qualifier, non déployé.**

## Portes de décision avant production

- Identifier les exigences contractuelles de souveraineté, les sous-traitants, les accès de support et les périmètres précis de qualification.
- Prouver l'isolation réseau sur le CNI et le noyau effectivement choisis, y compris le chemin d'approvisionnement des images et poids.
- Établir la chaîne d'identité utilisateur et workload, les secrets, la révocation et les journaux sans dépendre du seul comportement du LLM.
- Tester sauvegardes, restauration, concurrence, GPU, pannes et installation d'un cluster dans l'environnement cible.
- Faire un pilote avec données fictives, puis soumettre les usages réels aux validations sécurité, RGPD et AI Act nécessaires.

Voir [l'analyse de production](../PRODUCTION.md), [le schéma cible Kubernetes](../ARCHITECTURE-CIBLE-KUBERNETES.md) et [les choix documentés](../DECISIONS.md).
