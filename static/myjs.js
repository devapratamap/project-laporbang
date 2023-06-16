// Fungsi hapus cookie dan logout
function sign_out() {
    // Menghapus cookie mytoken saat sign out
    // $.removeCookie("mytoken", { path: "/" });
    Swal.fire({
        title: 'Apakah Anda yakin?',
        text: "Anda akan logout dari akun ini!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'OK!',
        cancelButtonText: 'Batal'
    }).then((result) => {
        if (result.isConfirmed) {
            $.removeCookie("mytoken", { path: "/", });
            window.location.href = "/login";
            // Kode JavaScript yang dieksekusi saat tombol "OK" diklik
            // Atau panggil fungsi lain di sini
        }
    });

    // Mengarahkan pengguna ke halaman login setelah sign out

}

// Mengirimkan permintaan AJAX POST untuk mengirim komentar dan tanggal posting ke server,
// lalu memperbarui halaman setelah berhasil.
function post() {
    let alamat = $("#alamat").val()
    let provinsi = $("#provinsi").val()
    let kotakab = $("#kotakab").val()
    let kecamatan = $("#kecamatan").val()
    let deskripsi = $("#deskripsi").val()

    let today = new Date().toISOString()
    $.ajax({
        type: "POST",
        url: "/posting",
        data: {
            alamat: alamat,
            provinsi: provinsi,
            kotakab: kotakab,
            kecamatan: kecamatan,
            deskripsi: deskripsi,
            date_give: today
        },
        success: function (response) {
            $("#modal-post").removeClass("is-active")
            window.location.reload()
        }
    })
}


// Mengkonversi waktu posting menjadi string yang menyatakan waktu yang telah berlalu.
function time2str(date) {
    let today = new Date();
    let time = (today - date) / 1000 / 60;  // minutes

    if (time < 60) {
        return parseInt(time) + " minutes ago";
    }
    time = time / 60;  // hours
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
        return parseInt(count / 1000) + "k"
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k"
    }
    if (count == 0) {
        return ""
    }
    return count
}


// Mengambil posting-posting terkait pengguna tertentu dengan melakukan permintaan AJAX GET 
// ke server dan memperbarui tampilan halaman dengan hasil respons.
function get_posts(username) {
    if (username == undefined) {
        username = "";
    }
    $("#post-box").empty();
    $.ajax({
        type: "GET",
        url: `/get_posts?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response["result"] === "success") {
                let posts = response["posts"];
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i];
                    console.log(post);
                    let time_post = new Date(post["date"]);
                    let time_before = time2str(time_post);
                    let class_heart = post['heart_by_me'] ? "fa-heart" : "fa-heart-o";
                    let class_star = post['star_by_me'] ? "fa-star" : "fa-star-o";
                    let class_thumbsup = post['thumbsup_by_me'] ? "fa-thumbs-up" : "fa-thumbs-o-up";
                    let html_temp = `<div class="card" id="${post["_id"]}">
                    <div class="card-image">
                        <figure class="image is-4by3">
                            <img src="/static/${post["profile_pic_real"]}" alt="Placeholder image">
                        </figure>
                    </div>
                    <div class="card-content">
                        <div class="media">
                            <div class="media-left">
                                <figure class="image is-48x48">
                                    <img src="/static/${post["profile_pic_real"]}">
                                </figure>
                            </div>
                            <div class="media-content">
                                <p class="title is-4">${post["profile_name"]}</p>
                                <p class="subtitle is-6">${post["username"]}</p>
                            </div>
                        </div>
        
                        <div class="content">
                            ${post["alamat"]}
                            <br>
                            ${post["provinsi"]}, ${post["kotakab"]}, ${post["kecamatan"]}
                            <br>
                            <div class="box">
                                <b>${post["deskripsi"]}</b>
                            </div>
                            <time datetime="2016-1-1">${time_before}</time>
                        </div>
                        <nav class="level is-mobile">
                            <div class="level-left">
                                <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post["_id"]}', 'heart')">
                                    <span class="icon is-small"><i class="fa ${class_heart}" aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post['count_heart'])}</span>
                                </a>
                                <a class="level-item is-sparta" aria-label="star" onclick="toggle_star('${post["_id"]}', 'star')">
                                    <span class="icon is-small"><i class="fa ${class_star}" aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post['count_star'])}</span>
                                </a>
                                <a class="level-item is-sparta" aria-label="thumbsup" onclick="toggle_thumbsup('${post["_id"]}', 'thumbsup')">
                                    <span class="icon is-small"><i class="fa ${class_thumbsup}" aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post['count_thumbsup'])}</span>
                                </a>
                            </div>
                        </nav>
                    </div>
                </div>`;
                    $("#post-box").append(html_temp);
                }
            }
        },
    });
}


// Mengirimkan permintaan AJAX POST untuk menambah atau menghapus tindakan 
// "like", 
// "star", atau 
// "thumbs-up" 
// pada suatu posting, lalu memperbarui tampilan halaman setelah berhasil.
function toggle_like(post_id, type) {
    console.log(post_id, type);
    let $a_like = $(`#${post_id} a[aria-label='heart']`);
    let $i_like = $a_like.find("i");
    if ($i_like.hasClass("fa-heart")) {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike",
            },
            success: function (response) {
                console.log("unlike");
                $i_like.addClass("fa-heart-o").removeClass("fa-heart");
                $a_like.find("span.like-num").text(num2str(response["count"]));
            },
        });
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like",
            },
            success: function (response) {
                console.log("like");
                $i_like.addClass("fa-heart").removeClass("fa-heart-o");
                $a_like.find("span.like-num").text(num2str(response["count"]));
            },
        });
    }
}

function toggle_star(post_id, type) {
    console.log(post_id, type);
    let $a_like = $(`#${post_id} a[aria-label='star']`);
    let $i_like = $a_like.find("i");
    if ($i_like.hasClass("fa-star")) {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike",
            },
            success: function (response) {
                console.log("unlike");
                $i_like.addClass("fa-star-o").removeClass("fa-star");
                $a_like.find("span.like-num").text(num2str(response["count"]));
            },
        });
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like",
            },
            success: function (response) {
                console.log("like");
                $i_like.addClass("fa-star").removeClass("fa-star-o");
                $a_like.find("span.like-num").text(num2str(response["count"]));
            },
        });
    }
}

function toggle_thumbsup(post_id, type) {
    console.log(post_id, type);
    let $a_like = $(`#${post_id} a[aria-label='thumbsup']`);
    let $i_like = $a_like.find("i");
    if ($i_like.hasClass("fa-thumbs-up")) {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike",
            },
            success: function (response) {
                console.log("unlike");
                $i_like.addClass("fa-thumbs-o-up").removeClass("fa-thumbs-up");
                $a_like.find("span.like-num").text(num2str(response["count"]));
            },
        });
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like",
            },
            success: function (response) {
                console.log("like");
                $i_like.addClass("fa-thumbs-up").removeClass("fa-thumbs-o-up");
                $a_like.find("span.like-num").text(num2str(response["count"]));
            },
        });
    }
}


