const API_URL = "http://127.0.0.1:5000";

// ===== USER =====
const user = JSON.parse(localStorage.getItem("user"));

if (!user) {
  window.location.href = "/login";
}

// ===== LOGOUT =====
function logout() {
  localStorage.removeItem("user");
  window.location.href = "/login";
}

// ===== RENDER =====
function renderSongs(data) {
  const list = document.getElementById("list");
  list.innerHTML = "";

  if (data.length === 0) {
    list.innerHTML = `<p style="color: var(--text-muted)">Không có bài hát</p>`;
    return;
  }

  data.forEach(song => {
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

      <button class="fav-btn ${song.isFavorite ? "active" : ""}" onclick="toggleFavorite(${song.id})">
  <i class="${song.isFavorite ? "fas" : "far"} fa-heart"></i>
</button>

      ${
        user.role === "admin"
          ? `
        <div class="song-actions">
          <button class="btn edit-btn" onclick="editSong(${song.id}, '${song.title}', '${song.artist}')">
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

// ===== LOAD =====
function loadSongs() {
  fetch(API_URL + "/api/songs?userId=" + user.id)
    .then(res => res.json())
    .then(data => renderSongs(data));
}

// ===== SEARCH =====
function searchSongs() {
  const query = document.getElementById("searchInput").value;

  if (!query.trim()) {
    loadSongs();
    return;
  }

  fetch(API_URL + "/api/songs/search?q=" + encodeURIComponent(query))
    .then(res => res.json())
    .then(data => renderSongs(data));
}

// ===== PLAY + RECENT =====
function play(url, songId) {
  const player = document.getElementById("player");
  player.src = API_URL + url;
  player.play();

  // lưu recent
  fetch(API_URL + "/api/recent", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      userId: user.id,
      songId: songId
    })
  });
}

// ===== FAVORITE =====
function toggleFavorite(songId) {
  fetch(API_URL + "/api/favorites/toggle", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      userId: user.id,
      songId: songId
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "added") {
      console.log("❤️ Added");
    } else {
      console.log("💔 Removed");
    }

    // reload lại UI (đơn giản)
    loadSongs();
  });
}

// ===== LOAD FAVORITE =====
function loadFavorites() {
  fetch(API_URL + "/api/favorites/" + user.id)
    .then(res => res.json())
    .then(data => renderSongs(data));
}

// ===== LOAD RECENT =====
function loadRecent() {
  fetch(API_URL + "/api/recent/" + user.id)
    .then(res => res.json())
    .then(data => renderSongs(data));
}

// ===== TOGGLE LIBRARY =====
function toggleLibrary() {
  const menu = document.getElementById("libraryMenu");

  if (!menu) return;

  menu.style.display =
    menu.style.display === "block" ? "none" : "block";
}

// ===== UPLOAD =====
function upload() {
  if (user.role !== "admin") {
    alert("Bạn không có quyền!");
    return;
  }

  const file = document.getElementById("file").files[0];
  const title = document.getElementById("title").value;
  const artist = document.getElementById("artist").value;
  const image = document.getElementById("image").files[0];

  if (!file || !title || !artist) {
    alert("Nhập đủ thông tin!");
    return;
  }

  const formData = new FormData();
  formData.append("song", file);
  formData.append("title", title);
  formData.append("artist", artist);
  if (image) formData.append("image", image);

  fetch(API_URL + "/api/songs", {
    method: "POST",
    headers: {
      "role": user.role
    },
    body: formData
  })
  .then(res => res.json())
  .then(() => {
    alert("Upload thành công!");
    loadSongs();
  });
}

// ===== DELETE =====
function deleteSong(id) {
  if (user.role !== "admin") {
    alert("Bạn không có quyền!");
    return;
  }

  if (!confirm("Xóa bài này?")) return;

  fetch(API_URL + "/api/songs/" + id, {
    method: "DELETE",
    headers: {
      "role": user.role
    }
  })
  .then(() => {
    alert("Đã xóa!");
    loadSongs();
  });
}

// ===== EDIT =====
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

function submitEdit() {
  if (user.role !== "admin") {
    alert("Bạn không có quyền!");
    return;
  }

  const title = document.getElementById("editTitle").value;
  const artist = document.getElementById("editArtist").value;
  const file = document.getElementById("editFile").files[0];
  const image = document.getElementById("editImage").files[0];

  const formData = new FormData();
  formData.append("title", title);
  formData.append("artist", artist);
  if (file) formData.append("song", file);
  if (image) formData.append("image", image);

  fetch(API_URL + "/api/songs/" + currentEditId, {
    method: "PUT",
    headers: {
      "role": user.role
    },
    body: formData
  })
  .then(() => {
    alert("Cập nhật thành công!");
    closeModal();
    loadSongs();
  });
}

// ===== NAV =====
function goToUpload() {
  if (user.role !== "admin") {
    alert("Chỉ admin được upload!");
    return;
  }
  window.location.href = "/upload";
}

function goHome() {
  window.location.href = "/";
}

// ===== INIT =====
window.onload = () => {
  loadSongs();

  // Ẩn upload nếu không phải admin
  if (user.role !== "admin") {
    document.querySelector(".upload-box")?.remove();
  }
};