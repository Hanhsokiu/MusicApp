const API_URL = "http://127.0.0.1:5000";

const user = JSON.parse(localStorage.getItem("user"));
const player = document.getElementById("player");
const mainPlayBtn = document.getElementById("mainPlayBtn");
const progressFill = document.getElementById("progressFill");
const progressWrapper = document.getElementById("progressWrapper");
const list = document.getElementById("list");
const viewTitle = document.getElementById("viewTitle");
const playlistNav = document.getElementById("playlistNav");
const playerImage = document.getElementById("p-img");
const playerImageWrapper = document.getElementById("p-img-wrapper");

let currentSongs = [];
let currentIndex = -1;
let currentView = "all";
let selectedPlaylistId = null;
let selectedPlaylistName = "";
let editId = null;

if (!user) {
  window.location.href = "/login";
}

function fetchJson(url, options = {}) {
  return fetch(url, {
    cache: "no-store",
    ...options,
    headers: {
      ...(options.headers || {})
    }
  }).then((res) => res.json());
}

function escapeHtml(text) {
  return String(text ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function escapeJsText(text) {
  return String(text ?? "")
    .replace(/\\/g, "\\\\")
    .replace(/`/g, "\\`");
}

function setActiveSidebar(buttonId) {
  document.querySelectorAll(".sidebar .nav-btn").forEach((btn) => btn.classList.remove("active"));
  if (!buttonId) return;
  const activeButton = document.getElementById(buttonId);
  if (activeButton) {
    activeButton.classList.add("active");
  }
}

function setViewTitle(title) {
  viewTitle.innerText = title;
}

function setListMode(mode) {
  list.classList.toggle("playlist-song-list", mode === "playlist");
}

function setPlayerArtwork(imageUrl) {
  if (!imageUrl) {
    playerImage.removeAttribute("src");
    playerImageWrapper.classList.add("is-placeholder");
    return;
  }

  playerImageWrapper.classList.remove("is-placeholder");
  playerImage.src = API_URL + imageUrl;
}

playerImage.addEventListener("error", () => {
  playerImage.removeAttribute("src");
  playerImageWrapper.classList.add("is-placeholder");
});

function renderSongs(data, mode = "grid") {
  list.innerHTML = "";
  currentSongs = data;
  currentIndex = data.length ? 0 : -1;
  setListMode(mode);

  if (!data.length) {
    list.innerHTML = `<div class="empty-state">${mode === "playlist" ? "Playlist này chưa có bài hát." : "Không có bài hát để hiển thị."}</div>`;
    return;
  }

  data.forEach((song, index) => {
    const item = document.createElement("div");
    item.className = mode === "playlist" ? "playlist-song-row" : "song-card";

    if (mode === "playlist") {
      item.innerHTML = `
        <div class="playlist-song-main" onclick="playByIndex(${index})">
          <div class="playlist-song-index">${index + 1}</div>
          <div class="playlist-song-cover">
            ${song.imageUrl
              ? `<img src="${API_URL + song.imageUrl}" alt="${escapeHtml(song.title)}">`
              : `<i class="fas fa-music"></i>`}
          </div>
          <div class="playlist-song-info">
            <div class="playlist-song-title">${escapeHtml(song.title)}</div>
            <div class="playlist-song-artist">${escapeHtml(song.artist)}</div>
          </div>
        </div>
        <div class="playlist-song-actions">
          <button class="row-icon-btn" onclick="event.stopPropagation(); playByIndex(${index})">
            <i class="fas fa-play"></i>
          </button>
          <button class="fav-btn ${song.isFavorite ? "active" : ""}" onclick="event.stopPropagation(); toggleFavorite(${song.id})">
            <i class="${song.isFavorite ? "fas" : "far"} fa-heart"></i>
          </button>
        </div>
      `;
    } else {
      item.innerHTML = `
        <div class="song-cover">
          ${song.imageUrl
            ? `<img src="${API_URL + song.imageUrl}" style="width:100%; height:100%; object-fit:cover; border-radius:6px;" alt="${escapeHtml(song.title)}">`
            : `<i class="fas fa-music"></i>`}
        </div>
        <div class="song-title">${escapeHtml(song.title)}</div>
        <div class="song-artist">${escapeHtml(song.artist)}</div>

        <button class="play-btn-circle" onclick="playByIndex(${index})">
          <i class="fas fa-play"></i>
        </button>

        <div class="card-bottom-actions">
          <button class="fav-btn ${song.isFavorite ? "active" : ""}" onclick="toggleFavorite(${song.id})">
            <i class="${song.isFavorite ? "fas" : "far"} fa-heart"></i>
          </button>
          <button class="fav-btn" onclick="addSongToPlaylist(${song.id})" title="Thêm vào playlist">
            <i class="fas fa-plus"></i>
          </button>
        </div>

        ${user.role === "admin" ? `
          <div class="song-actions">
            <button class="btn edit-btn" onclick="openEdit(${song.id}, \`${escapeJsText(song.title)}\`, \`${escapeJsText(song.artist)}\`)">
              <i class="fas fa-pen"></i>
            </button>
            <button class="btn delete-btn" onclick="deleteSong(${song.id})">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        ` : ""}
      `;
    }

    list.appendChild(item);
  });
}

function playByIndex(index) {
  if (index < 0 || index >= currentSongs.length) return;

  currentIndex = index;
  const song = currentSongs[currentIndex];
  player.src = API_URL + song.fileUrl;
  player.play();

  document.getElementById("p-title").innerText = song.title;
  document.getElementById("p-artist").innerText = song.artist;
  setPlayerArtwork(song.imageUrl);
  mainPlayBtn.innerHTML = '<i class="fas fa-pause"></i>';

  fetchJson(API_URL + "/api/recent", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId: user.id, songId: song.id })
  });
}

