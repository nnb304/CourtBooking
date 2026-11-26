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

// ============================================================
// CUSTOM SPORT DROPDOWN — toggle, select, click-outside-close
// Vanilla JS — không dùng thư viện ngoài
// ============================================================

// MỞ / ĐÓNG DROPDOWN
function toggleSportDropdown() {
    var menu    = document.getElementById('sportDropdownMenu');
    var chevron = document.getElementById('sportChevron');
    if (!menu) return;

    var isOpen = menu.style.display !== 'none';
    menu.style.display = isOpen ? 'none' : 'block';
    if (chevron) chevron.classList.toggle('chevron-rotated', !isOpen);
}

// CHỌN MỘT MỤC TRONG DROPDOWN
function selectSport(el) {
    var value = el.getAttribute('data-value');
    var label = el.getAttribute('data-label');

    // CẬP NHẬT HIDDEN INPUT (giá trị gửi form)
    var hiddenInput = document.getElementById('sportDropdownValue');
    if (hiddenInput) hiddenInput.value = value;

    // CẬP NHẬT LABEL HIỂN THỊ TRÊN TRIGGER
    var labelEl = document.getElementById('sportDropdownLabel');
    if (labelEl) labelEl.textContent = label;

    // CẬP NHẬT TRẠNG THÁI ACTIVE + CHECKMARK
    var wrap = document.getElementById('sportDropdownWrap');
    if (wrap) {
        wrap.querySelectorAll('.sport-dropdown-item').forEach(function (item) {
            item.classList.remove('sport-dropdown-active');
            // Xóa checkmark cũ
            var chk = item.querySelector('.bi-check-lg');
            if (chk) chk.remove();
        });
        // Thêm active + checkmark cho mục vừa chọn
        el.classList.add('sport-dropdown-active');
        var checkIcon = document.createElement('i');
        checkIcon.className = 'bi bi-check-lg';
        checkIcon.style.color = 'var(--primary)';
        el.appendChild(checkIcon);
    }

    // ĐÓNG MENU
    var menu    = document.getElementById('sportDropdownMenu');
    var chevron = document.getElementById('sportChevron');
    if (menu)    menu.style.display = 'none';
    if (chevron) chevron.classList.remove('chevron-rotated');
}

// CLICK BÊN NGOÀI → ĐÓNG DROPDOWN
document.addEventListener('click', function (e) {
    // Sport dropdown
    var sportWrap = document.getElementById('sportDropdownWrap');
    if (sportWrap && !sportWrap.contains(e.target)) {
        var sportMenu    = document.getElementById('sportDropdownMenu');
        var sportChevron = document.getElementById('sportChevron');
        if (sportMenu)    sportMenu.style.display = 'none';
        if (sportChevron) sportChevron.classList.remove('chevron-rotated');
    }

    // District dropdown
    var districtWrap = document.getElementById('districtDropdownWrap');
    if (districtWrap && !districtWrap.contains(e.target)) {
        var districtMenu    = document.getElementById('districtDropdownMenu');
        var districtChevron = document.getElementById('districtChevron');
        if (districtMenu)    districtMenu.style.display = 'none';
        if (districtChevron) districtChevron.classList.remove('chevron-rotated');
    }
});

// ============================================================
// CUSTOM DISTRICT DROPDOWN
// ============================================================

function toggleDistrictDropdown() {
    var menu    = document.getElementById('districtDropdownMenu');
    var chevron = document.getElementById('districtChevron');
    if (!menu) return;

    var isOpen = menu.style.display !== 'none';
    menu.style.display = isOpen ? 'none' : 'block';
    if (chevron) chevron.classList.toggle('chevron-rotated', !isOpen);
}

