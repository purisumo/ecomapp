$(document).ready(function () {
  // Save button click
  $(".primary-btn[data-modal='save-item']").click(function () {
    $(".modal").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay
    $('.modal .button-cont').removeClass('reverse');

    // Update the submit button to Save item
    const submitBtn = $(".modal button.primary-btn");
    $(".modal p span").html('save this new item info');
    submitBtn.html('Save');
    submitBtn.attr("name", "save");
    submitBtn.attr("type", "submit");
    $('#item_image_file').prop("required", true);
  });

  // Delete button click
  $(".border-btn-delete[data-modal='delete-item']").click(function () {
    $(".modal").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay
    $('.modal .button-cont').addClass('reverse');

    // Update the submit button to Delete item
    const submitBtn = $(".modal button.primary-btn");
    $(".modal p span").html('delete this item');
    submitBtn.html('Confirm');
    submitBtn.attr("name", "delete");
    submitBtn.attr("type", "submit");
    $('#id_image_file').prop("required", false);
  });

  // Overlay click to close modal
  $(".overlay").click(function () {
    $(".modal").removeClass("show-modal"); // Hide modal
    $(".overlay").removeClass("show-modal"); // Hide overlay
    $('.modal .button-cont').removeClass('reverse');

    const submitBtn = $(".modal button.primary-btn");
    submitBtn.attr("name", "");
    submitBtn.attr("type", "button");
  });

  // Close button click to close modal
  $(".modal .close").click(function () {
    $(".modal").removeClass("show-modal"); // Hide modal
    $(".overlay").removeClass("show-modal"); // Hide overlay
    $('.modal .button-cont').removeClass('reverse');

    const submitBtn = $(".modal button.primary-btn");
    submitBtn.attr("name", "");
    submitBtn.attr("type", "button");
  });

  // Close button click to close modal
  $(".modal .cancel-btn").click(function () {
    $(".modal").removeClass("show-modal"); // Hide modal
    $(".overlay").removeClass("show-modal"); // Hide overlay
    $('.modal .button-cont').removeClass('reverse');

    const submitBtn = $(".modal button.primary-btn");
    submitBtn.attr("name", "");
    submitBtn.attr("type", "button");
  });
});
