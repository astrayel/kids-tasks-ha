// Extension des formulaires pour KidsTasksManager
class KidsTasksFormMixin {
  
  showChildForm(childId = null) {
    const child = childId ? this.getChildById(childId) : null;
    const isEdit = !!child;
    
    const modal = this.createModal(
      isEdit ? 'Modifier un enfant' : 'Ajouter un enfant',
      this.getChildFormHTML(child),
      () => this.submitChildForm(childId)
    );
    
    this.showModal(modal);
  }

  getChildFormHTML(child = null) {
    return `
      <form id="child-form">
        <div class="form-group">
          <label class="form-label">Nom de l'enfant *</label>
          <input type="text" id="child-name" class="form-input" 
                 placeholder="Ex: Emma" value="${child?.name || ''}" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">Avatar (emoji)</label>
          <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
            ${this.getAvatarOptions(child?.avatar)}
          </div>
          <input type="text" id="child-avatar" class="form-input" 
                 placeholder="Ou tapez un emoji" value="${child?.avatar || ''}">
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Points initiaux</label>
            <input type="number" id="child-points" class="form-input" 
                   min="0" value="${child?.points || 0}">
          </div>
          <div class="form-group">
            <label class="form-label">Niveau</label>
            <input type="number" id="child-level" class="form-input" 
                   min="1" value="${child?.level || 1}" readonly>
          </div>
        </div>
      </form>
    `;
  }

  getAvatarOptions(selectedAvatar = '') {
    const avatars = ['👧', '👦', '🧒', '👶', '🦸‍♀️', '🦸‍♂️', '🎓', '🏃‍♀️', '🏃‍♂️', '🎨', '📚', '⚽'];
    
    return avatars.map(avatar => `
      <button type="button" class="avatar-option ${selectedAvatar === avatar ? 'selected' : ''}" 
              data-avatar="${avatar}" 
              style="padding: 8px; border: 2px solid ${selectedAvatar === avatar ? 'var(--accent-color)' : 'var(--divider-color)'}; 
                     border-radius: 8px; background: var(--secondary-background-color); cursor: pointer; font-size: 1.5em;">
        ${avatar}
      </button>
    `).join('');
  }

  submitChildForm(childId = null) {
    const form = this.shadowRoot.getElementById('child-form');
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const formData = {
      name: this.shadowRoot.getElementById('child-name').value,
      avatar: this.shadowRoot.getElementById('child-avatar').value,
    };

    if (childId) {
      formData.points = parseInt(this.shadowRoot.getElementById('child-points').value) || 0;
      // Appel service de mise à jour
      this._hass.callService('kids_tasks', 'update_child', {
        child_id: childId,
        ...formData
      });
    } else {
      // Appel service de création
      this._hass.callService('kids_tasks', 'add_child', formData);
    }

    this.hideModal();
  }

  showTaskForm(taskId = null) {
    const task = taskId ? this.getTaskById(taskId) : null;
    const isEdit = !!task;
    
    const modal = this.createModal(
      isEdit ? 'Modifier une tâche' : 'Ajouter une tâche',
      this.getTaskFormHTML(task),
      () => this.submitTaskForm(taskId)
    );
    
    this.showModal(modal);
  }

  getTaskFormHTML(task = null) {
    const children = this.getChildren();
    const categories = [
      { value: 'bedroom', label: '🛏️ Chambre' },
      { value: 'bathroom', label: '🛁 Salle de bain' },
      { value: 'kitchen', label: '🍽️ Cuisine' },
      { value: 'homework', label: '📚 Devoirs' },
      { value: 'outdoor', label: '🌳 Extérieur' },
      { value: 'pets', label: '🐕 Animaux' },
      { value: 'other', label: '📦 Autre' }
    ];

    const frequencies = [
      { value: 'daily', label: 'Quotidienne' },
      { value: 'weekly', label: 'Hebdomadaire' },
      { value: 'monthly', label: 'Mensuelle' },
      { value: 'once', label: 'Une seule fois' }
    ];

    return `
      <form id="task-form">
        <div class="form-group">
          <label class="form-label">Nom de la tâche *</label>
          <input type="text" id="task-name" class="form-input" 
                 placeholder="Ex: Ranger sa chambre" value="${task?.name || ''}" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">Description</label>
          <textarea id="task-description" class="form-textarea" 
                    placeholder="Description détaillée de la tâche">${task?.description || ''}</textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Catégorie</label>
            <select id="task-category" class="form-select">
              ${categories.map(cat => `
                <option value="${cat.value}" ${task?.category === cat.value ? 'selected' : ''}>${cat.label}</option>
              `).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Fréquence</label>
            <select id="task-frequency" class="form-select">
              ${frequencies.map(freq => `
                <option value="${freq.value}" ${task?.frequency === freq.value ? 'selected' : ''}>${freq.label}</option>
              `).join('')}
            </select>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Points attribués</label>
            <input type="number" id="task-points" class="form-input" 
                   min="1" max="100" value="${task?.points || 10}">
          </div>
          <div class="form-group">
            <label class="form-label">Assigné à</label>
            <select id="task-assigned" class="form-select">
              <option value="">Non assigné</option>
              ${children.map(child => `
                <option value="${child.id}" ${task?.assigned_child_id === child.id ? 'selected' : ''}>${child.name}</option>
              `).join('')}
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">
            <input type="checkbox" id="task-validation" ${task?.validation_required !== false ? 'checked' : ''}> 
            Validation parentale requise
          </label>
        </div>
      </form>
    `;
  }

