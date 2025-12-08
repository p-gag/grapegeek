---
english_hash: 01aee47e5dcaadf693f34275a8b7293cb847f1626e4bb42856ce8bc587ce2907
translated_date: '2025-12-07'
---

# Utilisation de l’IA et transparence

Cette page explique comment l’intelligence artificielle est utilisée sur ce site, la philosophie qui la guide, ainsi que des avis importants dont vous devriez être au courant.

!!! warning "Divulgation de contenu généré par IA"
    **Ce site est en grande partie généré à l’aide d’outils d’IA.** Tous les articles sur les cépages sont recherchés, rédigés et traduits à l’aide de l’intelligence artificielle. Même si je m’efforce d’assurer l’exactitude au moyen de citations et de recherche sur le web, veuillez vérifier l’information de façon indépendante avant de prendre des décisions de culture ou d’affaires.

!!! info "Avis de qualité — Projet personnel"
    Il s’agit d’un **projet de passion personnel** auquel je consacre peu de temps. La qualité du contenu peut varier, et les articles peuvent contenir des erreurs ou des informations incomplètes. Voyez-le comme un point de départ pour vos propres recherches, pas comme un avis agricole définitif.

## Ma philosophie en matière d’IA

Dans mon travail de jour, j’utilise l’IA pour aider les employé·e·s à naviguer de vastes bases de connaissances internes que les modèles d’IA ne connaissent pas. Cette expérience m’a appris que **les modèles d’IA retiennent mal l’information sur les cépages hybrides, parce que le sujet est trop niché.** Quand on interroge l’IA sur un cépage obscur, elle finit presque assurément par halluciner.

Plutôt que de miser sur la « mémoire » de l’IA, j’utilise ces outils puissants pour **m’aventurer dans les coins reculés du web**, afin de dénicher des faits intéressants, des témoignages et des expériences vécues par des producteurs et des vinificateurs. L’objectif, c’est la découverte et le lien, pas l’invention.

## Comment ça marche : le processus d’IA en trois couches

### 1. 🛠️ Développement du dépôt
Je m’appuie fortement sur l’IA pour coder l’ensemble de ce dépôt :
- Structure du site et navigation bilingue
- Scripts de génération de contenu
- Flux de travail de traduction
- Automatisation du déploiement

**Outils utilisés :** Claude Code, GitHub Copilot  
**Mon rôle :** décisions d’architecture, tests, mise au point

### 2. 🔍 Recherche et rédaction de contenu
Pour chaque article de cépage :
- L’IA parcourt le web pour trouver de l’information factuelle sur le cépage
- Met l’accent sur les témoignages, les études et les expériences de producteurs
- Assemble les trouvailles en un article cohérent, style magazine
- Conserve toutes les citations et références pour vérification

**Outils utilisés :** OpenAI GPT-5 avec capacités de recherche web  
**Mon rôle :** sélection des cépages, relecture rapide, décisions de publication

### 3. 🌍 Traduction

Mon idée de départ était de créer du contenu à la montréalaise — en tissant naturellement le français et l’anglais selon les sources et le contexte. Toutefois, c’était trop complexe pour le flux de travail actuel. Je pourrais y revenir plus tard. Pour l’instant, tout le contenu naît en anglais généré par IA.

Les articles en anglais sont traduits en français :
- Utilise un système intelligent basé sur des hachages pour ne traduire que le contenu modifié
- Adapté aux viticulteurs du Québec et de l’Est du Canada
- Préserve exactement les termes techniques et les citations
- Maintient un ton accessible et chaleureux

**Outils utilisés :** OpenAI GPT-5 avec contexte de français québécois  
**Mon rôle :** pas grand-chose pour l’instant

## Ce que ça signifie pour vous

**✅ Points forts :**
- Accès à de l’information peu commune provenant de partout sur le web
- Format cohérent et accessible
- Citations fournies pour approfondir
- Disponibilité bilingue

**⚠️ Limites :**
- L’IA peut manquer des nuances qu’un·e expert·e humain·e remarquerait
- L’information n’est aussi bonne que ce qui existe en ligne
- Projet personnel — non révisé de façon professionnelle
- Peut contenir des erreurs ou de l’information dépassée

**🎯 Bonne pratique :**
Servez-vous de ce site comme **un outil de découverte** pour repérer des cépages et des sources intéressants, puis suivez les citations pour joindre directement les producteurs, chercheur·euse·s et publications mentionnés.

## Détails techniques

Pour les développeurs et les personnes curieuses de l’implémentation :

- **Code source :** [GitHub Repository](https://github.com/p-gag/grapegeek)
- **Modèles d’IA :** OpenAI GPT-5 avec outils de recherche web
- **Langages :** Python, MkDocs avec le thème Material
- **Déploiement :** GitHub Pages avec domaine personnalisé

L’ensemble du flux de travail est conçu pour être transparent et reproductible. Vous pouvez voir exactement comment chaque article est généré en examinant le code et les invites dans le dépôt, y compris le [main system prompt](https://github.com/p-gag/grapegeek/blob/main/prompts/general/system_prompt.md) qui guide la génération du contenu sur les cépages.

---

*Cette page de transparence reflète mon engagement envers une utilisation honnête de l’IA. Si vous avez des questions ou des préoccupations au sujet d’un contenu, n’hésitez pas à me contacter ou à consulter le dépôt GitHub pour plus de détails.*