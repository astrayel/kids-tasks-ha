// Fichier principal qui assemble tous les composants de l'interface Kids Tasks Manager

// Import des mixins (dans un vrai environnement, ces scripts seraient chargés séparément)
// Pour l'instant, on les inclut directement dans ce fichier

class KidsTasksCompleteManager extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.currentView = 'dashboard';
    this.selectedChild = null;
    this.selectedTask = null;
  }

  setConfig(config) {
    this.config = config || {};
    this.title = config.title || 'Gestionnaire de Tâches Enfants';
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initialized = true;
      this.addEventListener('click', this.handleClick.bind(this));
    }
    this.render();
  }

  connectedCallback() {
    this.render();
  }

  render() {
    if (!this._hass) return;

    this.shadowRoot.innerHTML = `
      ${this.getStyles()}
      <div class="kids-tasks-manager">
        ${this.getNavigation()}
        <div class="content">
          ${this.getCurrentView()}
        </div>
      </div>
    `;
  }

  handleClick(event) {
    const target = event.target.closest('[data-action]');
    if (!target) return;

    event.preventDefault();
    event.stopPropagation();

    const action = target.dataset.action;
    const id = target.dataset.id;

    this.handleAction(action, id);
  }

  handleAction(action, id = null) {
    switch (action) {
      case 'switch-view':
        this.currentView = id;
        this.render();
        break;
      case 'add-child':
        this.showChildForm();
        break;
      case 'edit-child':
        this.showChildForm(id);
        break;
      case 'remove-child':
        this.confirm(`Êtes-vous sûr de vouloir supprimer cet enfant ?`, () => {
          this.removeChild(id);
        });
        break;
      case 'add-task':
        this.showTaskForm();
        break;
      case 'edit-task':
        this.showTaskForm(id);
        break;
      case 'remove-task':
        this.confirm(`Êtes-vous sûr de vouloir supprimer cette tâche ?`, () => {
          this.removeTask(id);
        });
        break;
      case 'complete-task':
        this.completeTask(id);
        break;
      case 'validate-task':
        this.validateTask(id);
        break;
      case 'reject-task':
        this.rejectTask(id);
        break;
      case 'add-reward':
        this.showRewardForm();
        break;
      case 'edit-reward':
        this.showRewardForm(id);
        break;
      case 'claim-reward':
        this.showClaimRewardDialog(id);
        break;
      case 'close-modal':
        this.hideModal();
        break;
    }
  }

  showClaimRewardDialog(rewardId) {
    const reward = this.getRewardById(rewardId);
    const children = this.getChildren();
    
    if (!reward || children.length === 0) return;

    const availableChildren = children.filter(child => child.points >= reward.cost);

    const modal = this.createModal(
      'Échanger une récompense',
      `
        <div class="reward-claim">
          <div class="reward-info">
            <h3>${reward.name}</h3>
            <p>Coût: ${reward.cost} points</p>
            ${reward.description ? `<p>${reward.description}</p>` : ''}
          </div>
          
          ${availableChildren.length > 0 ? `
            <div class="form-group">
              <label class="form-label">Choisir l'enfant :</label>
              <select id="claim-child" class="form-select">
                ${availableChildren.map(child => `
                  <option value="${child.id}">${child.name} (${child.points} points)</option>
                `).join('')}
              </select>
            </div>
          ` : `
            <div class="empty-state">
              <p>Aucun enfant n'a suffisamment de points pour cette récompense.</p>
            </div>
          `}
        </div>
      `,
      availableChildren.length > 0 ? () => {
        const childId = this.shadowRoot.getElementById('claim-child').value;
        this.claimReward(rewardId, childId);
      } : null
    );
    
    this.showModal(modal);
  }

  // Styles CSS complets
  getStyles() {
    return `
      <style>
        * {
          box-sizing: border-box;
        }
        
        .kids-tasks-manager {
          font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
          background: var(--card-background-color, white);
          border-radius: var(--border-radius, 8px);
          box-shadow: var(--card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
          overflow: hidden;
          min-height: 400px;
        }
        
        .nav-tabs {
          display: flex;
          background: var(--primary-color, #3f51b5);
          margin: 0;
          padding: 0;
          border-bottom: 1px solid var(--divider-color, #e0e0e0);
        }
        
        .nav-tab {
          flex: 1;
          padding: 12px 8px;
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          transition: all 0.3s;
          font-size: 13px;
          text-align: center;
          min-height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
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
          background: var(--card-background-color, white);
          min-height: 300px;
        }
        
        .section {
          margin-bottom: 24px;
        }
        
        .section h2 {
          margin: 0 0 16px 0;
          color: var(--primary-text-color, #212121);
          font-size: 1.3em;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        
        .stat-card {
          padding: 16px;
          background: var(--secondary-background-color, #fafafa);
          border-radius: 8px;
          border-left: 4px solid var(--accent-color, #ff4081);
          display: flex;
          align-items: center;
        }
        
        .stat-icon {
          font-size: 2em;
          margin-right: 16px;
        }
        
        .stat-info {
          flex: 1;
        }
        
        .stat-number {
          font-size: 1.5em;
          font-weight: bold;
          color: var(--primary-text-color, #212121);
        }
        
        .stat-label {
          color: var(--secondary-text-color, #757575);
          font-size: 0.9em;
        }
        
        .child-card {
          display: flex;
          align-items: center;
          padding: 16px;
          margin: 8px 0;
          background: var(--secondary-background-color, #fafafa);
          border-radius: 8px;
          border-left: 4px solid var(--accent-color, #ff4081);
          transition: all 0.3s;
        }
        
        .child-card:hover {
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .child-avatar {
          font-size: 2.5em;
          margin-right: 16px;
        }
        
        .child-info {
          flex: 1;
        }
        
        .child-name {
          font-size: 1.1em;
          font-weight: bold;
          margin-bottom: 4px;
          color: var(--primary-text-color, #212121);
        }
        
        .child-stats {
          color: var(--secondary-text-color, #757575);
          font-size: 0.9em;
          margin-bottom: 8px;
        }
        
        .level-badge {
          background: var(--accent-color, #ff4081);
          color: white;
          padding: 4px 12px;
          border-radius: 16px;
          font-weight: bold;
          font-size: 0.8em;
          margin: 0 8px;
        }
        
        .progress-bar {
          width: 120px;
          height: 6px;
          background: var(--divider-color, #e0e0e0);
          border-radius: 3px;
          overflow: hidden;
          margin-top: 6px;
        }
        
        .progress-fill {
          height: 100%;
          background: var(--accent-color, #ff4081);
          transition: width 0.3s ease;
        }
        
        .task-item {
          display: flex;
          align-items: center;
          padding: 12px;
          margin: 8px 0;
          background: var(--secondary-background-color, #fafafa);
          border-radius: 8px;
          border-left: 4px solid #ddd;
          transition: all 0.3s;
        }
        
        .task-item:hover {
          box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }
        
        .task-item.pending_validation {
          border-left-color: #ff5722;
          background: #fff3e0;
        }
        
        .task-item.validated {
          border-left-color: #4caf50;
        }
        
        .task-content {
          flex: 1;
        }
        
        .task-title {
          font-weight: bold;
          margin-bottom: 4px;
          color: var(--primary-text-color, #212121);
        }
        
        .task-meta {
          font-size: 0.85em;
          color: var(--secondary-text-color, #757575);
        }
        
        .task-actions {
          display: flex;
          gap: 8px;
        }
        
        .task-status {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 0.75em;
          font-weight: bold;
          text-transform: uppercase;
          margin: 0 8px;
          white-space: nowrap;
        }
        
        .status-todo { background: #ff9800; color: white; }
        .status-in_progress { background: #2196f3; color: white; }
        .status-pending_validation { background: #ff5722; color: white; }
        .status-validated { background: #4caf50; color: white; }
        .status-failed { background: #f44336; color: white; }
        
        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 500;
          transition: all 0.3s;
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-height: 32px;
        }
        
        .btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .btn:active {
          transform: translateY(0);
        }
        
        .btn-primary {
          background: var(--primary-color, #3f51b5);
          color: white;
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
          background: var(--secondary-background-color, #fafafa);
          color: var(--primary-text-color, #212121);
          border: 1px solid var(--divider-color, #e0e0e0);
        }
        
        .btn-icon {
          padding: 6px 12px;
          font-size: 12px;
        }
        
        .btn-icon::before {
          margin-right: 4px;
          font-weight: normal;
        }
        
        .add-btn::before { content: "+ "; }
        .edit-btn::before { content: "✎ "; }
        .delete-btn::before { content: "🗑 "; }
        .validate-btn::before { content: "✓ "; }
        .reject-btn::before { content: "✗ "; }
        .claim-btn::before { content = "🎁 "; }
        
        .form-group {
          margin-bottom: 16px;
        }
        
        .form-label {
          display: block;
          margin-bottom: 4px;
          font-weight: 500;
          color: var(--primary-text-color, #212121);
        }
        
        .form-input, .form-select, .form-textarea {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid var(--divider-color, #e0e0e0);
          border-radius: 4px;
          background: var(--card-background-color, white);
          color: var(--primary-text-color, #212121);
          font-size: 14px;
          font-family: inherit;
        }
        
        .form-input:focus, .form-select:focus, .form-textarea:focus {
          outline: none;
          border-color: var(--primary-color, #3f51b5);
          box-shadow: 0 0 0 2px rgba(63, 81, 181, 0.2);
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
        
        .avatar-options {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          margin-bottom: 8px;
        }
        
        .avatar-option {
          padding: 8px;
          border: 2px solid var(--divider-color, #e0e0e0);
          border-radius: 8px;
          background: var(--secondary-background-color, #fafafa);
          cursor: pointer;
          font-size: 1.5em;
          transition: all 0.3s;
        }
        
        .avatar-option:hover {
          border-color: var(--primary-color, #3f51b5);
        }
        
        .avatar-option.selected {
          border-color: var(--accent-color, #ff4081);
          background: rgba(255, 64, 129, 0.1);
        }
        
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
          opacity: 0;
          animation: fadeIn 0.3s forwards;
        }
        
        @keyframes fadeIn {
          to { opacity: 1; }
        }
        
        .modal-content {
          background: var(--card-background-color, white);
          border-radius: 8px;
          padding: 0;
          max-width: 500px;
          width: 90%;
          max-height: 90%;
          overflow: hidden;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
          transform: scale(0.9);
          animation: scaleIn 0.3s forwards;
        }
        
        @keyframes scaleIn {
          to { transform: scale(1); }
        }
        
        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 24px;
          border-bottom: 1px solid var(--divider-color, #e0e0e0);
          background: var(--secondary-background-color, #fafafa);
        }
        
        .modal-title {
          margin: 0;
          font-size: 1.2em;
          color: var(--primary-text-color, #212121);
        }
        
        .modal-body {
          padding: 24px;
          max-height: 60vh;
          overflow-y: auto;
        }
        
        .modal-footer {
          padding: 16px 24px;
          border-top: 1px solid var(--divider-color, #e0e0e0);
          background: var(--secondary-background-color, #fafafa);
          display: flex;
          justify-content: flex-end;
          gap: 12px;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: var(--secondary-text-color, #757575);
          padding: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          transition: all 0.3s;
        }
        
        .close-btn:hover {
          background: rgba(0,0,0,0.1);
        }
        
        .empty-state {
          text-align: center;
          padding: 40px;
          color: var(--secondary-text-color, #757575);
        }
        
        .empty-state-icon {
          font-size: 4em;
          margin-bottom: 16px;
          opacity: 0.5;
        }
        
        .empty-state p {
          margin: 0 0 20px 0;
          font-size: 1.1em;
        }
        
        .grid {
          display: grid;
          gap: 16px;
        }
        
        .grid-2 {
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }
        
        .grid-3 {
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        }
        
        .reward-claim {
          text-align: center;
        }
        
        .reward-info {
          margin-bottom: 24px;
          padding: 16px;
          background: var(--secondary-background-color, #fafafa);
          border-radius: 8px;
        }
        
        .reward-info h3 {
          margin: 0 0 8px 0;
          color: var(--primary-text-color, #212121);
        }
        
        .loading {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 40px;
          color: var(--secondary-text-color, #757575);
        }
        
        @media (max-width: 768px) {
          .content {
            padding: 16px;
          }
          
          .nav-tab {
            font-size: 11px;
            padding: 8px 4px;
          }
          
          .form-row {
            flex-direction: column;
          }
          
          .grid-2, .grid-3 {
            grid-template-columns: 1fr;
          }
          
          .child-card {
            flex-direction: column;
            text-align: center;
            padding: 16px 12px;
          }
          
          .child-avatar {
            margin: 0 0 12px 0;
          }
          
          .task-item {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .task-actions {
            margin-top: 12px;
            width: 100%;
            justify-content: center;
          }
          
          .modal-content {
            width: 95%;
            margin: 0 auto;
          }
          
          .modal-body {
            padding: 16px;
          }
        }
      </style>
    `;
  }

  // Navigation
  getNavigation() {
    const tabs = [
      { id: 'dashboard', label: '📊 Tableau', icon: '📊' },
      { id: 'children', label: '👶 Enfants', icon: '👶' },
      { id: 'tasks', label: '📝 Tâches', icon: '📝' },
      { id: 'rewards', label: '🎁 Récompenses', icon: '🎁' }
    ];

    return `
      <div class="nav-tabs">
        ${tabs.map(tab => `
          <button class="nav-tab ${this.currentView === tab.id ? 'active' : ''}" 
                  data-action="switch-view" data-id="${tab.id}">
            ${tab.label}
          </button>
        `).join('')}
      </div>
    `;
  }

  // Vues
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
      default:
        return this.getDashboardView();
    }
  }

  getDashboardView() {
    const children = this.getChildren();
    const tasks = this.getTasks();
    const stats = this.getStats();
    const pendingTasks = tasks.filter(t => t.status === 'pending_validation');
    const leaderboard = this.getChildrenLeaderboard();

    return `
      <div class="section">
        <h2>Tableau de bord</h2>
        
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">👶</div>
            <div class="stat-info">
              <div class="stat-number">${stats.totalChildren}</div>
              <div class="stat-label">Enfant${stats.totalChildren > 1 ? 's' : ''}</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-info">
              <div class="stat-number">${stats.totalTasks}</div>
              <div class="stat-label">Tâches créées</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <div class="stat-number">${stats.completedToday}</div>
              <div class="stat-label">Terminées aujourd'hui</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏳</div>
            <div class="stat-info">
              <div class="stat-number">${stats.pendingValidation}</div>
              <div class="stat-label">À valider</div>
            </div>
          </div>
        </div>
      </div>

      ${leaderboard.length > 0 ? `
        <div class="section">
          <h2>Classement des enfants</h2>
          ${leaderboard.map((child, index) => `
            <div class="child-card">
              <div class="stat-icon">${index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '👶'}</div>
              <div class="child-avatar">${child.avatar}</div>
              <div class="child-info">
                <div class="child-name">${child.name}</div>
                <div class="child-stats">
                  ${child.points} points • ${child.todayCompleted}/${child.todayTasks} tâches aujourd'hui
                  ${child.completionRate > 0 ? `• ${Math.round(child.completionRate)}% de réussite` : ''}
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: ${child.completionRate || 0}%"></div>
                  </div>
                </div>
              </div>
              <div class="level-badge">Niveau ${child.level}</div>
            </div>
          `).join('')}
        </div>
      ` : `
        <div class="empty-state">
          <div class="empty-state-icon">👶</div>
          <p>Aucun enfant enregistré</p>
          <button class="btn btn-primary" data-action="add-child">Ajouter votre premier enfant</button>
        </div>
      `}

      ${pendingTasks.length > 0 ? `
        <div class="section">
          <h2>Tâches à valider (${pendingTasks.length})</h2>
          ${pendingTasks.map(task => this.renderTaskItem(task, children, true)).join('')}
        </div>
      ` : ''}
    `;
  }

  getChildrenView() {
    const children = this.getChildren();

    return `
      <div class="section">
        <h2>
          Gestion des enfants
          <button class="btn btn-primary add-btn" data-action="add-child">Ajouter</button>
        </h2>
        
        ${children.length > 0 ? `
          <div class="grid grid-2">
            ${children.map(child => this.renderChildCard(child)).join('')}
          </div>
        ` : `
          <div class="empty-state">
            <div class="empty-state-icon">👶</div>
            <p>Aucun enfant ajouté</p>
            <button class="btn btn-primary" data-action="add-child">Ajouter votre premier enfant</button>
          </div>
        `}
      </div>
    `;
  }

  getTasksView() {
    const children = this.getChildren();
    const tasks = this.getTasks();

    return `
      <div class="section">
        <h2>
          Gestion des tâches
          <button class="btn btn-primary add-btn" data-action="add-task">Ajouter</button>
        </h2>
        
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
    `;
  }

  getRewardsView() {
    const rewards = this.getRewards();

    return `
      <div class="section">
        <h2>
          Gestion des récompenses
          <button class="btn btn-primary add-btn" data-action="add-reward">Ajouter</button>
        </h2>
        
        ${rewards.length > 0 ? `
          <div class="grid grid-2">
            ${rewards.map(reward => this.renderRewardCard(reward)).join('')}
          </div>
        ` : `
          <div class="empty-state">
            <div class="empty-state-icon">🎁</div>
            <p>Aucune récompense créée</p>
            <button class="btn btn-primary" data-action="add-reward">Créer votre première récompense</button>
          </div>
        `}
      </div>
    `;
  }

  // Rendu des éléments
  renderChildCard(child) {
    const tasks = this.getTasks();
    const completedToday = this.getChildCompletedToday(child.id, tasks).length;
    const todayTasks = this.getChildTasksToday(child.id, tasks).length;

    return `
      <div class="child-card">
        <div class="child-avatar">${child.avatar}</div>
        <div class="child-info">
          <div class="child-name">${child.name}</div>
          <div class="child-stats">
            ${child.points} points • Niveau ${child.level}<br>
            ${completedToday}/${todayTasks} tâches aujourd'hui
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${child.progress || 0}%"></div>
            </div>
          </div>
        </div>
        <div class="level-badge">Niveau ${child.level}</div>
        <div class="task-actions">
          <button class="btn btn-secondary btn-icon edit-btn" data-action="edit-child" data-id="${child.id}">Modifier</button>
        </div>
      </div>
    `;
  }

  renderTaskItem(task, children, showValidation = false) {
    const childName = this.getChildName(task.assigned_child_id, children);
    
    return `
      <div class="task-item ${task.status}">
        <div class="task-content">
          <div class="task-title">${task.name}</div>
          <div class="task-meta">
            ${childName} • ${task.points} points • ${this.getCategoryLabel(task.category)} • ${this.getFrequencyLabel(task.frequency)}
            ${task.description ? `<br>${task.description}` : ''}
          </div>
        </div>
        <div class="task-status status-${task.status}">${this.getStatusLabel(task.status)}</div>
        <div class="task-actions">
          ${showValidation && task.status === 'pending_validation' ? `
            <button class="btn btn-success btn-icon validate-btn" data-action="validate-task" data-id="${task.id}">Valider</button>
            <button class="btn btn-danger btn-icon reject-btn" data-action="reject-task" data-id="${task.id}">Rejeter</button>
          ` : `
            <button class="btn btn-secondary btn-icon edit-btn" data-action="edit-task" data-id="${task.id}">Modifier</button>
          `}
        </div>
      </div>
    `;
  }

  renderRewardCard(reward) {
    return `
      <div class="child-card">
        <div class="child-avatar">🎁</div>
        <div class="child-info">
          <div class="child-name">${reward.name}</div>
          <div class="child-stats">
            ${reward.cost} points • ${this.getCategoryLabel(reward.category)}
            ${reward.remaining_quantity !== null ? `<br>${reward.remaining_quantity} restant(s)` : ''}
            ${reward.description ? `<br>${reward.description}` : ''}
          </div>
        </div>
        <div class="task-actions">
          <button class="btn btn-primary btn-icon claim-btn" data-action="claim-reward" data-id="${reward.id}">Échanger</button>
          <button class="btn btn-secondary btn-icon edit-btn" data-action="edit-reward" data-id="${reward.id}">Modifier</button>
        </div>
      </div>
    `;
  }

  // Intégration des autres composants (forms et data)
  // Ces méthodes seront ajoutées via les mixins dans les autres fichiers

  // Méthodes de base qui seront étendues
  getChildren() { return []; }
  getTasks() { return []; }
  getRewards() { return []; }
  getStats() { return { totalChildren: 0, totalTasks: 0, completedToday: 0, pendingValidation: 0 }; }
  getChildrenLeaderboard() { return []; }
  getChildTasksToday() { return []; }
  getChildCompletedToday() { return []; }
  getChildName() { return 'Non assigné'; }
  getStatusLabel() { return 'Inconnu'; }
  getCategoryLabel() { return 'Autre'; }
  getFrequencyLabel() { return 'Une fois'; }
  showChildForm() { console.log('showChildForm not implemented'); }
  showTaskForm() { console.log('showTaskForm not implemented'); }
  showRewardForm() { console.log('showRewardForm not implemented'); }
  validateTask(id) { console.log('validateTask not implemented', id); }
  rejectTask(id) { console.log('rejectTask not implemented', id); }
  claimReward(rewardId, childId) { console.log('claimReward not implemented', rewardId, childId); }
  createModal() { return ''; }
  showModal() { console.log('showModal not implemented'); }
  hideModal() { console.log('hideModal not implemented'); }
  confirm(message, callback) { if (window.confirm(message)) callback(); }
  getChildById() { return null; }
  getTaskById() { return null; }
  getRewardById() { return null; }
  removeChild() { console.log('removeChild not implemented'); }
  removeTask() { console.log('removeTask not implemented'); }
  completeTask() { console.log('completeTask not implemented'); }
}

// Configuration de la carte pour Home Assistant
KidsTasksCompleteManager.getConfigElement = function() {
  const element = document.createElement('div');
  element.innerHTML = `
    <div>
      <paper-input 
        label="Titre (optionnel)" 
        .value="\${this.config.title || ''}"
        .configValue="title">
      </paper-input>
    </div>
  `;
  return element;
};

KidsTasksCompleteManager.getStubConfig = function() {
  return {
    title: "Gestionnaire de Tâches Enfants"
  };
};

// Enregistrer le composant
customElements.define('kids-tasks-complete-manager', KidsTasksCompleteManager);

// Déclarer la carte pour HACS/Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'kids-tasks-complete-manager',
  name: 'Kids Tasks Manager',
  description: 'Interface complète pour gérer les tâches et récompenses des enfants'
});