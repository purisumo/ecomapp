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
    const cancelBtn = modal.find(".button-cont-below .cancel-btn");

    modal.addClass("show-modal");
    overlay.addClass("show-modal");

    // Set order ID
    modal.find("input#selected-id").val(orderId);

    // Reset classes
    confirmBtn.removeClass("primary-btn delete-btn");

    // Set modal content and button based on action type
    if (actionType === "cancel-order") {
      contentWrap.html(`Are you sure you want to cancel this <b>order</b>?`);
      confirmBtn.addClass("delete-btn").text("Confirm").attr("name", "cancel-order");
    } else if (actionType === "approve-order") {
      contentWrap.html(`Are you sure you want to approve this order and mark it as <b>shipped</b>?`);
      confirmBtn.addClass("primary-btn").text("Confirm").attr("name", "approve-order");
    } else if (actionType === "complete-order") {
      contentWrap.html(`Are you sure you want to mark this order as <b>completed</b>?`);
      confirmBtn.addClass("primary-btn").text("Confirm").attr("name", "complete-order");
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

  const gcashModal = $("#gcash-receipt-modal");
  const fileInput = gcashModal.find('input[type="file"]');
  const previewArea = gcashModal.find('.preview-area');
  const previewImg = $("#receipt-preview");

  // Open modal when clicking upload button
  $(document).on('click', '.gcash-upload-btn', function() {
    const orderId = $(this).data('id');
    gcashModal.find('#gcash-order-id').val(orderId);
    
    // Reset modal
    fileInput.val('');
    previewArea.hide();
    previewImg.attr('src', '');
    
    gcashModal.addClass('show-modal');
    $(".overlay").addClass('show-modal');
  });

  // File preview
  fileInput.on('change', function(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(ev) {
        previewImg.attr('src', ev.target.result);
        previewArea.show();
      };
      reader.readAsDataURL(file);
    } else {
      previewArea.hide();
    }
  });

  $(".overlay").click(() => closeModal());
  $("#update-order-status-modal .close").click(() => closeModal());
  $("#update-order-status-modal .button-cont-below button.border-btn-primary2").click(() => closeModal());
});
