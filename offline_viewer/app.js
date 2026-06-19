/* ==========================================================================
   OFFLINEFEED APP LOGIC
   ========================================================================== */

// DOM Elements
const navTabEntertainment = document.getElementById('nav-tab-entertainment');
const navTabSports = document.getElementById('nav-tab-sports');
const navTabTechnology = document.getElementById('nav-tab-technology');
const navTabSettings = document.getElementById('nav-tab-settings');
const newsView = document.getElementById('news-view');
const settingsView = document.getElementById('settings-view');
const syncIndicator = document.getElementById('sync-indicator');

let activeTab = 'entertainment'; // 'entertainment', 'sports', or 'technology'

let allNewsArticles = [];
let globalNewsChannels = [];
let selectedChannelId = null;
let newsReactionsMap = {};
let newsUnreadsMap = {};
let selectedAvatarBase64 = '';
let detectedIsRss = true;

// Hash helper for deterministic styling / reactions / view counts
function hashCode(str) {
  let hash = 0;
  if (!str) return hash;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return hash;
}

// SVG Icon generator for reaction pills instead of standard platform emojis
function getReactionSvg(idx) {
  if (idx === 0) {
    // Thumbs Up
    return `<svg class="telegram-reaction-svg reaction-thumbsup" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>`;
  } else if (idx === 1) {
    // Heart
    return `<svg class="telegram-reaction-svg reaction-heart" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path></svg>`;
  } else if (idx === 2) {
    // Flame
    return `<svg class="telegram-reaction-svg reaction-flame" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>`;
  } else if (idx === 3) {
    // Star
    return `<svg class="telegram-reaction-svg reaction-star" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`;
  }
  return '';
}

// Toast notification helper using clean Lucide SVGs
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast-notification toast-${type}`;
  
  let iconHtml = '';
  if (type === 'success') {
    iconHtml = `
      <svg class="toast-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
    `;
  } else if (type === 'error') {
    iconHtml = `
      <svg class="toast-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
    `;
  } else {
    // Info / default
    iconHtml = `
      <svg class="toast-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="16" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12.01" y2="8"></line>
      </svg>
    `;
  }
  
  toast.innerHTML = `
    ${iconHtml}
    <span class="toast-message">${message}</span>
  `;
  
  container.appendChild(toast);
  
  // Trigger entry animation
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  // Auto remove after 3.5s
  setTimeout(() => {
    toast.classList.remove('show');
    // Allow animation to finish before removing DOM node
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3500);
}

function getAvatarClass(source) {
  const hash = Math.abs(hashCode(source));
  return `tg-bg-${hash % 9}`;
}


function getChannelDomain(sourceName) {
  const s = sourceName.toLowerCase();
  if (s.includes('(x)') || s.includes('twitter') || s.includes('x.com')) return 'x.com';
  if (s.includes('variety')) return 'variety.com';
  if (s.includes('hollywood reporter') || s.includes('thr')) return 'hollywoodreporter.com';
  if (s.includes('vulture')) return 'vulture.com';
  if (s.includes('entertainment weekly') || s.includes('ew.com')) return 'ew.com';
  if (s.includes('screen daily')) return 'screendaily.com';
  if (s.includes('rotten tomatoes')) return 'rottentomatoes.com';
  if (s.includes('indiewire')) return 'indiewire.com';
  if (s.includes('slashfilm')) return 'slashfilm.com';
  if (s.includes('deadline')) return 'deadline.com';
  if (s.includes('collider')) return 'collider.com';
  if (s.includes('rogerebert')) return 'rogerebert.com';
  if (s.includes('av club') || s.includes('avclub')) return 'avclub.com';
  if (s.includes('letterboxd')) return 'letterboxd.com';
  if (s.includes('little white lies') || s.includes('lwlies')) return 'lwlies.com';
  if (s.includes('empireonline') || s.includes('empire magazine')) return 'empireonline.com';
  if (s.includes('cinemablend')) return 'cinemablend.com';
  if (s.includes('espn')) return 'espn.com';
  if (s.includes('bbc')) return 'bbc.co.uk';
  if (s.includes('sky sports')) return 'skysports.com';
  if (s.includes('techcrunch')) return 'techcrunch.com';
  if (s.includes('wired')) return 'wired.com';
  if (s.includes('the verge')) return 'theverge.com';
  
  if (window.customNewsSourcesList) {
    const found = window.customNewsSourcesList.find(src => src.name.toLowerCase() === s);
    if (found && found.url) {
      try {
        const u = new URL(found.url);
        return u.hostname;
      } catch(e) {}
    }
  }
  return '';
}

function getChannelAvatarHtml(source, size = 44, id = '') {
  const s = source.toLowerCase();
  const initial = source.charAt(0);
  const avatarClass = getAvatarClass(source);
  const idAttr = id ? `id="${id}"` : '';
  const style = `width: ${size}px; height: ${size}px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; user-select: none; box-shadow: 0 2px 5px rgba(0,0,0,0.25); overflow: hidden; background: #fff; border: 1.5px solid rgba(0,0,0,0.1); margin-right: 12px;`;
  
  if (s.includes('system logs') || s.includes('app logs')) {
    return `
      <div ${idAttr} style="${style} background: #202b36; border-color: rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: center;" class="telegram-avatar telegram-avatar-container">
        <img src="assets/database.svg" style="width: 50%; height: 50%; object-fit: contain; filter: invert(1); margin-right: 0;" alt="Database" />
      </div>
    `;
  }

  // Check if there is a custom avatar mapped to this source
  let customAvatarPath = window.customNewsSourcesMap && window.customNewsSourcesMap[s];
  if (!customAvatarPath && window.customNewsSourcesMap) {
    const keys = Object.keys(window.customNewsSourcesMap);
    for (const key of keys) {
      if (s === key) {
        customAvatarPath = window.customNewsSourcesMap[key];
        break;
      }
      // Substring check for brand sub-channels
      if (s.includes(key) || key.includes(s)) {
        customAvatarPath = window.customNewsSourcesMap[key];
        break;
      }
      // Prefix matching for networks/brands with slightly different sub-channel naming
      if ((s.startsWith('espn') && key.startsWith('espn')) ||
          (s.startsWith('bbc sport') && key.startsWith('bbc sport')) ||
          (s.startsWith('sky sports') && key.startsWith('sky sports')) ||
          (s.startsWith('techcrunch') && key.startsWith('techcrunch')) ||
          (s.startsWith('wired') && key.startsWith('wired')) ||
          (s.startsWith('the verge') && key.startsWith('the verge')) ||
          (s.startsWith('collider') && key.startsWith('collider')) ||
          (s.startsWith('deadline') && key.startsWith('deadline')) ||
          (s.startsWith('variety') && key.startsWith('variety')) ||
          (s.startsWith('vulture') && key.startsWith('vulture')) ||
          (s.startsWith('entertainment weekly') && key.startsWith('entertainment weekly')) ||
          (s.startsWith('rotten tomatoes') && key.startsWith('rotten tomatoes')) ||
          (s.startsWith('fabrizio romano') && key.startsWith('fabrizio romano')) ||
          (s.startsWith('the athletic') && key.startsWith('the athletic')) ||
          (s.startsWith('the madrid zone') && key.startsWith('the madrid zone'))) {
        customAvatarPath = window.customNewsSourcesMap[key];
        break;
      }
    }
  }

  if (customAvatarPath) {
    return `
      <div ${idAttr} style="${style} padding: ${size * 0.08}px;" class="telegram-avatar telegram-avatar-container">
        <img src="${customAvatarPath}" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="${source}" onerror="this.parentNode.innerHTML='<span style=&quot;font-weight: 800; font-size: ${size * 0.5}px;&quot;>${initial}</span>'; this.parentNode.className='telegram-avatar ${avatarClass}';" />
      </div>
    `;
  }
  
  if (s.includes('variety')) {
    return `
      <div ${idAttr} style="${style} padding: ${size * 0.15}px;" class="telegram-avatar telegram-avatar-container">
        <img src="assets/variety-logo.svg" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="Variety" />
      </div>
    `;
  } else if (s.includes('hollywood reporter') || s.includes('thr')) {
    return `
      <div ${idAttr} style="${style} padding: ${size * 0.15}px;" class="telegram-avatar telegram-avatar-container">
        <img src="assets/thr-logo.svg" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="THR" />
      </div>
    `;
  } else if (s.includes('vulture')) {
    return `
      <div ${idAttr} style="${style} padding: ${size * 0.12}px; background: #000; border-color: rgba(255,255,255,0.1);" class="telegram-avatar telegram-avatar-container">
        <img src="assets/vulture-logo.svg" style="width: 100%; height: 100%; object-fit: contain; display: block; filter: invert(1);" alt="Vulture" />
      </div>
    `;
  } else if (s.includes('entertainment weekly') || s.includes('ew.com')) {
    return `
      <div ${idAttr} style="${style} padding: ${size * 0.12}px;" class="telegram-avatar telegram-avatar-container">
        <img src="assets/ew-logo.svg" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="EW" />
      </div>
    `;
  } else if (s.includes('screen daily')) {
    return `
      <div ${idAttr} style="${style} padding: ${size * 0.08}px;" class="telegram-avatar telegram-avatar-container">
        <img src="assets/screendaily-logo.svg" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="Screen Daily" />
      </div>
    `;
  } else if (s.includes('rotten tomatoes')) {
    return `
      <div ${idAttr} style="${style} padding: ${size * 0.12}px;" class="telegram-avatar telegram-avatar-container">
        <img src="assets/Rotten-tomatoes-logo.svg" style="width: 100%; height: 100%; object-fit: contain; display: block;" alt="Rotten Tomatoes" />
      </div>
    `;
  } else if (s.includes('saved messages')) {
    return `
      <div ${idAttr} style="${style} background: #2481cc; border: none;" class="telegram-avatar telegram-avatar-container">
        <svg viewBox="0 0 24 24" width="${size * 0.45}" height="${size * 0.45}" fill="currentColor" stroke="none" style="color: #fff; display: block;">
          <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
    `;
  }

  // Automatic favicon fetch for custom feeds
  const domain = getChannelDomain(source);
  if (domain) {
    const faviconUrl = `https://www.google.com/s2/favicons?sz=64&domain=${domain}`;
    return `
      <div ${idAttr} style="${style} padding: ${size * 0.16}px;" class="telegram-avatar telegram-avatar-container">
        <img src="${faviconUrl}" style="width: 100%; height: 100%; object-fit: contain; display: block; border-radius: 4px;" alt="${source}" onerror="this.parentNode.innerHTML='<span style=&quot;font-weight: 800; font-size: ${size * 0.5}px;&quot;>${initial}</span>'; this.parentNode.className='telegram-avatar ${avatarClass}';" />
      </div>
    `;
  }
  
  return `<div class="telegram-avatar ${avatarClass}" ${idAttr} style="${style}">${initial}</div>`;
}

