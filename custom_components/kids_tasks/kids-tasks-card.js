class KidsTasksCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
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

    const children = this.getChildren();
    const tasks = this.getTasks();
    const pendingValidations = this.getPendingValidations();

    this.shadowRoot.innerHTML = `
      <style>
        .card {
          padding: 16px;
          background: var(--card-background-color);
          border-radius: var(--border-radius);
          box-shadow: var(--card-box-shadow);
        }
        .child-card {
          margin: 8px 0;
          padding: 12px;
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-radius: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .child-info {
          display: flex;
          flex-direction: column;
        }
        .child-name {
          font-weight: bold;
          font-size: 1.1em;
        }
        .child-stats {
          font-size: 0.9em;
          opacity: 0.8;
        }
        .level-badge {
          background: var(--accent-color);
          color: white;
          padding: 4px 8px;
          border-radius: 12px;
          font-weight: bold;
        }
        .task-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px;
          margin: 4px 0;
          background: var(--secondary-background-color);
          border-radius: 6px;
        }
        .task-status {
          padding: 2px 8px;
          border-radius: 10px;
          font-size: 0.8em;
          font-weight: bold;
        }
        .status-todo { background: #ff9800; color: white; }
        .status-progress { background: #2196f3; color: white; }
        .status-pending { background: #ff5722; color: white; }
        .status-validated { background: #4caf50; color: white; }
        .button-group {
          display: flex;
          gap: 8px;
        }
        .btn {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9em;
        }
        .btn-primary { background: var(--primary-color); color: white; }
        .btn-success { background: #4caf50; color: white; }
        .btn-danger { background: #f44336; color: white; }
      </style>
      
      <div class="card">
        <h2>Gestion des Tâches Enfants</h2>
        
        <div class="children-section">
          <h3>Enfants</h3>
          ${children.map(child => `
            <div class="child-card">
              <div class="child-info">
                <div class="child-name">${child.name}</div>
                <div class="child-stats">${child.points} points • ${this.getChildTasksToday(child.id, tasks)} tâches aujourd'hui</div>
              </div>
              <div class="level-badge">Niveau ${child.level}</div>
            </div>
          `).join('')}
        </div>

        ${pendingValidations.length > 0 ? `
          <div class="validation-section">
            <h3>Tâches en attente de validation (${pendingValidations.length})</h3>
            ${pendingValidations.map(task => `
              <div class="task-item">
                <div>
                  <strong>${task.name}</strong><br>
                  <small>${this.getChildName(task.assigned_child_id, children)} • ${task.points} points</small>
                </div>
                <div class="button-group">
                  <button class="btn btn-success" onclick="this.validateTask('${task.id}')">Valider</button>
                  <button class="btn btn-danger" onclick="this.rejectTask('${task.id}')">Rejeter</button>
                </div>
              </div>
            `).join('')}
          </div>
        ` : ''}
        
        <div class="tasks-section">
          <h3>Toutes les tâches</h3>
          ${tasks.map(task => `
            <div class="task-item">
              <div>
                <strong>${task.name}</strong><br>
                <small>${this.getChildName(task.assigned_child_id, children)} • ${task.points} points</small>
              </div>
              <div class="task-status status-${task.status.replace('_', '-')}">${this.getStatusLabel(task.status)}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  getChildren() {
    const children = [];
    Object.keys(this._hass.states).forEach(entityId => {
      if (entityId.includes('kids_tasks') && entityId.includes('_points')) {
        const childId = entityId.split('_')[2];
        const pointsEntity = this._hass.states[entityId];
        const levelEntity = this._hass.states[`sensor.kids_tasks_${childId}_level`];
        
        if (pointsEntity && levelEntity) {
          children.push({
            id: childId,
            name: pointsEntity.attributes.friendly_name?.replace(' Points', '') || childId,
            points: parseInt(pointsEntity.state) || 0,
            level: parseInt(levelEntity.state) || 1,
          });
        }
      }
    });
    return children;
  }

  getTasks() {
    // Logique pour récupérer les tâches depuis les entités HA
    return [];
  }

  getPendingValidations() {
    // Logique pour récupérer les tâches en attente
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

  validateTask(taskId) {
    this._hass.callService('kids_tasks', 'validate_task', { task_id: taskId });
  }

  rejectTask(taskId) {
    this._hass.callService('kids_tasks', 'reset_task', { task_id: taskId });
  }
}

customElements.define('kids-tasks-card', KidsTasksCard);