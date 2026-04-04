let dia_chi_api = "http://127.0.0.1:5000";

let nguoi_dung = JSON.parse(localStorage.getItem("user"));
let trinh_phat = null;
let danh_sach_bai_hat = [];
let vi_tri_hien_tai = -1;
let che_do_hien_tai = "all";
let ma_playlist_da_chon = null;
let ten_playlist_da_chon = "";
let ma_bai_hat_dang_sua = null;
let ma_bai_hat_cho_playlist = null;
let ma_bai_hat_hien_tai = null;
let che_do_lap_bai = false;

$(document).ready(function () {
  if (!nguoi_dung) {
    window.location.href = "/login";
    return;
  }

  trinh_phat = $("#player")[0];
  gan_su_kien_trinh_phat();

  if (window.location.pathname === "/upload") {
    if (nguoi_dung.role !== "admin") {
      alert("Ban khong co quyen truy cap trang nay.");
      window.location.href = "/";
      return;
    }
    return;
  }

  $("#userName").text(nguoi_dung.username || "");
  $("#userRole").text(nguoi_dung.role || "");

  if (nguoi_dung.role !== "admin") {
    $('.nav-btn[onclick="goToUpload()"]').remove();
  }

  cap_nhat_nut_tai_trinh_phat(null);
  loadPlaylists(function () {
    loadSongs();
  });
});

function goi_api_json(tuy_chon) {
  return $.ajax({
    cache: false,
    ...tuy_chon
  });
}

