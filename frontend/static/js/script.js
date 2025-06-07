
// Configuración de la API
const API_BASE_URL = window.location.origin;

// Variables para controlar el scroll infinito
let isLoading = false;

// Variables globales
let currentFilters = {
    discount: null,
    minPrice: 5,
    maxPrice: 500,
    brands: [],
    store: '',
    colors: [],
    genres: [],
    sort: '',
    saleToday: false,
    newToday: false
};
let allBrands = new Set();

// ------------- UTILIDADES -------------
function getElement(id) {
    return document.getElementById(id);
}

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

// Función para toggle del sidebar en móvil
function toggleSidebar() {
    const sidebar = getElement('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

// Función para toggle de filtros
function toggleFilter(filterId) {
    const content = getElement(filterId + '-content');
    const title = content.previousElementSibling;

    if (content && title) {
        content.classList.toggle('collapsed');
        title.classList.toggle('collapsed');
    }
}

// Inicializar controles de filtros
function initializeFilters() {
    // PLEGAR TODOS LOS FILTROS AL INICIO
    document.querySelectorAll('.filter-title').forEach(title => {
        title.classList.add('collapsed');
    });

    document.querySelectorAll('.filter-content').forEach(content => {
        content.classList.add('collapsed');
    });

    // Botones de descuento.
    const discountButtons = document.querySelectorAll('.discount-btn');
    discountButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            discountButtons.forEach(b => b.classList.remove('active'));

            if (currentFilters.discount === parseInt(this.dataset.discount)) {
                currentFilters.discount = null;
            } else {
                this.classList.add('active');
                currentFilters.discount = parseInt(this.dataset.discount);
            }
        });
    });

    // Agregar event listeners para géneros
    document.querySelectorAll('#genre-checkboxes input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', updateGenreCount);
    });

    // Inicializar sliders de precio
    initializePriceSliders();
}

// Función específica para inicializar los sliders de precio
function initializePriceSliders() {
    const priceMinSlider = getElement('price-min');
    const priceMaxSlider = getElement('price-max');
    const priceFill = getElement('price-fill');
    const priceMinDisplay = getElement('price-min-display');
    const priceMaxDisplay = getElement('price-max-display');

    if (!priceMinSlider || !priceMaxSlider || !priceFill || !priceMinDisplay || !priceMaxDisplay) {
        console.error('No se encontraron todos los elementos del slider de precio');
        return;
    }

    function updatePriceSlider() {
        const min = parseInt(priceMinSlider.value);
        const max = parseInt(priceMaxSlider.value);

        if (min > max) {
            if (priceMinSlider === document.activeElement) {
                priceMaxSlider.value = min;
            } else {
                priceMinSlider.value = max;
            }
        }

        const minVal = parseInt(priceMinSlider.value);
        const maxVal = parseInt(priceMaxSlider.value);

        currentFilters.minPrice = minVal;
        currentFilters.maxPrice = maxVal;

        // Actualizar displays
        priceMinDisplay.textContent = `${minVal} €`;
        priceMaxDisplay.textContent = `${maxVal} €`;

        // Actualizar barra de relleno
        actualizarRellenoSlider();
    }

    priceMinSlider.addEventListener('input', updatePriceSlider);
    priceMaxSlider.addEventListener('input', updatePriceSlider);

    // Inicializar slider
    updatePriceSlider();
}

// Función para actualizar el relleno del slider de precio
function actualizarRellenoSlider() {
    const sliderMin = getElement('price-min');
    const sliderMax = getElement('price-max');
    const fill = getElement('price-fill');

    if (!sliderMin || !sliderMax || !fill) return;

    const min = Number(sliderMin.min);
    const max = Number(sliderMin.max);
    const vmin = Number(sliderMin.value);
    const vmax = Number(sliderMax.value);

    // Calcula el % a partir de los valores actuales
    const left = ((vmin - min) / (max - min)) * 100;
    const width = ((vmax - vmin) / (max - min)) * 100;

    fill.style.left = left + "%";
    fill.style.width = width + "%";
}

