// Extension pour la récupération et gestion des données
class KidsTasksDataMixin {

  // Récupération des enfants depuis les entités Home Assistant
  getChildren() {
    const children = [];
    const entities = this._hass.states;
    
    // Chercher les entités de points des enfants
    Object.keys(entities).forEach(entityId => {
      if (entityId.startsWith('sensor.kids_tasks_') && entityId.includes('_points')) {
        const childMatch = entityId.match(/sensor\.kids_tasks_(.+)_points/);
        if (childMatch) {
          const childId = childMatch[1];
          const pointsEntity = entities[entityId];
          const levelEntity = entities[`sensor.kids_tasks_${childId}_level`];
          
          if (pointsEntity && levelEntity) {
            const points = parseInt(pointsEntity.state) || 0;
            const level = parseInt(levelEntity.state) || 1;
            const pointsToNext = level * 100;
            const progress = ((points % 100) / 100) * 100;
            
            children.push({
              id: childId,
              name: pointsEntity.attributes.friendly_name?.replace(' Points', '') || childId,
              points: points,
              level: level,
              progress: progress,
              avatar: pointsEntity.attributes.avatar || '👶',
              created_at: pointsEntity.attributes.created_at || new Date().toISOString()
            });
          }
        }
      }
    });
    
    return children.sort((a, b) => a.name.localeCompare(b.name));
  }

  // Récupération des tâches depuis les entités Home Assistant
  getTasks() {
    const tasks = [];
    const entities = this._hass.states;
    
    // Chercher les entités de tâches
    Object.keys(entities).forEach(entityId => {
      if (entityId.startsWith('sensor.kids_tasks_task_')) {
        const taskEntity = entities[entityId];
        if (taskEntity && taskEntity.attributes) {
          const attrs = taskEntity.attributes;
          
          tasks.push({
            id: attrs.task_id || entityId.replace('sensor.kids_tasks_task_', ''),
            name: attrs.friendly_name || attrs.task_name || 'Tâche sans nom',
            description: attrs.description || '',
            category: attrs.category || 'other',
            points: parseInt(attrs.points) || 10,
            frequency: attrs.frequency || 'daily',
            status: taskEntity.state || 'todo',
            assigned_child_id: attrs.assigned_child_id || null,
            validation_required: attrs.validation_required !== false,
            active: attrs.active !== false,
            created_at: attrs.created_at || new Date().toISOString(),
            last_completed_at: attrs.last_completed_at || null,
            due_date: attrs.due_date || null
          });
        }
      }
    });
    
    return tasks.sort((a, b) => {
      // Trier par statut (en attente en premier) puis par nom
      if (a.status === 'pending_validation' && b.status !== 'pending_validation') return -1;
      if (b.status === 'pending_validation' && a.status !== 'pending_validation') return 1;
      return a.name.localeCompare(b.name);
    });
  }

  // Récupération des récompenses depuis les entités Home Assistant
  getRewards() {
    const rewards = [];
    const entities = this._hass.states;
    
    // Chercher les entités de récompenses
    Object.keys(entities).forEach(entityId => {
      if (entityId.startsWith('sensor.kids_tasks_reward_')) {
        const rewardEntity = entities[entityId];
        if (rewardEntity && rewardEntity.attributes) {
          const attrs = rewardEntity.attributes;
          
          rewards.push({
            id: attrs.reward_id || entityId.replace('sensor.kids_tasks_reward_', ''),
            name: attrs.friendly_name || attrs.reward_name || 'Récompense sans nom',
            description: attrs.description || '',
            category: attrs.category || 'fun',
            cost: parseInt(attrs.cost) || 50,
            active: attrs.active !== false,
            limited_quantity: attrs.limited_quantity || null,
            remaining_quantity: attrs.remaining_quantity || null
          });
        }
      }
    });
    
    return rewards.sort((a, b) => a.name.localeCompare(b.name));
  }

  // Récupérer les statistiques générales
  getStats() {
    const children = this.getChildren();
    const tasks = this.getTasks();
    const todayTasks = tasks.filter(task => 
      task.frequency === 'daily' || 
      (task.last_completed_at && this.isToday(task.last_completed_at))
    );
    const completedToday = tasks.filter(task => 
      task.status === 'validated' && 
      task.last_completed_at && 
      this.isToday(task.last_completed_at)
    ).length;

    return {
      totalChildren: children.length,
      totalTasks: tasks.length,
      todayTasks: todayTasks.length,
      completedToday: completedToday,
      pendingValidation: tasks.filter(t => t.status === 'pending_validation').length,
      totalPoints: children.reduce((sum, child) => sum + child.points, 0)
    };
  }

