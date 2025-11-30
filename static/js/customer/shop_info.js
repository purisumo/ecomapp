$(document).ready(function () {
  $('#follow-btn').on('click', function (e) {
    e.preventDefault();

    const btn = $(this);
    const shopId = btn.data('shop-id');
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    $.ajax({
      url: `/shop/shop_info/${shopId}/toggle_follow/`,
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      success: function (response) {
        if (response.status === 'followed') {
          btn.html('<i class="bi bi-dash-circle"></i>Unfollow');
        } else {
          btn.html('<i class="bi bi-plus-circle"></i>Follow');
        }

        $('#followers-count').text(response.followers);
      },
      error: function (xhr) {
        alert('Something went wrong: ' + xhr.status);
      }
    });
  });


  const listOfItemsBtn = $(".switch-cont button[data-cont='items']");
  const listOfRatingsBtn = $(".switch-cont button[data-cont='ratings']");
  const itemsSection = $(".customer-info-page .page-wrapper .items-section");
  const ratesSection = $(".customer-info-page .page-wrapper .rates-section");

  if (itemsSection.hasClass('show-section')) {
    ratesSection.hide();
  } else {
    itemsSection.hide();
  }

  // List of Items click
  listOfItemsBtn.click(function () {
    listOfRatingsBtn.addClass('transparent');
    $(this).removeClass('transparent');

    if (!itemsSection.hasClass('show-section')) {
      ratesSection.removeClass('show-section');
      ratesSection.hide();
      itemsSection.addClass('show-section');
      itemsSection.show();
    }
  });

  // List of Ratings click
  listOfRatingsBtn.click(function () {
    listOfItemsBtn.addClass('transparent');
    $(this).removeClass('transparent');

    if (!ratesSection.hasClass('show-section')) {
      itemsSection.removeClass('show-section');
      itemsSection.hide();
      ratesSection.addClass('show-section');
      ratesSection.show();
    }
  });


  // Rate shop
  const rateShopModal = $(".modal.rate-shop");
  const overlay = $(".overlay");

  $(".user-info button[data-modal='rate-shop']").click(function () {
    $("#item-id").val($(this).data("id"));

    rateShopModal.addClass("show-modal"); // Show modal
    overlay.addClass("show-modal"); // Show overlay
  });

  $(".rating-star-buttons button").click(function () {
    const selectedIndex = parseInt($(this).data("index"));

    // Set the hidden input value
    $("#rating-value").val(selectedIndex);

    // Loop through all stars
    $(".rating-star-buttons button").each(function () {
      const starIndex = parseInt($(this).data("index"));
      const icon = $(this).find("i");

      if (starIndex <= selectedIndex) {
        icon.removeClass("bi-star").addClass("bi-star-fill");
      } else {
        icon.removeClass("bi-star-fill").addClass("bi-star");
      }
    });
  });

  const closeModal = () => {
    $(".modal").removeClass("show-modal"); // Hide modal
    overlay.removeClass("show-modal"); // Hide overlay
  }

  rateShopModal.find(".border-btn-primary2").click(() => closeModal);
  overlay.click(() => closeModal);
  $(".modal .close").click(() => closeModal);
});