function togglePlay() {
  if (!player.src) return;
  if (player.paused) {
    player.play();
    mainPlayBtn.innerHTML = '<i class="fas fa-pause"></i>';
  } else {
    player.pause();
    mainPlayBtn.innerHTML = '<i class="fas fa-play"></i>';
  }
}

function nextSong() {
  if (!currentSongs.length) return;
  let next = currentIndex + 1;
  if (next >= currentSongs.length) next = 0;
  playByIndex(next);
}

function prevSong() {
  if (!currentSongs.length) return;
  let prev = currentIndex - 1;
  if (prev < 0) prev = currentSongs.length - 1;
  playByIndex(prev);
}

function replaySong() {
  player.currentTime = 0;
  player.play();
  mainPlayBtn.innerHTML = '<i class="fas fa-pause"></i>';
}

player.onended = () => {
  nextSong();
};

player.ontimeupdate = () => {
  if (!player.duration) return;
  const pct = (player.currentTime / player.duration) * 100;
  progressFill.style.width = pct + "%";
  document.getElementById("currentTime").innerText = formatTime(player.currentTime);
  document.getElementById("duration").innerText = formatTime(player.duration);
};

progressWrapper.onclick = (e) => {
  if (!player.duration) return;
  const width = progressWrapper.clientWidth;
  const clickX = e.offsetX;
  player.currentTime = (clickX / width) * player.duration;
};

function changeVolume(val) {
  player.volume = val;
}

function formatTime(seconds) {
  const min = Math.floor(seconds / 60);
  const sec = Math.floor(seconds % 60);
  return `${min < 10 ? "0" + min : min}:${sec < 10 ? "0" + sec : sec}`;
}

function loadSongs() {
  currentView = "all";
  selectedPlaylistId = null;
  selectedPlaylistName = "";
  setActiveSidebar("homeNavBtn");
  setViewTitle("Danh sách bài hát");
  fetchJson(API_URL + "/api/songs?userId=" + user.id + "&_=" + Date.now())
    .then((data) => renderSongs(data, "grid"));
}

function searchSongs() {
  const query = document.getElementById("searchInput").value.trim();
  if (!query) {
    if (currentView === "playlist" && selectedPlaylistId) {
      loadPlaylistSongs(selectedPlaylistId, selectedPlaylistName);
      return;
    }
    loadSongs();
    return;
  }

  fetchJson(API_URL + "/api/songs/search?q=" + encodeURIComponent(query) + "&_=" + Date.now())
    .then((data) => {
      setActiveSidebar(null);
      currentView = "search";
      setViewTitle(`Kết quả tìm kiếm: ${query}`);
      renderSongs(data, "grid");
    });
}