function getCleanChannelInfo(art) {
  let site = art.source || 'General';
  const src = (art.source || '').toLowerCase();
  
  if (src.includes('variety')) {
    site = 'Variety';
  } else if (src.includes('hollywood reporter') || src.includes('thr')) {
    site = 'The Hollywood Reporter';
  } else if (src.includes('vulture')) {
    site = 'Vulture';
  } else if (src.includes('entertainment weekly') || src.includes('ew.com')) {
    site = 'Entertainment Weekly';
  } else if (src.includes('screen daily')) {
    site = 'Screen Daily';
  } else if (src.includes('rotten tomatoes')) {
    site = 'Rotten Tomatoes';
  } else if (src.includes('deadline')) {
    site = 'Deadline Hollywood';
  } else if (src.includes('collider')) {
    site = 'Collider';
  } else if (src.includes('rogerebert')) {
    site = 'RogerEbert.com';
  } else if (src.includes('av club') || src.includes('avclub') || src.includes('a.v. club')) {
    site = 'The A.V. Club';
  } else if (src.includes('letterboxd')) {
    site = 'Letterboxd Journal';
  } else if (src.includes('little white lies') || src.includes('lwlies')) {
    site = 'Little White Lies';
  } else if (src.includes('empireonline') || src.includes('empire magazine')) {
    site = 'Empire Magazine';
  } else if (src.includes('cinemablend')) {
    site = 'CinemaBlend';
  } else if (src.includes('espn')) {
    site = 'ESPN News';
  } else if (src.includes('bbc')) {
    site = 'BBC Sport';
  } else if (src.includes('sky sports')) {
    site = 'Sky Sports News';
  } else if (src.includes('techcrunch')) {
    site = 'TechCrunch';
  } else if (src.includes('wired')) {
    site = 'Wired Tech';
  } else if (src.includes('the verge')) {
    site = 'The Verge';
  }
  
  let cat = art.topic || art.category || 'General';
  return {
    channelId: site,
    sourceName: site,
    categoryName: cat
  };
}

function formatTelegramDate(dateStr) {
  if (!dateStr) return '';
  let cleanStr = dateStr;
  if (cleanStr.includes(' +0000')) cleanStr = cleanStr.replace(' +0000', '');
  if (cleanStr.includes(' GMT')) cleanStr = cleanStr.replace(' GMT', '');
  
  try {
    const d = new Date(cleanStr);
    if (isNaN(d.getTime())) return dateStr;
    // Item 3: always show the exact absolute date + time (YYYY-MM-DD HH:MM)
    // instead of vague relative labels like "Yesterday". RTL/Persian layouts
    // render this numeric string correctly without reordering.
    const pad = (n) => String(n).padStart(2, '0');
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate())
      + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  } catch (e) {
    return dateStr;
  }
}

// Global window reactions click handler
window.toggleNewsReaction = function(url, idx, element) {
  const reactions = newsReactionsMap[url];
  if (!reactions) return;
  
  const reaction = reactions[idx];
  if (reaction.active) {
    reaction.count--;
    reaction.active = false;
    element.classList.remove('active');
  } else {
    reaction.count++;
    reaction.active = true;
    element.classList.add('active');
  }
  element.querySelector('.telegram-reaction-count').textContent = reaction.count;
};

// Global window forward to Saved Messages handler
window.forwardToSavedMessages = function(articleJsonStr) {
  try {
    const art = JSON.parse(decodeURIComponent(articleJsonStr));
    let savedArticles = JSON.parse(localStorage.getItem('offlineboxd-saved-news') || '[]');
    
    if (savedArticles.some(saved => saved.url === art.url)) {
      showToast(`Article is already in Saved Messages!`, 'info');
      return;
    }
    
    savedArticles.unshift(art);
    localStorage.setItem('offlineboxd-saved-news', JSON.stringify(savedArticles));
    showToast(`Forwarded to Saved Messages!`, 'success');
    
    // Sync to backend
    fetch('/api/news/saved/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(art)
    }).catch(e => console.error("Error syncing save to server:", e));

    filterNews();
  } catch (e) {
    console.error('Error forwarding news:', e);
  }
};

// Global window remove from Saved Messages handler
window.removeFromSavedMessages = function(url) {
  let savedArticles = JSON.parse(localStorage.getItem('offlineboxd-saved-news') || '[]');
  savedArticles = savedArticles.filter(art => art.url !== url);
  localStorage.setItem('offlineboxd-saved-news', JSON.stringify(savedArticles));
  showToast(`Removed from Saved Messages!`, 'info');
  
  // Sync to backend
  fetch('/api/news/saved/remove', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: url, url: url })
  }).catch(e => console.error("Error syncing unsave to server:", e));

  filterNews();
};

// Global window copy link fallback
window.shareNewsLink = function(url) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url)
      .then(() => showToast(`Link copied to clipboard!`))
      .catch(() => fallbackCopy(url));
  } else {
    fallbackCopy(url);
  }
};

function fallbackCopy(url) {
  const el = document.createElement('textarea');
  el.value = url;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
  showToast(`Link copied to clipboard!`);
}

function showSectionTab(section) {
  activeTab = section;
  
  if (settingsView) settingsView.classList.add('hidden');
  if (newsView) newsView.classList.remove('hidden');
  
  document.querySelectorAll('.header-center-nav .nav-link').forEach(link => {
    link.classList.remove('active');
  });
  
  const titleEl = document.getElementById('feed-list-title');
  const subtitleEl = document.getElementById('feed-list-subtitle');
  
  if (section === 'entertainment') {
    if (navTabEntertainment) navTabEntertainment.classList.add('active');
    if (titleEl) titleEl.textContent = 'Cinema & TV News';
    if (subtitleEl) subtitleEl.textContent = 'Aggregated entertainment feeds saved locally for offline consumption';
  } else if (section === 'sports') {
    if (navTabSports) navTabSports.classList.add('active');
    if (titleEl) titleEl.textContent = 'Sports News';
    if (subtitleEl) subtitleEl.textContent = 'Aggregated sports feeds and real-time coverage updates';
  } else if (section === 'technology') {
    if (navTabTechnology) navTabTechnology.classList.add('active');
    if (titleEl) titleEl.textContent = 'Technology & Gear';
    if (subtitleEl) subtitleEl.textContent = 'Aggregated tech feeds, gadget reviews, and industry insights';
  }
  
  if (allNewsArticles.length === 0) {
    loadNewsContent(false);
  } else {
    filterNews();
  }
}

function showNewsTab() {
  showSectionTab('entertainment');
}

function showSettingsTab() {
  if (newsView) newsView.classList.add('hidden');
  if (settingsView) settingsView.classList.remove('hidden');
  
  document.querySelectorAll('.header-center-nav .nav-link').forEach(link => {
    link.classList.remove('active');
  });
  if (navTabSettings) navTabSettings.classList.add('active');
  
  renderCustomSourcesInModal();
  if (typeof refreshTelegramChannelsList === 'function') {
    refreshTelegramChannelsList();
  }
}