function selectDistrict(el) {
    var value = el.getAttribute('data-value');
    var label = el.getAttribute('data-label');

    // Cập nhật giá trị
    var hiddenInput = document.getElementById('districtDropdownValue');
    if (hiddenInput) hiddenInput.value = value;

    // Cập nhật nhãn
    var labelEl = document.getElementById('districtDropdownLabel');
    if (labelEl) labelEl.innerHTML = label;

    // Cập nhật active state
    var wrap = document.getElementById('districtDropdownWrap');
    if (wrap) {
        wrap.querySelectorAll('.sport-dropdown-item').forEach(function (item) {
            item.classList.remove('sport-dropdown-active');
            var chk = item.querySelector('.bi-check-lg');
            if (chk) chk.remove();
        });
        el.classList.add('sport-dropdown-active');
        var checkIcon = document.createElement('i');
        checkIcon.className = 'bi bi-check-lg';
        checkIcon.style.color = 'var(--primary)';
        el.appendChild(checkIcon);
    }

    // Đóng menu
    var menu    = document.getElementById('districtDropdownMenu');
    var chevron = document.getElementById('districtChevron');
    if (menu)    menu.style.display = 'none';
    if (chevron) chevron.classList.remove('chevron-rotated');
}

// ============================================================
// CUỘN MƯỢT (Lenis) + HIỆU ỨNG KHI LƯỚT
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // -------- LENIS SMOOTH SCROLL --------
    if (!reduce && window.Lenis) {
        document.documentElement.style.scrollBehavior = 'auto';
        var lenis = new window.Lenis({ duration: 1.15, smoothWheel: true, anchors: true });
        (function raf(t) { lenis.raf(t); requestAnimationFrame(raf); })(0);
        window.cbLenis = lenis;
    }

    // -------- REVEAL CHO CÁC KHỐI CHUNG (card, section title...) --------
    var auto = document.querySelectorAll('main .card, main .feature-tile, main .sport-cat, main .section-title, main h2');
    auto.forEach(function (el) {
        if (!el.closest('.reveal-slide-up') && !el.classList.contains('reveal-slide-up')) el.classList.add('reveal-fx');
    });
    if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting) { e.target.classList.add('revealed'); io.unobserve(e.target); }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
        document.querySelectorAll('.reveal-fx, .reveal-slide-up').forEach(function (el, i) {
            el.style.setProperty('--d', (i % 6) * 60 + 'ms');
            io.observe(el);
        });
    } else {
        document.querySelectorAll('.reveal-fx, .reveal-slide-up').forEach(function (el) { el.classList.add('revealed'); });
    }

    // -------- PARALLAX NHẸ CHO HERO --------
    var hero = document.querySelector('.hero-dark');
    if (hero && !reduce) {
        var copy = hero.querySelector('.hero-copy');
        var glows = hero.querySelectorAll('.hero-glow');
        var ticking = false;
        window.addEventListener('scroll', function () {
            if (ticking) return; ticking = true;
            requestAnimationFrame(function () {
                var y = Math.min(window.scrollY, 700);
                if (copy) { copy.style.transform = 'translate3d(0,' + y * 0.18 + 'px,0)'; copy.style.opacity = String(1 - y / 900); }
                glows.forEach(function (g, i) { g.style.translate = '0 ' + y * (i ? -0.25 : 0.35) + 'px'; });
                ticking = false;
            });
        }, { passive: true });
    }

    // -------- CARD NGHIÊNG THEO CHUỘT (chỉ desktop) --------
    if (!reduce && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
        document.querySelectorAll('.court-card').forEach(function (card) {
            card.addEventListener('mousemove', function (ev) {
                var r = card.getBoundingClientRect();
                var x = (ev.clientX - r.left) / r.width - 0.5, y = (ev.clientY - r.top) / r.height - 0.5;
                card.style.transform = 'translateY(-6px) perspective(900px) rotateX(' + (-y * 5) + 'deg) rotateY(' + (x * 5) + 'deg)';
            });
            card.addEventListener('mouseleave', function () { card.style.transform = ''; });
        });
    }
});