  // Récupérer les tâches d'un enfant pour aujourd'hui
  getChildTasksToday(childId, tasks = null) {
    if (!tasks) tasks = this.getTasks();
    
    return tasks.filter(task => 
      task.assigned_child_id === childId && 
      (task.frequency === 'daily' || 
       (task.last_completed_at && this.isToday(task.last_completed_at)))
    );
  }

  // Récupérer les tâches complétées aujourd'hui pour un enfant
  getChildCompletedToday(childId, tasks = null) {
    if (!tasks) tasks = this.getTasks();
    
    return tasks.filter(task => 
      task.assigned_child_id === childId && 
      task.status === 'validated' &&
      task.last_completed_at && 
      this.isToday(task.last_completed_at)
    );
  }

  // Récupérer le leaderboard des enfants
  getChildrenLeaderboard() {
    const children = this.getChildren();
    const tasks = this.getTasks();
    
    return children.map(child => {
      const todayCompleted = this.getChildCompletedToday(child.id, tasks).length;
      const todayTasks = this.getChildTasksToday(child.id, tasks).length;
      const completionRate = todayTasks > 0 ? (todayCompleted / todayTasks) * 100 : 0;
      
      return {
        ...child,
        todayCompleted,
        todayTasks,
        completionRate
      };
    }).sort((a, b) => b.points - a.points);
  }

  // Services Home Assistant
  async callService(service, serviceData = {}) {
    try {
      await this._hass.callService('kids_tasks', service, serviceData);
      
      // Attendre un peu puis rafraîchir l'affichage
      setTimeout(() => {
        this.render();
      }, 1000);
      
      return true;
    } catch (error) {
      console.error(`Erreur lors de l'appel du service ${service}:`, error);
      this.showNotification(`Erreur: ${error.message}`, 'error');
      return false;
    }
  }

  // Services spécifiques
  async addChild(childData) {
    return await this.callService('add_child', childData);
  }

  async updateChild(childId, childData) {
    return await this.callService('update_child', { child_id: childId, ...childData });
  }

  async removeChild(childId) {
    return await this.callService('remove_child', { child_id: childId });
  }

  async addTask(taskData) {
    return await this.callService('add_task', taskData);
  }

  async updateTask(taskId, taskData) {
    return await this.callService('update_task', { task_id: taskId, ...taskData });
  }

  async removeTask(taskId) {
    return await this.callService('remove_task', { task_id: taskId });
  }

  async completeTask(taskId, validationRequired = null) {
    return await this.callService('complete_task', { 
      task_id: taskId, 
      validation_required: validationRequired 
    });
  }

  async validateTask(taskId) {
    return await this.callService('validate_task', { task_id: taskId });
  }

  async rejectTask(taskId) {
    return await this.callService('reset_task', { task_id: taskId });
  }

  async addReward(rewardData) {
    return await this.callService('add_reward', rewardData);
  }

  async updateReward(rewardId, rewardData) {
    return await this.callService('update_reward', { reward_id: rewardId, ...rewardData });
  }

  async claimReward(rewardId, childId) {
    return await this.callService('claim_reward', { reward_id: rewardId, child_id: childId });
  }

  // Utilitaires
  isToday(dateString) {
    if (!dateString) return false;
    const date = new Date(dateString);
    const today = new Date();
    return date.toDateString() === today.toDateString();
  }

  formatDate(dateString) {
    if (!dateString) return 'Jamais';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Aujourd\'hui';
    if (diffDays === 1) return 'Hier';
    if (diffDays < 7) return `Il y a ${diffDays} jours`;
    
    return date.toLocaleDateString('fr-FR');
  }

  getChildName(childId, children = null) {
    if (!children) children = this.getChildren();
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

  getCategoryLabel(category) {
    const labels = {
      'bedroom': '🛏️ Chambre',
      'bathroom': '🛁 Salle de bain', 
      'kitchen': '🍽️ Cuisine',
      'homework': '📚 Devoirs',
      'outdoor': '🌳 Extérieur',
      'pets': '🐕 Animaux',
      'other': '📦 Autre'
    };
    return labels[category] || category;
  }

  getFrequencyLabel(frequency) {
    const labels = {
      'daily': 'Quotidienne',
      'weekly': 'Hebdomadaire', 
      'monthly': 'Mensuelle',
      'once': 'Une fois'
    };
    return labels[frequency] || frequency;
  }

  // Notification simple
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 20px;
      background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#2196f3'};
      color: white;
      border-radius: 4px;
      z-index: 10000;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  // Confirmer une action
  confirm(message, callback) {
    if (window.confirm(message)) {
      callback();
    }
  }
}

// Appliquer le mixin à la classe principale
Object.assign(KidsTasksManager.prototype, KidsTasksDataMixin.prototype);