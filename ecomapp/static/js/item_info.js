$(document).ready(function () {
  const itemInfoModal = $(".modal.item-info");
  const overlay = $(".overlay");

  // Item click
  $(".items-section .item").click(function () {
    $("#item-id").val($(this).data("id"));

    itemInfoModal.addClass("show-modal"); // Show modal
    overlay.addClass("show-modal"); // Show overlay
  });

  // Add to cart button click
  itemInfoModal.find(".border-btn-primary2").click(function () {
    $(".modal").removeClass("show-modal"); // Hide modal
    overlay.removeClass("show-modal"); // Hide overlay
  });

  // Overlay click to close modal
  overlay.click(function () {
    $(".modal").removeClass("show-modal"); // Hide modal
    overlay.removeClass("show-modal"); // Hide overlay
  });

  // Close button click to close modal
  $(".modal .close").click(function () {
    $(".modal").removeClass("show-modal"); // Hide modal
    overlay.removeClass("show-modal"); // Hide overlay
  });
});
