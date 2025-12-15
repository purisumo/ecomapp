$(document).ready(function () {
  // Image render on upload
  const inputImage = $(".crud_item form .image-cont input[type='file']");
  const output = $(".crud_item form .image-cont #output");
  const span = $(".crud_item form .image-cont span");

  inputImage.on('change', (event) => {
    span.hide();
    output.attr('src', URL.createObjectURL(event.target.files[0]));
    output.show();
  });

  const markAsItemFun = (itemStatus) => {
    $(".modal").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay

    $(".modal p span").html('mark this item as');
    $(".modal p b").html(itemStatus);
    const submitBtn = $(".modal .button-cont-below button.primary-btn");
    submitBtn.attr("name", "mark-" + itemStatus);
  }

  // Modal popup
  // Mark as item Modal
  $("button[data-modal='mark-as']").click(function () { markAsItemFun($(this).data('mark')); })

  // Save Modal
  $("button[data-modal='save-edit']").click(() => {
    $(".modal").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay

    $(".modal p span").html('save this new item info');
    const submitBtn = $(".modal .button-cont-below button.primary-btn");
    submitBtn.html('Save');
    submitBtn.attr("name", "save-edit");
  })

  // Delete Modal
  $("button[data-modal='delete-item']").click(() => {
    $(".modal").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay
    $('.modal .button-cont-below').addClass('reverse');

    const submitBtn = $(".modal .button-cont-below button.primary-btn");
    $(".modal p span").html('delete this item');
    submitBtn.html('Confirm');
    submitBtn.attr("name", "delete");
  })

  // Overlay and close click
  const closeModal = () => {
    $(".modal").removeClass("show-modal");
    $(".overlay").removeClass("show-modal");
    $('.modal .button-cont-below').removeClass('reverse');
  }

  $(".overlay").click(() => closeModal())
  $(".modal.confirmation .close").click(() => closeModal())
  $(".modal.confirmation .button-cont-below button.border-btn-primary2").click(() => closeModal())

  function appendNotification(message, level = 'success') {
    const container = $("#notification-container");
    const notification = $(`
      <div class="notification ${level}">
        ${message}
      </div>
    `);

    container.append(notification);
    notification.fadeIn(200); // Show with animation

    setTimeout(() => {
      notification.fadeOut(400, () => notification.remove());
    }, 3000); // Auto-remove after 3s
  }

  $('form.page-wrapper').on('submit', function (e) {
    let isValid = true;

    // Clear previous errors
    $('.input-cont, .image-cont').removeClass('error-input');
    $('.input-error-message').text('');

    // Validate Name
    const nameInput = $('input[name="name"]');
    if (!nameInput.val().trim()) {
      nameInput.closest('.input-cont').addClass('error-input');
      nameInput.siblings('.input-error-message').text('Name is required.');
      isValid = false;
    }

    // Validate Price
    const priceInput = $('input[name="price"]');
    if (!priceInput.val().trim()) {
      priceInput.closest('.input-cont').addClass('error-input');
      priceInput.siblings('.input-error-message').text('Price is required.');
      isValid = false;
    }

    // Validate Description
    const descInput = $('textarea[name="description"]');
    if (!descInput.val().trim()) {
      descInput.closest('.input-cont').addClass('error-input');
      descInput.siblings('.input-error-message').text('Description is required.');
      isValid = false;
    }

    // Validate Image (only if not editing)
    const imageInput = $('input[name="image"]');
    const hasImage = imageInput.get(0).files.length > 0 || $('#output').attr('src');
    if (!hasImage) {
      imageInput.addClass('error-input');
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault(); // Stop form submission
      appendNotification("Please fill out all required fields.", "error");
    }
  });
});