$(document).ready(function () {
    // ==================== PROFILE PICTURE PREVIEW (Vanilla JS) ====================
    const fileInput = document.querySelector('input[name="profile"]');
    const profileImgContainer = document.querySelector('.profile-img');
    const originalProfileHTML = profileImgContainer.innerHTML; // Save original for reset

    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];

            if (!file) {
                profileImgContainer.innerHTML = originalProfileHTML; // Reset if cleared
                return;
            }

            if (!file.type.startsWith('image/')) {
                alert('Please select a valid image file.');
                this.value = '';
                profileImgContainer.innerHTML = originalProfileHTML;
                return;
            }

            const reader = new FileReader();
            reader.onload = function (event) {
                let img = profileImgContainer.querySelector('img');
                if (!img) {
                    img = document.createElement('img');
                    img.classList.add('profile-avatar');
                    profileImgContainer.innerHTML = ''; // Remove icon
                    profileImgContainer.appendChild(img);
                }
                img.src = event.target.result;
                img.alt = 'Profile Preview';
            };
            reader.readAsDataURL(file);
        });
    }

    // ==================== MODALS (jQuery) ====================

    // Open Save Info Confirmation Modal
    $("button[data-modal='save-info']").click(function () {
        $(".modal.confirmation").addClass("show-modal");
        $(".overlay").addClass("show-modal");

        // Important: Give the Confirm button a name so Django can detect it
        $(".modal.confirmation .primary-btn").attr("name", "save-info"); // fixed name
    });

    // Open Change Password Modal
    $("button[data-modal='change-password']").click(function () {
        $(".modal.change-password").addClass("show-modal");
        $(".overlay").addClass("show-modal");

        // Give the Save button in password modal a name
        $(".modal.change-password .primary-btn").attr("name", "change-password");
    });

    // Close modals
    function closeAllModals() {
        $(".modal").removeClass("show-modal");
        $(".overlay").removeClass("show-modal");

        // Optional: clean up button names when closing
        $(".modal .primary-btn").removeAttr("name");
    }

    // Close triggers
    $(".overlay").click(closeAllModals);
    $(".modal .close").click(closeAllModals);
    $(".modal .border-btn-primary2").click(closeAllModals); // All cancel buttons

    // Optional: Close with Escape key
    $(document).keydown(function (e) {
        if (e.key === "Escape") {
            closeAllModals();
        }
    });
});