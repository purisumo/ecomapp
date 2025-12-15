$(document).ready(function () {
  const navCartModal = $(".nav-cart-cont");
  const overlay = $(".overlay");

  $(".nav-cart-cont .close-modal-btn").click(() => {
    navCartModal.removeClass('show-modal');
    overlay.removeClass('show-modal global-overlay');
  });
});