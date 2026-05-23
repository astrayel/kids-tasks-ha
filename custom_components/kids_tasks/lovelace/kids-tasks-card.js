/**
 * Kids Tasks Manager — Custom Lovelace Cards
 *
 * 4 cards in one file:
 *   kids-tasks-child-card       — compact child view (avatar, XP, today's tasks)
 *   kids-tasks-validation-card  — parent validation queue
 *   kids-tasks-task-list-card   — full task list with filters
 *   kids-tasks-reward-card      — reward catalog with claim button
 *
 * No build step required. Uses vanilla custom elements + Shadow DOM.
 * Compatible with Home Assistant 2024.11+
 */

// ─── Shared constants ────────────────────────────────────────────────────────

const CATEGORY_ICONS = {
  bedroom:  "mdi:bed",
  hygiene:  "mdi:shower",
  kitchen:  "mdi:silverware-fork-knife",
  homework: "mdi:book-open-variant",
  outdoor:  "mdi:tree",
  music:    "mdi:music",
  other:    "mdi:clipboard-list",
};

const REWARD_ICONS = {
  fun:         "mdi:gamepad-variant",
  screen_time: "mdi:monitor",
  outing:      "mdi:car",
  privilege:   "mdi:crown",
  toy:         "mdi:toy-brick",
  treat:       "mdi:food-apple",
};

const STATUS_META = {
  todo:               { label: "A faire",    color: "#9e9e9e", icon: "mdi:circle-outline" },
  in_progress:        { label: "En cours",   color: "#2196f3", icon: "mdi:play-circle-outline" },
  completed:          { label: "Termine",    color: "#4caf50", icon: "mdi:check-circle-outline" },
  pending_validation: { label: "En attente", color: "#ff9800", icon: "mdi:clock-outline" },
  validated:          { label: "Valide",     color: "#4caf50", icon: "mdi:check-circle" },
  failed:             { label: "Echoue",     color: "#f44336", icon: "mdi:close-circle-outline" },
};

// ─── Shared styles ───────────────────────────────────────────────────────────

const BASE_STYLES = `
  :host { display: block; }

  .kt-card {
    background: var(--card-background-color);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: var(--box-shadow);
    font-family: var(--paper-font-body1_-_font-family, sans-serif);
    color: var(--primary-text-color);
  }

  .kt-header {
    padding: 14px 16px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
    font-size: 15px;
  }

  .kt-badge {
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 12px;
    font-weight: 700;
  }

  .kt-divider {
    height: 1px;
    background: var(--divider-color);
    margin: 0;
  }

  .kt-btn {
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity .15s;
  }
  .kt-btn:active { opacity: .7; }
  .kt-btn-validate { background: #4caf50; color: #fff; }
  .kt-btn-reject   { background: #f44336; color: #fff; }
  .kt-btn-claim    { background: var(--primary-color); color: var(--text-primary-color, #fff); }
  .kt-btn-disabled { background: var(--disabled-color, #bdbdbd); color: #fff; cursor: default; }

  .kt-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: var(--secondary-background-color);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    border: 1.5px solid transparent;
    transition: border-color .15s;
  }
  .kt-chip.active {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }

  .kt-empty {
    padding: 24px;
    text-align: center;
    color: var(--secondary-text-color);
    font-size: 14px;
  }

  ha-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    vertical-align: middle;
  }
`;

// ─── Helpers ─────────────────────────────────────────────────────────────────

function callService(hass, domain, service, data) {
  hass.callService(domain, service, data);
}

function xpForLevel(level) {
  return level * 100;
}

function pointsToNextLevel(points, level) {
  return Math.max(0, xpForLevel(level) - points);
}

function xpProgress(points, level) {
  const base = xpForLevel(level - 1);
  const target = xpForLevel(level);
  return Math.min(100, Math.round(((points - base) / (target - base)) * 100));
}

/** Renders an icon: MDI via ha-icon, empty string/null → person placeholder, else text span. */
function iconHtml(icon, size = "20px") {
  if (icon && icon.startsWith("mdi:")) {
    return `<ha-icon icon="${icon}" style="--mdc-icon-size:${size};"></ha-icon>`;
  }
  if (icon) {
    return `<span style="font-size:${size};">${icon}</span>`;
  }
  return `<ha-icon icon="mdi:help-circle-outline" style="--mdc-icon-size:${size};"></ha-icon>`;
}

