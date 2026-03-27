const API_URL = "http://127.0.0.1:5000";

let user = null;
let currentView = "songs";

function handleUnauthorized(response) {
  if (response.status === 401) {
    localStorage.removeItem("user");
    window.location.href = "/login";
    return true;
  }
  return false;
}

async function apiFetch(path, options = {}) {
  const response = await fetch(API_URL + path, options);

  if (handleUnauthorized(response)) {
    throw new Error("Unauthorized");
  }

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}

function setSectionTitle(title, showCreatePlaylist = false) {
  const titleElement = document.getElementById("sectionTitle");
  const createButton = document.getElementById("createPlaylistBtn");

  if (titleElement) {
    titleElement.textContent = title;
  }

  if (createButton) {
    createButton.style.display = showCreatePlaylist ? "inline-flex" : "none";
  }
}

async function loadCurrentUser() {
  const data = await apiFetch("/api/me");
  user = data.user;
  localStorage.setItem("user", JSON.stringify(user));

  const userName = document.getElementById("userName");
  const userRole = document.getElementById("userRole");

  if (userName) {
    userName.textContent = user.username;
  }

  if (userRole) {
    userRole.textContent = user.role;
  }
}

async function logout() {
  try {
    await apiFetch("/api/logout", { method: "POST" });
  } catch (error) {
    console.error(error);
  } finally {
    localStorage.removeItem("user");
    window.location.href = "/login";
  }
}

function renderSongs(data) {
  const list = document.getElementById("list");
  if (!list) {
    return;
  }

  list.className = "song-list";
  list.innerHTML = "";

  if (data.length === 0) {
    list.innerHTML = `<p style="color: var(--text-muted)">Khong co du lieu</p>`;
    return;
  }

  data.forEach((song) => {
    const card = document.createElement("div");
    card.className = "song-card";

    card.innerHTML = `
      <div class="song-cover">
        ${
          song.imageUrl
            ? `<img src="${API_URL + song.imageUrl}" style="width:100%; height:100%; object-fit:cover; border-radius:6px;">`
            : `<i class="fas fa-music"></i>`
        }
      </div>

      <div class="song-title">${song.title}</div>
      <div class="song-artist">${song.artist}</div>

      <button class="play-btn-circle" onclick="play('${song.fileUrl}', ${song.id})">
        <i class="fas fa-play"></i>
      </button>

      <div class="song-meta-actions">
        <button class="fav-btn ${song.isFavorite ? "active" : ""}" onclick="toggleFavorite(${song.id})">
          <i class="${song.isFavorite ? "fas" : "far"} fa-heart"></i>
        </button>
        <button class="fav-btn" onclick="addToPlaylist(${song.id}, '${song.title.replace(/'/g, "\\'")}')">
          <i class="fas fa-list-ul"></i>
        </button>
      </div>

      ${
        user && user.role === "admin"
          ? `
        <div class="song-actions">
          <button class="btn edit-btn" onclick="editSong(${song.id}, '${song.title.replace(/'/g, "\\'")}', '${song.artist.replace(/'/g, "\\'")}')">
            <i class="fas fa-pen"></i>
          </button>
          <button class="btn delete-btn" onclick="deleteSong(${song.id})">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      `
          : ""
      }
    `;

    list.appendChild(card);
  });
}

function renderPlaylists(playlists) {
  const list = document.getElementById("list");
  if (!list) {
    return;
  }

  list.className = "playlist-list";
  list.innerHTML = "";

  if (playlists.length === 0) {
    list.innerHTML = `<p style="color: var(--text-muted)">Ban chua co playlist nao</p>`;
    return;
  }

  playlists.forEach((playlist) => {
    const card = document.createElement("div");
    card.className = "playlist-card";
    card.innerHTML = `
      <div class="playlist-icon"><i class="fas fa-list-music"></i></div>
      <div class="playlist-name">${playlist.name}</div>
      <div class="playlist-count">${playlist.songCount} bai hat</div>
      <button class="btn playlist-open-btn" onclick="openPlaylist(${playlist.id})">Mo playlist</button>
    `;
    list.appendChild(card);
  });
}

async function loadSongs() {
  currentView = "songs";
  setSectionTitle("Danh sach bai hat", false);
  const data = await apiFetch("/api/songs");
  renderSongs(data);
}

async function searchSongs() {
  const input = document.getElementById("searchInput");
  const query = input ? input.value : "";

  if (!query.trim()) {
    await loadSongs();
    return;
  }

  currentView = "songs";
  setSectionTitle("Ket qua tim kiem", false);
  const data = await apiFetch("/api/songs/search?q=" + encodeURIComponent(query));
  renderSongs(data);
}

async function play(url, songId) {
  const player = document.getElementById("player");
  player.src = API_URL + url;
  player.play();

  try {
    await apiFetch("/api/recent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ songId }),
    });
  } catch (error) {
    console.error(error);
  }
}

