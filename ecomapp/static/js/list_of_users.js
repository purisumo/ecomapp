$(document).ready(function () {
  // Filtering
  const filterBtns = $('.list-of-orders-page .sub-navbar button.border-btn-primary2');
  const pageContainer = $('.list-of-orders-page .page-container');
  const contentSections = pageContainer.find('.content-section');

  // contentSections.hide();

  filterBtns.click(function () {
    filterBtns.removeClass('selected');
    $(this).addClass('selected');

    contentSections.removeClass('show-section');
    pageContainer.find($(this).data('view')).addClass('show-section');
  });

  const modal = $("#update-order-status-modal");

  // Reusable modal setup function
  function openConfirmationModal(actionType, orderId) {
    const overlay = $(".overlay");
    const contentWrap = modal.find(".content-wrap p");
    const confirmBtn = modal.find(".button-cont-below button[type='submit']");

    modal.addClass("show-modal");
    overlay.addClass("show-modal");

    // Set order ID
    modal.find("input#selected-id").val(orderId);

    // Reset classes
    confirmBtn.removeClass("primary-btn delete-btn");

    // Set modal content and button based on action type
    if (actionType === "ban-account") {
      contentWrap.html(`Are you sure you want to Ban this <b>User account</b>?`);
      confirmBtn.addClass("delete-btn").text("Confirm").attr("name", "ban-account");
    } else if (actionType === "activate-account") {
      contentWrap.html(`Are you sure you want to Activate this <b>user account</b>?`);
      confirmBtn.addClass("primary-btn").text("Confirm").attr("name", "activate-account");
    }
  }

  // Trigger modal based on action
  $(".list-of-orders-page button[data-modal]").click(function () {
    const actionType = $(this).data("modal");
    const orderId = $(this).data("id");

    openConfirmationModal(actionType, orderId);
  });

  // Overlay and close click
  const closeModal = () => {
    $("#update-order-status-modal").removeClass("show-modal");
    $(".overlay").removeClass("show-modal");
    modal.find('input#selected-id').val(''); // Reset value
  }

  $(".overlay").click(() => closeModal());
  $("#update-order-status-modal .close").click(() => closeModal());
  $("#update-order-status-modal .button-cont-below button.border-btn-primary2").click(() => closeModal());
});
