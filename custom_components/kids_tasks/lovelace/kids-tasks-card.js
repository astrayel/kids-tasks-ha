const KT_VERSION = '1.1.0';
console.info(
  `%c KIDS-TASKS-CARD %c v${KT_VERSION} `,
  'background:#6b73ff;color:#fff;font-weight:700;padding:2px 4px;border-radius:3px 0 0 3px;',
  'background:#9c27b0;color:#fff;font-weight:400;padding:2px 4px;border-radius:0 3px 3px 0;'
);

const CATEGORY_ICONS = {
  bedroom:  'mdi:bed',
  hygiene:  'mdi:shower',
  kitchen:  'mdi:silverware-fork-knife',
  homework: 'mdi:book-open-variant',
  outdoor:  'mdi:tree',
  music:    'mdi:music',
  other:    'mdi:clipboard-list',
};

const REWARD_ICONS = {
  fun:         'mdi:gamepad-variant',
  screen_time: 'mdi:monitor',
  outing:      'mdi:car',
  privilege:   'mdi:crown',
  toy:         'mdi:toy-brick',
  treat:       'mdi:food-apple',
};

const FREQ_LABELS = {
  daily:        'Quotidien',
  weekly:       'Hebdo',
  monthly:      'Mensuel',
  once:         'Unique',
  Quotidienne:  'Quotidien',
  Hebdomadaire: 'Hebdo',
  Mensuelle:    'Mensuel',
  Unique:       'Unique',
};

const STATUS_KEY = {
  'A faire':                  'todo',
  'En cours':                 'in_progress',
  'Termine':                  'completed',
  'En validation':            'pending_validation',
  'En attente de validation': 'pending_validation',
  'Valide':                   'validated',
  'Echoue':                   'failed',
};

const STATUS_META = {
  todo:               { label: 'A faire',    icon: 'mdi:circle-outline' },
  in_progress:        { label: 'En cours',   icon: 'mdi:play-circle-outline' },
  completed:          { label: 'Termine',    icon: 'mdi:check-circle-outline' },
  pending_validation: { label: 'En attente', icon: 'mdi:clock-outline' },
  validated:          { label: 'Valide',     icon: 'mdi:check-circle' },
  failed:             { label: 'Echoue',     icon: 'mdi:close-circle-outline' },
};

const FIELD_STYLE = [
  'width:100%', 'box-sizing:border-box', 'padding:9px 12px',
  'border:1.5px solid var(--divider-color)', 'border-radius:8px',
  'font-size:14px', 'background:var(--secondary-background-color)',
  'color:var(--primary-text-color)', 'outline:none',
].join(';');
const LABEL_STYLE = 'display:block;margin-bottom:4px;font-size:13px;font-weight:600;';
const ROW_STYLE   = 'margin-bottom:14px;';

const BASE_STYLES = `
  :host {
    display: block;

    --kt-bg:         var(--card-background-color);
    --kt-surface:    var(--secondary-background-color);
    --kt-divider:    var(--divider-color);
    --kt-shadow:     var(--box-shadow, 0 2px 8px rgba(0,0,0,.12));

    --kt-text:       var(--primary-text-color);
    --kt-text-muted: var(--secondary-text-color);
    --kt-font:       var(--paper-font-body1_-_font-family, 'Roboto', sans-serif);

    --kt-success: var(--success-color, #4caf50);
    --kt-warning: var(--warning-color, #ff9800);
    --kt-error:   var(--error-color,   #f44336);
    --kt-info:    var(--info-color,    #2196f3);
    --kt-muted:   var(--disabled-text-color, #9e9e9e);

    --kt-grad-start: var(--primary-color, #6b73ff);
    --kt-grad-end:   var(--accent-color,  #9c27b0);

    --kt-r-card: 16px;
    --kt-r-btn:  8px;
    --kt-r-pill: 20px;
    --kt-r-chip: 12px;
  }

  [data-status="todo"]               { --s-color: var(--kt-muted);   --s-bg: rgba(158,158,158,.12); }
  [data-status="in_progress"]        { --s-color: var(--kt-info);    --s-bg: rgba(33,150,243,.12);  }
  [data-status="completed"]          { --s-color: var(--kt-success); --s-bg: rgba(76,175,80,.12);   }
  [data-status="pending_validation"] { --s-color: var(--kt-warning); --s-bg: rgba(255,152,0,.12);   }
  [data-status="validated"]          { --s-color: var(--kt-success); --s-bg: rgba(76,175,80,.12);   }
  [data-status="failed"]             { --s-color: var(--kt-error);   --s-bg: rgba(244,67,54,.12);   }

  .status-dot  { background: var(--s-color, var(--kt-muted)); }
  .status-icon { color:      var(--s-color, var(--kt-muted)); }
  .task-chip   {
    border-color: var(--s-color, var(--kt-muted));
    background:   var(--s-bg,    rgba(158,158,158,.12));
  }

  .kt-card {
    background:    var(--kt-bg);
    border-radius: var(--kt-r-card);
    overflow:      hidden;
    box-shadow:    var(--kt-shadow);
    font-family:   var(--kt-font);
    color:         var(--kt-text);
  }

  .kt-header {
    padding:         14px 16px 12px;
    display:         flex;
    align-items:     center;
    justify-content: space-between;
    font-weight:     600;
    font-size:       15px;
  }

  .kt-badge {
    background:    var(--primary-color);
    color:         var(--text-primary-color, #fff);
    border-radius: var(--kt-r-pill);
    padding:       2px 9px;
    font-size:     12px;
    font-weight:   700;
    min-width:     22px;
    text-align:    center;
    line-height:   1.5;
  }

  .kt-divider { height: 1px; background: var(--kt-divider); margin: 0; }

  .kt-btn {
    border:        none;
    border-radius: var(--kt-r-btn);
    padding:       6px 14px;
    font-size:     13px;
    font-weight:   600;
    cursor:        pointer;
    transition:    opacity .15s, transform .1s;
    white-space:   nowrap;
  }
  .kt-btn:active  { opacity: .75; transform: scale(.97); }
  .kt-btn:disabled { cursor: default; opacity: .7; }
  .kt-btn.sm      { padding: 4px 10px; font-size: 12px; }

  .kt-btn-validate  { background: var(--kt-success); color: #fff; }
  .kt-btn-reject    { background: var(--kt-error);   color: #fff; }
  .kt-btn-claim     { background: var(--primary-color); color: var(--text-primary-color, #fff); }
  .kt-btn-secondary {
    background:  transparent;
    border:      1.5px solid var(--primary-color);
    color:       var(--primary-color);
    padding:     4px 12px;
  }
  .kt-btn-disabled { background: var(--kt-muted); color: #fff; cursor: default; }
  .kt-btn-add      { background: var(--primary-color); color: var(--text-primary-color, #fff); }

  .kt-chip {
    display:       inline-flex;
    align-items:   center;
    gap:           4px;
    background:    var(--kt-surface);
    border-radius: var(--kt-r-pill);
    padding:       4px 11px;
    font-size:     12px;
    font-weight:   500;
    cursor:        pointer;
    border:        1.5px solid transparent;
    transition:    border-color .15s, color .15s;
    user-select:   none;
  }
  .kt-chip.active { border-color: var(--primary-color); color: var(--primary-color); }

  .kt-empty {
    padding:         24px;
    text-align:      center;
    color:           var(--kt-text-muted);
    font-size:       14px;
    display:         flex;
    align-items:     center;
    justify-content: center;
    gap:             6px;
  }

  ha-icon {
    display:         inline-flex;
    align-items:     center;
    justify-content: center;
    vertical-align:  middle;
  }
`;