function categoryIconHtml(category, size = "20px") {
  const icon = CATEGORY_ICONS[(category || "").toLowerCase()] || "mdi:clipboard-list";
  return `<ha-icon icon="${icon}" style="--mdc-icon-size:${size};"></ha-icon>`;
}

function avatarHtml(avatar, avatarType, size = 40) {
  if ((avatarType === "url" || avatarType === "inline") && avatar) {
    return `<img src="${avatar}" style="width:${size}px;height:${size}px;border-radius:50%;object-fit:cover;">`;
  }
  if (avatarType === "emoji" && avatar) {
    return `<span style="font-size:${size * 0.6}px;line-height:${size}px;">${avatar}</span>`;
  }
  return `<ha-icon icon="mdi:account-circle" style="--mdc-icon-size:${size}px;color:rgba(255,255,255,.8);"></ha-icon>`;
}

// ═══════════════════════════════════════════════════════════════════════════════
// 1. KidsTasksChildCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksChildCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._filter = "today";
  }

  setConfig(config) {
    if (!config.entity) throw new Error("kids-tasks-child-card: 'entity' required (points sensor)");
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 3; }

  _tasks(childId) {
    const allTasks = this._hass.states["sensor.kidtasks_all_tasks_list"];
    if (!allTasks) return [];
    return (allTasks.attributes.tasks || []).filter(t =>
      Array.isArray(t.assigned_child_ids) && t.assigned_child_ids.includes(childId)
    );
  }

  _pendingCount(childId) {
    const pv = this._hass.states["sensor.kidtasks_pending_validations"];
    if (!pv) return 0;
    return (pv.attributes.pending_tasks || []).filter(t =>
      Array.isArray(t.child_ids) && t.child_ids.includes(childId)
    ).length;
  }

  _render() {
    const state = this._hass.states[this._config.entity];
    if (!state) {
      this.shadowRoot.innerHTML = `<div class="kt-card"><div class="kt-empty">Entite introuvable : ${this._config.entity}</div></div>`;
      return;
    }

    const a = state.attributes;
    const childName = a.name || "Enfant";
    const childId = a.child_id || "";
    this._childName = childName;
    const points = state.state !== undefined ? parseInt(state.state) : (a.points || 0);
    const level = a.level || 1;
    const coins = a.coins || 0;
    const avatar = a.avatar || "";
    const avatarType = a.avatar_type || "emoji";
    const gradStart = a.card_gradient_start || "var(--primary-color)";
    const gradEnd = a.card_gradient_end || "var(--accent-color, #7c4dff)";
    const pct = xpProgress(points, level);
    const toNext = pointsToNextLevel(points, level);
    const tasks = this._tasks(childId);
    const pending = this._pendingCount(childId);

    const taskChips = tasks.slice(0, 5).map(t => {
      const meta = STATUS_META[this._rawStatus(t.status)] || STATUS_META["todo"];
      return `<span class="task-chip" style="border-color:${meta.color}20;background:${meta.color}15;">
        ${categoryIconHtml(t.category, "14px")}
        <ha-icon icon="${meta.icon}" style="--mdc-icon-size:12px;color:${meta.color};"></ha-icon>
        <span style="max-width:70px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;">${t.name}</span>
      </span>`;
    }).join("");

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}
        .child-header {
          background: linear-gradient(135deg, ${gradStart}, ${gradEnd});
          padding: 14px 16px;
          display: flex;
          align-items: center;
          gap: 12px;
          color: #fff;
        }
        .avatar-ring {
          width: 52px; height: 52px;
          border-radius: 50%;
          background: rgba(255,255,255,.25);
          display: flex; align-items: center; justify-content: center;
          flex-shrink: 0;
        }
        .child-name { font-size: 17px; font-weight: 700; }
        .child-sub  { font-size: 12px; opacity: .85; margin-top: 2px; display: flex; align-items: center; gap: 4px; }
        .level-badge {
          margin-left: auto;
          background: rgba(255,255,255,.25);
          border-radius: 20px;
          padding: 4px 10px;
          font-size: 12px;
          font-weight: 700;
          white-space: nowrap;
          display: flex; align-items: center; gap: 4px;
        }
        .kt-body { padding: 12px 16px; }
        .xp-row { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
        .xp-bar-bg {
          flex: 1; height: 8px; border-radius: 4px;
          background: var(--secondary-background-color);
          overflow: hidden;
        }
        .xp-bar-fill {
          height: 100%; border-radius: 4px;
          background: linear-gradient(90deg, ${gradStart}, ${gradEnd});
          transition: width .4s;
        }
        .xp-label { font-size: 11px; color: var(--secondary-text-color); white-space: nowrap; }
        .coins-row {
          display: flex; align-items: center; gap: 6px;
          font-size: 13px; color: var(--secondary-text-color); margin-bottom: 10px;
        }
        .tasks-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
        .task-chip {
          display: inline-flex; align-items: center; gap: 4px;
          border: 1.5px solid; border-radius: 20px;
          padding: 3px 8px; font-size: 11px;
        }
        .actions { display: flex; gap: 8px; justify-content: flex-end; }
        .validate-btn {
          background: #ff9800; color: #fff;
          border: none; border-radius: 8px;
          padding: 6px 14px; font-size: 13px; font-weight: 600;
          cursor: pointer; display: ${pending > 0 ? "flex" : "none"};
          align-items: center; gap: 6px;
        }
        .all-done { font-size: 12px; color: var(--secondary-text-color); display: flex; align-items: center; gap: 4px; }
      </style>
      <div class="kt-card">
        <div class="child-header">
          <div class="avatar-ring">${avatarHtml(avatar, avatarType, 40)}</div>
          <div>
            <div class="child-name">${childName}</div>
            <div class="child-sub">
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
            <div class="xp-bar-bg"><div class="xp-bar-fill" style="width:${pct}%"></div></div>
            <div class="xp-label">${points} pts · encore ${toNext} avant niv. ${level + 1}</div>
          </div>

          ${tasks.length > 0
            ? `<div class="tasks-chips">${taskChips}</div>`
            : `<div style="font-size:12px;color:var(--secondary-text-color);margin-bottom:10px;">Aucune tache assignee</div>`
          }

          <div class="actions">
            ${pending > 0
              ? `<button class="validate-btn" id="val-btn">
                   <ha-icon icon="mdi:clock-outline" style="--mdc-icon-size:16px;"></ha-icon>
                   ${pending} a valider
                 </button>`
              : `<span class="all-done">
                   <ha-icon icon="mdi:check-circle-outline" style="--mdc-icon-size:14px;color:#4caf50;"></ha-icon>
                   Tout est valide
                 </span>`
            }
          </div>
        </div>
      </div>`;

    const btn = this.shadowRoot.getElementById("val-btn");
    if (btn) {
      btn.addEventListener("click", () => {
        const pv = this._hass.states["sensor.kidtasks_pending_validations"];
        const myPending = (pv?.attributes.pending_tasks || []).filter(t =>
          Array.isArray(t.child_ids) && t.child_ids.includes(childId)
        );
        myPending.forEach(t => callService(this._hass, "kids_tasks", "validate_task", { task_id: t.task_id }));
      });
    }
  }

  _rawStatus(displayStatus) {
    const map = {
      "A faire": "todo", "En cours": "in_progress", "Termine": "completed",
      "En validation": "pending_validation", "En attente de validation": "pending_validation",
      "Valide": "validated", "Echoue": "failed",
    };
    return map[displayStatus] || "todo";
  }
}

customElements.define("kids-tasks-child-card", KidsTasksChildCard);

// ═══════════════════════════════════════════════════════════════════════════════
// 2. KidsTasksValidationCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksValidationCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    this._config = { entity: "sensor.kidtasks_pending_validations", ...config };
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 3; }

  _render() {
    const state = this._hass.states[this._config.entity];
    const pending = state?.attributes?.pending_tasks || [];

    const rows = pending.map((t, i) => `
      <div class="task-row" data-idx="${i}">
        <div class="task-info">
          <span class="task-icon">${categoryIconHtml(t.category, "22px")}</span>
          <div class="task-details">
            <div class="task-name">${t.name}</div>
            <div class="task-child">${t.child} · ${t.points} pts</div>
          </div>
        </div>
        <div class="task-actions">
          <button class="kt-btn kt-btn-validate" data-id="${t.task_id}" data-action="validate">Valider</button>
          <button class="kt-btn kt-btn-reject"   data-id="${t.task_id}" data-action="reject">Rejeter</button>
        </div>
      </div>
    `).join('<div class="kt-divider"></div>');

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}
        .task-row {
          display: flex; align-items: center;
          justify-content: space-between;
          padding: 12px 16px; gap: 10px;
        }
        .task-info { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
        .task-icon { display: flex; align-items: center; flex-shrink: 0; }
        .task-details { min-width: 0; }
        .task-name {
          font-size: 14px; font-weight: 600;
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .task-child { font-size: 12px; color: var(--secondary-text-color); margin-top: 2px; }
        .task-actions { display: flex; gap: 6px; flex-shrink: 0; }
        .kt-btn { padding: 6px 12px; font-size: 13px; font-weight: 600; }
      </style>
      <div class="kt-card">
        <div class="kt-header">
          A valider
          ${pending.length > 0 ? `<span class="kt-badge">${pending.length}</span>` : ""}
        </div>
        <div class="kt-divider"></div>
        ${pending.length === 0
          ? `<div class="kt-empty">Tout est valide</div>`
          : rows
        }
      </div>`;

    this.shadowRoot.querySelectorAll("button[data-id]").forEach(btn => {
      btn.addEventListener("click", () => {
        const { id, action } = btn.dataset;
        const svc = action === "validate" ? "validate_task" : "reject_task";
        callService(this._hass, "kids_tasks", svc, { task_id: id });
      });
    });
  }
}

