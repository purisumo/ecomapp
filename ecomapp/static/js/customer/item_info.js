$(document).ready(function () {
  const itemInfoModal = $(".modal.item-info");
  const overlay = $(".overlay");

  // Item click
  $(".item").click(function () {
    $("#item-id").val($(this).data("id"));
    console.log('meow');

    itemInfoModal.addClass("show-modal"); // Show modal
    overlay.addClass("show-modal"); // Show overlay
  });

  const closeModal = () => {
    $(".modal").removeClass("show-modal"); // Hide modal
    overlay.removeClass("show-modal"); // Hide overlay
  }

  // Add to cart or add to wish list button click
  itemInfoModal.find(".add-to-cart").click(() => closeModal());
  itemInfoModal.find(".border-btn-primary2").click(() => closeModal());

  // Overlay click to close modal
  overlay.click(() => closeModal());

  // Close button click to close modal
  $(".modal .close").click(() => closeModal());


});