function loadNewsContent(forceRefresh = false) {
  const loadingEl = document.getElementById('news-loading');
  const emptyEl = document.getElementById('news-empty');
  const errorEl = document.getElementById('news-error');
  const gridEl = document.getElementById('news-articles-grid');
  
  if (loadingEl) loadingEl.classList.remove('hidden');
  if (emptyEl) emptyEl.classList.add('hidden');
  if (errorEl) errorEl.classList.add('hidden');
  if (gridEl) {
    const articles = gridEl.querySelectorAll('.telegram-message-wrapper');
    articles.forEach(el => el.remove());
  }
  
  const url = forceRefresh ? '/api/news?refresh=true' : '/api/news';
  
  fetch(url)
    .then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then(data => {
      if (loadingEl) loadingEl.classList.add('hidden');
      
      if (data.error) {
        showNewsError(data.error);
        return;
      }
      
      window.customNewsSourcesMap = {};
      window.customNewsSourcesList = data.custom_sources || [];
      if (data.custom_sources) {
        data.custom_sources.forEach(src => {
          if (src.name && src.avatar_path) {
            window.customNewsSourcesMap[src.name.toLowerCase()] = src.avatar_path;
          }
        });
      }
      if (data.default_sources_avatars) {
        Object.keys(data.default_sources_avatars).forEach(name => {
          window.customNewsSourcesMap[name.toLowerCase()] = data.default_sources_avatars[name];
        });
      }
      
      allNewsArticles = data.articles || [];
      window.archivedArticles = data.archived_articles || [];

      // Reconcile saved articles
      if (data.saved_articles) {
        let localSaved = JSON.parse(localStorage.getItem('offlineboxd-saved-news') || '[]');
        let localMap = new Map(localSaved.map(a => [a.url || a.title, a]));
        let serverMap = new Map(data.saved_articles.map(a => [a.url || a.title, a]));
        let changed = false;

        for (let [key, art] of localMap) {
          if (!serverMap.has(key)) {
            fetch('/api/news/saved/add', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(art)
            }).catch(e => console.error("Error syncing local save to server:", e));
            serverMap.set(key, art);
            changed = true;
          }
        }
        let merged = Array.from(serverMap.values());
        localStorage.setItem('offlineboxd-saved-news', JSON.stringify(merged));
      }

      filterNews();
      
      // Update UI in settings
      renderCustomSourcesInModal();
      setIndicator(true);
    })
    .catch(err => {
      if (loadingEl) loadingEl.classList.add('hidden');
      showNewsError(err.message || err);
      setIndicator(false);
    });
}

function showNewsError(msg) {
  const errorEl = document.getElementById('news-error');
  const errorMsgEl = document.getElementById('news-error-message');
  if (errorEl) errorEl.classList.remove('hidden');
  if (errorMsgEl) errorMsgEl.textContent = `Error details: ${msg}`;
}

function renderChannelsList(channels) {
  const listEl = document.getElementById('telegram-channels-list');
  if (!listEl) return;
  
  listEl.innerHTML = '';
  
  // Count channels per source name to dynamically hide categories when there is only one feed
  const sourceCounts = {};
  channels.forEach(ch => {
    if (ch.source) {
      sourceCounts[ch.source] = (sourceCounts[ch.source] || 0) + 1;
    }
  });
  
  channels.forEach(ch => {
    const isSelected = ch.id === selectedChannelId;
    const avatarHtml = getChannelAvatarHtml(ch.source, 44);
    
    let timeText = '';
    let previewText = 'No messages';
    
    if (ch.latestArticle) {
      timeText = formatTelegramDate(ch.latestArticle.published);
      previewText = ch.latestArticle.title;
    }
    
    const showCategory = sourceCounts[ch.source] > 1;
    const channelName = (ch.id === 'SavedMessages' || ch.id === 'ArchivedMessages' || ch.id === 'SystemLogs') 
      ? ch.source 
      : (showCategory ? `${ch.source} ${ch.category}` : ch.source);
    const unreads = newsUnreadsMap[ch.id] || 0;
    const badgeHtml = unreads > 0 ? `<span class="telegram-unread-badge">${unreads}</span>` : '';
    
    const itemHtml = `
      <div class="telegram-channel-item ${isSelected ? 'active' : ''}" data-id="${ch.id}">
        ${avatarHtml}
        <div class="telegram-channel-info">
          <div class="telegram-channel-meta">
            <span class="telegram-channel-name" style="${ch.id === 'SavedMessages' ? 'color: var(--accent-blue);' : (ch.id === 'ArchivedMessages' ? 'color: #4caf50;' : '')}">${channelName}</span>
            <span class="telegram-channel-time">${timeText}</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <span class="telegram-channel-preview" style="flex-grow: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 6px;">${previewText}</span>
            ${badgeHtml}
          </div>
        </div>
      </div>
    `;
    listEl.insertAdjacentHTML('beforeend', itemHtml);
  });
  
  listEl.querySelectorAll('.telegram-channel-item').forEach(el => {
    el.addEventListener('click', () => {
      const channelId = el.getAttribute('data-id');
      selectNewsChannel(channelId);
    });
  });
}

function selectNewsChannel(channelId) {
  selectedChannelId = channelId;
  newsUnreadsMap[channelId] = 0;
  
  const ch = globalNewsChannels.find(c => c.id === channelId);
  if (!ch) return;
  
  renderChannelsList(globalNewsChannels);
  
  const btnSendToTg = document.getElementById('btn-send-to-tg');
  const btnSendAllToTg = document.getElementById('btn-send-all-to-tg');
  const isSpecialChannel = ch.id === 'SavedMessages' || ch.id === 'ArchivedMessages' || ch.id === 'SystemLogs';
  if (btnSendToTg) {
    btnSendToTg.style.display = isSpecialChannel ? 'none' : 'flex';
  }
  if (btnSendAllToTg) {
    btnSendAllToTg.style.display = isSpecialChannel ? 'none' : 'flex';
  }
  
  const headerAvatar = document.getElementById('telegram-header-avatar');
  const headerTitle = document.getElementById('telegram-header-title');
  const headerSubtitle = document.getElementById('telegram-header-subtitle');
  
  if (headerTitle) {
    if (ch.id === 'SavedMessages') {
      headerTitle.textContent = 'Saved Messages';
    } else if (ch.id === 'ArchivedMessages') {
      headerTitle.textContent = 'Archived Messages';
    } else if (ch.id === 'SystemLogs') {
      headerTitle.textContent = 'System & App Logs';
    } else {
      headerTitle.textContent = ch.source;
    }
  }
  
  if (headerSubtitle) {
    if (ch.id === 'SavedMessages') {
      const postCount = ch.articles.length;
      headerSubtitle.textContent = `${postCount} saved message${postCount === 1 ? '' : 's'} • Personal Archive`;
    } else if (ch.id === 'ArchivedMessages') {
      const postCount = ch.articles.length;
      headerSubtitle.textContent = `${postCount} archived message${postCount === 1 ? '' : 's'} • Removed from Feed`;
    } else if (ch.id === 'SystemLogs') {
      headerSubtitle.textContent = `Server logs and active harvester timelines`;
    } else {
      const postCount = ch.articles.length;
      let domain = ch.source.toLowerCase().replace(/[^a-z0-9]+/g, '') + '.com';
      if (ch.source === 'The Hollywood Reporter') domain = 'hollywoodreporter.com';
      else if (ch.source === 'Screen Daily') domain = 'screendaily.com';
      else if (ch.source === 'Rotten Tomatoes') domain = 'rottentomatoes.com';
      else if (ch.source === 'Fabrizio Romano') domain = 'x.com/FabrizioRomano';
      else if (ch.source === 'ESPN News') domain = 'espn.com';
      else if (ch.source === 'BBC Sport') domain = 'bbc.co.uk/sport';
      else if (ch.source === 'Sky Sports News') domain = 'skysports.com';
      else if (ch.source === 'Wired Tech') domain = 'wired.com';
      
      headerSubtitle.textContent = `${postCount} article${postCount === 1 ? '' : 's'} • ${domain}`;
    }
  }
  
  if (headerAvatar) {
    headerAvatar.outerHTML = getChannelAvatarHtml(ch.source, 40, 'telegram-header-avatar');
  }
  
  const pinnedBanner = document.getElementById('telegram-pinned-banner');
  const pinnedContent = document.getElementById('telegram-pinned-content');
  if (pinnedBanner && pinnedContent) {
    if (ch.id === 'SavedMessages') {
      pinnedContent.innerHTML = `<strong>Pinned Message:</strong> Click here to scroll to the top of your archived news.`;
    } else if (ch.id === 'ArchivedMessages') {
      pinnedContent.innerHTML = `<strong>Pinned Message:</strong> Click here to scroll to the top of the removed-from-feed archive.`;
    } else if (ch.id === 'SystemLogs') {
      pinnedContent.innerHTML = `<strong>Pinned Message:</strong> System event history logs and cache metrics.`;
    } else if (ch.latestArticle) {
      pinnedContent.innerHTML = `<strong>Pinned Message:</strong> ${ch.latestArticle.title}`;
    }
    
    pinnedBanner.onclick = () => {
      const gridEl = document.getElementById('news-articles-grid');
      if (gridEl) gridEl.scrollTop = 0;
    };
  }
  
  if (ch.id === 'SystemLogs') {
    loadAndRenderSystemLogs();
  } else {
    renderNewsArticles(ch.articles);
  }
}