async function toggleFavorite(songId) {
  try {
    await apiFetch("/api/favorites/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ songId }),
    });

    if (currentView.startsWith("playlist:")) {
      await openPlaylist(Number(currentView.split(":")[1]));
      return;
    }

    if (currentView === "favorites") {
      await loadFavorites();
      return;
    }

    await loadSongs();
  } catch (error) {
    alert(error.message);
  }
}

async function loadFavorites() {
  currentView = "favorites";
  setSectionTitle("Bai hat yeu thich", false);
  const data = await apiFetch("/api/favorites/" + user.id);
  renderSongs(data);
}

async function loadRecent() {
  currentView = "recent";
  setSectionTitle("Nghe gan day", false);
  const data = await apiFetch("/api/recent/" + user.id);
  renderSongs(data);
}

async function loadPlaylists() {
  currentView = "playlists";
  setSectionTitle("Playlist cua toi", true);
  const data = await apiFetch("/api/playlists");
  renderPlaylists(data);
}

async function openPlaylist(playlistId) {
  currentView = `playlist:${playlistId}`;
  const data = await apiFetch("/api/playlists/" + playlistId);
  setSectionTitle(data.playlist.name, false);
  renderSongs(data.songs);
}

async function createPlaylist() {
  const name = prompt("Nhap ten playlist moi:");
  if (!name) {
    return;
  }

  try {
    await apiFetch("/api/playlists", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    await loadPlaylists();
  } catch (error) {
    alert(error.message);
  }
}

async function addToPlaylist(songId, songTitle) {
  try {
    const playlists = await apiFetch("/api/playlists");
    if (playlists.length === 0) {
      alert("Ban chua co playlist. Hay tao playlist truoc.");
      await loadPlaylists();
      return;
    }

    const options = playlists.map((playlist) => `${playlist.id} - ${playlist.name}`).join("\n");
    const chosen = prompt(`Them "${songTitle}" vao playlist nao?\n${options}`);

    if (!chosen) {
      return;
    }

    const playlistId = Number(chosen.split("-")[0].trim());
    if (!playlistId) {
      alert("Playlist khong hop le.");
      return;
    }

    const result = await apiFetch(`/api/playlists/${playlistId}/songs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ songId }),
    });

    alert(result.message);
  } catch (error) {
    alert(error.message);
  }
}

function toggleLibrary() {
  const menu = document.getElementById("libraryMenu");
  if (!menu) {
    return;
  }

  menu.style.display = menu.style.display === "block" ? "none" : "block";
}

async function upload() {
  if (!user || user.role !== "admin") {
    alert("Ban khong co quyen!");
    return;
  }

  const file = document.getElementById("file").files[0];
  const title = document.getElementById("title").value;
  const artist = document.getElementById("artist").value;
  const image = document.getElementById("image").files[0];

  if (!file || !title || !artist) {
    alert("Nhap du thong tin!");
    return;
  }

  const formData = new FormData();
  formData.append("song", file);
  formData.append("title", title);
  formData.append("artist", artist);
  if (image) {
    formData.append("image", image);
  }

  try {
    await apiFetch("/api/songs", {
      method: "POST",
      body: formData,
    });
    alert("Upload thanh cong!");
    window.location.href = "/";
  } catch (error) {
    alert(error.message);
  }
}

async function deleteSong(id) {
  if (!user || user.role !== "admin") {
    alert("Ban khong co quyen!");
    return;
  }

  if (!confirm("Xoa bai nay?")) {
    return;
  }

  try {
    await apiFetch("/api/songs/" + id, { method: "DELETE" });
    alert("Da xoa!");
    await loadSongs();
  } catch (error) {
    alert(error.message);
  }
}

let currentEditId = null;

function editSong(id, title, artist) {
  currentEditId = id;
  document.getElementById("editTitle").value = title;
  document.getElementById("editArtist").value = artist;
  document.getElementById("editModal").style.display = "flex";
}

function closeModal() {
  document.getElementById("editModal").style.display = "none";
}

async function submitEdit() {
  if (!user || user.role !== "admin") {
    alert("Ban khong co quyen!");
    return;
  }

  const title = document.getElementById("editTitle").value;
  const artist = document.getElementById("editArtist").value;
  const file = document.getElementById("editFile").files[0];
  const image = document.getElementById("editImage").files[0];

  const formData = new FormData();
  formData.append("title", title);
  formData.append("artist", artist);
  if (file) {
    formData.append("song", file);
  }
  if (image) {
    formData.append("image", image);
  }

  try {
    await apiFetch("/api/songs/" + currentEditId, {
      method: "PUT",
      body: formData,
    });
    alert("Cap nhat thanh cong!");
    closeModal();
    await loadSongs();
  } catch (error) {
    alert(error.message);
  }
}

function goToUpload() {
  if (!user || user.role !== "admin") {
    alert("Chi admin duoc upload!");
    return;
  }

  window.location.href = "/upload";
}

function goHome() {
  window.location.href = "/";
}

window.onload = async () => {
  try {
    await loadCurrentUser();
    await loadSongs();
  } catch (error) {
    console.error(error);
  }
};
