// ============================================
// TechAware - Enhanced JavaScript Utilities
// ============================================

// ========== Toast Notification System ==========
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <div class="toast-content">
                <div class="toast-title">${titles[type] || titles.info}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        this.container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideInRight 0.3s ease-out reverse';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);

        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Initialize global toast manager
const toast = new ToastManager();

// ========== Modal Dialog System ==========
class ModalManager {
    constructor() {
        this.activeModal = null;
    }

    show(html, options = {}) {
        const {
            title = 'Dialog',
            size = 'medium',
            closable = true,
            onClose = null
        } = options;

        // Remove existing modal
        if (this.activeModal) {
            this.activeModal.remove();
        }

        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay active';
        
        const sizes = {
            small: 'max-width: 400px',
            medium: 'max-width: 600px',
            large: 'max-width: 900px',
            xlarge: 'max-width: 1200px'
        };

        overlay.innerHTML = `
            <div class="modal" style="${sizes[size] || sizes.medium}">
                <div class="modal-header">
                    <h2 class="modal-title">${title}</h2>
                    ${closable ? '<button class="modal-close" onclick="modal.close()">×</button>' : ''}
                </div>
                <div class="modal-body">
                    ${html}
                </div>
            </div>
        `;

        // Close on overlay click
        if (closable) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.close();
                }
            });
        }

        document.body.appendChild(overlay);
        this.activeModal = overlay;
        this.onClose = onClose;

        // Close on ESC key
        if (closable) {
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    this.close();
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);
        }

        return overlay;
    }

    close() {
        if (this.activeModal) {
            this.activeModal.style.animation = 'scaleIn 0.3s ease-out reverse';
            setTimeout(() => {
                if (this.activeModal && this.activeModal.parentElement) {
                    this.activeModal.remove();
                }
                this.activeModal = null;
                if (this.onClose) {
                    this.onClose();
                    this.onClose = null;
                }
            }, 300);
        }
    }

    confirm(message, onConfirm, onCancel) {
        const html = `
            <p style="margin-bottom: 1.5rem;">${message}</p>
        `;

        const footer = document.createElement('div');
        footer.className = 'modal-footer';
        footer.innerHTML = `
            <button class="btn btn-secondary" onclick="modal.close()">Cancel</button>
            <button class="btn btn-primary" onclick="this.onClick()">Confirm</button>
        `;

        footer.querySelector('.btn-primary').onClick = () => {
            this.close();
            if (onConfirm) onConfirm();
        };

        const modal = this.show(html, { title: 'Confirm Action' });
        modal.querySelector('.modal').appendChild(footer);
    }
}

const modal = new ModalManager();

// ========== Loading Overlay ==========
class LoadingManager {
    constructor() {
        this.overlay = null;
        this.init();
    }