function renderNewsArticles(articles) {
  const gridEl = document.getElementById('news-articles-grid');
  const emptyEl = document.getElementById('news-empty');
  if (!gridEl) return;
  
  const existingArticles = gridEl.querySelectorAll('.telegram-message-wrapper');
  existingArticles.forEach(el => el.remove());
  
  if (articles.length === 0) {
    if (emptyEl) emptyEl.classList.remove('hidden');
    return;
  }
  
  if (emptyEl) emptyEl.classList.add('hidden');
  const isSavedFeed = (selectedChannelId === 'SavedMessages');
  
  articles.forEach(art => {
    // Item 3: show the exact absolute date + time for every post.
    let timeText = art.published ? formatTelegramDate(art.published) : '';
    
    const hash = Math.abs(hashCode(art.title));
    const viewsCount = (hash % 8500) + 1200;
    
    if (!newsReactionsMap[art.url]) {
      newsReactionsMap[art.url] = [
        { emoji: '👍', count: hash % 47 + 6, active: false },
        { emoji: '❤️', count: hash % 23 + 2, active: false },
        { emoji: '🔥', count: hash % 18 + 1, active: false },
        { emoji: '🤩', count: hash % 8, active: false }
      ];
    }
    
    const reactions = newsReactionsMap[art.url];
    let reactionsHtml = `<div class="telegram-reactions-container">`;
    reactions.forEach((reaction, idx) => {
      if (reaction.count > 0 || reaction.active) {
        reactionsHtml += `
          <span class="telegram-reaction-pill ${reaction.active ? 'active' : ''}" onclick="toggleNewsReaction('${art.url}', ${idx}, this)">
            ${getReactionSvg(idx)}
            <span class="telegram-reaction-count">${reaction.count}</span>
          </span>
        `;
      }
    });
    reactionsHtml += `</div>`;
    
    const avatarHtml = getChannelAvatarHtml(art.source, 32);
    const forwardedHeader = isSavedFeed ? `
      <div style="font-size: 11px; color: #5288c1; margin-bottom: 6px; font-style: italic; font-weight: 600;">
        Forwarded from ${art.source}
      </div>
    ` : '';
    
    const actionBtnHtml = isSavedFeed ? `
      <button class="telegram-share-btn" title="Remove from Saved Messages" onclick="removeFromSavedMessages('${art.url.replace(/'/g, "\\'")}')" style="color: #e0565b;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    ` : `
      <button class="telegram-share-btn" title="Forward to Saved Messages" onclick="forwardToSavedMessages('${encodeURIComponent(JSON.stringify(art))}')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    `;
    
    const messageHtml = `
      <div class="telegram-message-wrapper">
        ${avatarHtml}
        <div class="telegram-message-container">
          <div class="telegram-message-bubble">
            ${art.thumbnail ? `
              <div class="telegram-bubble-image-wrapper">
                <img src="${art.thumbnail}" class="telegram-bubble-image" alt="" loading="lazy" onerror="this.parentNode.style.display='none';" />
              </div>
            ` : ''}
            <div class="telegram-bubble-body">
              ${forwardedHeader}
              <h4 class="telegram-bubble-title">${art.title}</h4>
              ${art.description ? `<p class="telegram-bubble-description">${art.description}</p>` : ''}
              <div class="topic-hashtag-container">
                <span class="topic-hashtag">#${art.topic || art.category || 'General'}</span>
              </div>
              <div style="display: flex; gap: 10px; margin-top: 8px; flex-wrap: wrap;">
                <a href="${art.url}" target="_blank" rel="noopener" class="telegram-bubble-link" style="margin-top: 0; padding: 4px 10px; background: rgba(36, 129, 204, 0.1); border-radius: 6px; display: inline-flex; align-items: center; gap: 4px; border: 1px solid rgba(36, 129, 204, 0.2); font-weight: 600; text-decoration: none;">
                  Open Site ↗
                </a>
                <span class="telegram-bubble-link offline-read-btn" style="margin-top: 0; padding: 4px 10px; background: rgba(60, 192, 92, 0.1); border-radius: 6px; display: inline-flex; align-items: center; gap: 4px; border: 1px solid rgba(60, 192, 92, 0.2); color: #3cc05c; cursor: pointer; font-weight: 700; text-decoration: none;" onclick="openOfflineReader('${art.url.replace(/'/g, "\\'")}', '${art.title.replace(/'/g, "\\'")}')">
                  Read Offline 📖
                </span>
              </div>
              <div class="telegram-bubble-meta">
                <span class="telegram-views">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="vertical-align: middle;">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                  </svg>
                  ${viewsCount.toLocaleString()}
                </span>
                <span>${timeText}</span>
              </div>
            </div>
            ${reactionsHtml}
          </div>
          <div class="telegram-message-actions" style="display: flex; flex-direction: column; gap: 8px; align-self: center;">
            ${actionBtnHtml}
            <button class="telegram-trash-btn" title="Ignore/Delete Post" onclick="ignorePost(this, '${art.url.replace(/'/g, "\\'")}')">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
    gridEl.insertAdjacentHTML('beforeend', messageHtml);
  });
}

function filterNews() {
  const searchInput = document.getElementById('news-search-input');
  const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
  
  const channelMap = {};
  allNewsArticles.forEach(art => {
    const info = getCleanChannelInfo(art);
    const channelId = info.channelId;
    const source = info.sourceName;
    const category = info.categoryName;
    
    let matches = true;
    if (query) {
      const titleMatch = (art.title || '').toLowerCase().includes(query);
      const descMatch = (art.description || '').toLowerCase().includes(query);
      const categoryMatch = (category || '').toLowerCase().includes(query);
      const sourceMatch = (source || '').toLowerCase().includes(query);
      matches = titleMatch || descMatch || categoryMatch || sourceMatch;
    }
    
    // Check if article matches the current active section
    const artSection = (art.section || 'Entertainment').toLowerCase();
    const matchesSection = (artSection === activeTab);
    
    if (matches && matchesSection) {
      if (!channelMap[channelId]) {
        channelMap[channelId] = {
          id: channelId,
          source: source,
          category: category,
          articles: []
        };
      }
      channelMap[channelId].articles.push(art);
    }
  });
  
  const filteredChannels = Object.values(channelMap);
  filteredChannels.forEach(ch => {
    // Item 4: render posts oldest -> newest (ascending) to mirror the desktop.
    ch.articles.sort((a, b) => {
      const dA = a.published ? new Date(a.published) : 0;
      const dB = b.published ? new Date(b.published) : 0;
      return dA - dB;
    });
    // Newest post is now last; use it for the channel preview/most-recent time.
    ch.latestArticle = ch.articles[ch.articles.length - 1];
    
    if (newsUnreadsMap[ch.id] === undefined) {
      const hash = Math.abs(hashCode(ch.id));
      newsUnreadsMap[ch.id] = (hash % 10 < 7) ? (hash % 4 + 1) : 0;
    }
  });
  
  filteredChannels.sort((a, b) => {
    const dA = a.latestArticle && a.latestArticle.published ? new Date(a.latestArticle.published) : 0;
    const dB = b.latestArticle && b.latestArticle.published ? new Date(b.latestArticle.published) : 0;
    return dB - dA;
  });
  
  const savedArticles = JSON.parse(localStorage.getItem('offlineboxd-saved-news') || '[]');
  const savedChannel = {
    id: 'SavedMessages',
    source: 'Saved Messages',
    category: 'Archive',
    articles: savedArticles,
    latestArticle: savedArticles[0] || null
  };
  
  const archivedArticles = window.archivedArticles || [];
  const archivedChannel = {
    id: 'ArchivedMessages',
    source: 'Archived Messages',
    category: 'Archive',
    articles: archivedArticles,
    latestArticle: archivedArticles[0] || null
  };
  
  const systemLogsChannel = {
    id: 'SystemLogs',
    source: 'App Logs',
    category: 'Timeline',
    articles: [],
    latestArticle: { title: "System activity log records", published: new Date().toISOString() }
  };
  
  newsUnreadsMap['SavedMessages'] = 0;
  newsUnreadsMap['ArchivedMessages'] = 0;
  newsUnreadsMap['SystemLogs'] = 0;
  
  filteredChannels.unshift(systemLogsChannel);
  filteredChannels.unshift(archivedChannel);
  filteredChannels.unshift(savedChannel);
  
  globalNewsChannels = filteredChannels;
  renderChannelsList(filteredChannels);
  
  if (filteredChannels.length > 0) {
    const exists = filteredChannels.find(ch => ch.id === selectedChannelId);
    if (exists) {
      selectNewsChannel(selectedChannelId);
    } else {
      selectNewsChannel(filteredChannels[0].id);
    }
  } else {
    const gridEl = document.getElementById('news-articles-grid');
    const emptyEl = document.getElementById('news-empty');
    if (gridEl) {
      const existingArticles = gridEl.querySelectorAll('.telegram-message-wrapper');
      existingArticles.forEach(el => el.remove());
    }
    if (emptyEl) emptyEl.classList.remove('hidden');
    
    const headerTitle = document.getElementById('telegram-header-title');
    const headerSubtitle = document.getElementById('telegram-header-subtitle');
    if (headerTitle) headerTitle.textContent = 'No channels';
    if (headerSubtitle) headerSubtitle.textContent = '0 channels match query';
  }
}

function loadAndRenderSystemLogs() {
  const gridEl = document.getElementById('news-articles-grid');
  if (!gridEl) return;
  
  gridEl.innerHTML = `
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 100px 20px; gap: 15px; margin: auto;">
      <div class="shimmer-placeholder" style="width: 50px; height: 50px; border-radius: 50%;"></div>
      <span style="font-size: 14px; color: var(--text-muted); font-weight: 500;">Aggregating system statistics and timelines...</span>
    </div>
  `;
  
  Promise.all([
    fetch('/api/news').then(res => res.json()),
    fetch('/api/activity_log').then(res => res.json())
  ]).then(([newsData, logs]) => {
    if (selectedChannelId !== 'SystemLogs') return;
    
    let html = `<div class="enriched-container">`;
    
    const totalFeeds = (newsData.custom_sources ? newsData.custom_sources.length : 0) + 6;
    const activeArticles = newsData.articles ? newsData.articles.length : 0;
    const bookmarkedCount = JSON.parse(localStorage.getItem('offlineboxd-saved-news') || '[]').length;
    
    html += `
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <h2 style="font-size: 18px; font-weight: 700; color: #fff; margin: 0;">Feed Aggregator Statistics</h2>
        <p style="font-size: 13px; color: var(--text-muted); margin: 0 0 10px 0;">Metrics on subscriptions, memory storage, and bookmarks.</p>
        
        <div class="analytics-grid">
          <div class="analytics-stat-card">
            <div class="analytics-stat-value">${totalFeeds}</div>
            <div class="analytics-stat-label">Total Channels</div>
          </div>
          <div class="analytics-stat-card">
            <div class="analytics-stat-value">${activeArticles}</div>
            <div class="analytics-stat-label">Stories Cached</div>
          </div>
          <div class="analytics-stat-card">
            <div class="analytics-stat-value">${bookmarkedCount}</div>
            <div class="analytics-stat-label">Saved Articles</div>
          </div>
          <div class="analytics-stat-card">
            <div class="analytics-stat-value" style="color: var(--accent-green);">Active</div>
            <div class="analytics-stat-label">Server Status</div>
          </div>
        </div>
      </div>
    `;
    
    html += `
      <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
        <h2 style="font-size: 16px; font-weight: 700; color: #fff; margin: 0;">System Log Records</h2>
        <p style="font-size: 13px; color: var(--text-muted); margin: 0 0 15px 0;">Recent actions, feed refreshes, cache cleanups, and additions.</p>
        
        <div class="timeline-list">
    `;
    
    if (logs.length === 0) {
      html += `<div style="color: var(--text-muted); font-size: 12px; padding: 10px 0;">No system logs available yet.</div>`;
    } else {
      logs.forEach(log => {
        const d = new Date(log.timestamp * 1000);
        const dateText = d.toLocaleString();
        const typeClass = (log.type && log.type.toLowerCase().includes('custom')) ? 'extension-type' : 'sync-type';
        const markerClass = (log.type && log.type.toLowerCase().includes('custom')) ? 'extension-marker' : 'sync-marker';
        html += `
          <div class="timeline-item">
            <div class="timeline-marker ${markerClass}"></div>
            <div class="timeline-item-meta">
              <span class="timeline-item-type ${typeClass}">${log.type || 'SYSTEM'}</span>
              <span>${dateText}</span>
            </div>
            <div class="timeline-item-desc">${log.details}</div>
          </div>
        `;
      });
    }
    
    html += `</div></div></div>`;
    gridEl.innerHTML = html;
  }).catch(err => {
    gridEl.innerHTML = `<div style="text-align: center; padding: 50px;">Failed to load system logs and stats: ${err.message || err}</div>`;
  });
}

function toggleTelegramFullscreen() {
  const isFullscreen = document.body.classList.toggle('telegram-fullscreen-mode');
  const btnFullscreen = document.getElementById('btn-toggle-fullscreen');
  const fullscreenSvg = document.getElementById('fullscreen-svg');
  
  if (fullscreenSvg && btnFullscreen) {
    if (isFullscreen) {
      fullscreenSvg.innerHTML = `
        <path d="M4 14h6v6m10-6h-6v6M4 10h6V4m10 6h-6V4"></path>
      `;
      btnFullscreen.title = "Exit Window Fullscreen";
    } else {
      fullscreenSvg.innerHTML = `
        <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
      `;
      btnFullscreen.title = "Toggle Window Fullscreen";
    }
  }
}

function initNewsEvents() {
  const searchInput = document.getElementById('news-search-input');
  const refreshBtn = document.getElementById('btn-refresh-news');
  const retryBtn = document.getElementById('btn-news-retry');
  const btnToggleFullscreen = document.getElementById('btn-toggle-fullscreen');
  
  if (searchInput) {
    searchInput.addEventListener('input', filterNews);
  }
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => loadNewsContent(true));
  }
  if (retryBtn) {
    retryBtn.addEventListener('click', () => loadNewsContent(true));
  }
  if (btnToggleFullscreen) {
    btnToggleFullscreen.addEventListener('click', toggleTelegramFullscreen);
  }
  
  initCustomNewsSources();
}

function renderCustomSourcesInModal() {
  const modalContainer = document.getElementById('custom-feeds-list-container');
  const settingsContainer = document.getElementById('custom-feeds-settings-list');
  const sources = window.customNewsSourcesList || [];
  
  const renderItemHtml = (src) => {
    const avatarHtml = getChannelAvatarHtml(src.name, 32);
    return `
      <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; width: 100%;">
        <div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex-grow: 1;">
          ${avatarHtml}
          <div style="display: flex; flex-direction: column; min-width: 0; text-align: left;">
            <span style="font-size: 13.5px; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${src.name}</span>
            <span style="font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 320px;">${src.url}</span>
          </div>
        </div>
        <button onclick="deleteCustomNewsSource('${src.name.replace(/'/g, "\\'")}')" style="background: transparent; border: none; color: #e0565b; cursor: pointer; padding: 6px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0;" onmouseover="this.style.background='rgba(224,86,91,0.1)';" onmouseout="this.style.background='transparent';">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </div>
    `;
  };
  
  const emptyHtml = `
    <div style="text-align: center; color: var(--text-muted); font-size: 13px; padding: 20px;">
      No custom feeds subscribed yet.
    </div>
  `;
  
  if (modalContainer) {
    if (sources.length === 0) {
      modalContainer.innerHTML = emptyHtml;
    } else {
      modalContainer.innerHTML = '';
      sources.forEach(src => {
        modalContainer.insertAdjacentHTML('beforeend', renderItemHtml(src));
      });
    }
  }
  
  if (settingsContainer) {
    if (sources.length === 0) {
      settingsContainer.innerHTML = emptyHtml;
    } else {
      settingsContainer.innerHTML = '';
      sources.forEach(src => {
        settingsContainer.insertAdjacentHTML('beforeend', renderItemHtml(src));
      });
    }
  }
}

window.deleteCustomNewsSource = function(name) {
  if (!confirm(`Are you sure you want to delete the custom feed "${name}"?`)) return;
  
  fetch('/api/news/sources/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: name })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      showToast(data.error, 'error');
    } else {
      showToast('Custom news feed deleted!', 'success');
      loadNewsContent(true);
    }
  })
  .catch(err => {
    showToast(err.message || err, 'error');
  });
};

window.openNewsSourcesModal = function() {
  const modal = document.getElementById('news-sources-modal');
  if (modal) {
    modal.classList.remove('hidden');
    renderCustomSourcesInModal();
  }
};

window.closeNewsSourcesModal = function() {
  const modal = document.getElementById('news-sources-modal');
  if (modal) {
    modal.classList.add('hidden');
    document.getElementById('add-feed-name').value = '';
    document.getElementById('add-feed-url').value = '';
    document.getElementById('add-feed-category').value = 'General';
    document.getElementById('btn-select-avatar').textContent = 'Choose File...';
    document.getElementById('modal-avatar-filename').textContent = 'No file selected';
    selectedAvatarBase64 = '';
    detectedIsRss = true;
    
    const addStatus = document.getElementById('add-feed-url-status');
    if (addStatus) addStatus.innerHTML = '';
    const addPreview = document.getElementById('add-feed-avatar-preview');
    if (addPreview) {
      addPreview.src = '';
      addPreview.style.display = 'none';
    }
  }
};

function analyzeFeedUrl(urlInputId, nameInputId, statusDivId, previewImgId) {
  const urlEl = document.getElementById(urlInputId);
  const nameEl = document.getElementById(nameInputId);
  const statusEl = document.getElementById(statusDivId);
  const previewEl = document.getElementById(previewImgId);
  
  if (!urlEl) return;
  const urlVal = urlEl.value.trim();
  if (!urlVal) return;
  
  if (!urlVal.includes('.') || urlVal.length < 5) return;
  
  if (statusEl) {
    statusEl.innerHTML = `<span style="color: var(--accent-orange); display: flex; align-items: center; gap: 6px;">
      <svg class="spinner" width="12" height="12" viewBox="0 0 50 50" style="animation: spin 1s linear infinite; display: inline-block;">
        <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="5" stroke-dasharray="80, 200" stroke-dashoffset="0"></circle>
      </svg>
      Analyzing feed source... detecting RSS feed, site name & logo
    </span>`;
  }
  
  fetch('/api/news/sources/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: urlVal })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      if (statusEl) {
        statusEl.innerHTML = `<span style="color: #e0565b;">⚠️ Could not auto-detect details (${data.error}). Enter manually.</span>`;
      }
    } else if (data.success) {
      if (nameEl) {
        nameEl.value = data.name;
      }
      
      if (data.feed_url) {
        urlEl.value = data.feed_url;
      }
      
      detectedIsRss = data.is_rss;
      
      if (data.logo_base64) {
        selectedAvatarBase64 = data.logo_base64;
        if (previewEl) {
          previewEl.src = data.logo_base64;
          previewEl.style.display = 'block';
          previewEl.style.marginRight = '8px';
        }
        
        const modalLabel = document.getElementById('btn-select-avatar');
        const modalFilename = document.getElementById('modal-avatar-filename');
        const settingsLabel = document.getElementById('btn-settings-select-avatar');
        const settingsFilename = document.getElementById('settings-avatar-filename');
        
        if (urlInputId.includes('settings')) {
          if (settingsLabel) settingsLabel.textContent = 'Change file...';
          if (settingsFilename) settingsFilename.textContent = 'Auto-fetched Logo';
        } else {
          if (modalLabel) modalLabel.textContent = 'Change file...';
          if (modalFilename) modalFilename.textContent = 'Auto-fetched Logo';
        }
      }
      
      if (statusEl) {
        const typeLabel = data.is_rss ? 'RSS Feed' : 'HTML Index Scraper';
        statusEl.innerHTML = `<span style="color: #2ea44f; font-weight: 700;">✅ Connected! Detected ${typeLabel} & high-res logo.</span>`;
      }
    }
  })
  .catch(err => {
    if (statusEl) {
      statusEl.innerHTML = `<span style="color: #e0565b;">⚠️ Connection error. You can fill details manually.</span>`;
    }
  });
}

function initCustomNewsSources() {
  const btnManage = document.getElementById('btn-manage-news-sources');
  const btnCloseShortcut = document.getElementById('btn-close-news-sources-modal');
  
  // Shortcut modal handlers
  if (btnManage) {
    btnManage.addEventListener('click', window.openNewsSourcesModal);
  }
  if (btnCloseShortcut) {
    btnCloseShortcut.addEventListener('click', window.closeNewsSourcesModal);
  }
  
  // Avatar upload file selectors
  const modalAvatarInput = document.getElementById('add-feed-avatar');
  const settingsAvatarInput = document.getElementById('settings-feed-avatar');
  
  const setupAvatarFileReader = (inputEl, labelEl, filenameEl) => {
    if (inputEl && labelEl) {
      inputEl.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        labelEl.textContent = 'Change file...';
        if (filenameEl) filenameEl.textContent = file.name;
        
        const reader = new FileReader();
        reader.onload = function(evt) {
          selectedAvatarBase64 = evt.target.result;
        };
        reader.readAsDataURL(file);
      });
    }
  };
  
  setupAvatarFileReader(
    modalAvatarInput, 
    document.getElementById('btn-select-avatar'), 
    document.getElementById('modal-avatar-filename')
  );
  
  setupAvatarFileReader(
    settingsAvatarInput, 
    document.getElementById('btn-settings-select-avatar'), 
    document.getElementById('settings-avatar-filename')
  );

  // Form submit triggers
  const submitFeedSource = (nameId, urlId, catId, btnEl) => {
    const name = document.getElementById(nameId).value.trim();
    const url = document.getElementById(urlId).value.trim();
    const category = document.getElementById(catId).value;
    
    const prefix = nameId.split('-')[0];
    const sectionId = `${prefix}-feed-section`;
    const sectionEl = document.getElementById(sectionId);
    const section = sectionEl ? sectionEl.value : 'Entertainment';
    
    if (!name || !url) {
      showToast('Please fill in both Feed Name and URL!', 'error');
      return;
    }
    
    btnEl.disabled = true;
    btnEl.textContent = 'ADDING FEED...';
    
    fetch('/api/news/sources/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        url: url,
        category: category,
        section: section,
        avatar_base64: selectedAvatarBase64,
        is_rss: detectedIsRss
      })
    })
    .then(res => res.json())
    .then(data => {
      btnEl.disabled = false;
      btnEl.textContent = btnEl.id.includes('settings') ? 'ADD CUSTOM FEED' : 'ADD FEED SOURCE';
      
      if (data.error) {
        showToast(data.error, 'error');
      } else {
        showToast('Custom news feed added successfully!', 'success');
        
        // Reset form fields
        document.getElementById(nameId).value = '';
        document.getElementById(urlId).value = '';
        document.getElementById(catId).value = 'General';
        if (sectionEl) sectionEl.value = 'Entertainment';
        selectedAvatarBase64 = '';
        detectedIsRss = true;
        
        const fileLabelModal = document.getElementById('btn-select-avatar');
        const fnModal = document.getElementById('modal-avatar-filename');
        if (fileLabelModal) fileLabelModal.textContent = 'Choose File...';
        if (fnModal) fnModal.textContent = 'No file selected';

        const fileLabelSettings = document.getElementById('btn-settings-select-avatar');
        const fnSettings = document.getElementById('settings-avatar-filename');
        if (fileLabelSettings) fileLabelSettings.textContent = 'Choose File...';
        if (fnSettings) fnSettings.textContent = 'No file selected';

        const addPreview = document.getElementById('add-feed-avatar-preview');
        if (addPreview) { addPreview.src = ''; addPreview.style.display = 'none'; }
        const settingsPreview = document.getElementById('settings-feed-avatar-preview');
        if (settingsPreview) { settingsPreview.src = ''; settingsPreview.style.display = 'none'; }

        const addStatus = document.getElementById('add-feed-url-status');
        if (addStatus) addStatus.innerHTML = '';
        const settingsStatus = document.getElementById('settings-feed-url-status');
        if (settingsStatus) settingsStatus.innerHTML = '';

        // Close shortcut modal if open
        window.closeNewsSourcesModal();
        
        loadNewsContent(true);
      }
    })
    .catch(err => {
      btnEl.disabled = false;
      btnEl.textContent = btnEl.id.includes('settings') ? 'ADD CUSTOM FEED' : 'ADD FEED SOURCE';
      showToast(err.message || err, 'error');
    });
  };

  const setupUrlAutodetect = (urlId, nameId, statusId, previewId) => {
    const urlEl = document.getElementById(urlId);
    if (urlEl) {
      urlEl.addEventListener('blur', () => {
        analyzeFeedUrl(urlId, nameId, statusId, previewId);
      });
      urlEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          analyzeFeedUrl(urlId, nameId, statusId, previewId);
        }
      });
    }
  };
  
  setupUrlAutodetect('add-feed-url', 'add-feed-name', 'add-feed-url-status', 'add-feed-avatar-preview');
  setupUrlAutodetect('settings-feed-url', 'settings-feed-name', 'settings-feed-url-status', 'settings-feed-avatar-preview');

  const btnSubmitModal = document.getElementById('btn-submit-new-feed');
  if (btnSubmitModal) {
    btnSubmitModal.addEventListener('click', () => {
      submitFeedSource('add-feed-name', 'add-feed-url', 'add-feed-category', btnSubmitModal);
    });
  }

  const btnSubmitSettings = document.getElementById('btn-settings-submit-feed');
  if (btnSubmitSettings) {
    btnSubmitSettings.addEventListener('click', () => {
      submitFeedSource('settings-feed-name', 'settings-feed-url', 'settings-feed-category', btnSubmitSettings);
    });
  }
}

// Fullscreen Offline Article Reader
window.openOfflineReader = function(url, title) {
  const readerModal = document.getElementById('article-reader');
  const readerTitle = document.getElementById('reader-title-content');
  const readerBody = document.getElementById('reader-body-content');
  
  if (!readerModal || !readerTitle || !readerBody) return;
  
  readerTitle.textContent = title;
  readerBody.innerHTML = `
    <div class="skeleton-reader-body" style="display: flex; flex-direction: column; gap: 20px; width: 100%; max-width: 720px; margin: auto; padding: 20px 0;">
      <div class="shimmer-placeholder" style="height: 38px; width: 85%; border-radius: 6px; margin-bottom: 15px;"></div>
      <div class="shimmer-placeholder" style="height: 320px; width: 100%; border-radius: 8px; margin-bottom: 25px;"></div>
      <div class="shimmer-placeholder" style="height: 16px; width: 100%; border-radius: 4px; margin-bottom: 8px;"></div>
      <div class="shimmer-placeholder" style="height: 16px; width: 95%; border-radius: 4px; margin-bottom: 8px;"></div>
      <div class="shimmer-placeholder" style="height: 16px; width: 98%; border-radius: 4px; margin-bottom: 8px;"></div>
      <div class="shimmer-placeholder" style="height: 16px; width: 80%; border-radius: 4px; margin-bottom: 25px;"></div>
      <div class="shimmer-placeholder" style="height: 16px; width: 95%; border-radius: 4px; margin-bottom: 8px;"></div>
      <div class="shimmer-placeholder" style="height: 16px; width: 92%; border-radius: 4px; margin-bottom: 8px;"></div>
      <div class="shimmer-placeholder" style="height: 16px; width: 70%; border-radius: 4px;"></div>
    </div>
  `;
  
  readerModal.classList.add('active');
  
  fetch(`/api/news/article?url=${encodeURIComponent(url)}`)
    .then(res => {
      if (!res.ok) throw new Error("Could not download article. You might be offline.");
      return res.json();
    })
    .then(data => {
      if (data.error) throw new Error(data.error);
      
      readerTitle.textContent = data.title || title;
      
      if (!data.blocks || data.blocks.length === 0) {
        readerBody.innerHTML = `<p style="text-align: center; color: var(--text-muted);">No readable text blocks parsed. Try opening the website link directly.</p>`;
        return;
      }
      
      let bodyHtml = `
        <div class="reader-meta-header">
          <span class="reader-meta-badge">Offline View</span>
          <a href="${url}" target="_blank" rel="noopener" class="reader-original-link">
            <span>Open Original Article</span>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
          </a>
        </div>
      `;
      data.blocks.forEach(block => {
        if (block.type === 'p') {
          bodyHtml += `<p>${block.content}</p>`;
        } else if (block.type === 'h') {
          bodyHtml += `<h${block.level || 2}>${block.content}</h${block.level || 2}>`;
        } else if (block.type === 'img') {
          bodyHtml += `<img src="${block.content}" onerror="this.style.display='none';" />`;
        } else if (block.type === 'quote') {
          bodyHtml += `<blockquote>${block.content}</blockquote>`;
        }
      });
      readerBody.innerHTML = bodyHtml;
    })
    .catch(err => {
      readerBody.innerHTML = `
        <div style="text-align: center; padding: 40px 20px;">
          <span style="font-size: 32px; display: block; margin-bottom: 15px;">⚠️</span>
          <h4 style="color: #fff; margin-bottom: 8px;">Offline Reader Error</h4>
          <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 20px;">${err.message || err}</p>
          <a href="${url}" target="_blank" rel="noopener" class="btn btn-primary" style="display: inline-block; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 13px;">
            Open Website ↗
          </a>
        </div>
      `;
    });
};

window.closeOfflineReader = function() {
  const readerModal = document.getElementById('article-reader');
  if (readerModal) {
    readerModal.classList.remove('active');
  }
};

window.ignorePost = function(buttonEl, url) {
  // Find the message wrapper parent
  const wrapper = buttonEl.closest('.telegram-message-wrapper');
  if (wrapper) {
    // Add a nice fade-out and slide-up animation
    wrapper.style.transition = "all 0.4s ease-out";
    wrapper.style.opacity = "0";
    wrapper.style.transform = "translateY(-20px)";
    wrapper.style.maxHeight = wrapper.offsetHeight + "px";
    wrapper.style.overflow = "hidden";
    
    setTimeout(() => {
      wrapper.style.maxHeight = "0";
      wrapper.style.padding = "0";
      wrapper.style.margin = "0";
      setTimeout(() => {
        wrapper.remove();
      }, 300);
    }, 100);
  }
  
  // Call the backend API to record the ignore request
  fetch('/api/news/ignore', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url: url })
  })
  .then(res => {
    if (!res.ok) {
      console.error("Failed to ignore post on the server.");
    }
  })
  .catch(err => {
    console.error("Error sending ignore request:", err);
  });
};

// Theme toggle
function initThemeToggle() {
  const btnToggle = document.getElementById('btn-theme-toggle');
  if (!btnToggle) return;
  
  const toggleIcon = document.getElementById('theme-toggle-icon');
  const toggleText = document.getElementById('theme-toggle-text');
  const readerOverlay = document.getElementById('article-reader');
  
  const savedTheme = localStorage.getItem('offlineboxd-news-theme') || 'dark';
  if (savedTheme === 'parchment') {
    document.body.classList.add('parchment-theme');
    if (readerOverlay) readerOverlay.classList.add('parchment-theme');
    if (toggleText) toggleText.textContent = 'Dark Mode';
    if (toggleIcon) toggleIcon.style.filter = 'none';
    btnToggle.style.background = 'rgba(0,0,0,0.04)';
    btnToggle.style.borderColor = 'rgba(0,0,0,0.1)';
    btnToggle.style.color = '#1d1916';
  } else {
    document.body.classList.remove('parchment-theme');
    if (readerOverlay) readerOverlay.classList.remove('parchment-theme');
    if (toggleText) toggleText.textContent = 'Parchment Mode';
    if (toggleIcon) toggleIcon.style.filter = 'invert(1)';
    btnToggle.style.background = 'rgba(255,255,255,0.03)';
    btnToggle.style.borderColor = 'rgba(255,255,255,0.08)';
    btnToggle.style.color = '#fff';
  }
  
  btnToggle.addEventListener('click', () => {
    const isParchment = document.body.classList.contains('parchment-theme');
    if (isParchment) {
      document.body.classList.remove('parchment-theme');
      if (readerOverlay) readerOverlay.classList.remove('parchment-theme');
      if (toggleText) toggleText.textContent = 'Parchment Mode';
      if (toggleIcon) toggleIcon.style.filter = 'invert(1)';
      btnToggle.style.background = 'rgba(255,255,255,0.03)';
      btnToggle.style.borderColor = 'rgba(255,255,255,0.08)';
      btnToggle.style.color = '#fff';
      localStorage.setItem('offlineboxd-news-theme', 'dark');
      showToast("Switched to dark mode");
    } else {
      document.body.classList.add('parchment-theme');
      if (readerOverlay) readerOverlay.classList.add('parchment-theme');
      if (toggleText) toggleText.textContent = 'Dark Mode';
      if (toggleIcon) toggleIcon.style.filter = 'none';
      btnToggle.style.background = 'rgba(0,0,0,0.04)';
      btnToggle.style.borderColor = 'rgba(0,0,0,0.1)';
      btnToggle.style.color = '#1d1916';
      localStorage.setItem('offlineboxd-news-theme', 'parchment');
      showToast("Switched to parchment mode");
    }
  });
}

// Clear system vault cache
function clearCache() {
  if (!confirm("Are you sure you want to clear the offline cached articles and system activity logs?")) return;
  
  const btn = document.getElementById('btn-clear-cache');
  btn.disabled = true;
  btn.textContent = 'CLEARING...';
  
  fetch('/api/cache/clear', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      btn.disabled = false;
      btn.textContent = 'CLEAR CACHE';
      if (data.success) {
        showToast(`Cleared cache! Deleted ${data.deleted_count} offline articles.`, 'success');
        if (selectedChannelId === 'SystemLogs') {
          loadAndRenderSystemLogs();
        }
      } else {
        showToast(data.error || 'Failed to clear cache', 'error');
      }
    })
    .catch(err => {
      btn.disabled = false;
      btn.textContent = 'CLEAR CACHE';
      showToast(err.message || err, 'error');
    });
}

// Reset Telegram history log
function resetTelegramHistory() {
  if (!confirm("Are you sure you want to clear the Telegram forwarding history? This allows already sent articles to be sent again.")) return;
  
  const btn = document.getElementById('btn-reset-tg-history');
  btn.disabled = true;
  btn.textContent = 'RESETTING...';
  
  fetch('/api/telegram/reset_history', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      btn.disabled = false;
      btn.textContent = 'RESET HISTORY';
      if (data.success) {
        showToast('Successfully reset Telegram forwarding history.', 'success');
        if (selectedChannelId === 'SystemLogs') {
          loadAndRenderSystemLogs();
        }
      } else {
        showToast(data.error || 'Failed to reset history', 'error');
      }
    })
    .catch(err => {
      btn.disabled = false;
      btn.textContent = 'RESET HISTORY';
      showToast(err.message || err, 'error');
    });
}

// Sync Connection Indicator Helper
function setIndicator(online) {
  if (!syncIndicator) return;
  if (online) {
    syncIndicator.style.background = 'var(--accent-green)';
    syncIndicator.style.boxShadow = '0 0 8px var(--accent-green)';
    syncIndicator.title = 'Online - Connected to Aggregator Server';
  } else {
    syncIndicator.style.background = '#fa3232';
    syncIndicator.style.boxShadow = '0 0 8px #fa3232';
    syncIndicator.title = 'Offline - Server Connection Lost';
  }
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  if (navTabEntertainment) navTabEntertainment.addEventListener('click', () => showSectionTab('entertainment'));
  if (navTabSports) navTabSports.addEventListener('click', () => showSectionTab('sports'));
  if (navTabTechnology) navTabTechnology.addEventListener('click', () => showSectionTab('technology'));
  if (navTabSettings) navTabSettings.addEventListener('click', showSettingsTab);
  
  initNewsEvents();
  initThemeToggle();
  
  const btnClearCache = document.getElementById('btn-clear-cache');
  if (btnClearCache) {
    btnClearCache.addEventListener('click', clearCache);
  }

  const btnResetTgHistory = document.getElementById('btn-reset-tg-history');
  if (btnResetTgHistory) {
    btnResetTgHistory.addEventListener('click', resetTelegramHistory);
  }
  
  // Close modals or exit fullscreen on Escape keypress
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (document.body.classList.contains('telegram-fullscreen-mode')) {
        toggleTelegramFullscreen();
      } else {
        if (typeof window.closeOfflineReader === 'function') {
          window.closeOfflineReader();
        }
        if (typeof window.closeNewsSourcesModal === 'function') {
          window.closeNewsSourcesModal();
        }
      }
    }
  });

  // Close custom sources modal when clicking outside of the modal card
  const modalOverlay = document.getElementById('news-sources-modal');
  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) {
        window.closeNewsSourcesModal();
      }
    });
  }
  
  // Set default view
  showNewsTab();
  
  // Initialize Telegram settings and action listener
  initTelegramSettings();
  
  const btnSendToTg = document.getElementById('btn-send-to-tg');
  if (btnSendToTg) {
    btnSendToTg.addEventListener('click', () => {
      if (!selectedChannelId) return;
      const ch = globalNewsChannels.find(c => c.id === selectedChannelId);
      if (!ch) return;
      forwardChannelToTelegram(ch);
    });
  }
  
  const btnSendAllToTg = document.getElementById('btn-send-all-to-tg');
  if (btnSendAllToTg) {
    btnSendAllToTg.addEventListener('click', () => {
      forwardAllChannelsToTelegram();
    });
  }
});

function initTelegramSettings() {
  const btnSave = document.getElementById('btn-save-tg-settings');
  const inputBotToken = document.getElementById('tg-bot-token');
  const inputChatIdEnt = document.getElementById('tg-chat-id-entertainment');
  const inputChatIdSports = document.getElementById('tg-chat-id-sports');
  const inputChatIdTech = document.getElementById('tg-chat-id-technology');
  
  if (!btnSave) return;
  
  // Load current settings from backend
  fetch('/api/telegram/config')
    .then(res => {
      if (res.ok) return res.json();
      throw new Error("Failed to load Telegram configuration.");
    })
    .then(data => {
      if (data) {
        currentTelegramConfig = data;
        if (data.bot_token) inputBotToken.value = data.bot_token;
        if (data.default_chat_id) inputChatIdEnt.value = data.default_chat_id;
        if (data.sports_chat_id) inputChatIdSports.value = data.sports_chat_id;
        if (data.technology_chat_id) inputChatIdTech.value = data.technology_chat_id;
        renderTelegramChannelSettings(data.channel_threads || {});
      }
    })
    .catch(err => {
      console.warn("Could not load Telegram settings:", err.message);
    });
    
  // Save settings on click
  btnSave.addEventListener('click', () => {
    const channelThreads = {};
    document.querySelectorAll('.tg-channel-thread-input').forEach(input => {
      const channel = input.getAttribute('data-channel');
      const val = input.value.trim();
      if (val) {
        channelThreads[channel] = val;
      }
    });

    const config = {
      bot_token: inputBotToken.value.trim(),
      default_chat_id: inputChatIdEnt.value.trim(),
      sports_chat_id: inputChatIdSports.value.trim(),
      technology_chat_id: inputChatIdTech.value.trim(),
      channel_threads: channelThreads
    };
    
    btnSave.disabled = true;
    btnSave.textContent = "Saving...";
    
    fetch('/api/telegram/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    .then(res => res.json())
    .then(data => {
      btnSave.disabled = false;
      btnSave.textContent = "Save Telegram Settings";
      if (data.status === 'success') {
        currentTelegramConfig = config;
        showToast("Telegram Settings saved successfully!", "success");
      } else {
        showToast(`Error: ${data.error || 'Failed to save settings'}`, "error");
      }
    })
    .catch(err => {
      btnSave.disabled = false;
      btnSave.textContent = "Save Telegram Settings";
      showToast(`Error saving settings: ${err.message || err}`, "error");
    });
  });
}

let currentTelegramConfig = null;

function refreshTelegramChannelsList() {
  if (currentTelegramConfig) {
    renderTelegramChannelSettings(currentTelegramConfig.channel_threads || {});
  } else {
    fetch('/api/telegram/config')
      .then(res => res.json())
      .then(data => {
        currentTelegramConfig = data;
        renderTelegramChannelSettings(data.channel_threads || {});
      })
      .catch(err => {
        console.warn("Could not load Telegram settings:", err);
        renderTelegramChannelSettings({});
      });
  }
}

function renderTelegramChannelSettings(savedThreads = {}) {
  const container = document.getElementById('tg-channel-threads-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  // Filter out system channels
  const activeFeeds = globalNewsChannels.filter(c => c.id !== 'SavedMessages' && c.id !== 'ArchivedMessages' && c.id !== 'SystemLogs');
  
  if (activeFeeds.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted); font-size: 12px; font-style: italic;">No active feeds loaded yet. Refresh your feeds to see them here.</p>';
    return;
  }
  
  let html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; background: rgba(255,255,255,0.01);">';
  activeFeeds.forEach(ch => {
    const threadId = savedThreads[ch.source] || '';
    html += `
      <div>
        <label style="display: block; font-size: 11px; font-weight: 700; color: var(--text-secondary); margin-bottom: 6px; text-transform: uppercase; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;" title="${ch.source}">
          ${ch.source} Thread ID
        </label>
        <input type="text" class="tg-channel-thread-input" data-channel="${ch.source}" value="${threadId}" placeholder="e.g. 12" style="width: 100%; padding: 8px 12px; border-radius: 6px; background: #0d1117; border: 1px solid rgba(255,255,255,0.08); color: #fff; outline: none; font-size: 13px;">
      </div>
    `;
  });
  html += '</div>';
  container.innerHTML = html;
}

function forwardChannelToTelegram(ch) {
  const btnSend = document.getElementById('btn-send-to-tg');
  if (!btnSend) return;
  
  const originalHtml = btnSend.innerHTML;
  btnSend.disabled = true;
  btnSend.style.opacity = '0.5';
  btnSend.title = "Forwarding to Telegram...";
  
  showToast(`Forwarding news from ${ch.source} to Telegram...`, "info");
  
  fetch('/api/telegram/send_channel', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      channel_name: ch.source,
      articles: ch.articles.map(art => ({
        title: art.title,
        description: art.description || "",
        url: art.url,
        thumbnail: art.thumbnail || "",
        category: art.topic || art.category || "",
        section: art.section || "Entertainment"
      }))
    })
  })
  .then(res => res.json())
  .then(data => {
    btnSend.disabled = false;
    btnSend.style.opacity = '';
    btnSend.innerHTML = originalHtml;
    btnSend.title = "Forward Channel to Telegram";
    
    if (data.status === 'success') {
      if (data.all_skipped) {
        showToast(`No new posts to send. (${data.already_sent_count} already forwarded)`, "info");
      } else {
        showToast(`Sending ${data.to_send_count} new posts (${data.already_sent_count} skipped). Check "App Logs".`, "success");
      }
    } else {
      showToast(`Error: ${data.error || 'Failed to send to Telegram'}`, "error");
    }
  })
  .catch(err => {
    btnSend.disabled = false;
    btnSend.style.opacity = '';
    btnSend.innerHTML = originalHtml;
    btnSend.title = "Forward Channel to Telegram";
    showToast(`Error sending request: ${err.message || err}`, "error");
  });
}

function forwardAllChannelsToTelegram() {
  const activeFeeds = globalNewsChannels.filter(c => c.id !== 'SavedMessages' && c.id !== 'ArchivedMessages' && c.id !== 'SystemLogs' && c.articles && c.articles.length > 0);
  if (activeFeeds.length === 0) {
    showToast("No channels to forward.", "info");
    return;
  }
  
  if (!confirm(`Are you sure you want to forward articles from ALL ${activeFeeds.length} channels to Telegram? This will process new posts in the background.`)) {
    return;
  }
  
  const btnSendAll = document.getElementById('btn-send-all-to-tg');
  let originalHtml = '';
  if (btnSendAll) {
    originalHtml = btnSendAll.innerHTML;
    btnSendAll.disabled = true;
    btnSendAll.style.opacity = '0.5';
    btnSendAll.title = "Forwarding all channels...";
  }
  
  showToast(`Starting background forward for all ${activeFeeds.length} channels...`, "info");
  
  let successCount = 0;
  let skippedCount = 0;
  let totalToSendCount = 0;
  let errorMessages = [];
  
  const promises = activeFeeds.map(ch => {
    return fetch('/api/telegram/send_channel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        channel_name: ch.source,
        articles: ch.articles.map(art => ({
          title: art.title,
          description: art.description || "",
          url: art.url,
          thumbnail: art.thumbnail || "",
          category: art.topic || art.category || "",
          section: art.section || "Entertainment"
        }))
      })
    })
    .then(res => {
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      return res.json();
    })
    .then(data => {
      if (data.status === 'success') {
        successCount++;
        totalToSendCount += data.to_send_count || 0;
        skippedCount += data.already_sent_count || 0;
      } else {
        errorMessages.push(`${ch.source}: ${data.error || 'Unknown error'}`);
      }
    })
    .catch(err => {
      errorMessages.push(`${ch.source}: ${err.message || err}`);
    });
  });
  
  Promise.all(promises)
    .then(() => {
      if (btnSendAll) {
        btnSendAll.disabled = false;
        btnSendAll.style.opacity = '';
        btnSendAll.innerHTML = originalHtml;
        btnSendAll.title = "Forward All Channels to Telegram";
      }
      
      if (errorMessages.length === 0) {
        if (totalToSendCount === 0) {
          showToast(`All ${activeFeeds.length} channels up-to-date. (${skippedCount} posts already forwarded)`, "success");
        } else {
          showToast(`Started forwarding ${totalToSendCount} new posts across all channels in background. Check "App Logs".`, "success");
        }
      } else if (successCount > 0) {
        showToast(`Forwarded some channels. Errors in ${errorMessages.length} channels. Check "App Logs".`, "warning");
      } else {
        showToast(`Failed to forward channels. Errors: ${errorMessages.slice(0, 2).join(', ')}`, "error");
      }
      
      if (selectedChannelId === 'SystemLogs') {
        setTimeout(loadAndRenderSystemLogs, 1500);
      }
    });
}

/* ==========================================================================
   OFFLINEFEED — per-post deep link (ADDITIVE; reuses window.openOfflineReader)
   --------------------------------------------------------------------------
   Lets the PySide6 desktop app open ONE article in this existing offline
   viewer by opening a normal browser URL:
       http://127.0.0.1:8080/?reader=<encoded article url>&title=<encoded title>
   No backend route is added. No existing code is modified. This block only
   reads the query string and calls the viewer's existing reader function.
   Paste this at the VERY END of offline_viewer/app.js.
   ========================================================================== */
(function () {
  function openReaderFromQuery() {
    try {
      var params = new URLSearchParams(window.location.search || '');
      var readerUrl = params.get('reader');
      if (!readerUrl) return;
      var title = params.get('title') || '';
      if (typeof window.openOfflineReader === 'function') {
        window.openOfflineReader(readerUrl, title);
      } else {
        // app.js may still be initializing — retry shortly.
        setTimeout(openReaderFromQuery, 250);
      }
    } catch (e) {
      console.error('OfflineFeed deep-link reader failed:', e);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', openReaderFromQuery);
  } else {
    openReaderFromQuery();
  }
})();

