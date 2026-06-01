// COURTBOOKING — MAIN JS
// Animations, micro-interactions, toast notifications
// Vanilla JS only — không dùng thư viện ngoài

document.addEventListener('DOMContentLoaded', function () {

    // -------- TOAST NOTIFICATIONS --------
    // Khởi tạo tất cả Bootstrap Toast đã được render từ server
    document.querySelectorAll('.toast').forEach(function (toastEl) {
        new bootstrap.Toast(toastEl, { autohide: true, delay: 4000 }).show();
    });

    // -------- NAVBAR SHADOW KHI SCROLL --------
    var navbar = document.querySelector('.navbar');
    if (navbar) {
        var rafPending = false;
        window.addEventListener('scroll', function () {
            if (rafPending) return;
            rafPending = true;
            requestAnimationFrame(function () {
                // Toggle class nav-scrolled khi cuộn quá 10px
                navbar.classList.toggle('nav-scrolled', window.scrollY > 10);
                rafPending = false;
            });
        }, { passive: true });
    }

    // -------- HEART BOUNCE KHI CLICK FAVORITE --------
    document.querySelectorAll('.court-fav-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            // Xóa class cũ trước để restart animation khi click liên tiếp
            btn.classList.remove('heart-pop');
            // Force reflow — buộc browser acknowledge việc xóa class
            void btn.offsetWidth;
            btn.classList.add('heart-pop');
            // Dọn class sau khi animation xong (form vẫn submit bình thường)
            btn.addEventListener('animationend', function () {
                btn.classList.remove('heart-pop');
            }, { once: true });
        });
    });

});