    init() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'loading-overlay';
        this.overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <p style="color: var(--text-secondary); font-weight: 600;">Loading...</p>
        `;
        document.body.appendChild(this.overlay);
    }

    show(message = 'Loading...') {
        if (this.overlay) {
            this.overlay.querySelector('p').textContent = message;
            this.overlay.classList.add('active');
        }
    }

    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }
    }
}

const loading = new LoadingManager();

// ========== Advanced Table System ==========
class DataTable {
    constructor(selector, options = {}) {
        this.table = typeof selector === 'string' ? document.querySelector(selector) : selector;
        this.options = {
            searchable: true,
            sortable: true,
            pagination: true,
            perPage: 10,
            ...options
        };
        this.data = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.init();
    }

    init() {
        this.loadData();
        if (this.options.searchable) this.addSearch();
        if (this.options.sortable) this.addSorting();
        if (this.options.pagination) this.addPagination();
    }

    loadData() {
        const rows = Array.from(this.table.querySelectorAll('tbody tr'));
        this.data = rows.map(row => ({
            element: row,
            cells: Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim())
        }));
        this.filteredData = [...this.data];
        this.render();
    }

    addSearch() {
        const searchBox = document.createElement('div');
        searchBox.className = 'search-box';
        searchBox.innerHTML = `
            <input type="text" class="search-input" placeholder="Search...">
            <span class="search-icon">🔍</span>
        `;
        this.table.parentElement.insertBefore(searchBox, this.table);

        const input = searchBox.querySelector('.search-input');
        input.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            this.filteredData = this.data.filter(row => 
                row.cells.some(cell => cell.toLowerCase().includes(query))
            );
            this.currentPage = 1;
            this.render();
        });
    }

    addSorting() {
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            header.classList.add('sortable');
            header.addEventListener('click', () => {
                if (this.sortColumn === index) {
                    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortColumn = index;
                    this.sortDirection = 'asc';
                }
                this.sort();
                this.updateSortUI();
            });
        });
    }

    sort() {
        this.filteredData.sort((a, b) => {
            const aVal = a.cells[this.sortColumn] || '';
            const bVal = b.cells[this.sortColumn] || '';
            const comparison = aVal.localeCompare(bVal);
            return this.sortDirection === 'asc' ? comparison : -comparison;
        });
        this.render();
    }

    updateSortUI() {
        const headers = this.table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            header.classList.remove('sort-asc', 'sort-desc');
            if (index === this.sortColumn) {
                header.classList.add(`sort-${this.sortDirection}`);
            }
        });
    }

    addPagination() {
        const pagination = document.createElement('div');
        pagination.className = 'table-pagination';
        this.table.parentElement.appendChild(pagination);
        this.paginationEl = pagination;
    }

    render() {
        const start = (this.currentPage - 1) * this.options.perPage;
        const end = start + this.options.perPage;
        const pageData = this.filteredData.slice(start, end);

        // Hide all rows
        this.data.forEach(row => row.element.style.display = 'none');

        // Show page rows
        pageData.forEach(row => row.element.style.display = '');

        // Update pagination
        if (this.paginationEl) {
            const totalPages = Math.ceil(this.filteredData.length / this.options.perPage);
            this.paginationEl.innerHTML = `
                <div class="pagination-info">
                    Showing ${start + 1}-${Math.min(end, this.filteredData.length)} of ${this.filteredData.length}
                </div>
                <div class="pagination-controls">
                    <button class="pagination-btn" onclick="this.dataset.table.goToPage(${this.currentPage - 1})" 
                            ${this.currentPage === 1 ? 'disabled' : ''}>Previous</button>
                    ${Array.from({ length: totalPages }, (_, i) => i + 1).map(page => `
                        <button class="pagination-btn ${page === this.currentPage ? 'active' : ''}" 
                                onclick="this.dataset.table.goToPage(${page})">${page}</button>
                    `).join('')}
                    <button class="pagination-btn" onclick="this.dataset.table.goToPage(${this.currentPage + 1})" 
                            ${this.currentPage === totalPages ? 'disabled' : ''}>Next</button>
                </div>
            `;
            this.paginationEl.querySelectorAll('.pagination-btn').forEach(btn => {
                if (btn.onclick) {
                    const originalOnClick = btn.onclick;
                    btn.onclick = null;
                    btn.addEventListener('click', originalOnClick);
                    btn.dataset.table = this;
                }
            });
        }
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.filteredData.length / this.options.perPage);
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.render();
        }
    }

    refresh() {
        this.loadData();
    }
}

// ========== Export Functions ==========
const ExportManager = {
    toCSV(table, filename = 'data.csv') {
        const rows = Array.from(table.querySelectorAll('tr'));
        const csv = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('th, td'));
            return cells.map(cell => `"${cell.textContent.trim()}"`).join(',');
        }).join('\n');

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    },

    toJSON(data, filename = 'data.json') {
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    },

    print(element) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print</title>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background: #f2f2f2; }
                    </style>
                </head>
                <body>
                    ${element.outerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
};

// ========== Utility Functions ==========
const Utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    formatDateTime(date) {
        return new Date(date).toLocaleString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            toast.success('Copied to clipboard!');
        }).catch(() => {
            toast.error('Failed to copy to clipboard');
        });
    },

    animateValue(element, start, end, duration) {
        const startTime = performance.now();
        const change = end - start;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = start + (change * progress);
            element.textContent = Math.floor(current);
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }
};

// ========== Real-time Updates ==========
class RealTimeManager {
    constructor(interval = 5000) {
        this.interval = interval;
        this.callbacks = [];
        this.timer = null;
    }

    subscribe(callback) {
        this.callbacks.push(callback);
        if (!this.timer) {
            this.start();
        }
    }

    unsubscribe(callback) {
        this.callbacks = this.callbacks.filter(cb => cb !== callback);
        if (this.callbacks.length === 0) {
            this.stop();
        }
    }

    start() {
        this.timer = setInterval(() => {
            this.callbacks.forEach(callback => callback());
        }, this.interval);
    }

    stop() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
}

const realTime = new RealTimeManager(5000);

// Export for use in other scripts
window.toast = toast;
window.modal = modal;
window.loading = loading;
window.DataTable = DataTable;
window.ExportManager = ExportManager;
window.Utils = Utils;
window.realTime = realTime;

