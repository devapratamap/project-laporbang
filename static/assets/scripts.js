// Mengkonversi waktu posting menjadi string yang menyatakan waktu yang telah berlalu.
function time2str(date) {
    let today = new Date();
    let time = (today - date) / 1000 / 60; // minutes
    if (time < 60) {
        return parseInt(time) + " minutes ago";
    }
    time = time / 60; // hours
    if (time < 24) {
        return parseInt(time) + " hours ago";
    }
    time = time / 24; // days
    if (time < 7) {
        return parseInt(time) + " days ago";
    }
    return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`;
}

// Mengkonversi angka menjadi string dengan format yang lebih singkat.
function num2str(count) {
    if (count > 10000) {
        return parseInt(count / 1000) + "k";
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k";
    }
    if (count == 0) {
        return "";
    }
    return count;
}

function post() {
    // Mendapatkan data dari input pengguna
    let alamat = $("#alamat").val();
    let provinsi = $("#provinsi").val();
    let kotakab = $("#kotakab").val();
    let kecamatan = $("#kecamatan").val();
    let deskripsi = $("#deskripsi").val();

    let today = new Date().toISOString();
    let fileInput = document.getElementById("imageInput");
    let file = fileInput.files[0];

    let formData = new FormData();
    formData.append("alamat", alamat);
    formData.append("provinsi", provinsi);
    formData.append("kotakab", kotakab);
    formData.append("kecamatan", kecamatan);
    formData.append("deskripsi", deskripsi);
    formData.append("date_give", today);
    formData.append("image", file);

    $.ajax({
        type: "POST",
        url: "/posting",
        data: formData,
        contentType: false,
        processData: false,
        success: function (response) {
            $("#modal-post").removeClass("is-active");
            window.location.reload();
        },
        error: function (xhr, status, error) {
            if (xhr.status === 401) {
                // Pengguna belum login, arahkan ke halaman login
                window.location.href = "/login";
            }
        }
    });
}

function get_posts_all() {
    $("#post-box").empty();
    $.ajax({
        type: "GET",
        url: `/get_posts_all`,
        data: {},
        success: function (response) {
            let postinganList = response
            for (let i = 0; i < postinganList.length; i++) {
                let postingan = postinganList[i];
                let time_post = new Date(postingan["date"]);
                let time_before = time2str(time_post);
                console.log(time_before)
                let html_temp = `
                <div class="card" id="">
                    <div class="card-image">
                        <figure class="image is-4by3">
                            <img src="/static/post/${postingan["image_filename"]}" alt="">
                        </figure>
                    </div>
                    <div class="card-content">
                        <div class="media">
                            <div class="media-left">
                                <figure class="image is-48x48">
                                    <img src="/static/${postingan["profile_pic_real"]}">
                                </figure>
                            </div>
                            <div class="media-content" data-title>
                                <p class="title is-4">${postingan["profile_name"]}</p>
                                <p class="subtitle is-6">${postingan["username"]}</p>
                            </div>
                        </div>
            
                        <div class="content" data-body>
                            ${postingan["alamat"]}
                            <br>
                            ${postingan["provinsi"]}, ${postingan["kotakab"]}, ${postingan["kecamatan"]}
                            <br>
                            <div class="box">
                                <b>${postingan["deskripsi"]}</b>
                            </div>
                            <time datetime="2016-1-1">${time_before}</time>
                            <br>
                            <br>
                        </div>
                    </div>
                </div>
                        <br>
                
                        `;
                $("#post-box").append(html_temp);
            }
            console.log(response)

        },
    });
}


function get_posts(username) {
    if (username == undefined) {
        username = "";
    }
    $("#post-box").empty();
    $.ajax({
        type: "GET",
        url: `/get_posts?username_give=${username}`,
        data: {},
        cache: false,
        success: function (response) {
            if (response["result"] === "success") {
                let posts = response["posts"];
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i];
                    let time_post = new Date(post["date"]);
                    let time_before = time2str(time_post);
                    console.log(post);
                    let deleteButton = "";
                    if (username === post["username"] || username === "admlapor") {
                        deleteButton = `<button class="button is-danger" onclick="deletePost('${post['_id']}')">Delete</button>`;
                    }
                    let html_temp = `
                        <div class="card" id="${post["_id"]}">
                            <div class="card-image">
                                <figure class="image is-4by3">
                                    <img src="/static/post/${post["image_filename"]}" alt="">
                                </figure>
                            </div>
                            <div class="card-content">
                                <div class="media">
                                    <div class="media-left">
                                        <figure class="image is-48x48">
                                            <img src="/static/${post["profile_pic_real"]}">
                                        </figure>
                                    </div>
                                    <div class="media-content" data-title>
                                        <p class="title is-4">${post["profile_name"]}</p>
                                        <p class="subtitle is-6">${post["username"]}</p>
                                    </div>
                                </div>
                    
                                <div class="content" data-body>
                                    ${post["alamat"]}
                                    <br>
                                    ${post["provinsi"]}, ${post["kotakab"]}, ${post["kecamatan"]}
                                    <br>
                                    <div class="box">
                                        <b>${post["deskripsi"]}</b>
                                    </div>
                                    <time datetime="2016-1-1">${time_before}</time>
                                    <br>
                                    <br>
                                    ${deleteButton}
                                </div>
                            </div>
                        </div>
                        <br>
                    `;
                    $("#post-box").append(html_temp);
                }
            }
        }
    });
}


function deletePost(postId) {
    Swal.fire({
        title: 'Apaka Anda Yakin?',
        text: 'Data akan dihapus permanen',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No'
    }).then((result) => {
        if (result.isConfirmed) {
            // Jika tombol "Yes" diklik
            $.ajax({
                type: "DELETE",
                url: `/delete_post/${postId}`,
                success: function (response) {
                    Swal.fire('Deleted!', 'Post berhasil dihapus.', 'success').then(() => {
                        $("#modal-post").removeClass("is-active");
                        window.location.reload();
                    });
                }
            });
        }
    });
}


function news_post() {
    let judul = $("#judul").val();
    let news_deskripsi = $("#news_deskripsi").val();

    let today = new Date().toISOString();
    let fileInput = document.getElementById("file_name");
    let file = fileInput.files[0];

    let formData = new FormData();
    formData.append("judul", judul);
    formData.append("news_deskripsi", news_deskripsi);
    formData.append("date_give", today);
    formData.append("file_name", file);

    $.ajax({
        type: "POST",
        url: "/news_posting",
        data: formData,
        contentType: false,
        processData: false,
        success: function (response) {
            $("#modal-post").removeClass("is-active");
            get_news_post(); // Memanggil fungsi get_news_post untuk memperbarui tampilan dengan berita terbaru
        },
    });
}


function get_news_post() {
    $("#post-box").empty();
    $.ajax({
        type: "GET",
        url: "/get_news_post",
        success: function (response) {
            let newsList = response;
            for (let i = 0; i < newsList.length; i++) {
                let news = newsList[i];
                let time_post = new Date(news["date"]);
                let time_before = time2str(time_post);
                console.log(time_before);
                let html_temp = `
                    <div class="card" id="${i}" style="margin-bottom: 20px;">
                        <div class="card-image">
                            <figure class="image is-4by3">
                                <img src="${news["image_url"]}">
                            </figure>
                        </div>

                        <div class="card-content">
                            <div class="media">
                                <div class="media-content">
                                    <p class="title is-4">${news["judul"]}</p>
                                </div>
                            </div>
                            <div class="content">
                                ${news["news_deskripsi"]}
                                <br>
                                <br>
                                <time datetime="2016-1-1">${time_before}</time>
                                <br>
                            </div>
                        </div>
                    </div>
                `;
                $("#post-box").append(html_temp);
            }
        },
    });
}

function deleteNews(newsId) {
    Swal.fire({
        title: 'Apakah Anda Yakin?',
        text: 'Data akan dihapus permanen',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No'
    }).then((result) => {
        if (result.isConfirmed) {
            // Jika tombol "Yes" diklik
            $.ajax({
                type: "DELETE",
                url: `/delete_news/${newsId}`,
                success: function (response) {
                    if (response.result === 'success') {
                        Swal.fire({
                            title: 'Deleted!',
                            text: 'Post berhasil dihapus.',
                            icon: 'success',
                            onClose: function () {
                                $("#modal-post").removeClass("is-active");
                                window.location.reload();
                            }
                        });
                    } else {
                        Swal.fire('Error!', 'Gagal menghapus post.', 'error');
                    }
                },
                error: function () {
                    Swal.fire('Error!', 'Gagal menghapus post.', 'error');
                }
            });
        }
    });
}









// Fungsi hapus cookie dan logout
function sign_out() {
    // Menghapus cookie mytoken saat sign out
    // $.removeCookie("mytoken", { path: "/" });
    Swal.fire({
        title: "Apakah Anda yakin?",
        text: "Anda akan logout dari akun ini!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "OK!",
        cancelButtonText: "Batal",
    }).then((result) => {
        if (result.isConfirmed) {
            $.removeCookie("mytoken", { path: "/" });
            window.location.href = "/";
            // Kode JavaScript yang dieksekusi saat tombol "OK" diklik
            // Atau panggil fungsi lain di sini
        }
    });
}

function sign_in() {
    // Mendapatkan nilai username dan password dari input
    let username = $("#input-username").val();
    let password = $("#input-password").val();

    // Memvalidasi input username
    if (username === "") {
        $("#help-id-login").text("Masukkan nama pengguna");
        $("#input-username").focus();
        return;
    } else {
        $("#help-id-login").text("");
    }

    // Memvalidasi input password
    if (password === "") {
        $("#help-password").text("Masukkan kata sandi");
        $("#input-password").focus();
        return;
    } else {
        $("#help-password-login").text("");
    }

    // Mengirim permintaan POST menggunakan AJAX untuk proses sign in
    $.ajax({
        type: "POST",
        url: "/sign_in",
        data: {
            username_give: username,
            password_give: password,
        },
        success: function (response) {
            if (response["result"] === "success") {
                // Menyimpan token dalam cookie
                $.cookie("mytoken", response["token"], { path: "/" });
                // Mengarahkan pengguna ke halaman utama
                window.location.replace("/");
            } else {
                Swal.fire({
                    title: 'Login Failed!',
                    text: 'Kombinasi Nama Pengguna dan Kata Sandi tidak ditemukan',
                    icon: 'warning'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = "/login";
                    }
                });
            }
        },
    });
}

function sign_up() {
    // Mendapatkan nilai username, password, dan password2 dari input
    let username = $("#input-username").val();
    let password = $("#input-password").val();
    let password2 = $("#input-password2").val();
    console.log(username, password, password2);

    // Memvalidasi input username
    if ($("#help-id").hasClass("is-danger")) {
        Swal.fire(
            'Warning!',
            'Nama Pengguna sudah digunakan',
            'warning'
        );
        return;
    } else if (!$("#help-id").hasClass("is-success")) {
        Swal.fire(
            'Warning!',
            'Periksa nama pengguna terlebih dahulu',
            'warning'
        );
        return;
    }

    // Memvalidasi input password
    if (password === "") {
        $("#help-password")
            .text("Masukkan kata sandi")
            .removeClass("is-safe")
            .addClass("is-danger");
        $("#input-password").focus();
        return;
    } else if (!is_password(password)) {
        $("#help-password")
            .text(
                "Kata sandi harus terdiri minmal 8 karakter alfabet, angka, atau karakter khusus."
            )
            .removeClass("is-safe")
            .addClass("is-danger");
        $("#input-password").focus();
        return;
    } else {
        $("#help-password")
            .text("Kata sandi ini dapat digunakan!")
            .removeClass("is-danger")
            .addClass("is-success");
    }

    // Memvalidasi input password2
    if (password2 === "") {
        $("#help-password2")
            .text("Masukkan kata sandi")
            .removeClass("is-safe")
            .addClass("is-danger");
        $("#input-password2").focus();
        return;
    } else if (password2 !== password) {
        $("#help-password2")
            .text("Kata sandi tidak cocok")
            .removeClass("is-safe")
            .addClass("is-danger");
        $("#input-password2").focus();
        return;
    } else {
        $("#help-password2")
            .text("Kata sandi cocok")
            .removeClass("is-danger")
            .addClass("is-success");
    }

    // Mengirim permintaan POST menggunakan AJAX untuk proses sign up
    $.ajax({
        type: "POST",
        url: "/sign_up/save",
        data: {
            username_give: username,
            password_give: password,
        },
        success: function (response) {
            Swal.fire({
                title: 'Berhasil mendaftar!',
                text: 'Silakan masuk!',
                icon: 'success'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = "/login";
                }
            });
        },
    });
}

function toggle_sign_up() {
    // Toggle tampilan kotak sign up dan elemen terkait
    $("#sign-up-box").toggleClass("is-hidden");
    $("#div-sign-in-or-up").toggleClass("is-hidden");
    $("#btn-check-dup").toggleClass("is-hidden");
    $("#help-id").toggleClass("is-hidden");
    $("#help-password").toggleClass("is-hidden");
    $("#help-password2").toggleClass("is-hidden");
}

function is_nickname(asValue) {
    // Validasi format nickname menggunakan regular expression
    var regExp = /^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{2,10}$/;
    return regExp.test(asValue);
}

function is_password(asValue) {
    // Validasi format password menggunakan regular expression
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}

function check_dup() {
    // Mendapatkan nilai username dari input
    let username = $("#input-username").val();
    console.log(username);

    // Memvalidasi input username
    if (username === "") {
        $("#help-id")
            .text("Masukkan Nama Pengguna!")
            .removeClass("is-safe")
            .addClass("is-danger");
        $("#input-username").focus();
        return;
    }

    // Memvalidasi format username
    if (!is_nickname(username)) {
        $("#help-id")
            .text(
                "Nama pengguna harus terdiri 2-10 karakter alfabet, angka, atau karakter khusus."
            )
            .removeClass("is-safe")
            .addClass("is-danger");
        $("#input-username").focus();
        return;
    }

    // Menampilkan indikator loading saat melakukan pemeriksaan duplikasi username
    $("#help-id").addClass("is-loading");

    // Mengirim permintaan POST menggunakan AJAX untuk pemeriksaan duplikasi username
    $.ajax({
        type: "POST",
        url: "/sign_up/check_dup",
        data: {
            username_give: username,
        },
        success: function (response) {
            if (response['exists']) {
                // Jika username sudah digunakan
                $("#help-id")
                    .text("Nama pengguna ini sudah digunakan.")
                    .removeClass("is-safe")
                    .addClass("is-danger");
                $("#input-username").focus();
            } else {
                // Jika username tersedia
                $("#help-id")
                    .text("Nama pengguna ini tersedia!")
                    .removeClass("is-danger")
                    .addClass("is-success");
            }
            // Menghapus indikator loading setelah selesai
            $("#help-id").removeClass("is-loading");
        },
    });
}

function clearInputs() {
    // Menghapus nilai input username, password, dan password2
    $('#input-username').val('');
    $('#input-password').val('');
    $('#input-password2').val('');
}