function callService(hass, domain, service, data) {
  hass.callService(domain, service, data);
}

function scheduleRender(card) {
  if (card._renderTimer) return;
  card._renderTimer = setTimeout(() => {
    card._renderTimer = null;
    card._render();
  }, 16);
}

function showModal(content, title) {
  document.querySelector('[data-kt-modal]')?.remove();

  const overlay = document.createElement('div');
  overlay.setAttribute('data-kt-modal', '');
  Object.assign(overlay.style, {
    position:       'fixed',
    inset:          '0',
    zIndex:         '9999',
    background:     'rgba(0,0,0,.45)',
    display:        'flex',
    alignItems:     'center',
    justifyContent: 'center',
    padding:        '16px',
  });

  const box = document.createElement('div');
  Object.assign(box.style, {
    background:   'var(--card-background-color, #fff)',
    borderRadius: '16px',
    padding:      '24px',
    maxWidth:     '480px',
    width:        '100%',
    maxHeight:    '85vh',
    overflowY:    'auto',
    boxShadow:    '0 8px 32px rgba(0,0,0,.2)',
    fontFamily:   'var(--paper-font-body1_-_font-family, sans-serif)',
    color:        'var(--primary-text-color)',
  });

  if (title) {
    const h = document.createElement('h3');
    Object.assign(h.style, { margin: '0 0 20px', fontSize: '18px', fontWeight: '700' });
    h.textContent = title;
    box.appendChild(h);
  }

  const inner = document.createElement('div');
  inner.innerHTML = content;
  box.appendChild(inner);

  overlay.appendChild(box);
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
  document.body.appendChild(overlay);
  return overlay;
}

function confirmModal(message, onConfirm) {
  const content = `
    <p style="margin:0 0 20px;font-size:14px;">${message}</p>
    <div style="display:flex;gap:10px;justify-content:flex-end;">
      <button id="kt-no" style="padding:8px 18px;border-radius:8px;border:1.5px solid var(--divider-color);background:var(--secondary-background-color);color:var(--primary-text-color);font-size:14px;cursor:pointer;">Annuler</button>
      <button id="kt-yes" style="padding:8px 18px;border-radius:8px;border:none;background:var(--error-color,#f44336);color:#fff;font-size:14px;font-weight:600;cursor:pointer;">Supprimer</button>
    </div>`;
  const dlg = showModal(content, 'Confirmation');
  dlg.querySelector('#kt-no')?.addEventListener('click', () => dlg.remove());
  dlg.querySelector('#kt-yes')?.addEventListener('click', () => { dlg.remove(); onConfirm(); });
}

function xpForLevel(level) { return level * 100; }

function xpProgress(points, level) {
  const base   = xpForLevel(level - 1);
  const target = xpForLevel(level);
  if (target === base) return 100;
  return Math.min(100, Math.round(((points - base) / (target - base)) * 100));
}

function pointsToNextLevel(points, level) {
  return Math.max(0, xpForLevel(level) - points);
}

function toStatusKey(displayStatus) {
  if (STATUS_KEY[displayStatus]) return STATUS_KEY[displayStatus];
  if (Object.values(STATUS_KEY).includes(displayStatus)) return displayStatus;
  return 'todo';
}

function avatarHtml(avatar, avatarType, size = 40) {
  if ((avatarType === 'url' || avatarType === 'inline') && avatar) {
    return `<img src="${avatar}" style="width:${size}px;height:${size}px;border-radius:50%;object-fit:cover;" alt="">`;
  }
  if (avatarType === 'emoji' && avatar) {
    return `<span style="font-size:${Math.round(size * 0.6)}px;line-height:${size}px;">${avatar}</span>`;
  }
  return `<ha-icon icon="mdi:account-circle" style="--mdc-icon-size:${size}px;color:rgba(255,255,255,.8);"></ha-icon>`;
}

function categoryIconHtml(category, size = '20px') {
  const icon = CATEGORY_ICONS[(category || '').toLowerCase()] || 'mdi:clipboard-list';
  return `<ha-icon icon="${icon}" style="--mdc-icon-size:${size};"></ha-icon>`;
}

function rewardIconHtml(r, size = '28px') {
  const icon = r.icon && r.icon.startsWith('mdi:')
    ? r.icon
    : (REWARD_ICONS[(r.category || '').toLowerCase()] || 'mdi:gift');
  return `<ha-icon icon="${icon}" style="--mdc-icon-size:${size};"></ha-icon>`;
}

function childOptsHtml(hass) {
  const s = hass.states['sensor.kidtasks_all_children_list'];
  return (s?.attributes?.children || [])
    .map(c => `<option value="${c.id}">${c.name}</option>`)
    .join('');
}

function taskCategoryOptsHtml(selected = '') {
  return [
    ['bedroom', 'Chambre'], ['hygiene', 'Hygiene'], ['kitchen', 'Cuisine'],
    ['homework', 'Devoirs'], ['outdoor', 'Exterieur'], ['music', 'Musique'], ['other', 'Autre'],
  ].map(([v, l]) => `<option value="${v}"${v === selected ? ' selected' : ''}>${l}</option>`).join('');
}

function taskFreqOptsHtml(selected = '') {
  return [
    ['daily', 'Quotidienne'], ['weekly', 'Hebdomadaire'], ['monthly', 'Mensuelle'], ['once', 'Unique'],
  ].map(([v, l]) => `<option value="${v}"${v === selected ? ' selected' : ''}>${l}</option>`).join('');
}

function rewardCategoryOptsHtml(selected = '') {
  return [
    ['fun', 'Fun'], ['screen_time', 'Ecran'], ['outing', 'Sortie'],
    ['privilege', 'Privilege'], ['toy', 'Jouet'], ['treat', 'Friandise'],
  ].map(([v, l]) => `<option value="${v}"${v === selected ? ' selected' : ''}>${l}</option>`).join('');
}

function freqRawFromDisplay(display) {
  const map = { 'Quotidienne': 'daily', 'Hebdomadaire': 'weekly', 'Mensuelle': 'monthly', 'Unique': 'once' };
  return map[display] || display || 'daily';
}

function catRawFromDisplay(display) {
  return (display || 'other').toLowerCase();
}

