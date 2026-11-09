# Composants tiers

| Composant | Usage et attribution |
|---|---|
| Open WebUI v0.12.5 | Image officielle récupérée par digest. Les fichiers `demonstrateur/webui_patch/auth.py` et `socket_main.py` dérivent du backend Open WebUI et comportent des adaptations de révocation THIGA. Copyright 2023– Open WebUI Inc., créé par Timothy Jaeryang Baek. La marque de l’interface est conservée. [Licence v0.12.5](docs/Open-WebUI-LICENSE.txt) · [Historique des licences](docs/Open-WebUI-LICENSE_HISTORY.txt) |
| Ollama 0.40.13 | Image officielle référencée. Le code Ollama est sous licence MIT. [Licence de la version](https://github.com/ollama/ollama/blob/v0.40.13/LICENSE) |
| Qwen3.5 9B | Modèle de l’équipe Qwen, publié sous Apache-2.0. La quantification est acquise via Ollama. [Licence amont](https://huggingface.co/Qwen/Qwen3.5-9B/blob/main/LICENSE) · [Distribution Ollama](https://ollama.com/library/qwen3.5:9b-q4_K_M) |
| SDK Python MCP 2.3.0 | Dépendance applicative, référence et empreintes dans le verrou. [Licence MIT](https://github.com/modelcontextprotocol/python-sdk/blob/v2.3.0/LICENSE) |
| Python 3.12.16 / Debian Bookworm | Bases système des layouts OCI. Les paquets Debian ont des licences et obligations propres. [Licence Python](https://docs.python.org/3.12/license.html) · [Licences Debian](https://www.debian.org/legal/licenses/) |

Les images tierces, bases OCI et poids ne sont pas redistribués par ce dépôt. Les recettes et les empreintes des bases sont conservées. La documentation publique ne vaut ni approbation des éditeurs ni déclaration de licence pour les sources propres au projet.
