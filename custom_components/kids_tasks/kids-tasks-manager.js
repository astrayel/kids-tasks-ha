class KidsTasksManager extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.currentView = 'dashboard';
    this.selectedChild = null;
    this.selectedTask = null;
  }

  setConfig(config) {
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  render() {
    if (!this._hass) return;

    this.shadowRoot.innerHTML = `
      ${this.getStyles()}
      <div class="kids-tasks-manager">
        ${this.getNavigation()}
        ${this.getCurrentView()}
      </div>
    `;

    this.attachEventListeners();
  }

  getStyles() {
    return `
      <style>
        .kids-tasks-manager {
          font-family: var(--paper-font-body1_-_font-family);
          background: var(--card-background-color);
          border-radius: var(--border-radius);
          box-shadow: var(--card-box-shadow);
          overflow: hidden;
        }
        
        .nav-tabs {
          display: flex;
          background: var(--primary-color);
          margin: 0;
          padding: 0;
        }
        
        .nav-tab {
          flex: 1;
          padding: 16px;
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          transition: background-color 0.3s;
          font-size: 14px;
        }
        
        .nav-tab:hover {
          background: rgba(255, 255, 255, 0.1);
        }
        
        .nav-tab.active {
          background: rgba(255, 255, 255, 0.2);
          font-weight: bold;
        }
        
        .content {
          padding: 20px;
        }
        
        .section {
          margin-bottom: 24px;
        }
        
        .section h2 {
          margin: 0 0 16px 0;
          color: var(--primary-text-color);
          font-size: 1.3em;
        }
        
        .child-card {
          display: flex;
          align-items: center;
          padding: 16px;
          margin: 8px 0;
          background: var(--secondary-background-color);
          border-radius: 8px;
          border-left: 4px solid var(--accent-color);
        }
        
        .child-avatar {
          font-size: 2em;
          margin-right: 16px;
        }
        
        .child-info {
          flex: 1;
        }
        
        .child-name {
          font-size: 1.1em;
          font-weight: bold;
          margin-bottom: 4px;
        }
        
        .child-stats {
          color: var(--secondary-text-color);
          font-size: 0.9em;
        }
        
        .level-badge {
          background: var(--accent-color);
          color: white;
          padding: 6px 12px;
          border-radius: 16px;
          font-weight: bold;
          margin: 0 8px;
        }
        
        .progress-bar {
          width: 100px;
          height: 8px;
          background: var(--divider-color);
          border-radius: 4px;
          overflow: hidden;
          margin-top: 4px;
        }
        
        .progress-fill {
          height: 100%;
          background: var(--accent-color);
          transition: width 0.3s;
        }
        
        .task-item {
          display: flex;
          align-items: center;
          padding: 12px;
          margin: 8px 0;
          background: var(--secondary-background-color);
          border-radius: 8px;
          border-left: 4px solid #ddd;
        }
        
        .task-item.pending {
          border-left-color: #ff5722;
        }
        
        .task-item.completed {
          border-left-color: #4caf50;
        }
        
        .task-content {
          flex: 1;
        }
        
        .task-title {
          font-weight: bold;
          margin-bottom: 4px;
        }
        
        .task-meta {
          font-size: 0.85em;
          color: var(--secondary-text-color);
        }
        
        .task-status {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 0.8em;
          font-weight: bold;
          text-transform: uppercase;
          margin: 0 8px;
        }
        
        .status-todo { background: #ff9800; color: white; }
        .status-in_progress { background: #2196f3; color: white; }
        .status-pending_validation { background: #ff5722; color: white; }
        .status-validated { background: #4caf50; color: white; }
        .status-failed { background: #f44336; color: white; }
        
        .form-group {
          margin-bottom: 16px;
        }
        
        .form-label {
          display: block;
          margin-bottom: 4px;
          font-weight: 500;
        }
        
        .form-input, .form-select, .form-textarea {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font-size: 14px;
          box-sizing: border-box;
        }
        
        .form-textarea {
          height: 80px;
          resize: vertical;
        }
        
        .form-row {
          display: flex;
          gap: 12px;
        }
        
        .form-row .form-group {
          flex: 1;
        }
        
        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.3s;
          margin-right: 8px;
        }
        
        .btn-primary {
          background: var(--primary-color);
          color: white;
        }
        
        .btn-primary:hover {
          background: color-mix(in srgb, var(--primary-color) 90%, black);
        }
        
        .btn-success {
          background: #4caf50;
          color: white;
        }
        
        .btn-danger {
          background: #f44336;
          color: white;
        }
        
        .btn-secondary {
          background: var(--secondary-background-color);
          color: var(--primary-text-color);
          border: 1px solid var(--divider-color);
        }
        
        .btn-icon {
          display: inline-flex;
          align-items: center;
          padding: 6px 12px;
          font-size: 12px;
        }
        
        .btn-icon::before {
          margin-right: 4px;
        }
        
        .add-btn::before { content: "+"; }
        .edit-btn::before { content: "✎"; }
        .delete-btn::before { content: "×"; }
        .validate-btn::before { content: "✓"; }
        .reject-btn::before { content = "×"; }
        
        .modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        
        .modal-content {
          background: var(--card-background-color);
          border-radius: 8px;
          padding: 24px;
          max-width: 500px;
          width: 90%;
          max-height: 90%;
          overflow-y: auto;
        }
        
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        
        .modal-title {
          margin: 0;
          font-size: 1.2em;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: var(--secondary-text-color);
        }
        
        .empty-state {
          text-align: center;
          padding: 40px;
          color: var(--secondary-text-color);
        }
        
        .empty-state-icon {
          font-size: 3em;
          margin-bottom: 16px;
        }
        
        .grid {
          display: grid;
          gap: 16px;
        }
        
        .grid-2 {
          grid-template-columns: 1fr 1fr;
        }
        
        .grid-3 {
          grid-template-columns: repeat(3, 1fr);
        }
        
        @media (max-width: 768px) {
          .grid-2, .grid-3 {
            grid-template-columns: 1fr;
          }
          
          .form-row {
            flex-direction: column;
          }
          
          .nav-tab {
            font-size: 12px;
            padding: 12px;
          }
        }
      </style>
    `;
  }

  getNavigation() {
    const tabs = [
      { id: 'dashboard', label: '📊 Tableau de bord', icon: '📊' },
      { id: 'children', label: '👶 Enfants', icon: '👶' },
      { id: 'tasks', label: '📝 Tâches', icon: '📝' },
      { id: 'rewards', label: '🎁 Récompenses', icon: '🎁' },
      { id: 'settings', label: '⚙️ Paramètres', icon: '⚙️' }
    ];

    return `
      <div class="nav-tabs">
        ${tabs.map(tab => `
          <button class="nav-tab ${this.currentView === tab.id ? 'active' : ''}" 
                  data-view="${tab.id}">
            ${tab.label}
          </button>
        `).join('')}
      </div>
    `;
  }

  getCurrentView() {
    switch (this.currentView) {
      case 'dashboard':
        return this.getDashboardView();
      case 'children':
        return this.getChildrenView();
      case 'tasks':
        return this.getTasksView();
      case 'rewards':
        return this.getRewardsView();
      case 'settings':
        return this.getSettingsView();
      default:
        return this.getDashboardView();
    }
  }

  getDashboardView() {
    const children = this.getChildren();
    const tasks = this.getTasks();
    const pendingTasks = tasks.filter(t => t.status === 'pending_validation');

    return `
      <div class="content">
        <div class="section">
          <h2>Vue d'ensemble</h2>
          <div class="grid grid-3">
            <div class="child-card">
              <div class="child-avatar">👶</div>
              <div class="child-info">
                <div class="child-name">${children.length} Enfant${children.length > 1 ? 's' : ''}</div>
                <div class="child-stats">Inscrits dans le système</div>
              </div>
            </div>
            <div class="child-card">
              <div class="child-avatar">📝</div>
              <div class="child-info">
                <div class="child-name">${tasks.length} Tâches</div>
                <div class="child-stats">Créées au total</div>
              </div>
            </div>
            <div class="child-card">
              <div class="child-avatar">⏳</div>
              <div class="child-info">
                <div class="child-name">${pendingTasks.length} En attente</div>
                <div class="child-stats">À valider</div>
              </div>
            </div>
          </div>
        </div>

        ${children.length > 0 ? `
          <div class="section">
            <h2>Enfants</h2>
            ${children.map(child => this.renderChildCard(child, tasks)).join('')}
          </div>
        ` : `
          <div class="empty-state">
            <div class="empty-state-icon">👶</div>
            <p>Aucun enfant ajouté pour le moment</p>
            <button class="btn btn-primary" data-action="add-child">Ajouter un enfant</button>
          </div>
        `}

        ${pendingTasks.length > 0 ? `
          <div class="section">
            <h2>Tâches à valider (${pendingTasks.length})</h2>
            ${pendingTasks.map(task => this.renderTaskItem(task, children, true)).join('')}
          </div>
        ` : ''}
      </div>
    `;
  }

  getChildrenView() {
    const children = this.getChildren();

    return `
      <div class="content">
        <div class="section">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2>Gestion des enfants</h2>
            <button class="btn btn-primary add-btn" data-action="add-child">Ajouter un enfant</button>
          </div>
          
          ${children.length > 0 ? `
            <div class="grid grid-2">
              ${children.map(child => `
                <div class="child-card">
                  <div class="child-avatar">${child.avatar || '👶'}</div>
                  <div class="child-info">
                    <div class="child-name">${child.name}</div>
                    <div class="child-stats">
                      ${child.points} points • Niveau ${child.level}
                      <div class="progress-bar">
                        <div class="progress-fill" style="width: ${child.progress}%"></div>
                      </div>
                    </div>
                  </div>
                  <div class="level-badge">Niveau ${child.level}</div>
                  <button class="btn btn-secondary btn-icon edit-btn" data-action="edit-child" data-id="${child.id}">Modifier</button>
                </div>
              `).join('')}
            </div>
          ` : `
            <div class="empty-state">
              <div class="empty-state-icon">👶</div>
              <p>Aucun enfant ajouté</p>
              <button class="btn btn-primary" data-action="add-child">Ajouter votre premier enfant</button>
            </div>
          `}
        </div>
      </div>
    `;
  }

  getTasksView() {
    const children = this.getChildren();
    const tasks = this.getTasks();

    return `
      <div class="content">
        <div class="section">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2>Gestion des tâches</h2>
            <button class="btn btn-primary add-btn" data-action="add-task">Ajouter une tâche</button>
          </div>
          
          ${tasks.length > 0 ? `
            ${tasks.map(task => this.renderTaskItem(task, children, false)).join('')}
          ` : `
            <div class="empty-state">
              <div class="empty-state-icon">📝</div>
              <p>Aucune tâche créée</p>
              <button class="btn btn-primary" data-action="add-task">Créer votre première tâche</button>
            </div>
          `}
        </div>
      </div>
    `;
  }

  getRewardsView() {
    const rewards = this.getRewards();

    return `
      <div class="content">
        <div class="section">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2>Gestion des récompenses</h2>
            <button class="btn btn-primary add-btn" data-action="add-reward">Ajouter une récompense</button>
          </div>
          
          ${rewards.length > 0 ? `
            <div class="grid grid-2">
              ${rewards.map(reward => `
                <div class="child-card">
                  <div class="child-avatar">🎁</div>
                  <div class="child-info">
                    <div class="child-name">${reward.name}</div>
                    <div class="child-stats">
                      ${reward.cost} points • ${reward.category}
                      ${reward.remaining_quantity !== null ? `• ${reward.remaining_quantity} restant(s)` : ''}
                    </div>
                  </div>
                  <button class="btn btn-secondary btn-icon edit-btn" data-action="edit-reward" data-id="${reward.id}">Modifier</button>
                </div>
              `).join('')}
            </div>
          ` : `
            <div class="empty-state">
              <div class="empty-state-icon">🎁</div>
              <p>Aucune récompense créée</p>
              <button class="btn btn-primary" data-action="add-reward">Créer votre première récompense</button>
            </div>
          `}
        </div>
      </div>
    `;
  }

  getSettingsView() {
    return `
      <div class="content">
        <div class="section">
          <h2>Paramètres de l'intégration</h2>
          <div class="form-group">
            <label class="form-label">
              <input type="checkbox" ${this.config?.validation_required !== false ? 'checked' : ''}> 
              Validation parentale requise par défaut
            </label>
          </div>
          <div class="form-group">
            <label class="form-label">
              <input type="checkbox" ${this.config?.notifications_enabled !== false ? 'checked' : ''}> 
              Notifications activées
            </label>
          </div>
          <div class="form-group">
            <label class="form-label">
              <input type="checkbox" ${this.config?.auto_reset_tasks !== false ? 'checked' : ''}> 
              Remise à zéro automatique des tâches quotidiennes
            </label>
          </div>
          <button class="btn btn-primary">Sauvegarder les paramètres</button>
        </div>
      </div>
    `;
  }

  renderChildCard(child, tasks) {
    const todayTasks = this.getChildTasksToday(child.id, tasks);
    const completedToday = tasks.filter(t => 
      t.assigned_child_id === child.id && 
      t.status === 'validated' && 
      this.isToday(t.last_completed_at)
    ).length;

    return `
      <div class="child-card">
        <div class="child-avatar">${child.avatar || '👶'}</div>
        <div class="child-info">
          <div class="child-name">${child.name}</div>
          <div class="child-stats">
            ${child.points} points • Niveau ${child.level} • ${completedToday} tâches terminées aujourd'hui
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${child.progress || 0}%"></div>
            </div>
          </div>
        </div>
        <div class="level-badge">Niveau ${child.level}</div>
      </div>
    `;
  }

  renderTaskItem(task, children, showActions = false) {
    const childName = this.getChildName(task.assigned_child_id, children);
    
    return `
      <div class="task-item ${task.status}">
        <div class="task-content">
          <div class="task-title">${task.name}</div>
          <div class="task-meta">
            ${childName} • ${task.points} points • ${task.category} • ${task.frequency}
            ${task.description ? `<br>${task.description}` : ''}
          </div>
        </div>
        <div class="task-status status-${task.status}">${this.getStatusLabel(task.status)}</div>
        ${showActions && task.status === 'pending_validation' ? `
          <button class="btn btn-success btn-icon validate-btn" data-action="validate-task" data-id="${task.id}">Valider</button>
          <button class="btn btn-danger btn-icon reject-btn" data-action="reject-task" data-id="${task.id}">Rejeter</button>
        ` : `
          <button class="btn btn-secondary btn-icon edit-btn" data-action="edit-task" data-id="${task.id}">Modifier</button>
        `}
      </div>
    `;
  }

  // Data retrieval methods (mocked for now)
  getChildren() {
    // Cette méthode sera implémentée pour récupérer les enfants depuis les entités HA
    return [];
  }

  getTasks() {
    // Cette méthode sera implémentée pour récupérer les tâches depuis les entités HA
    return [];
  }

  getRewards() {
    // Cette méthode sera implémentée pour récupérer les récompenses depuis les entités HA
    return [];
  }

  getChildTasksToday(childId, tasks) {
    return tasks.filter(task => 
      task.assigned_child_id === childId && 
      task.status === 'validated' &&
      this.isToday(task.last_completed_at)
    ).length;
  }

  getChildName(childId, children) {
    const child = children.find(c => c.id === childId);
    return child ? child.name : 'Non assigné';
  }

  getStatusLabel(status) {
    const labels = {
      'todo': 'À faire',
      'in_progress': 'En cours',
      'completed': 'Terminé',
      'pending_validation': 'En attente',
      'validated': 'Validé',
      'failed': 'Échoué',
    };
    return labels[status] || status;
  }

  isToday(dateString) {
    if (!dateString) return false;
    const date = new Date(dateString);
    const today = new Date();
    return date.toDateString() === today.toDateString();
  }

  attachEventListeners() {
    // Navigation tabs
    this.shadowRoot.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        this.currentView = e.target.dataset.view;
        this.render();
      });
    });

    // Action buttons
    this.shadowRoot.querySelectorAll('[data-action]').forEach(button => {
      button.addEventListener('click', (e) => {
        this.handleAction(e.target.dataset.action, e.target.dataset.id);
      });
    });
  }

  handleAction(action, id = null) {
    switch (action) {
      case 'add-child':
        this.showChildForm();
        break;
      case 'edit-child':
        this.showChildForm(id);
        break;
      case 'add-task':
        this.showTaskForm();
        break;
      case 'edit-task':
        this.showTaskForm(id);
        break;
      case 'add-reward':
        this.showRewardForm();
        break;
      case 'edit-reward':
        this.showRewardForm(id);
        break;
      case 'validate-task':
        this.validateTask(id);
        break;
      case 'reject-task':
        this.rejectTask(id);
        break;
    }
  }

  showChildForm(childId = null) {
    // Cette méthode sera implémentée dans la partie suivante
    console.log('Show child form', childId);
  }

  showTaskForm(taskId = null) {
    // Cette méthode sera implémentée dans la partie suivante
    console.log('Show task form', taskId);
  }

  showRewardForm(rewardId = null) {
    // Cette méthode sera implémentée dans la partie suivante
    console.log('Show reward form', rewardId);
  }

  validateTask(taskId) {
    this._hass.callService('kids_tasks', 'validate_task', { task_id: taskId });
  }

  rejectTask(taskId) {
    this._hass.callService('kids_tasks', 'reset_task', { task_id: taskId });
  }
}

customElements.define('kids-tasks-manager', KidsTasksManager);