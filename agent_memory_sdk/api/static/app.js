// Memory Visualization Web UI
class MemoryUI {
    constructor() {
        this.apiBase = window.location.origin;
        this.currentPage = 1;
        this.pageSize = 20;
        this.currentFilters = {};
        this.currentSort = { field: 'created_at', order: 'desc' };
        this.selectedMemory = null;
        
        this.init();
    }
    
    async init() {
        this.bindEvents();
        await this.checkHealth();
        await this.loadStats();
        await this.loadMemories();
        this.startAutoRefresh();
    }
    
    bindEvents() {
        // Search and filters
        document.getElementById('searchBtn').addEventListener('click', () => this.handleSearch());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
        
        document.getElementById('memoryTypeFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('agentFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('importanceFilter').addEventListener('input', (e) => {
            document.getElementById('importanceValue').textContent = `Min: ${e.target.value}`;
            this.applyFilters();
        });
        
        // Sorting
        document.getElementById('sortBy').addEventListener('change', () => this.applySort());
        document.getElementById('sortOrder').addEventListener('click', () => this.toggleSortOrder());
        
        // Refresh
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshAll());
        
        // Create memory
        document.getElementById('createMemoryFab').addEventListener('click', () => this.showCreateModal());
        document.getElementById('saveMemoryBtn').addEventListener('click', () => this.createMemory());
        document.getElementById('cancelCreateBtn').addEventListener('click', () => this.hideCreateModal());
        document.getElementById('closeCreateModal').addEventListener('click', () => this.hideCreateModal());
        
        // Modal close
        document.getElementById('closeModal').addEventListener('click', () => this.hideMemoryModal());
        
        // Click outside modal to close
        document.getElementById('memoryModal').addEventListener('click', (e) => {
            if (e.target.id === 'memoryModal') this.hideMemoryModal();
        });
        document.getElementById('createModal').addEventListener('click', (e) => {
            if (e.target.id === 'createModal') this.hideCreateModal();
        });
        // Tabs
        document.getElementById('memoriesTabBtn').addEventListener('click', () => this.showTab('memories'));
        document.getElementById('timelineTabBtn').addEventListener('click', () => this.showTab('timeline'));
        // Timeline filters
        document.getElementById('timelineFilterBtn').addEventListener('click', () => this.loadTimeline());
    }
    
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const health = await response.json();
            
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            
            if (response.ok) {
                statusDot.classList.remove('offline');
                statusText.textContent = 'Connected';
            } else {
                statusDot.classList.add('offline');
                statusText.textContent = 'Error';
            }
        } catch (error) {
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');
            statusDot.classList.add('offline');
            statusText.textContent = 'Offline';
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch(`${this.apiBase}/stats`);
            const stats = await response.json();
            
            // Update quick stats
            document.getElementById('totalMemories').textContent = stats.total_memories;
            document.getElementById('activeAgents').textContent = Object.keys(stats.by_agent).length;
            
            // Calculate average importance
            const totalImportance = Object.values(stats.importance_distribution).reduce((a, b) => a + b, 0);
            const avgImportance = totalImportance > 0 ? 
                ((stats.importance_distribution.low * 1.5 + stats.importance_distribution.medium * 5.5 + stats.importance_distribution.high * 9) / totalImportance).toFixed(1) : '0.0';
            document.getElementById('avgImportance').textContent = avgImportance;
            
            // Update memory types
            this.updateMemoryTypes(stats.by_type);
            
            // Update top agents
            this.updateTopAgents(stats.by_agent);
            
            // Update timeline agent/type filters
            this.updateTimelineFilters(stats.by_agent, stats.by_type);
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    updateMemoryTypes(byType) {
        const container = document.getElementById('memoryTypes');
        container.innerHTML = '';
        
        Object.entries(byType).forEach(([type, count]) => {
            const item = document.createElement('div');
            item.className = 'memory-type-item';
            item.innerHTML = `
                <span class="memory-type-name">${type.charAt(0).toUpperCase() + type.slice(1)}</span>
                <span class="memory-type-count">${count}</span>
            `;
            item.addEventListener('click', () => {
                document.querySelectorAll('.memory-type-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                document.getElementById('memoryTypeFilter').value = type;
                this.applyFilters();
            });
            container.appendChild(item);
        });
    }
    
    updateTopAgents(byAgent) {
        const container = document.getElementById('topAgents');
        container.innerHTML = '';
        
        // Sort agents by memory count and take top 5
        const sortedAgents = Object.entries(byAgent)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5);
        
        sortedAgents.forEach(([agent, count]) => {
            const item = document.createElement('div');
            item.className = 'agent-item';
            item.innerHTML = `
                <span class="agent-name">${agent || 'Unknown'}</span>
                <span class="agent-count">${count}</span>
            `;
            item.addEventListener('click', () => {
                document.querySelectorAll('.agent-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                document.getElementById('agentFilter').value = agent;
                this.applyFilters();
            });
            container.appendChild(item);
        });
        
        // Update agent filter options
        const agentFilter = document.getElementById('agentFilter');
        agentFilter.innerHTML = '<option value="">All Agents</option>';
        Object.keys(byAgent).forEach(agent => {
            const option = document.createElement('option');
            option.value = agent;
            option.textContent = agent || 'Unknown';
            agentFilter.appendChild(option);
        });
    }

    updateTimelineFilters(byAgent, byType) {
        const agentFilter = document.getElementById('timelineAgentFilter');
        agentFilter.innerHTML = '<option value="">All Agents</option>';
        Object.keys(byAgent).forEach(agent => {
            const option = document.createElement('option');
            option.value = agent;
            option.textContent = agent || 'Unknown';
            agentFilter.appendChild(option);
        });
        // Type filter is static
    }
    
    async loadMemories() {
        try {
            const params = new URLSearchParams({
                skip: (this.currentPage - 1) * this.pageSize,
                limit: this.pageSize,
                ...this.currentFilters
            });
            
            const response = await fetch(`${this.apiBase}/memories?${params}`);
            const data = await response.json();
            
            this.renderMemories(data.memories);
            this.renderPagination(data.total_count);
            
        } catch (error) {
            console.error('Error loading memories:', error);
            this.showEmptyState('Error loading memories');
        }
    }

    async loadTimeline() {
        const agent = document.getElementById('timelineAgentFilter').value;
        const type = document.getElementById('timelineTypeFilter').value;
        const start = document.getElementById('timelineStart').value;
        const end = document.getElementById('timelineEnd').value;
        const params = new URLSearchParams();
        if (agent) params.append('agent_id', agent);
        if (type) params.append('memory_type', type);
        if (start) params.append('start', start);
        if (end) params.append('end', end);
        params.append('limit', 200);
        try {
            const response = await fetch(`${this.apiBase}/memories/timeline?${params}`);
            const data = await response.json();
            this.renderTimeline(data.timeline);
        } catch (error) {
            this.renderTimeline([]);
        }
    }
    
    renderMemories(memories) {
        const container = document.getElementById('memoryList');
        
        if (memories.length === 0) {
            this.showEmptyState('No memories found');
            return;
        }
        
        container.innerHTML = '';
        
        memories.forEach(memory => {
            const item = document.createElement('div');
            item.className = 'memory-item';
            item.innerHTML = `
                <div class="memory-header">
                    <div class="memory-type-badge ${memory.memory_type}">${memory.memory_type}</div>
                    <div class="importance-badge">
                        <span class="importance-stars">${'★'.repeat(Math.round(memory.importance))}</span>
                        <span>${memory.importance}</span>
                    </div>
                </div>
                <div class="memory-content">${memory.content}</div>
                <div class="memory-meta">
                    <span>${memory.agent_id || 'No Agent'}</span>
                    <span>${this.formatDate(memory.created_at)}</span>
                    <span>Accessed ${memory.access_count} times</span>
                </div>
            `;
            
            item.addEventListener('click', () => this.showMemoryDetail(memory));
            container.appendChild(item);
        });
    }

    renderTimeline(timeline) {
        const container = document.getElementById('timelineContainer');
        if (!timeline || timeline.length === 0) {
            container.innerHTML = `<div class="empty-state"><i class="fas fa-stream"></i><h3>No timeline data</h3><p>Try adjusting filters or add more memories</p></div>`;
            return;
        }
        container.innerHTML = '';
        timeline.forEach(memory => {
            const item = document.createElement('div');
            item.className = 'timeline-item';
            item.innerHTML = `
                <div class="timeline-dot ${memory.memory_type}"></div>
                <div class="timeline-content">
                    <div class="timeline-date">${this.formatDate(memory.created_at)}</div>
                    <div class="timeline-type">${memory.memory_type}</div>
                    <div class="importance-badge">
                        <span class="importance-stars">${'★'.repeat(Math.round(memory.importance))}</span>
                        <span>${memory.importance}</span>
                    </div>
                    <div>${memory.content}</div>
                    <div class="timeline-agent">${memory.agent_id || 'No Agent'}</div>
                    ${memory.tags && memory.tags.length > 0 ? `<div class="timeline-tags">Tags: ${memory.tags.join(', ')}</div>` : ''}
                </div>
            `;
            container.appendChild(item);
        });
    }
    
    renderPagination(totalCount) {
        const container = document.getElementById('pagination');
        const totalPages = Math.ceil(totalCount / this.pageSize);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        container.innerHTML = '';
        
        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.textContent = 'Previous';
        prevBtn.disabled = this.currentPage === 1;
        prevBtn.addEventListener('click', () => {
            this.currentPage--;
            this.loadMemories();
        });
        container.appendChild(prevBtn);
        
        // Page numbers
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.classList.toggle('active', i === this.currentPage);
            pageBtn.addEventListener('click', () => {
                this.currentPage = i;
                this.loadMemories();
            });
            container.appendChild(pageBtn);
        }
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next';
        nextBtn.disabled = this.currentPage === totalPages;
        nextBtn.addEventListener('click', () => {
            this.currentPage++;
            this.loadMemories();
        });
        container.appendChild(nextBtn);
    }
    
    showEmptyState(message) {
        const container = document.getElementById('memoryList');
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>${message}</h3>
                <p>Try adjusting your search or filters</p>
            </div>
        `;
    }
    
    async handleSearch() {
        const query = document.getElementById('searchInput').value.trim();
        if (query) {
            try {
                const response = await fetch(`${this.apiBase}/memories/search`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: query,
                        limit: this.pageSize,
                        ...this.currentFilters
                    })
                });
                
                const data = await response.json();
                this.renderMemories(data.memories);
                this.renderPagination(data.total_count);
                
            } catch (error) {
                console.error('Error searching memories:', error);
            }
        } else {
            this.loadMemories();
        }
    }
    
    applyFilters() {
        this.currentFilters = {};
        
        const typeFilter = document.getElementById('memoryTypeFilter').value;
        const agentFilter = document.getElementById('agentFilter').value;
        const importanceFilter = document.getElementById('importanceFilter').value;
        
        if (typeFilter) this.currentFilters.memory_type = typeFilter;
        if (agentFilter) this.currentFilters.agent_id = agentFilter;
        if (importanceFilter > 0) this.currentFilters.min_importance = parseFloat(importanceFilter);
        
        this.currentPage = 1;
        this.loadMemories();
    }
    
    applySort() {
        this.currentSort.field = document.getElementById('sortBy').value;
        this.loadMemories();
    }
    
    toggleSortOrder() {
        this.currentSort.order = this.currentSort.order === 'asc' ? 'desc' : 'asc';
        const btn = document.getElementById('sortOrder');
        btn.innerHTML = this.currentSort.order === 'asc' ? 
            '<i class="fas fa-sort-amount-up"></i>' : 
            '<i class="fas fa-sort-amount-down"></i>';
        this.loadMemories();
    }

    showTab(tab) {
        if (tab === 'memories') {
            document.getElementById('memoriesTabBtn').classList.add('active');
            document.getElementById('timelineTabBtn').classList.remove('active');
            document.getElementById('memoriesSection').style.display = '';
            document.getElementById('timelineSection').style.display = 'none';
        } else {
            document.getElementById('memoriesTabBtn').classList.remove('active');
            document.getElementById('timelineTabBtn').classList.add('active');
            document.getElementById('memoriesSection').style.display = 'none';
            document.getElementById('timelineSection').style.display = '';
            this.loadTimeline();
        }
    }
    
    async showMemoryDetail(memory) {
        this.selectedMemory = memory;
        const modal = document.getElementById('memoryModal');
        const body = document.getElementById('modalBody');
        
        body.innerHTML = `
            <div class="memory-detail">
                <div class="memory-detail-header">
                    <div class="memory-type-badge ${memory.memory_type}">${memory.memory_type}</div>
                    <div class="importance-badge">
                        <span class="importance-stars">${'★'.repeat(Math.round(memory.importance))}</span>
                        <span>${memory.importance}</span>
                    </div>
                </div>
                <div class="memory-detail-content">${memory.content}</div>
                <div class="memory-detail-meta">
                    <div class="meta-item">
                        <div class="meta-label">ID</div>
                        <div class="meta-value">${memory.id}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Agent</div>
                        <div class="meta-value">${memory.agent_id || 'None'}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Created</div>
                        <div class="meta-value">${this.formatDate(memory.created_at)}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Updated</div>
                        <div class="meta-value">${this.formatDate(memory.updated_at)}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Access Count</div>
                        <div class="meta-value">${memory.access_count}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Last Accessed</div>
                        <div class="meta-value">${memory.last_accessed ? this.formatDate(memory.last_accessed) : 'Never'}</div>
                    </div>
                    ${memory.tags && memory.tags.length > 0 ? `
                        <div class="meta-item">
                            <div class="meta-label">Tags</div>
                            <div class="meta-value">${memory.tags.join(', ')}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Bind delete button
        document.getElementById('deleteMemoryBtn').onclick = () => this.deleteMemory(memory.id);
        
        modal.classList.add('show');
    }
    
    hideMemoryModal() {
        document.getElementById('memoryModal').classList.remove('show');
        this.selectedMemory = null;
    }
    
    showCreateModal() {
        document.getElementById('createModal').classList.add('show');
        document.getElementById('createMemoryForm').reset();
    }
    
    hideCreateModal() {
        document.getElementById('createModal').classList.remove('show');
    }
    
    async createMemory() {
        const form = document.getElementById('createMemoryForm');
        const formData = new FormData(form);
        
        const memoryData = {
            content: document.getElementById('memoryContent').value,
            memory_type: document.getElementById('memoryType').value,
            importance: parseFloat(document.getElementById('memoryImportance').value),
            agent_id: document.getElementById('memoryAgent').value || null,
            tags: document.getElementById('memoryTags').value ? 
                document.getElementById('memoryTags').value.split(',').map(t => t.trim()) : null
        };
        
        try {
            const response = await fetch(`${this.apiBase}/memories`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(memoryData)
            });
            
            if (response.ok) {
                this.hideCreateModal();
                this.refreshAll();
            } else {
                const error = await response.json();
                alert(`Error creating memory: ${error.detail || error.error}`);
            }
        } catch (error) {
            console.error('Error creating memory:', error);
            alert('Error creating memory');
        }
    }
    
    async deleteMemory(memoryId) {
        if (!confirm('Are you sure you want to delete this memory?')) return;
        
        try {
            const response = await fetch(`${this.apiBase}/memories/${memoryId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.hideMemoryModal();
                this.refreshAll();
            } else {
                const error = await response.json();
                alert(`Error deleting memory: ${error.detail || error.error}`);
            }
        } catch (error) {
            console.error('Error deleting memory:', error);
            alert('Error deleting memory');
        }
    }
    
    async refreshAll() {
        await Promise.all([
            this.loadStats(),
            this.loadMemories()
        ]);
    }
    
    startAutoRefresh() {
        // Refresh stats every 30 seconds
        setInterval(() => this.loadStats(), 30000);
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new MemoryUI();
}); 