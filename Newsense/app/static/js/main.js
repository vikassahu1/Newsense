document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const sourceButtons = document.querySelectorAll('.source-btn');
    const applyButton = document.getElementById('apply-btn');
    const newsContainer = document.getElementById('news-container');
    const placeholderMessage = document.getElementById('placeholder-message');
    const loadingContainer = document.getElementById('loading-container');
    const statusContainer = document.getElementById('status-container');
    
    // State
    let selectedSource = null;
    
    // Event listeners for source buttons
    sourceButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            sourceButtons.forEach(btn => {
                btn.classList.remove('bg-blue-500', 'text-white');
                btn.classList.add('bg-gray-200');
            });
            
            // Set active class to clicked button
            button.classList.remove('bg-gray-200');
            button.classList.add('bg-blue-500', 'text-white');
            
            // Update selected source
            selectedSource = button.dataset.source;
            
            // Enable apply button
            applyButton.disabled = false;
        });
    });
    
    // Event listener for apply button
    applyButton.addEventListener('click', async () => {
        if (!selectedSource) return;
        
        // Show loading spinner
        showLoading(true);
        
        // Clear previous status
        clearStatus();
        
        // Clear previous news
        clearNewsContainer();
        
        try {
            // Fetch news from the selected source
            const response = await fetch(`/api/articles/${selectedSource}`);
            const data = await response.json();
            
            if (data.status === 'error') {
                showStatus('error', `Error: ${data.message}`);
                return;
            }
            
            if (data.articles.length === 0) {
                showStatus('info', `No articles found for ${selectedSource}`);
                return;
            }
            
            // Show success message
            showStatus('success', `Successfully loaded ${data.articles.length} articles from ${selectedSource}`);
            
            // Render articles one by one with a delay for a nicer experience
            data.articles.forEach((article, index) => {
                setTimeout(() => {
                    renderArticleCard(article);
                }, index * 100); // 100ms delay between each card
            });
            
        } catch (error) {
            console.error('Error fetching news:', error);
            showStatus('error', 'Failed to fetch news. Please try again.');
        } finally {
            // Hide loading spinner
            showLoading(false);
        }
    });
    
    // Function to render a single article card
    function renderArticleCard(article) {
        const card = document.createElement('div');
        card.className = 'bg-white border rounded-lg overflow-hidden shadow-md card-transition fade-in';
        card.style.opacity = '0'; // Start invisible for fade-in effect
        
        // Image with lazy loading
        const imgSrc = article.image_url || '/static/images/placeholder.jpg';
        const imgAlt = article.title || 'News article';
        
        // Format date if available
        let formattedDate = '';
        if (article.published_date) {
            const date = new Date(article.published_date);
            formattedDate = date.toLocaleDateString('en-US', {
                year: 'numeric', 
                month: 'short', 
                day: 'numeric'
            });
        }
        
        // Prepare categories display
        let categoriesHtml = '';
        if (article.categories && article.categories.length > 0) {
            categoriesHtml = article.categories.map(category => 
                `<span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1">${category}</span>`
            ).join('');
        }
        
        // Set card HTML content
        card.innerHTML = `
            <div class="md:flex">
                <div class="md:w-1/3 h-48 md:h-auto overflow-hidden">
                    <img 
                        class="w-full h-full object-cover lazy-load" 
                        data-src="${imgSrc}" 
                        src="/static/images/placeholder.jpg"
                        alt="${imgAlt}"
                        loading="lazy">
                </div>
                <div class="md:w-2/3 p-4">
                    <div class="mb-2">
                        ${categoriesHtml}
                    </div>
                    <h3 class="text-xl font-bold mb-2">
                        <a href="${article.url}" target="_blank" class="text-blue-700 hover:text-blue-900 transition-colors">${article.title}</a>
                    </h3>
                    <p class="text-gray-700 mb-4">${article.summary || article.description || ''}</p>
                    <div class="flex justify-between items-center text-sm text-gray-600">
                        <div>
                            <span class="mr-2">
                                <i class="fas fa-user"></i> ${article.author || 'Unknown Author'}
                            </span>
                            ${formattedDate ? `<span><i class="far fa-calendar-alt"></i> ${formattedDate}</span>` : ''}
                        </div>
                        <a href="${article.url}" target="_blank" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors">
                            Read More
                        </a>
                    </div>
                </div>
            </div>
        `;
        
        // Add to news container
        newsContainer.appendChild(card);
        
        // Trigger fade-in animation
        setTimeout(() => {
            card.style.opacity = '1';
        }, 10);
        
        // Initialize lazy loading for the image
        const img = card.querySelector('img.lazy-load');
        if (img) {
            if ('IntersectionObserver' in window) {
                const lazyImageObserver = new IntersectionObserver((entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            let lazyImage = entry.target;
                            lazyImage.src = lazyImage.dataset.src;
                            lazyImage.classList.remove("lazy-load");
                            lazyImageObserver.unobserve(lazyImage);
                        }
                    });
                });
                
                lazyImageObserver.observe(img);
            } else {
                // Fallback for browsers without IntersectionObserver
                img.src = img.dataset.src;
            }
        }
    }
    
    // Function to show/hide loading spinner
    function showLoading(show) {
        if (show) {
            loadingContainer.classList.remove('hidden');
            placeholderMessage.classList.add('hidden');
        } else {
            loadingContainer.classList.add('hidden');
        }
    }
    
    // Function to clear the news container
    function clearNewsContainer() {
        // Remove all article cards but keep the placeholder
        Array.from(newsContainer.children).forEach(child => {
            if (child !== placeholderMessage) {
                newsContainer.removeChild(child);
            }
        });
        
        // Hide placeholder message while loading
        placeholderMessage.classList.add('hidden');
    }
    
    // Function to show status messages
    function showStatus(type, message) {
        statusContainer.classList.remove('hidden', 'bg-green-100', 'bg-red-100', 'bg-blue-100');
        
        switch (type) {
            case 'success':
                statusContainer.classList.add('bg-green-100', 'text-green-800');
                break;
            case 'error':
                statusContainer.classList.add('bg-red-100', 'text-red-800');
                break;
            case 'info':
            default:
                statusContainer.classList.add('bg-blue-100', 'text-blue-800');
                break;
        }
        
        statusContainer.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
                <p>${message}</p>
            </div>
        `;
    }
    
    // Function to clear status
    function clearStatus() {
        statusContainer.classList.add('hidden');
        statusContainer.innerHTML = '';
    }
    
    // Initialize the app (nothing to do on initial load since user needs to select a source)
}); 