// Función para limpiar filtros
function clearFilters() {
    // Limpiar botones de descuento
    document.querySelectorAll('.discount-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Resetear sliders de precio
    const priceMinSlider = getElement('price-min');
    const priceMaxSlider = getElement('price-max');

    if (priceMinSlider && priceMaxSlider) {
        priceMinSlider.value = 5;
        priceMaxSlider.value = 500;
    }

    // Resetear selects
    const storeFilter = getElement('store-filter');

    // Resetear checkbox
    const saleTodayFilter = getElement('sale-today-filter');
    const newTodayFilter = getElement('new-today-filter');

    if (saleTodayFilter) saleTodayFilter.checked = false;
    if (newTodayFilter) newTodayFilter.checked = false;
    if (storeFilter) storeFilter.value = '';

    // Limpiar todos los checkboxes de marcas, colores y géneros
    document.querySelectorAll('#brand-checkboxes input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.querySelectorAll('#color-checkboxes input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.querySelectorAll('#genre-checkboxes input[type="checkbox"]').forEach(cb => cb.checked = false);

    // Actualizar contadores
    updateBrandCount();
    updateColorCount();
    updateGenreCount();

    // Resetear filtros globales
    currentFilters = {
        discount: null,
        minPrice: 5,
        maxPrice: 500,
        brands: [],
        store: '',
        colors: [],
        genres: [],
        sort: '',
        saleToday: false,
        newToday: false
    };

    // Actualizar slider visual
    const priceFill = getElement('price-fill');
    const priceMinDisplay = getElement('price-min-display');
    const priceMaxDisplay = getElement('price-max-display');

    if (priceMinDisplay) priceMinDisplay.textContent = '5 €';
    if (priceMaxDisplay) priceMaxDisplay.textContent = '500 €';

    if (priceFill) {
        priceFill.style.left = '0.5%';
        priceFill.style.width = '99%';
    }

    // Ocultar sección filtrada
    const filteredSection = getElement('filtered-products-section');
    if (filteredSection) {
        filteredSection.style.display = 'none';
    }
}


// Función para crear tarjeta de producto
function createProductCard(product) {
    const discountPercentage = product.current_discount || 0;
    const originalPrice = product.first_price || 0;
    const currentPrice = product.current_price || originalPrice;

    return `
         <a href="${product.link_url}" class="product-link" target="_blank" rel="noopener noreferrer">
            <article class="product-card" itemscope itemtype="https://schema.org/Product">
                <div class="product-image">
                    <img src="${product.image || '/placeholder-image.jpg'}" alt="Imagen de ${product.description || 'Producto'}" loading="lazy" onerror="this.src='/placeholder-image.jpg'">
                </div>
                <h3 class="product-title" itemprop="name">${product.description || 'Producto sin nombre'}</h3>
                <div class="product-brand" itemprop="brand">${product.brand || 'Marca no especificada'}</div>
                <div class="product-store">🏪 ${product.platform || 'Tienda no especificada'}</div>
                <div class="product-prices">
                    <span class="current-price" itemprop="price">€${currentPrice}</span>
                    ${originalPrice > currentPrice ? `<span class="original-price">€${originalPrice}</span>` : ''}
                    <span class="discount-badge">${discountPercentage}%</span>
                </div>
                <meta itemprop="priceCurrency" content="EUR">
                <meta itemprop="availability" content="https://schema.org/InStock">
            </article>
        </a>
    `;
}

// Función para actualizar estadísticas
async function updateStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/products/count`);
        const data = await response.json();
        const statsElement = getElement('product-count');
        if (statsElement) {
            statsElement.innerHTML  = `<strong>${data.count || 0} ofertas recuperadas</strong>`;
        }
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        const statsElement = getElement('product-count');
        if (statsElement) {
            statsElement.textContent = 'Error al cargar stats';
        }
    }
}

// Función para cargar productos con mayor descuento
async function loadTopDiscounts() {
    try {
        const response = await fetch(`${API_BASE_URL}/products?sort=discount_desc&page=1&page_size=25`);
        const data = await response.json();

        const grid = getElement('top-discounts-grid');
        if (!grid) return;

        if (data.products && data.products.length > 0) {
            grid.innerHTML = data.products.map(createProductCard).join('');

        } else {
            grid.innerHTML = '<div class="error">No se encontraron productos con descuento</div>';
        }
    } catch (error) {
        console.error('Error al cargar productos con descuento:', error);
        const grid = getElement('top-discounts-grid');
        if (grid) {
            grid.innerHTML = '<div class="error">Error al cargar productos con descuento</div>';
        }
    }
}

// Función para cargar productos actualizados hoy
async function loadUpdatedProducts(page = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/products?sale_today=true&page=${page}&page_size=10`);
        const data = await response.json();

        const grid = getElement('updated-products-grid');
        if (!grid) return;

        if (data.products && data.products.length > 0) {
            grid.innerHTML = data.products.map(createProductCard).join('');

        } else {
            grid.innerHTML = '<div class="error">No se encontraron productos actualizados hoy</div>';
        }
    } catch (error) {
        console.error('Error al cargar productos actualizados:', error);
        const grid = getElement('updated-products-grid');
        if (grid) {
            grid.innerHTML = '<div class="error">Error al cargar productos actualizados</div>';
        }
    }
}

