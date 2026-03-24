const API_URL = "http://127.0.0.1:5000";

    // 1. Hàm vẽ giao diện thẻ bài hát (tái sử dụng)
    function renderSongs(data) {
      const list = document.getElementById("list");
      list.innerHTML = "";

      if (data.length === 0) {
        list.innerHTML = `<p style="color: var(--text-muted); margin-top: 10px;">Không tìm thấy bài hát nào phù hợp.</p>`;
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

          <button class="play-btn-circle" onclick="play('${song.fileUrl}')">
            <i class="fas fa-play"></i>
          </button>
          <div class="song-actions">
  <button class="btn edit-btn" onclick="editSong(${song.id}, '${song.title}', '${song.artist}')">
    <i class="fas fa-pen"></i>
  </button>
  <button class="btn delete-btn" onclick="deleteSong(${song.id})">
    <i class="fas fa-trash"></i>
  </button>
</div>
        `;
        list.appendChild(card);
      });
    }

    // 2. Hàm Load toàn bộ bài hát
    function loadSongs() {
      fetch(API_URL + "/api/songs")
        .then(res => res.json())
        .then(data => renderSongs(data))
        .catch(err => console.error("Lỗi tải danh sách:", err));
    }

    // 3. Hàm Tìm kiếm thời gian thực (Gọi API bạn đã viết)
    function searchSongs() {
      const query = document.getElementById("searchInput").value;

      // Nếu xóa trắng ô tìm kiếm, gọi lại toàn bộ bài hát
      if (query.trim() === "") {
        loadSongs();
        return;
      }

      // Gửi request tới API tìm kiếm
      fetch(API_URL + "/api/songs/search?q=" + encodeURIComponent(query))
        .then(res => res.json())
        .then(data => renderSongs(data))
        .catch(err => console.error("Lỗi tìm kiếm:", err));
    }

    // 4. Hàm Upload
    function upload() {
      const file = document.getElementById("file").files[0];
      const title = document.getElementById("title").value;
      const artist = document.getElementById("artist").value;
      const image = document.getElementById("image").files[0];


      if (!file || !title || !artist) {
        alert("Vui lòng điền đủ tên, ca sĩ và chọn file nhạc!");
        return;
      }

      const formData = new FormData();
      formData.append("song", file);
      formData.append("title", title);
      formData.append("artist", artist);
      formData.append("image", image);

      fetch(API_URL + "/api/songs", {
        method: "POST",
        body: formData
      })
      .then(res => res.json())
      .then(() => {
        alert("Upload thành công!");
        document.getElementById("title").value = "";
        document.getElementById("artist").value = "";
        document.getElementById("file").value = "";
        loadSongs(); // Tải lại danh sách sau khi up
      })
      .catch(err => console.error("Lỗi upload:", err));
    }

    // 5. Hàm Play nhạc
    function play(url) {
      const player = document.getElementById("player");
      player.src = API_URL + url;
      player.play();
    }
    //Xóa
    function deleteSong(id) {
  if (!confirm("Bạn có chắc muốn xóa?")) return;

  fetch(API_URL + "/api/songs/" + id, {
    method: "DELETE"
  })
  .then(res => res.json())
  .then(() => {
    alert("Đã xóa!");
    loadSongs();
  });
}
//Sửa
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
  const title = document.getElementById("editTitle").value;
  const artist = document.getElementById("editArtist").value;
  const file = document.getElementById("editFile").files[0];
  const image = document.getElementById("editImage").files[0];

  if (!title || !artist) {
    alert("Vui lòng nhập đầy đủ!");
    return;
  }

  const formData = new FormData();
  formData.append("title", title);
  formData.append("artist", artist);

  if (file) formData.append("song", file);
  if (image) formData.append("image", image);

  fetch(API_URL + "/api/songs/" + currentEditId, {
    method: "PUT",
    body: formData
  })
  .then(res => res.json())
  .then(() => {
    alert("Cập nhật thành công!");
    closeModal();
    loadSongs();
  })
  .catch(err => console.error(err));
}

    // Khởi chạy khi tải trang
    window.onload = loadSongs;