  submitTaskForm(taskId = null) {
    const form = this.shadowRoot.getElementById('task-form');
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const formData = {
      name: this.shadowRoot.getElementById('task-name').value,
      description: this.shadowRoot.getElementById('task-description').value,
      category: this.shadowRoot.getElementById('task-category').value,
      frequency: this.shadowRoot.getElementById('task-frequency').value,
      points: parseInt(this.shadowRoot.getElementById('task-points').value) || 10,
      assigned_child_id: this.shadowRoot.getElementById('task-assigned').value || null,
      validation_required: this.shadowRoot.getElementById('task-validation').checked
    };

    if (taskId) {
      // Appel service de mise à jour
      this._hass.callService('kids_tasks', 'update_task', {
        task_id: taskId,
        ...formData
      });
    } else {
      // Appel service de création
      this._hass.callService('kids_tasks', 'add_task', formData);
    }

    this.hideModal();
  }

  showRewardForm(rewardId = null) {
    const reward = rewardId ? this.getRewardById(rewardId) : null;
    const isEdit = !!reward;
    
    const modal = this.createModal(
      isEdit ? 'Modifier une récompense' : 'Ajouter une récompense',
      this.getRewardFormHTML(reward),
      () => this.submitRewardForm(rewardId)
    );
    
    this.showModal(modal);
  }

  getRewardFormHTML(reward = null) {
    const categories = [
      { value: 'screen_time', label: '📱 Temps d\'écran' },
      { value: 'outing', label: '🚗 Sortie' },
      { value: 'privilege', label: '👑 Privilège' },
      { value: 'toy', label: '🧸 Jouet' },
      { value: 'treat', label: '🍭 Friandise' },
      { value: 'fun', label: '🎉 Amusement' },
      { value: 'other', label: '📦 Autre' }
    ];

    return `
      <form id="reward-form">
        <div class="form-group">
          <label class="form-label">Nom de la récompense *</label>
          <input type="text" id="reward-name" class="form-input" 
                 placeholder="Ex: 30 min d'écran supplémentaire" value="${reward?.name || ''}" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">Description</label>
          <textarea id="reward-description" class="form-textarea" 
                    placeholder="Description de la récompense">${reward?.description || ''}</textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Catégorie</label>
            <select id="reward-category" class="form-select">
              ${categories.map(cat => `
                <option value="${cat.value}" ${reward?.category === cat.value ? 'selected' : ''}>${cat.label}</option>
              `).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Coût en points</label>
            <input type="number" id="reward-cost" class="form-input" 
                   min="1" max="1000" value="${reward?.cost || 50}">
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">
            <input type="checkbox" id="reward-limited" ${reward?.limited_quantity !== null ? 'checked' : ''}> 
            Quantité limitée
          </label>
        </div>
        
        <div class="form-group" id="quantity-group" style="display: ${reward?.limited_quantity !== null ? 'block' : 'none'};">
          <label class="form-label">Quantité disponible</label>
          <input type="number" id="reward-quantity" class="form-input" 
                 min="1" value="${reward?.limited_quantity || 1}">
        </div>
      </form>
    `;
  }

  submitRewardForm(rewardId = null) {
    const form = this.shadowRoot.getElementById('reward-form');
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const isLimited = this.shadowRoot.getElementById('reward-limited').checked;
    const formData = {
      name: this.shadowRoot.getElementById('reward-name').value,
      description: this.shadowRoot.getElementById('reward-description').value,
      category: this.shadowRoot.getElementById('reward-category').value,
      cost: parseInt(this.shadowRoot.getElementById('reward-cost').value) || 50,
    };

    if (isLimited) {
      formData.limited_quantity = parseInt(this.shadowRoot.getElementById('reward-quantity').value) || 1;
    }

    if (rewardId) {
      // Appel service de mise à jour
      this._hass.callService('kids_tasks', 'update_reward', {
        reward_id: rewardId,
        ...formData
      });
    } else {
      // Appel service de création
      this._hass.callService('kids_tasks', 'add_reward', formData);
    }

    this.hideModal();
  }