function toggleFavorite(songId) {
  fetchJson(API_URL + "/api/favorites/toggle", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId: user.id, songId })
  }).then(() => refreshCurrentView());
}

function loadFavorites() {
  currentView = "favorites";
  selectedPlaylistId = null;
  selectedPlaylistName = "";
  setActiveSidebar("libraryNavBtn");
  setViewTitle("Bài hát yêu thích");
  document.getElementById("libraryMenu").style.display = "block";
  fetchJson(API_URL + "/api/favorites/" + user.id + "?_=" + Date.now())
    .then((data) => renderSongs(data, "grid"));
}

function loadRecent() {
  currentView = "recent";
  selectedPlaylistId = null;
  selectedPlaylistName = "";
  setActiveSidebar("libraryNavBtn");
  setViewTitle("Nghe gần đây");
  document.getElementById("libraryMenu").style.display = "block";
  fetchJson(API_URL + "/api/recent/" + user.id + "?_=" + Date.now())
    .then((data) => renderSongs(data, "grid"));
}

function renderPlaylistNav(playlists) {
  playlistNav.innerHTML = "";

  if (!playlists.length) {
    playlistNav.innerHTML = `<div class="playlist-empty">Chưa có playlist nào</div>`;
    return;
  }

  playlists.forEach((playlist) => {
    const button = document.createElement("button");
    button.className = "playlist-nav-item";
    if (playlist.id === selectedPlaylistId) {
      button.classList.add("active");
    }
    button.innerHTML = `
      <span class="playlist-nav-name">${escapeHtml(playlist.name)}</span>
      <span class="playlist-nav-count">${playlist.songCount}</span>
    `;
    button.onclick = () => loadPlaylistSongs(playlist.id, playlist.name);
    playlistNav.appendChild(button);
  });
}

function loadPlaylists() {
  return fetchJson(API_URL + "/api/playlists?userId=" + user.id + "&_=" + Date.now())
    .then((playlists) => {
      renderPlaylistNav(playlists);
      return playlists;
    })
    .catch(() => {
      playlistNav.innerHTML = `<div class="playlist-empty">Không tải được playlist</div>`;
      return [];
    });
}

function loadPlaylistSongs(playlistId, playlistName) {
  currentView = "playlist";
  selectedPlaylistId = playlistId;
  if (playlistName) {
    selectedPlaylistName = playlistName;
  }
  setActiveSidebar(null);

  fetchJson(API_URL + `/api/playlists/${playlistId}/songs?userId=${user.id}&_=${Date.now()}`)
    .then((data) => {
      setViewTitle(selectedPlaylistName ? `Playlist: ${selectedPlaylistName}` : "Playlist");
      renderSongs(data, "playlist");
      return loadPlaylists();
    });
}

function createPlaylist() {
  const name = prompt("Nhập tên playlist:");
  if (!name || !name.trim()) return;

  fetchJson(API_URL + "/api/playlists", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId: user.id, name: name.trim() })
  }).then((data) => {
    if (data.error) {
      alert(data.error);
      return;
    }
    loadPlaylistSongs(data.playlist.id, data.playlist.name);
  });
}

