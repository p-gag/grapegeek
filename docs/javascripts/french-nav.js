// Replace navigation labels with French when on French pages
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a French page
    const path = window.location.pathname;
    const isFrenchPage = path.startsWith('/fr/');
    
    if (isFrenchPage) {
        // Translation map for navigation items
        const translations = {
            'Home': 'Accueil',
            'About': 'À Propos', 
            'Grape Varieties': 'Variétés de Raisin',
            'AI Usage': 'Usage de l\'IA'
        };
        
        // Wait a bit for MkDocs to fully load navigation
        setTimeout(function() {
            // Find all navigation links
            const navLinks = document.querySelectorAll('.md-nav__link');
            
            navLinks.forEach(function(link) {
                const originalText = link.textContent.trim();
                if (translations[originalText]) {
                    link.textContent = translations[originalText];
                }
            });
            
            // Also update any navigation titles
            const navTitles = document.querySelectorAll('.md-nav__title');
            navTitles.forEach(function(title) {
                const originalText = title.textContent.trim();
                if (translations[originalText]) {
                    title.textContent = translations[originalText];
                }
            });
            
        }, 100);
    }
});