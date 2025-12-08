// Add AI warning banner to grape variety pages
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a grape variety page
    const path = window.location.pathname;
    
    console.log('AI Banner Debug - Current path:', path);
    
    // Language detection: if path contains /fr/ then French, else English
    const isFrench = path.includes('/fr/');
    
    // Check if we're on a variety page (not index)
    const isVarietyPage = path.includes('/varieties/') && 
                         !path.endsWith('/varieties/') && 
                         !path.endsWith('/varieties/index.html');
    
    console.log('AI Banner Debug - Is variety page:', isVarietyPage, 'Is French:', isFrench);
    
    if (isVarietyPage) {
        // Create banner element
        const banner = document.createElement('div');
        banner.className = 'ai-warning-banner';
        
        // Set links based on language
        const aiUsageLink = isFrench ? '/fr/ai-usage/' : '/ai-usage/';
        
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