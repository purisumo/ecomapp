$(document).ready(function () {
  const navProfileModal = $(".link-cont[data-modal='nav-profile']");
  const navNotifModal = $(".link-cont[data-modal='nav-notif']");
  const navCartModal = $(".nav-cart-cont");
  const overlay = $(".overlay");

  const closeAllModals = () => {
    navProfileModal.removeClass('show-modal');
    navNotifModal.removeClass('show-modal');
    navCartModal.removeClass('show-modal');
  }

  const toggleModal = (targetModal) => {
    const isOpen = targetModal.hasClass('show-modal');
    closeAllModals();

    if (!isOpen) {
      targetModal.addClass('show-modal');

      if (targetModal === navCartModal) { overlay.removeClass('show-modal-transparent'); overlay.addClass('show-modal global-overlay'); } else overlay.addClass('show-modal-transparent');
    }
  }

  $(".profile-wrapper[data-modal='nav-profile']").click(() => toggleModal(navProfileModal));
  $(".ghost-btn[data-modal='nav-notif']").click(() => toggleModal(navNotifModal));
  $(".ghost-btn[data-modal='nav-cart']").click(() => toggleModal(navCartModal));

  overlay.click(() => closeAllModals());

  $(document).on('click', '.notification-link', function (e) {
    e.preventDefault(); // prevent immediate redirection

    const notifId = $(this).data('notif-id');
    const redirectUrl = $(this).attr('href');

    if (!notifId || !redirectUrl) return;

    $.ajax({
      url: "/shop/notification/mark-read/",
      type: "POST",
      data: {
        notif_id: notifId,
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
      },
      success: function (response) {
        if (response.success) {
          // Optional: Update unread count visually here
          window.location.href = redirectUrl; // redirect after marking as read
        } else {
          console.error("Notification read error:", response.error);
          // fallback redirect anyway
          window.location.href = redirectUrl;
        }
      },
      error: function () {
        // fallback redirect in case of server failure
        window.location.href = redirectUrl;
      }
    });
  });
});