// Add AI warning banner to grape variety pages
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a grape variety page
    const path = window.location.pathname;
    const isEnglishVariety = path.includes('/varieties/') && !path.endsWith('/varieties/') && !path.endsWith('/varieties/index.html');
    const isFrenchVariety = path.includes('/fr/varietes/') && !path.endsWith('/fr/varietes/') && !path.endsWith('/fr/varietes/index.html');
    
    if (isEnglishVariety || isFrenchVariety) {
        // Create banner element
        const banner = document.createElement('div');
        banner.className = 'ai-warning-banner';
        
        // Determine language and content
        const isFrench = path.includes('/fr/');
        const aiUsageLink = isFrench ? '/fr/usage-ia/' : '/ai-usage/';
        
        const bannerContent = isFrench ? 
            `<span class="ai-icon">🤖</span> <strong>Recherché avec l'IA.</strong> Vérifiez l'information de manière indépendante. <a href="${aiUsageLink}">Détails sur l'usage de l'IA</a>` :
            `<span class="ai-icon">🤖</span> <strong>AI-Researched Content.</strong> Verify information independently. <a href="${aiUsageLink}">AI usage details</a>`;
        
        banner.innerHTML = bannerContent;
        
        // Find the main content area and insert banner
        const content = document.querySelector('.md-content__inner');
        if (content) {
            // Insert before the first h1 (article title)
            const title = content.querySelector('h1');
            if (title) {
                title.insertAdjacentElement('beforebegin', banner);
            } else {
                // Fallback: insert at the beginning
                content.insertBefore(banner, content.firstChild);
            }
            
            // Show the banner
            banner.style.display = 'block';
        }
    }
});