function chuyen_html_an_toan(noi_dung) {
  return String(noi_dung || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function chuyen_js_an_toan(noi_dung) {
  return String(noi_dung || "")
    .replace(/\\/g, "\\\\")
    .replace(/`/g, "\\`");
}

function dat_nut_sidebar_dang_chon(ma_nut) {
  $(".sidebar .nav-btn").removeClass("active");
  if (ma_nut) {
    $("#" + ma_nut).addClass("active");
  }
}

function dat_tieu_de_xem(tieu_de) {
  $("#viewTitle").text(tieu_de);
}

function dat_che_do_danh_sach(che_do) {
  if (che_do === "playlist") {
    $("#list").addClass("playlist-song-list");
  } else {
    $("#list").removeClass("playlist-song-list");
  }
}

function dat_anh_trinh_phat(duong_dan_anh) {
  if (!duong_dan_anh) {
    $("#p-img").removeAttr("src");
    $("#p-img-wrapper").addClass("is-placeholder");
    return;
  }

  $("#p-img-wrapper").removeClass("is-placeholder");
  $("#p-img").attr("src", dia_chi_api + duong_dan_anh);
}

function lay_duong_dan_tai_bai_hat(ma_bai_hat) {
  return dia_chi_api + "/api/songs/" + ma_bai_hat + "/download";
}

function downloadSong(ma_bai_hat) {
  if (!ma_bai_hat) {
    return;
  }
  window.location.href = lay_duong_dan_tai_bai_hat(ma_bai_hat);
}

function cap_nhat_nut_tai_trinh_phat(bai_hat) {
  if (!$("#playerDownloadBtn").length) {
    return;
  }

  if (!bai_hat || !bai_hat.id) {
    $("#playerDownloadBtn").prop("disabled", true);
    $("#playerDownloadBtn").attr("title", "Chon bai hat de tai");
    return;
  }

  $("#playerDownloadBtn").prop("disabled", false);
  $("#playerDownloadBtn").attr("title", "Tai " + bai_hat.title);
}

function renderSongs(du_lieu, che_do) {
  let html = "";
  danh_sach_bai_hat = du_lieu || [];
  vi_tri_hien_tai = danh_sach_bai_hat.length ? 0 : -1;
  dat_che_do_danh_sach(che_do);

  if (!danh_sach_bai_hat.length) {
    if (che_do === "playlist") {
      html = '<div class="empty-state">Playlist nay chua co bai hat.</div>';
    } else {
      html = '<div class="empty-state">Khong co bai hat de hien thi.</div>';
    }
    $("#list").html(html);
    return;
  }

  for (let chi_so = 0; chi_so < danh_sach_bai_hat.length; chi_so++) {
    let bai_hat = danh_sach_bai_hat[chi_so];

    if (che_do === "playlist") {
      html += '<div class="playlist-song-row">';
      html += '<div class="playlist-song-main" onclick="playByIndex(' + chi_so + ')">';
      html += '<div class="playlist-song-index">' + (chi_so + 1) + "</div>";
      html += '<div class="playlist-song-cover">';
      if (bai_hat.imageUrl) {
        html += '<img src="' + dia_chi_api + bai_hat.imageUrl + '" alt="' + chuyen_html_an_toan(bai_hat.title) + '">';
      } else {
        html += '<i class="fas fa-music"></i>';
      }
      html += "</div>";
      html += '<div class="playlist-song-info">';
      html += '<div class="playlist-song-title">' + chuyen_html_an_toan(bai_hat.title) + "</div>";
      html += '<div class="playlist-song-artist">' + chuyen_html_an_toan(bai_hat.artist) + "</div>";
      html += "</div>";
      html += "</div>";
      html += '<div class="playlist-song-actions">';
      html += '<button class="row-icon-btn" onclick="event.stopPropagation(); playByIndex(' + chi_so + ')"><i class="fas fa-play"></i></button>';
      html += '<button class="icon-ghost-btn" onclick="event.stopPropagation(); downloadSong(' + bai_hat.id + ')" title="Tai ve may"><i class="fas fa-download"></i></button>';
      html += '<button class="fav-btn ' + (bai_hat.isFavorite ? "active" : "") + '" onclick="event.stopPropagation(); toggleFavorite(' + bai_hat.id + ')">';
      html += '<i class="' + (bai_hat.isFavorite ? "fas" : "far") + ' fa-heart"></i>';
      html += "</button>";
      html += "</div>";
      html += "</div>";
    } else {
      html += '<div class="song-card">';
      html += '<div class="song-cover">';
      if (bai_hat.imageUrl) {
        html += '<img src="' + dia_chi_api + bai_hat.imageUrl + '" style="width:100%; height:100%; object-fit:cover; border-radius:6px;" alt="' + chuyen_html_an_toan(bai_hat.title) + '">';
      } else {
        html += '<i class="fas fa-music"></i>';
      }
      html += "</div>";
      html += '<div class="song-title">' + chuyen_html_an_toan(bai_hat.title) + "</div>";
      html += '<div class="song-artist">' + chuyen_html_an_toan(bai_hat.artist) + "</div>";
      html += '<button class="play-btn-circle" onclick="playByIndex(' + chi_so + ')"><i class="fas fa-play"></i></button>';
      html += '<div class="card-bottom-actions">';
      html += '<button class="fav-btn ' + (bai_hat.isFavorite ? "active" : "") + '" onclick="toggleFavorite(' + bai_hat.id + ')"><i class="' + (bai_hat.isFavorite ? "fas" : "far") + ' fa-heart"></i></button>';
      html += '<button class="fav-btn" onclick="downloadSong(' + bai_hat.id + ')" title="Tai ve may"><i class="fas fa-download"></i></button>';
      html += '<button class="fav-btn" onclick="addSongToPlaylist(' + bai_hat.id + ')" title="Them vao playlist"><i class="fas fa-plus"></i></button>';
      html += "</div>";

      if (nguoi_dung.role === "admin") {
        html += '<div class="song-actions">';
        html += '<button class="btn edit-btn" onclick="openEdit(' + bai_hat.id + ', `' + chuyen_js_an_toan(bai_hat.title) + '`, `' + chuyen_js_an_toan(bai_hat.artist) + '`)"><i class="fas fa-pen"></i></button>';
        html += '<button class="btn delete-btn" onclick="deleteSong(' + bai_hat.id + ')"><i class="fas fa-trash"></i></button>';
        html += "</div>";
      }

      html += "</div>";
    }
  }

  $("#list").html(html);
}

function playByIndex(chi_so) {
  if (chi_so < 0 || chi_so >= danh_sach_bai_hat.length) {
    return;
  }

  vi_tri_hien_tai = chi_so;
  let bai_hat = danh_sach_bai_hat[vi_tri_hien_tai];
  ma_bai_hat_hien_tai = bai_hat.id;

  trinh_phat.src = dia_chi_api + bai_hat.fileUrl;
  trinh_phat.play();

  $("#p-title").text(bai_hat.title);
  $("#p-artist").text(bai_hat.artist);
  dat_anh_trinh_phat(bai_hat.imageUrl);
  cap_nhat_nut_tai_trinh_phat(bai_hat);
  $("#mainPlayBtn").html('<i class="fas fa-pause"></i>');

  goi_api_json({
    url: dia_chi_api + "/api/recent",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      userId: nguoi_dung.id,
      songId: bai_hat.id
    })
  });
}

function togglePlay() {
  if (!trinh_phat || !trinh_phat.src) {
    return;
  }

  if (trinh_phat.paused) {
    trinh_phat.play();
    $("#mainPlayBtn").html('<i class="fas fa-pause"></i>');
  } else {
    trinh_phat.pause();
    $("#mainPlayBtn").html('<i class="fas fa-play"></i>');
  }
}

function nextSong() {
  if (!danh_sach_bai_hat.length) {
    return;
  }

  let vi_tri_tiep = vi_tri_hien_tai + 1;
  if (vi_tri_tiep >= danh_sach_bai_hat.length) {
    vi_tri_tiep = 0;
  }
  playByIndex(vi_tri_tiep);
}

function prevSong() {
  if (!danh_sach_bai_hat.length) {
    return;
  }

  let vi_tri_truoc = vi_tri_hien_tai - 1;
  if (vi_tri_truoc < 0) {
    vi_tri_truoc = danh_sach_bai_hat.length - 1;
  }
  playByIndex(vi_tri_truoc);
}

function toggleRepeatSong() {
  che_do_lap_bai = !che_do_lap_bai;

  $("#repeatSongBtn").toggleClass("active", che_do_lap_bai);
  $("#repeatSongBtn").attr(
    "title",
    che_do_lap_bai ? "Tat lap bai hien tai" : "Bat lap bai hien tai"
  );
}

function replaySong() {
  if (!trinh_phat) {
    return;
  }

  trinh_phat.currentTime = 0;
  trinh_phat.play();
  $("#mainPlayBtn").html('<i class="fas fa-pause"></i>');
}

function gan_su_kien_trinh_phat() {
  $("#p-img").on("error", function () {
    $("#p-img").removeAttr("src");
    $("#p-img-wrapper").addClass("is-placeholder");
  });

  $("#progressWrapper").on("click", function (su_kien) {
    if (!trinh_phat || !trinh_phat.duration) {
      return;
    }

    let do_rong = $(this).width();
    let vi_tri_x = su_kien.pageX - $(this).offset().left;
    trinh_phat.currentTime = (vi_tri_x / do_rong) * trinh_phat.duration;
  });

  $("#player").on("ended", function () {
    if (che_do_lap_bai) {
      trinh_phat.currentTime = 0;
      trinh_phat.play();
      $("#mainPlayBtn").html('<i class="fas fa-pause"></i>');
      return;
    }

    nextSong();
  });

  $("#player").on("timeupdate", function () {
    if (!trinh_phat.duration) {
      return;
    }

    let phan_tram = (trinh_phat.currentTime / trinh_phat.duration) * 100;
    $("#progressFill").css("width", phan_tram + "%");
    $("#currentTime").text(formatTime(trinh_phat.currentTime));
    $("#duration").text(formatTime(trinh_phat.duration));
  });
}

function changeVolume(gia_tri) {
  if (trinh_phat) {
    trinh_phat.volume = gia_tri;
  }
}

function formatTime(so_giay) {
  let phut = Math.floor(so_giay / 60);
  let giay = Math.floor(so_giay % 60);
  return (phut < 10 ? "0" + phut : phut) + ":" + (giay < 10 ? "0" + giay : giay);
}

function loadSongs() {
  che_do_hien_tai = "all";
  ma_playlist_da_chon = null;
  ten_playlist_da_chon = "";
  dat_nut_sidebar_dang_chon("homeNavBtn");
  dat_tieu_de_xem("Danh sach bai hat");

  goi_api_json({
    url: dia_chi_api + "/api/songs",
    method: "GET",
    data: {
      userId: nguoi_dung.id,
      _: Date.now()
    },
    success: function (du_lieu) {
      renderSongs(du_lieu, "grid");
    }
  });
}

function searchSongs() {
  let tu_khoa = $("#searchInput").val().trim();

  if (tu_khoa === "") {
    if (che_do_hien_tai === "playlist" && ma_playlist_da_chon) {
      loadPlaylistSongs(ma_playlist_da_chon, ten_playlist_da_chon);
      return;
    }
    loadSongs();
    return;
  }

  goi_api_json({
    url: dia_chi_api + "/api/songs/search",
    method: "GET",
    data: {
      q: tu_khoa,
      _: Date.now()
    },
    success: function (du_lieu) {
      dat_nut_sidebar_dang_chon(null);
      che_do_hien_tai = "search";
      dat_tieu_de_xem("Ket qua tim kiem: " + tu_khoa);
      renderSongs(du_lieu, "grid");
    }
  });
}

function toggleFavorite(ma_bai_hat) {
  goi_api_json({
    url: dia_chi_api + "/api/favorites/toggle",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      userId: nguoi_dung.id,
      songId: ma_bai_hat
    }),
    success: function () {
      refreshCurrentView();
    }
  });
}