// ═══════════════════════════════════════════════════════════════════════════════
// Card 1 — KidsTasksChildSummaryCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksChildSummaryCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._renderTimer = null;
  }

  setConfig(config) {
    if (!config.entity) throw new Error("kids-tasks-child-summary-card: 'entity' required (points sensor)");
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    scheduleRender(this);
  }

  getCardSize() { return 3; }

  disconnectedCallback() {
    if (this._renderTimer) clearTimeout(this._renderTimer);
  }

  _tasks(childId) {
    const all = this._hass.states['sensor.kidtasks_all_tasks_list'];
    if (!all) return [];
    return (all.attributes.tasks || []).filter(t =>
      Array.isArray(t.assigned_child_ids) && t.assigned_child_ids.includes(childId)
    );
  }

  _pendingCount(childId) {
    const pv = this._hass.states['sensor.kidtasks_pending_validations'];
    if (!pv) return 0;
    return (pv.attributes.pending_tasks || []).filter(t =>
      Array.isArray(t.child_ids) && t.child_ids.includes(childId)
    ).length;
  }

  _openEditChildDialog(childId, attrs) {
    const gradStart = attrs.card_gradient_start || '#6b73ff';
    const gradEnd   = attrs.card_gradient_end   || '#9c27b0';
    const content = `
      <div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Nom</label>
          <input id="kt-name" type="text" value="${attrs.name || ''}" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Avatar (emoji ou URL)</label>
          <input id="kt-avatar" type="text" value="${attrs.avatar || ''}" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Couleur debut du gradient</label>
          <input id="kt-grad-start" type="color" value="${gradStart}" style="width:60px;height:36px;border:none;border-radius:8px;cursor:pointer;background:none;">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Couleur fin du gradient</label>
          <input id="kt-grad-end" type="color" value="${gradEnd}" style="width:60px;height:36px;border:none;border-radius:8px;cursor:pointer;background:none;">
        </div>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px;">
          <button id="kt-cancel" style="padding:8px 18px;border-radius:8px;border:1.5px solid var(--divider-color);background:var(--secondary-background-color);color:var(--primary-text-color);font-size:14px;cursor:pointer;">Annuler</button>
          <button id="kt-save" style="padding:8px 18px;border-radius:8px;border:none;background:var(--primary-color);color:var(--text-primary-color,#fff);font-size:14px;font-weight:600;cursor:pointer;">Sauvegarder</button>
        </div>
      </div>`;

    const dlg = showModal(content, 'Modifier l\'enfant');
    dlg.querySelector('#kt-cancel')?.addEventListener('click', () => dlg.remove());
    dlg.querySelector('#kt-save')?.addEventListener('click', () => {
      const name = dlg.querySelector('#kt-name')?.value?.trim();
      if (!name) { dlg.querySelector('#kt-name')?.focus(); return; }
      callService(this._hass, 'kids_tasks', 'update_child', {
        child_id:             childId,
        name,
        avatar:               dlg.querySelector('#kt-avatar')?.value?.trim() || '',
        card_gradient_start:  dlg.querySelector('#kt-grad-start')?.value || '#6b73ff',
        card_gradient_end:    dlg.querySelector('#kt-grad-end')?.value   || '#9c27b0',
      });
      dlg.remove();
    });
  }

  _render() {
    const state = this._hass.states[this._config.entity];
    if (!state) {
      this.shadowRoot.innerHTML = `
        <style>${BASE_STYLES}</style>
        <div class="kt-card">
          <div class="kt-empty">Entite introuvable : ${this._config.entity}</div>
        </div>`;
      return;
    }

    const a          = state.attributes;
    const childId    = a.child_id    || '';
    const childName  = a.name        || 'Enfant';
    const points     = parseInt(state.state) || 0;
    const level      = a.level       || 1;
    const coins      = a.coins       || 0;
    const avatar     = a.avatar      || '';
    const avatarType = a.avatar_type  || 'emoji';
    const gradStart  = a.card_gradient_start || 'var(--kt-grad-start)';
    const gradEnd    = a.card_gradient_end   || 'var(--kt-grad-end)';
    const pct        = xpProgress(points, level);
    const toNext     = pointsToNextLevel(points, level);
    const tasks      = this._tasks(childId);
    const pending    = this._pendingCount(childId);

    const chips = tasks.slice(0, 5).map(t => {
      const sk   = toStatusKey(t.status);
      const meta = STATUS_META[sk] || STATUS_META.todo;
      return `
        <span class="task-chip" data-status="${sk}">
          ${categoryIconHtml(t.category, '13px')}
          <ha-icon icon="${meta.icon}" style="--mdc-icon-size:12px;" class="status-icon" data-status="${sk}"></ha-icon>
          <span style="max-width:72px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${t.name}</span>
        </span>`;
    }).join('');

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}

        .child-header {
          background:  linear-gradient(135deg, ${gradStart}, ${gradEnd});
          padding:     14px 16px;
          display:     flex;
          align-items: center;
          gap:         12px;
          color:       #fff;
        }
        .avatar-ring {
          width:           52px;
          height:          52px;
          border-radius:   50%;
          background:      rgba(255,255,255,.22);
          display:         flex;
          align-items:     center;
          justify-content: center;
          flex-shrink:     0;
          overflow:        hidden;
        }
        .child-info  { flex: 1; min-width: 0; }
        .child-name  {
          font-size:     17px;
          font-weight:   700;
          white-space:   nowrap;
          overflow:      hidden;
          text-overflow: ellipsis;
        }
        .child-coins {
          font-size:   12px;
          opacity:     .85;
          margin-top:  2px;
          display:     flex;
          align-items: center;
          gap:         4px;
        }
        .level-badge {
          background:    rgba(255,255,255,.22);
          border-radius: var(--kt-r-pill);
          padding:       4px 11px;
          font-size:     12px;
          font-weight:   700;
          white-space:   nowrap;
          display:       flex;
          align-items:   center;
          gap:           4px;
          flex-shrink:   0;
        }

        .kt-body  { padding: 12px 16px; }

        .xp-row   { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
        .xp-bg    { flex: 1; height: 8px; border-radius: 4px; background: var(--kt-surface); overflow: hidden; }
        .xp-fill  {
          height:        100%;
          border-radius: 4px;
          background:    linear-gradient(90deg, ${gradStart}, ${gradEnd});
          transition:    width .4s;
        }
        .xp-label { font-size: 11px; color: var(--kt-text-muted); white-space: nowrap; }

        .chips     { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
        .task-chip {
          display:       inline-flex;
          align-items:   center;
          gap:           4px;
          border:        1.5px solid;
          border-radius: var(--kt-r-pill);
          padding:       3px 8px;
          font-size:     11px;
        }

        .actions  {
          display:         flex;
          gap:             8px;
          justify-content: flex-end;
          align-items:     center;
        }
        .all-done {
          font-size:   12px;
          color:       var(--kt-text-muted);
          display:     flex;
          align-items: center;
          gap:         4px;
        }
      </style>

      <div class="kt-card">
        <div class="child-header">
          <div class="avatar-ring">${avatarHtml(avatar, avatarType, 40)}</div>
          <div class="child-info">
            <div class="child-name">${childName}</div>
            <div class="child-coins">
              <ha-icon icon="mdi:cash" style="--mdc-icon-size:14px;"></ha-icon>
              ${coins} pieces
            </div>
          </div>
          <div class="level-badge">
            <ha-icon icon="mdi:star" style="--mdc-icon-size:14px;"></ha-icon>
            Niv. ${level}
          </div>
        </div>

        <div class="kt-body">
          <div class="xp-row">
            <div class="xp-bg"><div class="xp-fill" style="width:${pct}%"></div></div>
            <div class="xp-label">${points} pts &middot; encore ${toNext} avant niv. ${level + 1}</div>
          </div>

          ${tasks.length > 0
            ? `<div class="chips">${chips}</div>`
            : `<div style="font-size:12px;color:var(--kt-text-muted);margin-bottom:10px;">Aucune tache assignee</div>`
          }

          <div class="actions">
            ${pending > 0
              ? `<button class="kt-btn kt-btn-validate sm" id="val-btn">
                   <ha-icon icon="mdi:clock-check-outline" style="--mdc-icon-size:14px;"></ha-icon>
                   ${pending} a valider
                 </button>`
              : `<span class="all-done">
                   <ha-icon icon="mdi:check-circle-outline" style="--mdc-icon-size:15px;color:var(--kt-success);"></ha-icon>
                   Tout est valide
                 </span>`
            }
            <button class="kt-btn kt-btn-secondary sm" id="edit-child-btn">Modifier</button>
            <button class="kt-btn kt-btn-secondary sm" id="detail-btn">Details</button>
          </div>
        </div>
      </div>`;

    this.shadowRoot.getElementById('val-btn')?.addEventListener('click', () => {
      const pv = this._hass.states['sensor.kidtasks_pending_validations'];
      (pv?.attributes.pending_tasks || [])
        .filter(t => Array.isArray(t.child_ids) && t.child_ids.includes(childId))
        .forEach(t => callService(this._hass, 'kids_tasks', 'validate_task', { task_id: t.task_id }));
    });

    this.shadowRoot.getElementById('edit-child-btn')?.addEventListener('click', () => this._openEditChildDialog(childId, a));

    this.shadowRoot.getElementById('detail-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('hass-more-info', {
        detail:   { entityId: this._config.entity },
        bubbles:  true,
        composed: true,
      }));
    });
  }
}

customElements.define('kids-tasks-child-summary-card', KidsTasksChildSummaryCard);

// ═══════════════════════════════════════════════════════════════════════════════
// Card 2 — KidsTasksValidationCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksValidationCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._renderTimer = null;
  }

  setConfig(config) {
    this._config = { entity: 'sensor.kidtasks_pending_validations', ...config };
  }

  set hass(hass) {
    this._hass = hass;
    scheduleRender(this);
  }

  getCardSize() { return 3; }

  disconnectedCallback() {
    if (this._renderTimer) clearTimeout(this._renderTimer);
  }

  _render() {
    const state   = this._hass.states[this._config.entity];
    const pending = state?.attributes?.pending_tasks || [];

    const rows = pending.map((t, i) => `
      <div class="task-row">
        <div class="task-info">
          <span class="cat-icon">${categoryIconHtml(t.category, '22px')}</span>
          <div class="task-details">
            <div class="task-name">${t.name}</div>
            <div class="task-child">${t.child} &middot; ${t.points} pts</div>
          </div>
        </div>
        <div class="task-actions">
          <button class="kt-btn kt-btn-validate sm" data-id="${t.task_id}" data-action="validate">Valider</button>
          <button class="kt-btn kt-btn-reject sm"   data-id="${t.task_id}" data-action="reject">Rejeter</button>
        </div>
      </div>
      ${i < pending.length - 1 ? '<div class="kt-divider"></div>' : ''}
    `).join('');

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}
        .task-row {
          display:         flex;
          align-items:     center;
          justify-content: space-between;
          padding:         12px 16px;
          gap:             10px;
        }
        .task-info    { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
        .cat-icon     { display: flex; align-items: center; flex-shrink: 0; }
        .task-details { min-width: 0; }
        .task-name    {
          font-size:     14px;
          font-weight:   600;
          white-space:   nowrap;
          overflow:      hidden;
          text-overflow: ellipsis;
        }
        .task-child   { font-size: 12px; color: var(--kt-text-muted); margin-top: 2px; }
        .task-actions { display: flex; gap: 6px; flex-shrink: 0; }
      </style>

      <div class="kt-card">
        <div class="kt-header">
          A valider
          ${pending.length > 0 ? `<span class="kt-badge">${pending.length}</span>` : ''}
        </div>
        <div class="kt-divider"></div>
        ${pending.length === 0
          ? `<div class="kt-empty">
               <ha-icon icon="mdi:check-circle-outline" style="--mdc-icon-size:20px;color:var(--kt-success);"></ha-icon>
               Tout est valide
             </div>`
          : rows
        }
      </div>`;

    this.shadowRoot.querySelectorAll('button[data-id]').forEach(btn => {
      btn.addEventListener('click', () => {
        const svc = btn.dataset.action === 'validate' ? 'validate_task' : 'reject_task';
        callService(this._hass, 'kids_tasks', svc, { task_id: btn.dataset.id });
      });
    });
  }
}