customElements.define("kids-tasks-validation-card", KidsTasksValidationCard);

// ═══════════════════════════════════════════════════════════════════════════════
// 3. KidsTasksTaskListCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksTaskListCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._filter = "all";
  }

  setConfig(config) {
    this._config = { entity: "sensor.kidtasks_all_tasks_list", ...config };
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 4; }

  _filteredTasks(tasks) {
    switch (this._filter) {
      case "daily":   return tasks.filter(t => t.frequency === "Quotidienne");
      case "weekly":  return tasks.filter(t => t.frequency === "Hebdomadaire");
      case "pending": return tasks.filter(t => t.status === "En validation");
      case "done":    return tasks.filter(t => t.status === "Valide" || t.status === "Termine");
      default:        return tasks;
    }
  }

  _rawStatus(displayStatus) {
    const map = {
      "A faire": "todo", "En cours": "in_progress", "Termine": "completed",
      "En validation": "pending_validation", "Valide": "validated", "Echoue": "failed",
    };
    return map[displayStatus] || "todo";
  }

  _render() {
    const state = this._hass.states[this._config.entity];
    const allTasks = state?.attributes?.tasks || [];
    const tasks = this._filteredTasks(allTasks);

    const filters = [
      { key: "all",     label: "Tous" },
      { key: "daily",   label: "Quotidien" },
      { key: "weekly",  label: "Hebdo" },
      { key: "pending", label: "En attente" },
      { key: "done",    label: "Faits" },
    ];

    const filterChips = filters.map(f => `
      <span class="kt-chip ${this._filter === f.key ? "active" : ""}" data-filter="${f.key}">${f.label}</span>
    `).join("");

    const taskRows = tasks.map(t => {
      const rawStatus = this._rawStatus(t.status);
      const meta = STATUS_META[rawStatus] || STATUS_META["todo"];
      const isPending = rawStatus === "pending_validation";

      return `
        <div class="task-row">
          <span class="status-dot" style="background:${meta.color};" title="${meta.label}"></span>
          <span class="cat-icon">${categoryIconHtml(t.category, "18px")}</span>
          <div class="task-details">
            <div class="task-name">${t.name}</div>
            <div class="task-meta">${t.assigned_child} · ${t.frequency}</div>
          </div>
          <div class="task-right">
            <span class="pts-badge">${t.points} pts</span>
            ${isPending ? `
              <button class="kt-btn kt-btn-validate sm" data-id="${t.task_id}" data-action="validate">Valider</button>
              <button class="kt-btn kt-btn-reject sm"   data-id="${t.task_id}" data-action="reject">Rejeter</button>
            ` : ""}
          </div>
        </div>
        <div class="kt-divider"></div>`;
    }).join("");

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}
        .filter-row { display: flex; gap: 6px; flex-wrap: wrap; padding: 10px 16px; }
        .task-row {
          display: flex; align-items: center;
          padding: 10px 16px; gap: 10px;
        }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
        .cat-icon   { display: flex; align-items: center; flex-shrink: 0; }
        .task-details { flex: 1; min-width: 0; }
        .task-name {
          font-size: 13px; font-weight: 600;
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .task-meta { font-size: 11px; color: var(--secondary-text-color); margin-top: 2px; }
        .task-right { display: flex; align-items: center; gap: 5px; flex-shrink: 0; }
        .pts-badge {
          background: var(--secondary-background-color);
          border-radius: 10px; padding: 2px 7px;
          font-size: 11px; font-weight: 600;
        }
        .sm { padding: 4px 10px; font-size: 12px; }
      </style>
      <div class="kt-card">
        <div class="kt-header">
          Taches
          <span class="kt-badge">${tasks.length}</span>
        </div>
        <div class="filter-row">${filterChips}</div>
        <div class="kt-divider"></div>
        ${tasks.length === 0
          ? `<div class="kt-empty">Aucune tache dans cette categorie</div>`
          : taskRows
        }
      </div>`;

    this.shadowRoot.querySelectorAll(".kt-chip[data-filter]").forEach(chip => {
      chip.addEventListener("click", () => {
        this._filter = chip.dataset.filter;
        this._render();
      });
    });

    this.shadowRoot.querySelectorAll("button[data-action]").forEach(btn => {
      btn.addEventListener("click", () => {
        const svc = btn.dataset.action === "validate" ? "validate_task" : "reject_task";
        callService(this._hass, "kids_tasks", svc, { task_id: btn.dataset.id });
      });
    });
  }
}

customElements.define("kids-tasks-task-list-card", KidsTasksTaskListCard);

// ═══════════════════════════════════════════════════════════════════════════════
// 4. KidsTasksRewardCard
// ═══════════════════════════════════════════════════════════════════════════════

class KidsTasksRewardCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._filter = "all";
  }

  setConfig(config) {
    this._config = { entity: "sensor.kidtasks_all_rewards_list", ...config };
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() { return 4; }

  _childPoints() {
    if (!this._config.child_entity) return null;
    const s = this._hass.states[this._config.child_entity];
    return s ? parseInt(s.state) : null;
  }

  _childInfo() {
    if (!this._config.child_entity) return null;
    const s = this._hass.states[this._config.child_entity];
    if (!s) return null;
    return { name: s.attributes.name, points: parseInt(s.state), child_id: s.attributes.child_id };
  }

  _rewardIconHtml(r, size = "28px") {
    const icon = r.icon && r.icon.startsWith("mdi:")
      ? r.icon
      : (REWARD_ICONS[(r.category || "").toLowerCase()] || "mdi:gift");
    return `<ha-icon icon="${icon}" style="--mdc-icon-size:${size};"></ha-icon>`;
  }

  _render() {
    const state = this._hass.states[this._config.entity];
    const allRewards = (state?.attributes?.rewards || []).filter(r => r.active && r.is_available);
    const child = this._childInfo();
    const childPoints = child?.points ?? null;

    const categories = ["all", ...new Set(allRewards.map(r => r.category?.toLowerCase()).filter(Boolean))];

    const filtered = this._filter === "all"
      ? allRewards
      : allRewards.filter(r => r.category?.toLowerCase() === this._filter);

    const catChips = categories.map(c => {
      const icon = c === "all" ? "mdi:gift" : (REWARD_ICONS[c] || "mdi:gift");
      const label = c === "all" ? "Tous" : c.replace("_", " ");
      return `<span class="kt-chip ${this._filter === c ? "active" : ""}" data-cat="${c}">
        <ha-icon icon="${icon}" style="--mdc-icon-size:14px;"></ha-icon>
        ${label}
      </span>`;
    }).join("");

    const tiles = filtered.map(r => {
      const canAfford = childPoints !== null ? childPoints >= r.cost : null;
      const btnClass = child
        ? (canAfford ? "kt-btn kt-btn-claim" : "kt-btn kt-btn-disabled")
        : "kt-btn kt-btn-disabled";
      const btnLabel = !child ? "Admin" : canAfford ? "Echanger" : "Pas assez";
      const qty = r.limited_quantity ? `<span class="qty">x ${r.remaining_quantity}</span>` : "";

      return `
        <div class="reward-tile">
          <div class="reward-icon">${this._rewardIconHtml(r, "28px")}</div>
          <div class="reward-name">${r.name}</div>
          ${r.description ? `<div class="reward-desc">${r.description}</div>` : ""}
          <div class="reward-cost">
            <ha-icon icon="mdi:cash" style="--mdc-icon-size:14px;"></ha-icon>
            ${r.cost} pts ${qty}
          </div>
          <button class="${btnClass}"
            data-id="${r.reward_id}"
            data-child="${child?.child_id || ""}"
            ${(!child || !canAfford) ? "disabled" : ""}>
            ${btnLabel}
          </button>
        </div>`;
    }).join("");

    this.shadowRoot.innerHTML = `
      <style>
        ${BASE_STYLES}
        .reward-header {
          padding: 14px 16px 10px;
          display: flex; align-items: center; justify-content: space-between;
        }
        .reward-header-title { font-weight: 600; font-size: 15px; display: flex; align-items: center; gap: 6px; }
        .child-pts { font-size: 12px; color: var(--secondary-text-color); }
        .cat-row { display: flex; gap: 6px; flex-wrap: wrap; padding: 0 16px 10px; }
        .reward-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
          gap: 10px;
          padding: 0 16px 16px;
        }
        .reward-tile {
          background: var(--secondary-background-color);
          border-radius: 12px;
          padding: 14px 12px;
          display: flex; flex-direction: column;
          align-items: center; gap: 6px;
          text-align: center;
        }
        .reward-icon  { display: flex; align-items: center; justify-content: center; }
        .reward-name  { font-size: 13px; font-weight: 600; }
        .reward-desc  { font-size: 11px; color: var(--secondary-text-color); }
        .reward-cost  { font-size: 12px; font-weight: 600; color: var(--primary-color); display: flex; align-items: center; gap: 3px; }
        .qty { font-size: 10px; color: var(--secondary-text-color); }
        .kt-btn { width: 100%; margin-top: 4px; padding: 6px 0; font-size: 12px; }
      </style>
      <div class="kt-card">
        <div class="reward-header">
          <span class="reward-header-title">
            <ha-icon icon="mdi:gift-outline" style="--mdc-icon-size:18px;"></ha-icon>
            Recompenses
          </span>
          ${child ? `<span class="child-pts">${child.name} · ${child.points} pts</span>` : ""}
        </div>
        <div class="cat-row">${catChips}</div>
        <div class="kt-divider"></div>
        ${filtered.length === 0
          ? `<div class="kt-empty">Aucune recompense disponible</div>`
          : `<div class="reward-grid">${tiles}</div>`
        }
      </div>`;

    this.shadowRoot.querySelectorAll(".kt-chip[data-cat]").forEach(chip => {
      chip.addEventListener("click", () => {
        this._filter = chip.dataset.cat;
        this._render();
      });
    });

    this.shadowRoot.querySelectorAll("button[data-id]:not([disabled])").forEach(btn => {
      btn.addEventListener("click", () => {
        callService(this._hass, "kids_tasks", "claim_reward", {
          reward_id: btn.dataset.id,
          child_id: btn.dataset.child,
        });
      });
    });
  }
}

customElements.define("kids-tasks-reward-card", KidsTasksRewardCard);

// ─── HACS / Lovelace registration ────────────────────────────────────────────

window.customCards = window.customCards || [];
window.customCards.push(
  {
    type: "kids-tasks-child-card",
    name: "Kids Tasks — Enfant",
    description: "Vue compacte d'un enfant : avatar, XP, taches du jour",
  },
  {
    type: "kids-tasks-validation-card",
    name: "Kids Tasks — Validation",
    description: "Queue de validation parentale avec actions inline",
  },
  {
    type: "kids-tasks-task-list-card",
    name: "Kids Tasks — Liste de taches",
    description: "Liste filtree des taches avec statuts et actions",
  },
  {
    type: "kids-tasks-reward-card",
    name: "Kids Tasks — Recompenses",
    description: "Catalogue de recompenses avec echange en 1 tap",
  }
);