  createModal(title, content, onSubmit) {
    return `
      <div class="modal" id="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">${title}</h3>
            <button class="close-btn" onclick="this.hideModal()">&times;</button>
          </div>
          <div class="modal-body">
            ${content}
          </div>
          <div class="modal-footer" style="margin-top: 20px; text-align: right;">
            <button class="btn btn-secondary" onclick="this.hideModal()">Annuler</button>
            <button class="btn btn-primary" id="submit-btn">Enregistrer</button>
          </div>
        </div>
      </div>
    `;
  }

  showModal(modalHTML) {
    // Ajouter la modal au DOM
    const existingModal = this.shadowRoot.getElementById('modal');
    if (existingModal) {
      existingModal.remove();
    }

    this.shadowRoot.innerHTML += modalHTML;

    // Event listeners pour la modal
    const modal = this.shadowRoot.getElementById('modal');
    const closeBtn = modal.querySelector('.close-btn');
    const submitBtn = modal.querySelector('#submit-btn');

    closeBtn.addEventListener('click', () => this.hideModal());
    
    // Fermer en cliquant à l'extérieur
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        this.hideModal();
      }
    });

    // Event listeners spécifiques aux formulaires
    this.attachFormEventListeners();
  }

  hideModal() {
    const modal = this.shadowRoot.getElementById('modal');
    if (modal) {
      modal.remove();
    }
  }

  attachFormEventListeners() {
    // Avatar selection pour le formulaire enfant
    const avatarOptions = this.shadowRoot.querySelectorAll('.avatar-option');
    avatarOptions.forEach(option => {
      option.addEventListener('click', (e) => {
        // Désélectionner tous les avatars
        avatarOptions.forEach(opt => {
          opt.style.border = '2px solid var(--divider-color)';
          opt.classList.remove('selected');
        });
        
        // Sélectionner l'avatar cliqué
        e.target.style.border = '2px solid var(--accent-color)';
        e.target.classList.add('selected');
        
        // Mettre à jour le champ input
        const avatarInput = this.shadowRoot.getElementById('child-avatar');
        if (avatarInput) {
          avatarInput.value = e.target.dataset.avatar;
        }
      });
    });

    // Points automatiques basés sur le niveau (formulaire enfant)
    const pointsInput = this.shadowRoot.getElementById('child-points');
    const levelInput = this.shadowRoot.getElementById('child-level');
    if (pointsInput && levelInput) {
      pointsInput.addEventListener('input', (e) => {
        const points = parseInt(e.target.value) || 0;
        const level = Math.max(1, Math.floor(points / 100) + 1);
        levelInput.value = level;
      });
    }

    // Afficher/masquer la quantité limitée (formulaire récompense)
    const limitedCheckbox = this.shadowRoot.getElementById('reward-limited');
    const quantityGroup = this.shadowRoot.getElementById('quantity-group');
    if (limitedCheckbox && quantityGroup) {
      limitedCheckbox.addEventListener('change', (e) => {
        quantityGroup.style.display = e.target.checked ? 'block' : 'none';
      });
    }

    // Bouton de soumission
    const submitBtn = this.shadowRoot.getElementById('submit-btn');
    if (submitBtn) {
      submitBtn.addEventListener('click', () => {
        // Déterminer quel formulaire soumettre
        if (this.shadowRoot.getElementById('child-form')) {
          const childId = this.shadowRoot.getElementById('child-form').dataset.childId || null;
          this.submitChildForm(childId);
        } else if (this.shadowRoot.getElementById('task-form')) {
          const taskId = this.shadowRoot.getElementById('task-form').dataset.taskId || null;
          this.submitTaskForm(taskId);
        } else if (this.shadowRoot.getElementById('reward-form')) {
          const rewardId = this.shadowRoot.getElementById('reward-form').dataset.rewardId || null;
          this.submitRewardForm(rewardId);
        }
      });
    }
  }

  // Méthodes helper pour récupérer les données par ID
  getChildById(childId) {
    return this.getChildren().find(child => child.id === childId);
  }

  getTaskById(taskId) {
    return this.getTasks().find(task => task.id === taskId);
  }

  getRewardById(rewardId) {
    return this.getRewards().find(reward => reward.id === rewardId);
  }
}

// Appliquer le mixin à la classe principale
Object.assign(KidsTasksManager.prototype, KidsTasksFormMixin.prototype);