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