function loadFavorites() {
  che_do_hien_tai = "favorites";
  ma_playlist_da_chon = null;
  ten_playlist_da_chon = "";
  dat_nut_sidebar_dang_chon("libraryNavBtn");
  dat_tieu_de_xem("Bai hat yeu thich");
  $("#libraryMenu").css("display", "block");

  goi_api_json({
    url: dia_chi_api + "/api/favorites/" + nguoi_dung.id,
    method: "GET",
    data: { _: Date.now() },
    success: function (du_lieu) {
      renderSongs(du_lieu, "grid");
    }
  });
}

function loadRecent() {
  che_do_hien_tai = "recent";
  ma_playlist_da_chon = null;
  ten_playlist_da_chon = "";
  dat_nut_sidebar_dang_chon("libraryNavBtn");
  dat_tieu_de_xem("Nghe gan day");
  $("#libraryMenu").css("display", "block");

  goi_api_json({
    url: dia_chi_api + "/api/recent/" + nguoi_dung.id,
    method: "GET",
    data: { _: Date.now() },
    success: function (du_lieu) {
      renderSongs(du_lieu, "grid");
    }
  });
}

function hien_thi_danh_sach_playlist(danh_sach_playlist) {
  let html = "";

  if (!danh_sach_playlist.length) {
    html = '<div class="playlist-empty">Chua co playlist nao</div>';
    $("#playlistNav").html(html);
    return;
  }

  for (let chi_so = 0; chi_so < danh_sach_playlist.length; chi_so++) {
    let playlist = danh_sach_playlist[chi_so];
    html += '<button class="playlist-nav-item ' + (playlist.id === ma_playlist_da_chon ? "active" : "") + '" onclick="loadPlaylistSongs(' + playlist.id + ', `' + chuyen_js_an_toan(playlist.name) + '`)">';
    html += '<span class="playlist-nav-name">' + chuyen_html_an_toan(playlist.name) + "</span>";
    html += '<span class="playlist-nav-count">' + playlist.songCount + "</span>";
    html += "</button>";
  }

  $("#playlistNav").html(html);
}

