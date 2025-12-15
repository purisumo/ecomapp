$(document).ready(function () {
  // Save user info confirmation modal
  $("button[data-modal='save-info']").click(() => {
    $(".modal.confirmation").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay

    const submitBtn = $(".modal.confirmation .button-cont-below button.primary-btn");
    submitBtn.attr("name", "save-infos");
  })

  // Chane password modal
  $("button[data-modal='change-password']").click(() => {
    $(".modal.change-password").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay

    const submitBtn = $(".modal.changepassword .button-cont-below button.primary-btn");
    submitBtn.attr("name", "change-password");
  })

  // Overlay and close click
  const closeModal = () => {
    $(".modal").removeClass("show-modal");
    $(".overlay").removeClass("show-modal");
  }

  $(".overlay").click(() => closeModal())
  $(".modal.confirmation .close").click(() => closeModal())
  $(".modal.confirmation .button-cont-below button.border-btn-primary2").click(() => closeModal())
  $(".modal.change-password .close").click(() => closeModal())
  $(".modal.change-password .button-cont-below button.border-btn-primary2").click(() => closeModal())
});