customElements.define('kids-tasks-validation-card', KidsTasksValidationCard);

// ═══════════════════════════════════════════════════════════════════════════════
// Card 3 — KidsTasksTaskListCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksTaskListCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._filter = 'all';
    this._renderTimer = null;
  }

  setConfig(config) {
    this._config = { entity: 'sensor.kidtasks_all_tasks_list', ...config };
  }

  set hass(hass) {
    this._hass = hass;
    scheduleRender(this);
  }

  getCardSize() { return 4; }

  disconnectedCallback() {
    if (this._renderTimer) clearTimeout(this._renderTimer);
  }

  _filteredTasks(tasks) {
    switch (this._filter) {
      case 'daily':
        return tasks.filter(t => ['Quotidienne', 'daily'].includes(t.frequency));
      case 'weekly':
        return tasks.filter(t => ['Hebdomadaire', 'weekly'].includes(t.frequency));
      case 'pending':
        return tasks.filter(t => ['En validation', 'pending_validation'].includes(t.status));
      case 'done':
        return tasks.filter(t =>
          ['Valide', 'Termine', 'validated', 'completed'].includes(t.status)
        );
      default:
        return tasks;
    }
  }

  _openAddDialog() {
    const childOpts = childOptsHtml(this._hass);

    const content = `
      <div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Nom</label>
          <input id="kt-name" type="text" placeholder="Nom de la tache" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Categorie</label>
          <select id="kt-cat" style="${FIELD_STYLE}">${taskCategoryOptsHtml()}</select>
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Points</label>
          <input id="kt-pts" type="number" value="10" min="1" max="999" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Frequence</label>
          <select id="kt-freq" style="${FIELD_STYLE}">${taskFreqOptsHtml()}</select>
        </div>
        ${childOpts ? `
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Assigner a (optionnel)</label>
          <select id="kt-child" style="${FIELD_STYLE}">
            <option value="">— Non assigne —</option>
            ${childOpts}
          </select>
        </div>` : ''}
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px;">
          <button id="kt-cancel" style="padding:8px 18px;border-radius:8px;border:1.5px solid var(--divider-color);background:var(--secondary-background-color);color:var(--primary-text-color);font-size:14px;cursor:pointer;">Annuler</button>
          <button id="kt-save" style="padding:8px 18px;border-radius:8px;border:none;background:var(--primary-color);color:var(--text-primary-color,#fff);font-size:14px;font-weight:600;cursor:pointer;">Ajouter</button>
        </div>
      </div>`;

    const dlg = showModal(content, 'Nouvelle tache');

    dlg.querySelector('#kt-cancel')?.addEventListener('click', () => dlg.remove());

    dlg.querySelector('#kt-save')?.addEventListener('click', () => {
      const name = dlg.querySelector('#kt-name')?.value?.trim();
      if (!name) { dlg.querySelector('#kt-name')?.focus(); return; }

      const data = {
        name,
        category:  dlg.querySelector('#kt-cat')?.value  || 'other',
        points:    parseInt(dlg.querySelector('#kt-pts')?.value || '10', 10),
        frequency: dlg.querySelector('#kt-freq')?.value || 'daily',
      };
      const childId = dlg.querySelector('#kt-child')?.value;
      if (childId) data.assigned_child_ids = [childId];

      callService(this._hass, 'kids_tasks', 'add_task', data);
      dlg.remove();
    });
  }

  _openEditTaskDialog(task) {
    const catRaw  = catRawFromDisplay(task.category);
    const freqRaw = freqRawFromDisplay(task.frequency);
    const firstChild = Array.isArray(task.assigned_child_ids) ? task.assigned_child_ids[0] || '' : '';
    const childOpts = childOptsHtml(this._hass);

    const childSelectHtml = childOpts ? `
      <div style="${ROW_STYLE}">
        <label style="${LABEL_STYLE}">Assigner a (optionnel)</label>
        <select id="kt-child" style="${FIELD_STYLE}">
          <option value="">— Non assigne —</option>
          ${(this._hass.states['sensor.kidtasks_all_children_list']?.attributes?.children || [])
            .map(c => `<option value="${c.id}"${c.id === firstChild ? ' selected' : ''}>${c.name}</option>`)
            .join('')}
        </select>
      </div>` : '';

    const content = `
      <div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Nom</label>
          <input id="kt-name" type="text" value="${task.name || ''}" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Categorie</label>
          <select id="kt-cat" style="${FIELD_STYLE}">${taskCategoryOptsHtml(catRaw)}</select>
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Points</label>
          <input id="kt-pts" type="number" value="${task.points || 10}" min="1" max="999" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Frequence</label>
          <select id="kt-freq" style="${FIELD_STYLE}">${taskFreqOptsHtml(freqRaw)}</select>
        </div>
        ${childSelectHtml}
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px;">
          <button id="kt-cancel" style="padding:8px 18px;border-radius:8px;border:1.5px solid var(--divider-color);background:var(--secondary-background-color);color:var(--primary-text-color);font-size:14px;cursor:pointer;">Annuler</button>
          <button id="kt-save" style="padding:8px 18px;border-radius:8px;border:none;background:var(--primary-color);color:var(--text-primary-color,#fff);font-size:14px;font-weight:600;cursor:pointer;">Sauvegarder</button>
        </div>
      </div>`;

    const dlg = showModal(content, 'Modifier la tache');

    dlg.querySelector('#kt-cancel')?.addEventListener('click', () => dlg.remove());

    dlg.querySelector('#kt-save')?.addEventListener('click', () => {
      const name = dlg.querySelector('#kt-name')?.value?.trim();
      if (!name) { dlg.querySelector('#kt-name')?.focus(); return; }

      const data = {
        task_id:   task.task_id,
        name,
        category:  dlg.querySelector('#kt-cat')?.value  || 'other',
        points:    parseInt(dlg.querySelector('#kt-pts')?.value || '10', 10),
        frequency: dlg.querySelector('#kt-freq')?.value || 'daily',
      };
      const childId = dlg.querySelector('#kt-child')?.value;
      data.assigned_child_ids = childId ? [childId] : [];

      callService(this._hass, 'kids_tasks', 'update_task', data);
      dlg.remove();
    });
  }

  _openDeleteTaskConfirm(task) {
    confirmModal('Supprimer la tache "' + task.name + '" ?', () =>
      callService(this._hass, 'kids_tasks', 'remove_task', { task_id: task.task_id })
    );
  }

  _render() {
    const state    = this._hass.states[this._config.entity];
    const allTasks = state?.attributes?.tasks || [];
    const tasks    = this._filteredTasks(allTasks);

    const filters = [
      { key: 'all',     label: 'Tous' },
      { key: 'daily',   label: 'Quotidien' },
      { key: 'weekly',  label: 'Hebdo' },
      { key: 'pending', label: 'En attente' },
      { key: 'done',    label: 'Faits' },
    ];

    const filterChips = filters.map(f =>
      `<span class="kt-chip ${this._filter === f.key ? 'active' : ''}" data-filter="${f.key}">${f.label}</span>`
    ).join('');

    const taskRows = tasks.map((t, i) => {
      const sk        = toStatusKey(t.status);
      const isPending = sk === 'pending_validation';
      return `
        <div class="task-row">
          <span class="status-dot" data-status="${sk}"></span>
          <span class="cat-icon">${categoryIconHtml(t.category, '18px')}</span>
          <div class="task-details">
            <div class="task-name">${t.name}</div>
            <div class="task-meta">
              ${t.assigned_child ? `${t.assigned_child} &middot; ` : ''}${FREQ_LABELS[t.frequency] || t.frequency || ''}
            </div>
          </div>
          <div class="task-right">
            <span class="pts-badge">${t.points} pts</span>
            ${isPending ? `
              <button class="kt-btn kt-btn-validate sm" data-id="${t.task_id}" data-action="validate" title="Valider">
                <ha-icon icon="mdi:check" style="--mdc-icon-size:14px;"></ha-icon>
              </button>
              <button class="kt-btn kt-btn-reject sm" data-id="${t.task_id}" data-action="reject" title="Rejeter">
                <ha-icon icon="mdi:close" style="--mdc-icon-size:14px;"></ha-icon>
              </button>
            ` : ''}
            <button class="kt-btn sm icon-btn" data-id="${t.task_id}" data-action="edit-task" title="Modifier">
              <ha-icon icon="mdi:pencil" style="--mdc-icon-size:14px;"></ha-icon>
            </button>
            <button class="kt-btn sm icon-btn" data-id="${t.task_id}" data-action="delete-task" title="Supprimer">
              <ha-icon icon="mdi:trash-can-outline" style="--mdc-icon-size:14px;"></ha-icon>
            </button>
          </div>
        </div>
        ${i < tasks.length - 1 ? '<div class="kt-divider"></div>' : ''}
      `;
    }).join('');

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}
        .filter-row  { display: flex; gap: 6px; flex-wrap: wrap; padding: 10px 16px; }
        .task-row    { display: flex; align-items: center; padding: 10px 16px; gap: 10px; }
        .status-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
        .cat-icon    { display: flex; align-items: center; flex-shrink: 0; }
        .task-details { flex: 1; min-width: 0; }
        .task-name   {
          font-size:     13px;
          font-weight:   600;
          white-space:   nowrap;
          overflow:      hidden;
          text-overflow: ellipsis;
        }
        .task-meta   { font-size: 11px; color: var(--kt-text-muted); margin-top: 2px; }
        .task-right  { display: flex; align-items: center; gap: 5px; flex-shrink: 0; }
        .pts-badge   {
          background:    var(--kt-surface);
          border-radius: var(--kt-r-pill);
          padding:       2px 8px;
          font-size:     11px;
          font-weight:   600;
        }
        .header-right { display: flex; align-items: center; gap: 8px; }
        .icon-btn { background: var(--kt-surface); color: var(--kt-text-muted); padding: 4px 6px; }
        .icon-btn:hover { color: var(--primary-color); }
      </style>

      <div class="kt-card">
        <div class="kt-header">
          Taches du jour
          <div class="header-right">
            <span class="kt-badge">${tasks.length}</span>
            <button class="kt-btn kt-btn-add sm" id="add-btn">+ Ajouter</button>
          </div>
        </div>
        <div class="filter-row">${filterChips}</div>
        <div class="kt-divider"></div>
        ${tasks.length === 0
          ? `<div class="kt-empty">Aucune tache dans cette categorie</div>`
          : taskRows
        }
      </div>`;

    this.shadowRoot.getElementById('add-btn')?.addEventListener('click', () => this._openAddDialog());

    this.shadowRoot.querySelectorAll('.kt-chip[data-filter]').forEach(chip => {
      chip.addEventListener('click', () => {
        this._filter = chip.dataset.filter;
        this._render();
      });
    });

    this.shadowRoot.querySelectorAll('button[data-action="validate"], button[data-action="reject"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const svc = btn.dataset.action === 'validate' ? 'validate_task' : 'reject_task';
        callService(this._hass, 'kids_tasks', svc, { task_id: btn.dataset.id });
      });
    });

    this.shadowRoot.querySelectorAll('button[data-action="edit-task"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const task = allTasks.find(t => t.task_id === btn.dataset.id);
        if (task) this._openEditTaskDialog(task);
      });
    });

    this.shadowRoot.querySelectorAll('button[data-action="delete-task"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const task = allTasks.find(t => t.task_id === btn.dataset.id);
        if (task) this._openDeleteTaskConfirm(task);
      });
    });
  }
}

customElements.define('kids-tasks-task-list-card', KidsTasksTaskListCard);

// ═══════════════════════════════════════════════════════════════════════════════
// Card 4 — KidsTasksRewardCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksRewardCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._filter = 'all';
    this._renderTimer = null;
  }

  setConfig(config) {
    this._config = { entity: 'sensor.kidtasks_all_rewards_list', ...config };
  }

  set hass(hass) {
    this._hass = hass;
    scheduleRender(this);
  }

  getCardSize() { return 4; }

  disconnectedCallback() {
    if (this._renderTimer) clearTimeout(this._renderTimer);
  }

  _childInfo() {
    if (!this._config.child_entity) return null;
    const s = this._hass.states[this._config.child_entity];
    if (!s) return null;
    return {
      name:     s.attributes.name,
      points:   parseInt(s.state),
      child_id: s.attributes.child_id,
    };
  }

  _openAddRewardDialog() {
    const content = `
      <div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Nom</label>
          <input id="kt-name" type="text" placeholder="Nom de la recompense" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Description (optionnel)</label>
          <input id="kt-desc" type="text" placeholder="Description courte" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Cout (points)</label>
          <input id="kt-cost" type="number" value="50" min="1" max="9999" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Categorie</label>
          <select id="kt-cat" style="${FIELD_STYLE}">${rewardCategoryOptsHtml()}</select>
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Icone (ex: mdi:gift)</label>
          <input id="kt-icon" type="text" placeholder="mdi:gift" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Quantite limitee (optionnel)</label>
          <input id="kt-qty" type="number" placeholder="Laisser vide si illimite" min="1" style="${FIELD_STYLE}">
        </div>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px;">
          <button id="kt-cancel" style="padding:8px 18px;border-radius:8px;border:1.5px solid var(--divider-color);background:var(--secondary-background-color);color:var(--primary-text-color);font-size:14px;cursor:pointer;">Annuler</button>
          <button id="kt-save" style="padding:8px 18px;border-radius:8px;border:none;background:var(--primary-color);color:var(--text-primary-color,#fff);font-size:14px;font-weight:600;cursor:pointer;">Ajouter</button>
        </div>
      </div>`;

    const dlg = showModal(content, 'Nouvelle recompense');
    dlg.querySelector('#kt-cancel')?.addEventListener('click', () => dlg.remove());
    dlg.querySelector('#kt-save')?.addEventListener('click', () => {
      const name = dlg.querySelector('#kt-name')?.value?.trim();
      if (!name) { dlg.querySelector('#kt-name')?.focus(); return; }
      const data = {
        name,
        cost:     parseInt(dlg.querySelector('#kt-cost')?.value || '50', 10),
        category: dlg.querySelector('#kt-cat')?.value || 'fun',
      };
      const desc = dlg.querySelector('#kt-desc')?.value?.trim();
      if (desc) data.description = desc;
      const icon = dlg.querySelector('#kt-icon')?.value?.trim();
      if (icon) data.icon = icon;
      const qty = dlg.querySelector('#kt-qty')?.value?.trim();
      if (qty) data.limited_quantity = parseInt(qty, 10);
      callService(this._hass, 'kids_tasks', 'add_reward', data);
      dlg.remove();
    });
  }

  _openEditRewardDialog(reward) {
    const qtyVal = reward.limited_quantity != null ? reward.limited_quantity : '';
    const content = `
      <div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Nom</label>
          <input id="kt-name" type="text" value="${reward.name || ''}" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Description (optionnel)</label>
          <input id="kt-desc" type="text" value="${reward.description || ''}" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Cout (points)</label>
          <input id="kt-cost" type="number" value="${reward.cost || 50}" min="1" max="9999" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Categorie</label>
          <select id="kt-cat" style="${FIELD_STYLE}">${rewardCategoryOptsHtml((reward.category || '').toLowerCase())}</select>
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Icone (ex: mdi:gift)</label>
          <input id="kt-icon" type="text" value="${reward.icon || ''}" placeholder="mdi:gift" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Quantite limitee (optionnel)</label>
          <input id="kt-qty" type="number" value="${qtyVal}" placeholder="Laisser vide si illimite" min="1" style="${FIELD_STYLE}">
        </div>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px;">
          <button id="kt-cancel" style="padding:8px 18px;border-radius:8px;border:1.5px solid var(--divider-color);background:var(--secondary-background-color);color:var(--primary-text-color);font-size:14px;cursor:pointer;">Annuler</button>
          <button id="kt-save" style="padding:8px 18px;border-radius:8px;border:none;background:var(--primary-color);color:var(--text-primary-color,#fff);font-size:14px;font-weight:600;cursor:pointer;">Sauvegarder</button>
        </div>
      </div>`;

    const dlg = showModal(content, 'Modifier la recompense');
    dlg.querySelector('#kt-cancel')?.addEventListener('click', () => dlg.remove());
    dlg.querySelector('#kt-save')?.addEventListener('click', () => {
      const name = dlg.querySelector('#kt-name')?.value?.trim();
      if (!name) { dlg.querySelector('#kt-name')?.focus(); return; }
      const data = {
        reward_id: reward.reward_id,
        name,
        cost:      parseInt(dlg.querySelector('#kt-cost')?.value || '50', 10),
        category:  dlg.querySelector('#kt-cat')?.value || 'fun',
      };
      const desc = dlg.querySelector('#kt-desc')?.value?.trim();
      if (desc) data.description = desc;
      const icon = dlg.querySelector('#kt-icon')?.value?.trim();
      if (icon) data.icon = icon;
      const qty = dlg.querySelector('#kt-qty')?.value?.trim();
      data.limited_quantity = qty ? parseInt(qty, 10) : null;
      callService(this._hass, 'kids_tasks', 'update_reward', data);
      dlg.remove();
    });
  }

  _openDeleteRewardConfirm(reward) {
    confirmModal('Supprimer la recompense "' + reward.name + '" ?', () =>
      callService(this._hass, 'kids_tasks', 'remove_reward', { reward_id: reward.reward_id })
    );
  }

  _render() {
    const state      = this._hass.states[this._config.entity];
    const isAdmin    = !this._config.child_entity;
    const allRewards = isAdmin
      ? (state?.attributes?.rewards || [])
      : (state?.attributes?.rewards || []).filter(r => r.active && r.is_available);
    const child      = this._childInfo();
    const childPts   = child?.points ?? null;

    const displayRewards = isAdmin
      ? allRewards
      : allRewards;

    const categories = ['all', ...new Set(
      displayRewards.map(r => (r.category || '').toLowerCase()).filter(Boolean)
    )];

    const filtered = this._filter === 'all'
      ? displayRewards
      : displayRewards.filter(r => (r.category || '').toLowerCase() === this._filter);

    const catChips = categories.map(c => {
      const icon  = c === 'all' ? 'mdi:gift' : (REWARD_ICONS[c] || 'mdi:gift');
      const label = c === 'all' ? 'Tous' : c.replace(/_/g, ' ');
      return `
        <span class="kt-chip ${this._filter === c ? 'active' : ''}" data-cat="${c}">
          <ha-icon icon="${icon}" style="--mdc-icon-size:14px;"></ha-icon>
          ${label}
        </span>`;
    }).join('');

    const tiles = filtered.map(r => {
      const canAfford = childPts !== null ? childPts >= r.cost : null;
      const disabled  = !child || !canAfford;
      const btnClass  = disabled ? 'kt-btn kt-btn-disabled' : 'kt-btn kt-btn-claim';
      const btnLabel  = !child ? 'Vue admin' : canAfford ? 'Echanger' : 'Pas assez';
      const qty       = r.limited_quantity
        ? `<div class="reward-qty">${r.remaining_quantity} restant(s)</div>` : '';

      return `
        <div class="reward-tile">
          ${isAdmin ? `
            <div class="tile-actions">
              <button class="icon-btn" data-id="${r.reward_id}" data-action="edit-reward" title="Modifier">
                <ha-icon icon="mdi:pencil" style="--mdc-icon-size:13px;"></ha-icon>
              </button>
              <button class="icon-btn" data-id="${r.reward_id}" data-action="delete-reward" title="Supprimer">
                <ha-icon icon="mdi:trash-can-outline" style="--mdc-icon-size:13px;"></ha-icon>
              </button>
            </div>` : ''}
          <div class="reward-icon">${rewardIconHtml(r, '30px')}</div>
          <div class="reward-name">${r.name}</div>
          ${r.description ? `<div class="reward-desc">${r.description}</div>` : ''}
          <div class="reward-cost">
            <ha-icon icon="mdi:cash" style="--mdc-icon-size:13px;"></ha-icon>
            ${r.cost} pts
          </div>
          ${qty}
          ${!isAdmin ? `
          <button class="${btnClass}"
            data-id="${r.reward_id}"
            data-child="${child?.child_id || ''}"
            ${disabled ? 'disabled' : ''}>
            ${btnLabel}
          </button>` : ''}
        </div>`;
    }).join('');

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}
        .reward-header {
          padding:         14px 16px 10px;
          display:         flex;
          align-items:     center;
          justify-content: space-between;
        }
        .reward-header-title {
          font-weight: 600;
          font-size:   15px;
          display:     flex;
          align-items: center;
          gap:         6px;
        }
        .child-pts  { font-size: 12px; color: var(--kt-text-muted); }
        .cat-row    { display: flex; gap: 6px; flex-wrap: wrap; padding: 0 16px 10px; }
        .reward-grid {
          display:               grid;
          grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
          gap:                   10px;
          padding:               0 16px 16px;
        }
        .reward-tile {
          background:     var(--kt-surface);
          border-radius:  var(--kt-r-chip);
          padding:        14px 10px;
          display:        flex;
          flex-direction: column;
          align-items:    center;
          gap:            5px;
          text-align:     center;
          transition:     box-shadow .2s;
        }
        .reward-tile:hover { box-shadow: 0 2px 10px rgba(0,0,0,.12); }
        .reward-icon  { display: flex; align-items: center; justify-content: center; color: var(--primary-color); }
        .reward-name  { font-size: 13px; font-weight: 600; }
        .reward-desc  { font-size: 11px; color: var(--kt-text-muted); }
        .reward-cost  {
          font-size:   12px;
          font-weight: 600;
          color:       var(--primary-color);
          display:     flex;
          align-items: center;
          gap:         3px;
        }
        .reward-qty   { font-size: 10px; color: var(--kt-text-muted); }
        .kt-btn       { width: 100%; margin-top: 4px; padding: 6px 0; font-size: 12px; }
        .tile-actions { display: flex; gap: 4px; align-self: flex-end; margin-bottom: 2px; }
        .icon-btn     { background: var(--kt-surface); border: none; border-radius: 6px; padding: 3px 5px; cursor: pointer; color: var(--kt-text-muted); display: flex; align-items: center; }
        .icon-btn:hover { color: var(--primary-color); }
        .header-right { display: flex; align-items: center; gap: 8px; }
      </style>

      <div class="kt-card">
        <div class="reward-header">
          <span class="reward-header-title">
            <ha-icon icon="mdi:gift-outline" style="--mdc-icon-size:18px;"></ha-icon>
            Recompenses
          </span>
          <div class="header-right">
            ${child ? `<span class="child-pts">${child.name} &middot; ${child.points} pts</span>` : ''}
            ${isAdmin ? `<button class="kt-btn kt-btn-add sm" id="add-reward-btn">+ Ajouter</button>` : ''}
          </div>
        </div>
        <div class="cat-row">${catChips}</div>
        <div class="kt-divider"></div>
        ${filtered.length === 0
          ? `<div class="kt-empty">Aucune recompense disponible</div>`
          : `<div class="reward-grid">${tiles}</div>`
        }
      </div>`;

    this.shadowRoot.querySelector('#add-reward-btn')?.addEventListener('click', () => this._openAddRewardDialog());

    this.shadowRoot.querySelectorAll('.kt-chip[data-cat]').forEach(chip => {
      chip.addEventListener('click', () => {
        this._filter = chip.dataset.cat;
        this._render();
      });
    });

    this.shadowRoot.querySelectorAll('button[data-id]:not([disabled]):not([data-action])').forEach(btn => {
      btn.addEventListener('click', () => {
        callService(this._hass, 'kids_tasks', 'claim_reward', {
          reward_id: btn.dataset.id,
          child_id:  btn.dataset.child,
        });
      });
    });

    if (isAdmin) {
      this.shadowRoot.querySelectorAll('[data-action="edit-reward"]').forEach(btn => {
        btn.addEventListener('click', () => {
          const r = allRewards.find(x => x.reward_id === btn.dataset.id);
          if (r) this._openEditRewardDialog(r);
        });
      });
      this.shadowRoot.querySelectorAll('[data-action="delete-reward"]').forEach(btn => {
        btn.addEventListener('click', () => {
          const r = allRewards.find(x => x.reward_id === btn.dataset.id);
          if (r) this._openDeleteRewardConfirm(r);
        });
      });
    }
  }
}