function loadPlaylists(ham_sau_khi_tai) {
  goi_api_json({
    url: dia_chi_api + "/api/playlists",
    method: "GET",
    data: {
      userId: nguoi_dung.id,
      _: Date.now()
    },
    success: function (du_lieu) {
      hien_thi_danh_sach_playlist(du_lieu);
      if (ham_sau_khi_tai) {
        ham_sau_khi_tai(du_lieu);
      }
    },
    error: function () {
      $("#playlistNav").html('<div class="playlist-empty">Khong tai duoc playlist</div>');
      if (ham_sau_khi_tai) {
        ham_sau_khi_tai([]);
      }
    }
  });
}

function loadPlaylistSongs(ma_playlist, ten_playlist) {
  che_do_hien_tai = "playlist";
  ma_playlist_da_chon = ma_playlist;
  ten_playlist_da_chon = ten_playlist || ten_playlist_da_chon;
  dat_nut_sidebar_dang_chon(null);

  goi_api_json({
    url: dia_chi_api + "/api/playlists/" + ma_playlist + "/songs",
    method: "GET",
    data: {
      userId: nguoi_dung.id,
      _: Date.now()
    },
    success: function (du_lieu) {
      dat_tieu_de_xem(ten_playlist_da_chon ? "Playlist: " + ten_playlist_da_chon : "Playlist");
      renderSongs(du_lieu, "playlist");
      loadPlaylists();
    }
  });
}