function addSongToPlaylist(songId) {
  loadPlaylists().then((playlists) => {
    if (!playlists.length) {
      alert("Bạn cần tạo playlist trước.");
      return;
    }

    const options = playlists.map((playlist) => `${playlist.id}: ${playlist.name}`).join("\n");
    const selected = prompt(`Chọn playlist theo id:\n${options}`);
    if (!selected) return;

    const playlistId = parseInt(selected, 10);
    if (Number.isNaN(playlistId)) {
      alert("ID playlist không hợp lệ.");
      return;
    }

    fetchJson(API_URL + `/api/playlists/${playlistId}/songs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId: user.id, songId })
    }).then((data) => {
      alert(data.message || data.error || "Đã xử lý.");
      loadPlaylists();
      if (currentView === "playlist" && selectedPlaylistId === playlistId) {
        loadPlaylistSongs(playlistId, selectedPlaylistName);
      }
    });
  });
}

function refreshCurrentView() {
  if (currentView === "favorites") {
    loadFavorites();
    return;
  }
  if (currentView === "recent") {
    loadRecent();
    return;
  }
  if (currentView === "playlist" && selectedPlaylistId) {
    loadPlaylistSongs(selectedPlaylistId, selectedPlaylistName);
    return;
  }
  loadSongs();
}

function openEdit(id, title, artist) {
  editId = id;
  document.getElementById("editTitle").value = title;
  document.getElementById("editArtist").value = artist;
  document.getElementById("editModal").style.display = "flex";
}

function closeModal() {
  document.getElementById("editModal").style.display = "none";
  editId = null;
}

function submitEdit() {
  const title = document.getElementById("editTitle").value;
  const artist = document.getElementById("editArtist").value;
  const songFile = document.getElementById("editFile").files[0];
  const imageFile = document.getElementById("editImage").files[0];
  const formData = new FormData();

  formData.append("title", title);
  formData.append("artist", artist);
  if (songFile) formData.append("song", songFile);
  if (imageFile) formData.append("image", imageFile);

  fetchJson(API_URL + "/api/songs/" + editId, {
    method: "PUT",
    headers: { role: user.role },
    body: formData
  }).then((data) => {
    if (data.error) {
      alert(data.error);
      return;
    }
    alert("Cập nhật thành công!");
    closeModal();
    refreshCurrentView();
  });
}

function deleteSong(id) {
  if (!confirm("Bạn có chắc muốn xóa không?")) return;

  fetchJson(API_URL + "/api/songs/" + id, {
    method: "DELETE",
    headers: { role: user.role }
  }).then((data) => {
    if (data.error) {
      alert(data.error);
      return;
    }
    alert("Xóa thành công!");
    refreshCurrentView();
  });
}

function toggleLibrary() {
  const menu = document.getElementById("libraryMenu");
  menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function logout() {
  localStorage.removeItem("user");
  window.location.href = "/login";
}

function goToUpload() {
  window.location.href = "/upload";
}

function goHome() {
  window.location.href = "/";
}

function upload() {
  if (!user || user.role !== "admin") {
    alert("Bạn không có quyền tải nhạc.");
    window.location.href = "/";
    return;
  }

  const titleInput = document.getElementById("title");
  const artistInput = document.getElementById("artist");
  const fileInput = document.getElementById("file");
  const imageInput = document.getElementById("image");

  if (!titleInput || !artistInput || !fileInput) return;

  const title = titleInput.value.trim();
  const artist = artistInput.value.trim();
  const songFile = fileInput.files[0];
  const imageFile = imageInput?.files[0];

  if (!title || !artist) {
    alert("Vui lòng nhập tên bài hát và nghệ sĩ.");
    return;
  }

  if (!songFile) {
    alert("Vui lòng chọn file nhạc.");
    return;
  }

  const formData = new FormData();
  formData.append("title", title);
  formData.append("artist", artist);
  formData.append("song", songFile);
  if (imageFile) {
    formData.append("image", imageFile);
  }

  fetchJson(API_URL + "/api/songs", {
    method: "POST",
    headers: { role: user.role },
    body: formData
  }).then((data) => {
    if (data.error) {
      alert(data.error);
      return;
    }

    alert(data.message || "Tải nhạc thành công!");
    titleInput.value = "";
    artistInput.value = "";
    fileInput.value = "";
    if (imageInput) {
      imageInput.value = "";
    }
  }).catch(() => {
    alert("Không thể tải nhạc lên.");
  });
}

window.onload = async () => {
  if (window.location.pathname === "/upload") {
    if (!user) {
      window.location.href = "/login";
      return;
    }
    if (user.role !== "admin") {
      alert("Bạn không có quyền truy cập trang này.");
      window.location.href = "/";
    }
    return;
  }

  const userName = document.getElementById("userName");
  const userRole = document.getElementById("userRole");
  if (!userName || !userRole) return;

  userName.innerText = user.username;
  userRole.innerText = user.role;
  if (user.role !== "admin") {
    document.querySelector('.nav-btn[onclick="goToUpload()"]')?.remove();
  }

  await loadPlaylists();
  loadSongs();
};