customElements.define('kids-tasks-reward-card', KidsTasksRewardCard);

// ═══════════════════════════════════════════════════════════════════════════════
// Card 5 — KidsTasksChildrenCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksChildrenCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._renderTimer = null;
  }

  setConfig(config) {
    this._config = { entity: 'sensor.kidtasks_all_children_list', ...config };
  }

  set hass(hass) {
    this._hass = hass;
    scheduleRender(this);
  }

  getCardSize() { return 3; }

  disconnectedCallback() {
    if (this._renderTimer) clearTimeout(this._renderTimer);
  }

  _openAddChildDialog() {
    const content = `
      <div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Nom</label>
          <input id="kt-name" type="text" placeholder="Prenom de l'enfant" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Avatar (emoji ou URL)</label>
          <input id="kt-avatar" type="text" placeholder="Ex: ou https://..." style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Couleur debut du gradient</label>
          <input id="kt-grad-start" type="color" value="#6b73ff" style="width:60px;height:36px;border:none;border-radius:8px;cursor:pointer;background:none;">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Couleur fin du gradient</label>
          <input id="kt-grad-end" type="color" value="#9c27b0" style="width:60px;height:36px;border:none;border-radius:8px;cursor:pointer;background:none;">
        </div>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px;">
          <button id="kt-cancel" style="padding:8px 18px;border-radius:8px;border:1.5px solid var(--divider-color);background:var(--secondary-background-color);color:var(--primary-text-color);font-size:14px;cursor:pointer;">Annuler</button>
          <button id="kt-save" style="padding:8px 18px;border-radius:8px;border:none;background:var(--primary-color);color:var(--text-primary-color,#fff);font-size:14px;font-weight:600;cursor:pointer;">Ajouter</button>
        </div>
      </div>`;

    const dlg = showModal(content, 'Ajouter un enfant');
    dlg.querySelector('#kt-cancel')?.addEventListener('click', () => dlg.remove());
    dlg.querySelector('#kt-save')?.addEventListener('click', () => {
      const name = dlg.querySelector('#kt-name')?.value?.trim();
      if (!name) { dlg.querySelector('#kt-name')?.focus(); return; }
      callService(this._hass, 'kids_tasks', 'add_child', {
        name,
        avatar:               dlg.querySelector('#kt-avatar')?.value?.trim() || '',
        card_gradient_start:  dlg.querySelector('#kt-grad-start')?.value || '#6b73ff',
        card_gradient_end:    dlg.querySelector('#kt-grad-end')?.value   || '#9c27b0',
      });
      dlg.remove();
    });
  }

  _openEditChildDialog(child) {
    const gradStart = child.card_gradient_start || '#6b73ff';
    const gradEnd   = child.card_gradient_end   || '#9c27b0';
    const content = `
      <div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Nom</label>
          <input id="kt-name" type="text" value="${child.name || ''}" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Avatar (emoji ou URL)</label>
          <input id="kt-avatar" type="text" value="${child.avatar || ''}" style="${FIELD_STYLE}">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Couleur debut du gradient</label>
          <input id="kt-grad-start" type="color" value="${gradStart}" style="width:60px;height:36px;border:none;border-radius:8px;cursor:pointer;background:none;">
        </div>
        <div style="${ROW_STYLE}">
          <label style="${LABEL_STYLE}">Couleur fin du gradient</label>
          <input id="kt-grad-end" type="color" value="${gradEnd}" style="width:60px;height:36px;border:none;border-radius:8px;cursor:pointer;background:none;">
        </div>
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px;">
          <button id="kt-cancel" style="padding:8px 18px;border-radius:8px;border:1.5px solid var(--divider-color);background:var(--secondary-background-color);color:var(--primary-text-color);font-size:14px;cursor:pointer;">Annuler</button>
          <button id="kt-save" style="padding:8px 18px;border-radius:8px;border:none;background:var(--primary-color);color:var(--text-primary-color,#fff);font-size:14px;font-weight:600;cursor:pointer;">Sauvegarder</button>
        </div>
      </div>`;

    const dlg = showModal(content, 'Modifier l\'enfant');
    dlg.querySelector('#kt-cancel')?.addEventListener('click', () => dlg.remove());
    dlg.querySelector('#kt-save')?.addEventListener('click', () => {
      const name = dlg.querySelector('#kt-name')?.value?.trim();
      if (!name) { dlg.querySelector('#kt-name')?.focus(); return; }
      callService(this._hass, 'kids_tasks', 'update_child', {
        child_id:             child.id,
        name,
        avatar:               dlg.querySelector('#kt-avatar')?.value?.trim() || '',
        card_gradient_start:  dlg.querySelector('#kt-grad-start')?.value || '#6b73ff',
        card_gradient_end:    dlg.querySelector('#kt-grad-end')?.value   || '#9c27b0',
      });
      dlg.remove();
    });
  }

  _openDeleteChildConfirm(child) {
    confirmModal('Supprimer "' + child.name + '" ? Toutes les donnees associees seront perdues.', () =>
      callService(this._hass, 'kids_tasks', 'remove_child', { child_id: child.id })
    );
  }

  _render() {
    const state    = this._hass.states[this._config.entity];
    const children = state?.attributes?.children || [];

    const rows = children.map((c, i) => `
      <div class="child-row">
        <div class="child-avatar">${avatarHtml(c.avatar, c.avatar_type, 36)}</div>
        <div class="child-info">
          <div class="child-name">${c.name}</div>
          <div class="child-meta">Niv. ${c.level} &middot; ${c.points} pts &middot; ${c.coins} pieces</div>
        </div>
        <div class="child-actions">
          <button class="icon-btn" data-id="${c.id}" data-action="edit-child" title="Modifier">
            <ha-icon icon="mdi:pencil" style="--mdc-icon-size:16px;"></ha-icon>
          </button>
          <button class="icon-btn" data-id="${c.id}" data-action="delete-child" title="Supprimer">
            <ha-icon icon="mdi:trash-can-outline" style="--mdc-icon-size:16px;"></ha-icon>
          </button>
        </div>
      </div>
      ${i < children.length - 1 ? '<div class="kt-divider"></div>' : ''}
    `).join('');

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}
        .child-row     { display: flex; align-items: center; padding: 10px 16px; gap: 12px; }
        .child-avatar  { flex-shrink: 0; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 50%; overflow: hidden; background: var(--kt-surface); }
        .child-info    { flex: 1; min-width: 0; }
        .child-name    { font-size: 14px; font-weight: 600; }
        .child-meta    { font-size: 11px; color: var(--kt-text-muted); margin-top: 2px; }
        .child-actions { display: flex; gap: 6px; flex-shrink: 0; }
        .icon-btn      { background: var(--kt-surface); border: none; border-radius: 6px; padding: 5px 7px; cursor: pointer; color: var(--kt-text-muted); display: flex; align-items: center; }
        .icon-btn:hover { color: var(--primary-color); }
        .header-right  { display: flex; align-items: center; gap: 8px; }
      </style>

      <div class="kt-card">
        <div class="kt-header">
          Enfants
          <div class="header-right">
            <span class="kt-badge">${children.length}</span>
            <button class="kt-btn kt-btn-add sm" id="add-child-btn">+ Ajouter</button>
          </div>
        </div>
        <div class="kt-divider"></div>
        ${children.length === 0
          ? '<div class="kt-empty">Aucun enfant configure</div>'
          : rows
        }
      </div>`;

    this.shadowRoot.getElementById('add-child-btn')?.addEventListener('click', () => this._openAddChildDialog());

    this.shadowRoot.querySelectorAll('[data-action="edit-child"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const child = children.find(c => c.id === btn.dataset.id);
        if (child) this._openEditChildDialog(child);
      });
    });

    this.shadowRoot.querySelectorAll('[data-action="delete-child"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const child = children.find(c => c.id === btn.dataset.id);
        if (child) this._openDeleteChildConfirm(child);
      });
    });
  }
}

customElements.define('kids-tasks-children-card', KidsTasksChildrenCard);

// ─── HACS / Lovelace card registration ───────────────────────────────────────

window.customCards = window.customCards || [];
window.customCards.push(
  {
    type:        'kids-tasks-child-summary-card',
    name:        'Kids Tasks — Resume enfant',
    description: "Vue compacte d'un enfant : avatar, XP, taches du jour",
  },
  {
    type:        'kids-tasks-validation-card',
    name:        'Kids Tasks — Validation',
    description: 'Queue de validation parentale avec actions inline',
  },
  {
    type:        'kids-tasks-task-list-card',
    name:        'Kids Tasks — Liste de taches',
    description: "Liste filtree des taches avec statuts et bouton d'ajout",
  },
  {
    type:        'kids-tasks-reward-card',
    name:        'Kids Tasks — Recompenses',
    description: 'Catalogue de recompenses avec echange en 1 tap',
  },
  {
    type:        'kids-tasks-children-card',
    name:        'Kids Tasks — Gestion des enfants',
    description: 'Liste et gestion complete des enfants (ajouter, modifier, supprimer)',
  }
);
