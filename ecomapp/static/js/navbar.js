$(document).ready(function () {
  const profileModal = $(".link-cont[data-modal='nav-profile']");
  const notifModal = $(".link-cont[data-modal='nav-notif']");
  const overlay = $(".overlay");

  $(".profile-wrapper[data-modal='nav-profile']").click(() => {
    if (overlay.hasClass('show-modal-transparent') && notifModal.hasClass('show-modal')) {
      notifModal.removeClass("show-modal")
    }
    else if (profileModal.hasClass('show-modal')) {
      overlay.removeClass("show-modal-transparent")
    }
    else {
      overlay.addClass("show-modal-transparent");
    }

    profileModal.toggleClass("show-modal");
  });

  $(".ghost-btn[data-modal='nav-notif']").click(() => {
    if (overlay.hasClass('show-modal-transparent') && profileModal.hasClass('show-modal')) {
      profileModal.removeClass("show-modal")
    }
    else if (notifModal.hasClass('show-modal')) {
      overlay.removeClass("show-modal-transparent")
    }
    else {
      overlay.addClass("show-modal-transparent");
    }

    notifModal.toggleClass("show-modal");
  })

  overlay.click(() => {
    profileModal.removeClass("show-modal");
    notifModal.removeClass("show-modal");
    overlay.removeClass("show-modal-transparent");
  })
});