// Función para cargar productos de hoy
async function loadTodayProducts(page = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/products?new_today=true&page=${page}&page_size=10`);
        const data = await response.json();

        const grid = getElement('today-products-grid');
        if (!grid) return;

        if (data.products && data.products.length > 0) {
            grid.innerHTML = data.products.map(createProductCard).join('');

        } else {
            grid.innerHTML = '<div class="error">No se encontraron productos de hoy</div>';
        }
    } catch (error) {
        console.error('Error al cargar productos de hoy:', error);
        const grid = getElement('today-products-grid');
        if (grid) {
            grid.innerHTML = '<div class="error">Error al cargar productos de hoy</div>';
        }
    }
}

// Función para aplicar filtros
function applyFilters() {
    // Actualizar filtros desde los controles
    const storeFilter = getElement('store-filter');
    const sortSelect = getElement('sort-select');
    const saleTodayFilter = getElement('sale-today-filter');
    const newTodayFilter = getElement('new-today-filter');

    // Obtener marcas seleccionadas
    const selectedBrands = Array.from(document.querySelectorAll('#brand-checkboxes input[type="checkbox"]:checked'))
        .map(cb => cb.value);

    // Obtener colores seleccionados
    const selectedColors = Array.from(document.querySelectorAll('#color-checkboxes input[type="checkbox"]:checked'))
        .map(cb => cb.value);

    // Obtener géneros seleccionados
    const selectedGenres = Array.from(document.querySelectorAll('#genre-checkboxes input[type="checkbox"]:checked'))
        .map(cb => cb.value);

    currentFilters.brands = selectedBrands;
    currentFilters.colors = selectedColors;
    currentFilters.genres = selectedGenres;

    if (storeFilter) currentFilters.store = storeFilter.value;
    if (sortSelect) currentFilters.sort = sortSelect.value;
    if (saleTodayFilter) currentFilters.saleToday = saleTodayFilter.checked;
    if (newTodayFilter) currentFilters.newToday = newTodayFilter.checked;

    updateURL();

    // Cerrar sidebar en móvil después de aplicar filtros
    const sidebar = getElement('sidebar');
    if (sidebar && sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
    }

    // Si hay algún filtro aplicado, cargar productos filtrados
    if (currentFilters.discount ||
        currentFilters.minPrice > 5 ||
        currentFilters.maxPrice < 500 ||
        currentFilters.brands.length > 0 ||
        currentFilters.store ||
        currentFilters.colors.length > 0 ||
        currentFilters.genres.length > 0 ||
        currentFilters.sort ||
        currentFilters.saleToday ||
        currentFilters.newToday
    ) {
        loadFilteredProducts();
    } else {
        const filteredSection = getElement('filtered-products-section');
        if (filteredSection) {
            filteredSection.style.display = 'none';
        }
    }
}

// Función para cargar productos filtrados
async function loadFilteredProducts(page = 1) {
    if (page === 1) {
        showLoader('Aplicando filtros...');

        function fadeOutAndHide(elementId) {
            const el = document.getElementById(elementId);
            if (!el) return;

            el.style.transition = 'opacity 1s ease';
            el.style.opacity = '1';

            requestAnimationFrame(() => {
                el.style.opacity = '0';
            });

            el.addEventListener('transitionend', function handler() {
                el.style.display = 'none';
                el.removeEventListener('transitionend', handler);
            });
        }

        ['top-discounts-section', 'updated-products-section', 'today-products-section'].forEach(id => {
            fadeOutAndHide(id);
        });
    } else {
        addMiniLoader('filtered-products-grid');
    }

    try {
        let url = `${API_BASE_URL}/products?page=${page}&page_size=25`;

        if (currentFilters.discount) {
            url += `&min_discount=${currentFilters.discount}`;
        }

        url += `&min_price=${currentFilters.minPrice}`;
        url += `&max_price=${currentFilters.maxPrice}`;

        if (currentFilters.brands.length > 0) {
            url += `&brands=${encodeURIComponent(currentFilters.brands.join(','))}`;
        }
        if (currentFilters.store) {
            url += `&store=${encodeURIComponent(currentFilters.store)}`;
        }
        if (currentFilters.colors.length > 0) {
            url += `&colors=${encodeURIComponent(currentFilters.colors.join(','))}`;
        }
        if (currentFilters.genres.length > 0) {
            url += `&genres=${encodeURIComponent(currentFilters.genres.join(','))}`;
        }
        if (currentFilters.sort) {
            url += `&sort=${encodeURIComponent(currentFilters.sort)}`;
        }
        if (currentFilters.saleToday) {
            url += `&sale_today=true`;
        }
        if (currentFilters.newToday) {
            url += `&new_today=true`;
        }

        const response = await fetch(url);
        const data = await response.json();

        const section = getElement('filtered-products-section');
        const grid = getElement('filtered-products-grid');

        if (!section || !grid) return;

        section.style.display = 'block';

        if (data.products && data.products.length > 0) {
            if (page === 1) {
                grid.innerHTML = data.products.map(createProductCard).join('');
            } else {
                removeMiniLoader('filtered-products-grid');
                grid.innerHTML += data.products.map(createProductCard).join('');
            }

            grid.dataset.currentPage = data.page;
            grid.dataset.totalPages = data.pages;
            grid.dataset.hasMore = data.page < data.pages;
        } else {
            if (page === 1) {
                grid.innerHTML = '<div class="error">No se encontraron productos que coincidan con los filtros</div>';
            }
        }
    } catch (error) {
        console.error('Error al cargar productos filtrados:', error);
        const section = getElement('filtered-products-section');
        const grid = getElement('filtered-products-grid');

        if (section) section.style.display = 'block';
        if (grid && page === 1) {
            grid.innerHTML = '<div class="error">Error al cargar productos filtrados</div>';
        }
        if (page > 1) removeMiniLoader('filtered-products-grid');
    } finally {
        if (page === 1) hideLoader();
    }
}

// Función para detectar cuando hacer scroll infinito
function setupInfiniteScroll() {
    window.addEventListener('scroll', () => {
        if (isLoading) return;

        const scrollPosition = window.innerHeight + window.scrollY;
        const documentHeight = document.documentElement.offsetHeight;

        // Cargar más cuando estemos cerca del final (200px antes)
        if (scrollPosition >= documentHeight - 200) {
            loadMoreProducts();
        }
    });
}

// Función para cargar más productos según la sección visible
async function loadMoreProducts() {
    if (isLoading) return;

    isLoading = true;

    // Determinar qué sección está visible y cargar más productos
    const filteredSection = getElement('filtered-products-section');

    try {
        if (filteredSection && filteredSection.style.display !== 'none') {
            // Cargar más productos filtrados
            const grid = getElement('filtered-products-grid');
            if (grid && grid.dataset.hasMore === 'true') {
                const nextPage = parseInt(grid.dataset.currentPage) + 1;
                await loadFilteredProducts(nextPage);
            }
        } else {
            // Cargar más productos de las secciones normales
            const updatedGrid = getElement('updated-products-grid');
            const todayGrid = getElement('today-products-grid');

            if (updatedGrid && updatedGrid.dataset.hasMore === 'true') {
                const nextPage = parseInt(updatedGrid.dataset.currentPage) + 1;
                await loadUpdatedProducts(nextPage);
            }

            if (todayGrid && todayGrid.dataset.hasMore === 'true') {
                const nextPage = parseInt(todayGrid.dataset.currentPage) + 1;
                await loadTodayProducts(nextPage);
            }
        }
    } catch (error) {
        console.error('Error al cargar más productos:', error);
    } finally {
        isLoading = false;
    }
}

// Carga las marcas desde el endpoint y actualiza tanto el filtro como allBrands
function cargarMarcas() {
    const brandContainer = getElement('brand-checkboxes');
    if (!brandContainer) return;

    fetch(`${API_BASE_URL}/brand`)
        .then(resp => {
            if (!resp.ok) throw new Error(`HTTP error! status: ${resp.status}`);
            return resp.json();
        })
        .then(data => {
            if (data.brands && Array.isArray(data.brands)) {
                brandContainer.innerHTML = '';
                data.brands.forEach(brand => {
                    if (typeof brand.title === 'string') {
                        allBrands.add(brand.title);
                        const checkboxItem = document.createElement('div');
                        checkboxItem.className = 'checkbox-item';
                        checkboxItem.innerHTML = `
                            <input type="checkbox" id="brand-${brand.title.replace(/\s+/g, '-').toLowerCase()}" value="${brand.title}">
                            <label for="brand-${brand.title.replace(/\s+/g, '-').toLowerCase()}">${brand.title}</label>
                        `;
                        brandContainer.appendChild(checkboxItem);
                    }
                });

                // Agregar event listeners
                brandContainer.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                    checkbox.addEventListener('change', updateBrandCount);
                });
            }
        })
        .catch(err => {
            console.error('Error al cargar las marcas:', err);
        });
}

// Carga el precio máximo desde /products/max_price y actualiza el slider
function cargarMaximoPrecio() {
    fetch(`${API_BASE_URL}/products/max_price`)
        .then(resp => {
            if (!resp.ok) throw new Error(`HTTP error! status: ${resp.status}`);
            return resp.json();
        })
        .then(data => {
            if (typeof data.max_price !== "undefined" && data.max_price > 0) {
                actualizarSliderMaximoPrecio(data.max_price);
            }
        })
        .catch(err => {
            console.error('Error al cargar el precio máximo:', err);
        });
}

// Ajusta los valores máximos del rango de precio en el formulario
function actualizarSliderMaximoPrecio(maxPrice) {
    const sliderMin = getElement('price-min');
    const sliderMax = getElement('price-max');
    const priceValues = document.querySelectorAll('.price-values span');
    const minDisplay = getElement('price-min-display');
    const maxDisplay = getElement('price-max-display');

    if (!sliderMin || !sliderMax) return;

    // Cambiar step a 1 para que llegue exactamente al precio máximo
    sliderMin.step = 1;
    sliderMax.step = 1;
    sliderMin.max = maxPrice;
    sliderMax.max = maxPrice;

    // Corrige los valores actuales si están fuera del nuevo rango
    if (parseInt(sliderMin.value) > maxPrice) sliderMin.value = maxPrice;
    if (parseInt(sliderMax.value) > maxPrice) sliderMax.value = maxPrice;

    // Actualiza los textos inferior y superior
    if (priceValues.length === 2) {
        priceValues[0].textContent = `${sliderMin.min} €`;
        priceValues[1].textContent = `${maxPrice} €`;
    }

    // Actualiza los textos de los valores seleccionados arriba
    if (minDisplay) minDisplay.textContent = `${sliderMin.value} €`;
    if (maxDisplay) maxDisplay.textContent = `${sliderMax.value} €`;

    // Actualizar filtros globales
    currentFilters.maxPrice = Math.min(currentFilters.maxPrice, maxPrice);

    // Ajusta la barra de relleno
    actualizarRellenoSlider();
}


// Asigna los valores de filtros de marca y color desde la URL (si existen)
function asignarFiltrosURL() {
    const storeSelect = getElement('store-filter');
    const sortSelect = getElement('sort-select');

    // Leer TODOS los parámetros de la URL
    const brands = getQueryParam('brands');
    const colors = getQueryParam('colors');
    const genres = getQueryParam('genres');
    const sort = getQueryParam('sort');
    const discount = getQueryParam('discount');
    const minPrice = getQueryParam('min_price');
    const maxPrice = getQueryParam('max_price');
    const store = getQueryParam('store');
    const saleToday = getQueryParam('sale_today');
    const newToday = getQueryParam('new_today');

    // Actualizar currentFilters con valores de la URL
    if (discount) currentFilters.discount = parseInt(discount);
    if (minPrice) currentFilters.minPrice = parseInt(minPrice);
    if (maxPrice) currentFilters.maxPrice = parseInt(maxPrice);
    if (brands) currentFilters.brands = brands.split(',');
    if (store) currentFilters.store = store;
    if (colors) currentFilters.colors = colors.split(',');
    if (genres) currentFilters.genres = genres.split(',');
    if (sort) currentFilters.sort = sort;
    if (saleToday) currentFilters.saleToday = saleToday === 'true';
    if (newToday) currentFilters.newToday = newToday === 'true';

    // Función para intentar asignar checkboxes con reintentos
    function intentarAsignarCheckboxes(containerId, valores, maxIntentos = 50) {
        if (!valores || valores.length === 0) return;

        let intentos = 0;
        const interval = setInterval(() => {
            intentos++;
            const container = getElement(containerId);
            if (container && container.children.length > 0) {
                valores.forEach(valor => {
                    const checkbox = container.querySelector(`input[value="${valor}"]`);
                    if (checkbox) checkbox.checked = true;
                });
                clearInterval(interval);

                // Actualizar contadores
                if (containerId === 'brand-checkboxes') updateBrandCount();
                if (containerId === 'color-checkboxes') updateColorCount();
                if (containerId === 'genre-checkboxes') updateGenreCount();
            } else if (intentos >= maxIntentos) {
                clearInterval(interval);
            }
        }, 100);
    }

    // Asignar valores a los elementos de la interfaz
    if (brands) {
        intentarAsignarCheckboxes('brand-checkboxes', currentFilters.brands);
    }

    if (colors) {
        intentarAsignarCheckboxes('color-checkboxes', currentFilters.colors);
    }

    if (genres) {
        intentarAsignarCheckboxes('genre-checkboxes', currentFilters.genres);
    }

    if (sortSelect && sort) {
        sortSelect.value = sort;
    }

    if (storeSelect && store) {
        storeSelect.value = store;
    }

    // Actualizar checkboxes individuales
    const saleTodayFilter = getElement('sale-today-filter');
    const newTodayFilter = getElement('new-today-filter');

    if (saleTodayFilter && saleToday) saleTodayFilter.checked = true;
    if (newTodayFilter && newToday) newTodayFilter.checked = true;

    // Actualizar controles de descuento
    if (discount) {
        const discountBtn = document.querySelector(`[data-discount="${discount}"]`);
        if (discountBtn) {
            document.querySelectorAll('.discount-btn').forEach(btn => btn.classList.remove('active'));
            discountBtn.classList.add('active');
        }
    }

    // Actualizar sliders de precio
    if (minPrice || maxPrice) {
        const priceMinSlider = getElement('price-min');
        const priceMaxSlider = getElement('price-max');

        if (priceMinSlider && minPrice) priceMinSlider.value = minPrice;
        if (priceMaxSlider && maxPrice) priceMaxSlider.value = maxPrice;

        // Actualizar displays y relleno
        setTimeout(() => {
            const priceMinDisplay = getElement('price-min-display');
            const priceMaxDisplay = getElement('price-max-display');

            if (priceMinDisplay) priceMinDisplay.textContent = `${currentFilters.minPrice} €`;
            if (priceMaxDisplay) priceMaxDisplay.textContent = `${currentFilters.maxPrice} €`;

            actualizarRellenoSlider();
        }, 100);
    }
}


// FUNCIONES DE FILTROS URL
function aplicarFiltros() {
    const brandSelect = getElement('brand-filter');
    const colorSelect = getElement('color-filter');
    const genreSelect = getElement('genre-filter');
    const sortSelect = getElement('sort-select');
    const updatedTodaylect = getElement('sale-today-filter');
    let params = new URLSearchParams();

    // Actualizar currentFilters con valores de los selects
    if (brandSelect) currentFilters.brand = brandSelect.value;
    if (colorSelect) currentFilters.color = colorSelect.value;
    if (genreSelect) currentFilters.genre = genreSelect.value;
    if (sortSelect) currentFilters.sort = sortSelect.value;
    if (updatedTodaylect) currentFilters.saleToday  = updatedTodaylect.checked;

    // Agregar todos los filtros activos a los parámetros de URL
    if (currentFilters.discount) {
        params.set('discount', currentFilters.discount);
    }

    if (currentFilters.minPrice > 5) {
        params.set('min_price', currentFilters.minPrice);
    }

    if (currentFilters.maxPrice < 500) {
        params.set('max_price', currentFilters.maxPrice);
    }

    if (currentFilters.brand) {
        params.set('brand', currentFilters.brand);
    }

    if (currentFilters.store) {
        params.set('store', currentFilters.store);
    }

    if (currentFilters.color) {
        params.set('color', currentFilters.color);
    }

    if (currentFilters.genre) {
        params.set('genre', currentFilters.genre);
    }

    if (currentFilters.sort) {
        params.set('sort', currentFilters.sort);
    }

    if (currentFilters.saleToday) {
        params.set('saleToday', currentFilters.saleToday);
    }

    const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
    window.location.href = newUrl;
}


function resetearFiltros() {
    window.location.href = window.location.pathname;
}

function loadColors() {
    const colorContainer = getElement('color-checkboxes');
    if (!colorContainer) return;

    fetch(`${API_BASE_URL}/color`)
        .then(resp => {
            if (!resp.ok) throw new Error(`HTTP error! status: ${resp.status}`);
            return resp.json();
        })
        .then(data => {
            if (data.colors && Array.isArray(data.colors)) {
                colorContainer.innerHTML = '';
                data.colors.forEach(color => {
                    if (typeof color.title === 'string') {
                        const checkboxItem = document.createElement('div');
                        checkboxItem.className = 'checkbox-item';
                        checkboxItem.innerHTML = `
                            <input type="checkbox" id="color-${color.title.replace(/\s+/g, '-').toLowerCase()}" value="${color.title}">
                            <label for="color-${color.title.replace(/\s+/g, '-').toLowerCase()}">${color.title}</label>
                        `;
                        colorContainer.appendChild(checkboxItem);
                    }
                });

                // Agregar event listeners
                colorContainer.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                    checkbox.addEventListener('change', updateColorCount);
                });
            }
        })
        .catch(err => {
            console.error('Error al cargar los colores:', err);
        });
}
function updateBrandCount() {
    const selectedBrands = document.querySelectorAll('#brand-checkboxes input[type="checkbox"]:checked');
    const countElement = getElement('brand-count');
    if (countElement) {
        countElement.textContent = selectedBrands.length > 0 ? `(${selectedBrands.length})` : '';
    }
}

function updateColorCount() {
    const selectedColors = document.querySelectorAll('#color-checkboxes input[type="checkbox"]:checked');
    const countElement = getElement('color-count');
    if (countElement) {
        countElement.textContent = selectedColors.length > 0 ? `(${selectedColors.length})` : '';
    }
}

function updateGenreCount() {
    const selectedGenres = document.querySelectorAll('#genre-checkboxes input[type="checkbox"]:checked');
    const countElement = getElement('genre-count');
    if (countElement) {
        countElement.textContent = selectedGenres.length > 0 ? `(${selectedGenres.length})` : '';
    }
}

function applySorting() {
    const sortSelect = getElement('sort-select');
    if (sortSelect) {
        currentFilters.sort = sortSelect.value;
        applyFilters();
    }
}

// Funciones para el loader
function showLoader(text = 'Cargando...') {
    const overlay = getElement('loader-overlay');
    const loaderText = document.querySelector('.loader-text');

    if (overlay) {
        if (loaderText) loaderText.textContent = text;
        overlay.classList.add('show');
    }
}

function hideLoader() {
    const overlay = getElement('loader-overlay');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

// Función para agregar mini loader al final de una sección
function addMiniLoader(gridId) {
    const grid = getElement(gridId);
    if (grid && !grid.querySelector('.mini-loader')) {
        const miniLoader = document.createElement('div');
        miniLoader.className = 'mini-loader';
        grid.appendChild(miniLoader);
    }
}

// Función para remover mini loader
function removeMiniLoader(gridId) {
    const grid = getElement(gridId);
    if (grid) {
        const miniLoader = grid.querySelector('.mini-loader');
        if (miniLoader) {
            miniLoader.remove();
        }
    }
}


// Inicializar la aplicación
async function init() {
    try {
        // Inicializar controles de filtros
        initializeFilters();

        // Cargar datos desde endpoints específicos
        cargarMarcas();
        loadColors();
        cargarMaximoPrecio();
        asignarFiltrosURL();

        // Cargar datos iniciales de productos
        await updateStats();
        await loadTopDiscounts();
        await loadUpdatedProducts();
        await loadTodayProducts();

        // Configurar scroll infinito
        setupInfiniteScroll();

    } catch (error) {
        console.error('Error durante la inicialización:', error);
    }
}
function updateURL() {
    let params = new URLSearchParams();

    // Agregar todos los filtros activos a los parámetros de URL
    if (currentFilters.discount) {
        params.set('discount', currentFilters.discount);
    }

    if (currentFilters.minPrice > 5) {
        params.set('min_price', currentFilters.minPrice);
    }

    if (currentFilters.maxPrice < 500) {
        params.set('max_price', currentFilters.maxPrice);
    }

    if (currentFilters.brands.length > 0) {
        params.set('brands', currentFilters.brands.join(','));
    }

    if (currentFilters.store) {
        params.set('store', currentFilters.store);
    }

    if (currentFilters.colors.length > 0) {
        params.set('colors', currentFilters.colors.join(','));
    }

    if (currentFilters.genres.length > 0) {
        params.set('genres', currentFilters.genres.join(','));
    }

    if (currentFilters.sort) {
        params.set('sort', currentFilters.sort);
    }

    if (currentFilters.saleToday) {
        params.set('sale_today', 'true');
    }

    if (currentFilters.newToday) {
        params.set('new_today', 'true');
    }

    const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
    window.history.pushState({}, '', newUrl);
}

// Hacer funciones globales para que puedan ser llamadas desde HTML
window.applyFilters = applyFilters;
window.clearFilters = clearFilters;
window.loadUpdatedProducts = loadUpdatedProducts;
window.loadTodayProducts = loadTodayProducts;
window.loadFilteredProducts = loadFilteredProducts;
window.aplicarFiltros = aplicarFiltros;
window.resetearFiltros = resetearFiltros;
window.applySorting = applySorting;
window.updateURL = updateURL;

// Cargar cuando la página esté lista
document.addEventListener('DOMContentLoaded', init);