function createPlaylist() {
  let ten_playlist = prompt("Nhap ten playlist:");
  if (!ten_playlist || ten_playlist.trim() === "") {
    return;
  }

  goi_api_json({
    url: dia_chi_api + "/api/playlists",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      userId: nguoi_dung.id,
      name: ten_playlist.trim()
    }),
    success: function (du_lieu) {
      if (du_lieu.error) {
        alert(du_lieu.error);
        return;
      }
      loadPlaylistSongs(du_lieu.playlist.id, du_lieu.playlist.name);
    }
  });
}

function addSongToPlaylist(ma_bai_hat) {
  loadPlaylists(function (danh_sach_playlist) {
    if (!danh_sach_playlist.length) {
      alert("Ban can tao playlist truoc.");
      return;
    }
    mo_hop_chon_playlist(ma_bai_hat, danh_sach_playlist);
  });
}

function mo_hop_chon_playlist(ma_bai_hat, danh_sach_playlist) {
  let html = "";
  ma_bai_hat_cho_playlist = ma_bai_hat;

  for (let chi_so = 0; chi_so < danh_sach_playlist.length; chi_so++) {
    let playlist = danh_sach_playlist[chi_so];
    html += '<button class="playlist-picker-item" onclick="submitAddToPlaylist(' + playlist.id + ', `' + chuyen_js_an_toan(playlist.name) + '`)">';
    html += '<span class="playlist-picker-name">' + chuyen_html_an_toan(playlist.name) + "</span>";
    html += '<span class="playlist-picker-count">' + playlist.songCount + " bai</span>";
    html += "</button>";
  }

  $("#playlistPickerBody").html(html);
  $("#playlistPickerModal").addClass("is-open");
}

function closePlaylistPicker() {
  $("#playlistPickerModal").removeClass("is-open");
  ma_bai_hat_cho_playlist = null;
}

function submitAddToPlaylist(ma_playlist, ten_playlist) {
  if (!ma_bai_hat_cho_playlist) {
    return;
  }

  goi_api_json({
    url: dia_chi_api + "/api/playlists/" + ma_playlist + "/songs",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      userId: nguoi_dung.id,
      songId: ma_bai_hat_cho_playlist
    }),
    success: function (du_lieu) {
      alert(du_lieu.message || du_lieu.error || "Da xu ly.");
      closePlaylistPicker();
      loadPlaylists();
      if (che_do_hien_tai === "playlist" && ma_playlist_da_chon === ma_playlist) {
        loadPlaylistSongs(ma_playlist, ten_playlist || ten_playlist_da_chon);
      }
    }
  });
}

function refreshCurrentView() {
  if (che_do_hien_tai === "favorites") {
    loadFavorites();
    return;
  }

  if (che_do_hien_tai === "recent") {
    loadRecent();
    return;
  }

  if (che_do_hien_tai === "playlist" && ma_playlist_da_chon) {
    loadPlaylistSongs(ma_playlist_da_chon, ten_playlist_da_chon);
    return;
  }

  loadSongs();
}

