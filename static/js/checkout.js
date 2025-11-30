$(document).ready(function () {
  const resetContactForm = () => {
    $("#id_contact-id").val('');
    $("#id_contact-num").val('');

    const submitBtn = $(".modal.contact-num button.primary-btn");
    submitBtn.html('');
    submitBtn.attr("name", "");
    submitBtn.attr("type", "button");
  }

  const contactModal = (isVisible) => {
    if (isVisible) {
      $(".modal.contact-num").addClass("show-modal");
      $(".overlay").addClass("show-modal");
    } else {
      $(".modal.contact-num").removeClass("show-modal");
      $(".overlay").removeClass("show-modal");
    }
  };

  // Add contact
  $(".border-btn-primary2[data-modal='add-contact-num']").click(function () {
    const submitBtn = $(".modal.contact-num button.primary-btn");
    submitBtn.html('Save new contact');
    submitBtn.attr("name", "add-contact");
    submitBtn.attr("type", "submit");

    contactModal(true);
  });

  // Edit contact
  $(".float-icon-btn[data-modal='edit-contact']").click(function () {
    const data = $(this).data("info").split("||");
    const [id, contact_num] = data;

    $("#id_contact-id").val(id);
    $("#id_contact-num").val(contact_num);

    const submitBtn = $(".modal.contact-num button.primary-btn");
    submitBtn.html('Save changes');
    submitBtn.attr("name", "edit-contact");
    submitBtn.attr("type", "submit");

    contactModal(true);
  });

  const resetAddressForm = () => {
    $("#id_address-id").val('');
    $("#id_barangay").val('');
    $("#id_drive").val('');
    $("#id_city").val('');

    const submitBtn = $(".modal.address button.primary-btn");
    submitBtn.html('');
    submitBtn.attr("name", "");
    submitBtn.attr("type", "button");
  }

  const addressModal = (isVisible) => {
    if (isVisible) {
      $(".modal.address").addClass("show-modal");
      $(".overlay").addClass("show-modal");
    } else {
      $(".modal.address").removeClass("show-modal");
      $(".overlay").removeClass("show-modal");
    }
  };

  // Add address
  $(".border-btn-primary2[data-modal='add-address']").click(function () {
    const submitBtn = $(".modal.address button.primary-btn");
    submitBtn.html('Save new address');
    submitBtn.attr("name", "add-address");
    submitBtn.attr("type", "submit");

    addressModal(true);
  });

  // Edit address
  $(".float-icon-btn[data-modal='edit-address']").click(function () {
    const data = $(this).data("info").split("||");
    const [id, barangay, drive, city] = data;

    $("#id_address-id").val(id);
    $("#id_barangay").val(barangay);
    $("#id_drive").val(drive);
    $("#id_city").val(city);

    const submitBtn = $(".modal.address button.primary-btn");
    submitBtn.html('Save changes');
    submitBtn.attr("name", "edit-address");
    submitBtn.attr("type", "submit");

    addressModal(true);
  });

  // -------- delete ---------
  const resetConfirmation = () => {
    $("#delete-id").val('');

    const submitBtn = $(".modal.confirmation button.primary-btn");
    submitBtn.attr("name", "");
    submitBtn.attr("type", "button");
  }

  const confirmationModal = (isVisible) => {
    if (isVisible) {
      $(".modal.confirmation").addClass("show-modal");
      $(".overlay").addClass("show-modal");
    } else {
      $(".modal.confirmation").removeClass("show-modal");
      $(".overlay").removeClass("show-modal");
    }
  };

  // delete item
  $(".float-icon-btn[data-modal='delete-item']").click(function () {
    $("#delete-id").val($(this).data('info'));
    $("#delete-id").attr("name", "delete-item-id");
    $(".modal.confirmation .content p span").html('delete this item from your cart');
    $(".modal.confirmation .button-cont").addClass('reverse');

    const submitBtn = $(".modal.confirmation button.primary-btn");
    submitBtn.attr("name", "delete-item");
    submitBtn.attr("type", "submit");

    confirmationModal(true);
  });

  // delete contact
  $(".float-icon-btn[data-modal='delete-contact']").click(function () {
    $("#delete-id").val($(this).data('info'));
    $("#delete-id").attr("name", "delete-contact-id");
    $(".modal.confirmation .content p span").html('delete this contact num');
    $(".modal.confirmation .button-cont").addClass('reverse');

    const submitBtn = $(".modal.confirmation button.primary-btn");
    submitBtn.attr("name", "delete-contact");
    submitBtn.attr("type", "submit");

    confirmationModal(true);
  });

  // delete address
  $(".float-icon-btn[data-modal='delete-address']").click(function () {
    $("#delete-id").val($(this).data('info'));
    $("#delete-id").attr("name", "delete-address-id");
    $(".modal.confirmation .content p span").html('delete this address');
    $(".modal.confirmation .button-cont").addClass('reverse');

    const submitBtn = $(".modal.confirmation button.primary-btn");
    submitBtn.attr("name", "delete-address");
    submitBtn.attr("type", "submit");

    confirmationModal(true);
  });

  // Overlay click to close modal
  $(".overlay").click(function () {
    resetAddressForm();
    addressModal(false);
    confirmationModal(false);
    resetConfirmation();
    resetContactForm();
    contactModal(false);
  });

  // Close button click to close modal
  $("form .close").click(function () {
    resetAddressForm();
    addressModal(false);
    confirmationModal(false);
    resetConfirmation();
    resetContactForm();
    contactModal(false);
  });

  $(".modal.confirmation button.border-btn-primary2").click(function () {
    confirmationModal(false);
    resetConfirmation();
  });

  // ------------------ items checkbox ------------------
  const placeOrderBtn = $(".primary-btn.place-order");

  // Listen for checkbox changes
  $('.item-checkbox').change(function() {
    // Check if any checkboxes are checked
    if ($('.item-checkbox:checked').length > 0) {
      // Enable submit button
      placeOrderBtn.removeClass('disabled');
      placeOrderBtn.attr("type", "submit");
      placeOrderBtn.attr("name", "place-order");
    } else {
      // Disable submit button
      placeOrderBtn.addClass('disabled');
      placeOrderBtn.attr("type", "button");
      placeOrderBtn.attr("name", "");
    }

    // Get the checked item
    var checkedItem = $(this).closest('.item');
    var itemId = checkedItem.data('item-id');
    var itemName = checkedItem.data('item-name');
    var itemPrice = checkedItem.data('item-price');
    var itemQuantity = checkedItem.find('.quantity').val();

    // Check if the item is already in the container
    var itemsContainer = $('#items-container');
    var existingItemRow = itemsContainer.find('.item-row').filter(function() {
      return $(this).find('.name').text() === itemName;
    });

    if ($(this).is(':checked')) {
      // Add the checked item to the items container
      if (existingItemRow.length === 0) {
        var itemRow = $('<div>').addClass('item-row');
        itemRow.append(
          '<input type="hidden" name="item-id" value="' + itemId + '">',
          '<input type="hidden" name="item-qty" value="' + itemQuantity + '">',
          '<p class="name">' + itemName + '</p>',
          '<p class="price">₱' + itemPrice + '</p>',
          '<p class="times">x</p>',
          '<p class="quantity">' + itemQuantity + '</p>',
          '<p class="total">₱' + (itemPrice * itemQuantity) + '</p>'
        );
        itemsContainer.append(itemRow);
      } else {
        // Update the existing item row
        existingItemRow.find('.quantity').text(itemQuantity);
        existingItemRow.find('.total').text('₱' + (itemPrice * itemQuantity));
      }
    } else {
      // Remove the item from the items container
      if (existingItemRow.length > 0) {
        existingItemRow.remove();
      }
    }

    // Compute and render total items, shipping fee, and overall total
    var totalItems = 0;
    var overallTotal = 0;
    itemsContainer.find('.item-row').each(function() {
      totalItems += parseInt($(this).find('.quantity').text());
      overallTotal += parseInt($(this).find('.total').text().replace('₱', ''));
    });
    var shippingFee = parseInt($('#shipping-fee-value').text().replace('₱', ''));
    if (totalItems > 0) {
      overallTotal += shippingFee;
    } else {
      overallTotal = 0;
    }

    $('#total-quantity').text(totalItems);
    $('#overall-total-value').text('₱' + overallTotal);

    // Show/hide shipping fee
    if (totalItems > 0) {
      $('#shipping-fee').show();
    } else {
      $('#shipping-fee').hide();
    }
  });

  // Hide shipping fee initially
  $('#shipping-fee').hide();

  // Listen for quantity input changes
  $('.quantity-input').on('click', '.increase-btn, .decrease-btn', function() {
    var $input = $(this).siblings('.quantity');
    var stock = parseInt($input.attr('max'));
    var value = parseInt($input.val());

    if ($(this).hasClass('increase-btn')) {
      value = Math.min(value + 1, stock);
    } else {
      value = Math.max(value - 1, 1);
    }

    $input.val(value);

    // Update total computation
    var itemPrice = parseFloat($(this).closest('.item').data('item-price'));
    var total = value * itemPrice;
    $(this).closest('.item').find('.total').text('Total: ₱' + total.toFixed(2));

    // Update selected item row
    updateSelectedItemRow($(this).closest('.item'));
  });

  // Listen for quantity input changes (keyboard input)
  $('.quantity-input .quantity').on('input', function() {
    var $input = $(this);
    var stock = parseInt($input.attr('max'));
    var value = parseInt($input.val());

    if (isNaN(value)) {
      $input.val(1);
    } else if (value < 1) {
      $input.val(1);
    } else if (value > stock) {
      $input.val(stock);
    }

    // Update total computation
    var itemPrice = parseFloat($input.closest('.item').data('item-price'));
    var total = parseInt($input.val()) * itemPrice;
    $input.closest('.item').find('.total').text('Total: ₱' + total.toFixed(2));

    // Update selected item row
    updateSelectedItemRow($input.closest('.item'));
  });

  // Function to update selected item row
  function updateSelectedItemRow($item) {
    var itemId = $item.data('item-id');
    var $itemRow = $('#items-container').find('.item-row').filter(function() {
      return $(this).find('.name').text() === $item.find('.name').text();
    });
    
    if ($itemRow.length > 0) {
      // Update item row
      $itemRow.find('input[name="item-qty"]').val($item.find('.quantity-input .quantity').val());
      $itemRow.find('.total').text('₱' + parseFloat($item.find('.total').text().replace('Total: ₱', '')));

      // Update total items, shipping fee, and overall total
      var totalItems = 0;
      var overallTotal = 0;
      $('#items-container').find('.item-row').each(function() {
        totalItems += parseInt($(this).find('.quantity').text());
        overallTotal += parseFloat($(this).find('.total').text().replace('₱', ''));
      });
      overallTotal += parseFloat($('#shipping-fee-value').text().replace('₱', ''));

      $('#total-quantity').text(totalItems);
      $('#overall-total-value').text('₱' + overallTotal.toFixed(2));
    }
  }
});