function openEdit(ma_bai_hat, ten_bai_hat, ten_nghe_si) {
  ma_bai_hat_dang_sua = ma_bai_hat;
  $("#editTitle").val(ten_bai_hat);
  $("#editArtist").val(ten_nghe_si);
  $("#editModal").css("display", "flex");
}

function closeModal() {
  $("#editModal").css("display", "none");
  ma_bai_hat_dang_sua = null;
}

function submitEdit() {
  let ten_bai_hat = $("#editTitle").val();
  let ten_nghe_si = $("#editArtist").val();
  let tep_nhac = $("#editFile")[0].files[0];
  let tep_anh = $("#editImage")[0].files[0];
  let du_lieu_form = new FormData();

  du_lieu_form.append("title", ten_bai_hat);
  du_lieu_form.append("artist", ten_nghe_si);

  if (tep_nhac) {
    du_lieu_form.append("song", tep_nhac);
  }

  if (tep_anh) {
    du_lieu_form.append("image", tep_anh);
  }

  $.ajax({
    url: dia_chi_api + "/api/songs/" + ma_bai_hat_dang_sua,
    method: "PUT",
    data: du_lieu_form,
    processData: false,
    contentType: false,
    headers: {
      role: nguoi_dung.role
    },
    success: function (du_lieu) {
      if (du_lieu.error) {
        alert(du_lieu.error);
        return;
      }
      alert("Cap nhat thanh cong!");
      closeModal();
      refreshCurrentView();
    }
  });
}

function deleteSong(ma_bai_hat) {
  if (confirm("Ban co chac muon xoa khong?") === false) {
    return;
  }

  goi_api_json({
    url: dia_chi_api + "/api/songs/" + ma_bai_hat,
    method: "DELETE",
    headers: {
      role: nguoi_dung.role
    },
    success: function (du_lieu) {
      if (du_lieu.error) {
        alert(du_lieu.error);
        return;
      }
      alert("Xoa thanh cong!");
      refreshCurrentView();
    }
  });
}

function toggleLibrary() {
  let menu_thu_vien = $("#libraryMenu");
  if (menu_thu_vien.css("display") === "block") {
    menu_thu_vien.css("display", "none");
  } else {
    menu_thu_vien.css("display", "block");
  }
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
  if (!nguoi_dung || nguoi_dung.role !== "admin") {
    alert("Ban khong co quyen tai nhac.");
    window.location.href = "/";
    return;
  }

  let ten_bai_hat = $("#title").val().trim();
  let ten_nghe_si = $("#artist").val().trim();
  let tep_nhac = $("#file")[0].files[0];
  let tep_anh = $("#image").length ? $("#image")[0].files[0] : null;

  if (ten_bai_hat === "" || ten_nghe_si === "") {
    alert("Vui long nhap ten bai hat va nghe si.");
    return;
  }

  if (!tep_nhac) {
    alert("Vui long chon file nhac.");
    return;
  }

  let du_lieu_form = new FormData();
  du_lieu_form.append("title", ten_bai_hat);
  du_lieu_form.append("artist", ten_nghe_si);
  du_lieu_form.append("song", tep_nhac);

  if (tep_anh) {
    du_lieu_form.append("image", tep_anh);
  }

  $.ajax({
    url: dia_chi_api + "/api/songs",
    method: "POST",
    data: du_lieu_form,
    processData: false,
    contentType: false,
    headers: {
      role: nguoi_dung.role
    },
    success: function (du_lieu) {
      if (du_lieu.error) {
        alert(du_lieu.error);
        return;
      }

      alert(du_lieu.message || "Tai nhac thanh cong!");
      $("#title").val("");
      $("#artist").val("");
      $("#file").val("");
      $("#image").val("");
    },
    error: function () {
      alert("Khong the tai nhac len.");
    }
  });
}
