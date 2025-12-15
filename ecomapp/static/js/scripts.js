$(document).ready(function () {
  const wishlistProducts = JSON.parse(
    document.getElementById("wishlist-products")?.textContent || "[]"
  );

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

  const chatId = $("#chat-id").val();
  const userUsername = $("#user-username").val();
  const messagesUrl = $("#messages-url").val();
  const sendUrl = $("#send-url").val();

  if (chatId) {
    // Fetch messages initially and every 5 seconds
    function loadMessages() {
      $.ajax({
        url: messagesUrl,
        method: "GET",
        success: function (data) {
          $("#chat-messages").empty();
          data.messages.forEach(function (msg) {
            const messageClass =
              msg.sender === userUsername ? "sent" : "received";
            $("#chat-messages").append(
              `<div class="message ${messageClass}">
                <small>(${new Date(
                msg.sent_at
              ).toLocaleString()})</small>
                <strong>${msg.sender}:</strong> ${msg.content}
              </div>`
            );
          });
          $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
        },
        error: function (xhr) {
          console.error("Error fetching messages:", xhr.responseText);
        },
      });
    }

    loadMessages();
    setInterval(loadMessages, 5000); // Poll every 5 seconds

    // Send message
    $("#send-message").click(function () {
      const content = $("#message-input").val().trim();
      if (content) {
        $.ajax({
          url: sendUrl,
          method: "POST",
          contentType: "application/json",
          data: JSON.stringify({ content: content }),
          headers: {
            "X-CSRFToken": getCookie("csrftoken"),
          },
          success: function (data) {
            $("#message-input").val("");
            loadMessages(); // Refresh messages
          },
          error: function (xhr) {
            console.error("Error sending message:", xhr.responseText);
          },
        });
      }
    });

    // Allow sending message with Enter key
    $("#message-input").keypress(function (e) {
      if (e.which === 13 && !e.shiftKey) {
        e.preventDefault();
        $("#send-message").click();
      }
    });
  }

  $("#signup-form").submit(function (e) {
    e.preventDefault();
    $.ajax({
      url: "/shop/signup/",
      method: "POST",
      data: $(this).serialize(),
      success: function (data) {
        if (data.success) {
          window.location.href = data.redirect;
        }
      },
      error: function (xhr) {
        $(".error").empty();
        let errors;
        try {
          errors = JSON.parse(xhr.responseText).errors;
        } catch (e) {
          errors = {
            non_field_errors: ["An error occurred. Please try again."],
          };
        }
        for (const [field, messages] of Object.entries(errors)) {
          messages.forEach(function (message) {
            $(".error").append(`<p>${message}</p>`);
          });
        }
      },
    });
  });

  $("#login-form").submit(function (e) {
    e.preventDefault();
    $.ajax({
      url: "/shop/login/",
      method: "POST",
      data: $(this).serialize(),
      success: function (data) {
        if (data.success) {
          window.location.href = data.redirect;
        }
      },
      error: function (xhr) {
        $(".error").empty();
        let errors;
        try {
          errors = JSON.parse(xhr.responseText).errors;
        } catch (e) {
          errors = { non_field_errors: ["Invalid username or password."] };
        }
        for (const [field, messages] of Object.entries(errors)) {
          messages.forEach(function (message) {
            $(".error").append(`<p>${message}</p>`);
          });
        }
      },
    });
  });

  $("#product-form").submit(function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    $.ajax({
      url: $(this).attr("action") || window.location.pathname,
      method: "POST",
      data: formData,
      processData: false,
      contentType: false,
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          window.location.href = data.redirect;
        }
      },
      error: function (xhr) {
        $(".error").empty();
        let errors;
        try {
          errors = JSON.parse(xhr.responseText).errors;
        } catch (e) {
          errors = {
            non_field_errors: ["An error occurred. Please try again."],
          };
        }
        for (const [field, messages] of Object.entries(errors)) {
          messages.forEach(function (message) {
            $(".error").append(`<p>${message}</p>`);
          });
        }
      },
    });
  });

  $("#shop-form").submit(function (e) {
    e.preventDefault();
    $.ajax({
      url: "/shop/seller/shop/edit/",
      method: "POST",
      data: $(this).serialize(),
      success: function (data) {
        if (data.success) {
          window.location.href = data.redirect;
        }
      },
      error: function (xhr) {
        $(".error").empty();
        let errors;
        try {
          errors = JSON.parse(xhr.responseText).errors;
        } catch (e) {
          errors = {
            non_field_errors: ["An error occurred. Please try again."],
          };
        }
        for (const [field, messages] of Object.entries(errors)) {
          messages.forEach(function (message) {
            $(".error").append(`<p>${message}</p>`);
          });
        }
      },
    });
  });

  $("#order-form").submit(function (e) {
    e.preventDefault();
    $.ajax({
      url: "/shop/api/orders/create/",
      method: "POST",
      data: $(this).serialize(),
      success: function (data) {
        if (data.success) {
          window.location.href = data.redirect;
        }
      },
      error: function (xhr) {
        $(".error").empty();
        let errors;
        try {
          errors = JSON.parse(xhr.responseText).errors;
        } catch (e) {
          errors = {
            non_field_errors: ["An error occurred. Please try again."],
          };
        }
        for (const [field, messages] of Object.entries(errors)) {
          messages.forEach(function (message) {
            $(".error").append(`<p>${message}</p>`);
          });
        }
      },
    });
  });

  $(document).on("click", ".add-to-cart", function () {
    const productId = $("#item-id").val();
    if (!productId) {
      console.error("Product ID is undefined in modal");
      alert("Error: Product ID not found. Please try again.");
      return;
    }
    $.ajax({
      url: `/shop/api/cart/add/${productId}/`,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ quantity: 1 }),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          appendNotification("Item added to cart!", "success");
          location.reload();
        }
      },
      error: function (xhr) {
        const errorMsg = xhr.responseJSON?.error || "Unknown error";
        appendNotification("Error adding to cart! <br/>" + errorMsg, "error");
      }
    });
  });

  $(document).on("click", ".delete-cart-item", function () {
    const cartItemId = $(this).data("id");
    if (!cartItemId) {
      console.error("Cart Item ID is undefined");
      alert("Error: Cart Item ID not found. Please try again.");
      return;
    }
    $.ajax({
      url: `/shop/api/cart/delete/${cartItemId}/`,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          appendNotification("Item removed from cart!", "success");
          location.reload();
        }
      },
      error: function (xhr) {
        alert(
          "Error deleting cart item: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  $(document).on("click", ".add-to-wishlist", function () {
    const productId = $("#item-id").val();
    if (!productId) {
      console.error("Product ID is undefined");
      alert("Error: Product ID not found. Please try again.");
      return;
    }
    $.ajax({
      url: `/shop/api/wishlist/add/${productId}/`,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          appendNotification("Item added to wish list!", "success");
        }
      },
      error: function (xhr) {
        alert(
          "Error adding to wishlist: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  $(document).on("click", ".add-review", function () {
    const productId = $("#item-id").val();
    if (!productId) {
      console.error("Product ID is undefined");
      alert("Error: Product ID not found. Please try again.");
      return;
    }
    const rating = prompt("Enter rating (1-5):");
    const comment = prompt("Enter comment:");
    if (rating && comment) {
      $.ajax({
        url: `/shop/api/reviews/add/${productId}/`,
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ rating: rating, comment: comment }),
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        success: function (data) {
          if (data.success) {
            alert("Review submitted!");
          }
        },
        error: function (xhr) {
          alert(
            "Error submitting review: " +
            (xhr.responseJSON?.error || "Unknown error")
          );
        },
      });
    }
  });

  $(document).on("change", ".quantity", function () {
    const cartItemId = $(this).closest(".cart-item").data("id");
    const quantity = $(this).val();
    $.ajax({
      url: `/shop/api/cart/update/${cartItemId}/`,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ quantity: quantity }),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          location.reload();
        }
      },
      error: function (xhr) {
        alert(
          "Error updating cart item: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  $(document).on("click", ".delete-wishlist-item", function () {
    const productId = $(this).closest(".wishlist-item").data("id");
    $.ajax({
      url: `/shop/api/wishlist/delete/${productId}/`,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          location.reload();
        }
      },
      error: function (xhr) {
        alert(
          "Error deleting wishlist item: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  $(document).on("click", ".cancel-order", function () {
    const orderId = $(this).closest(".order").data("id");
    $.ajax({
      url: `/shop/api/orders/cancel/${orderId}/`,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          location.reload();
        }
      },
      error: function (xhr) {
        alert(
          "Error cancelling order: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  $(document).on("submit", ".review-form", function (e) {
    e.preventDefault();
    const reviewId = $(this).data("id");
    const productId = $(this).data("product-id");
    const url = reviewId
      ? `/shop/api/reviews/update/${reviewId}/`
      : `/shop/api/reviews/add/${productId}/`;
    const data = {
      rating: $(this).find(".rating").val(),
      comment: $(this).find(".comment").val(),
    };
    $.ajax({
      url: url,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(data),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          location.reload();
        }
      },
      error: function (xhr) {
        alert(
          "Error saving review: " + (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  $(document).on("click", ".delete-review", function () {
    const reviewId = $(this).closest(".review").data("id");
    $.ajax({
      url: `/shop/api/reviews/delete/${reviewId}/`,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          location.reload();
        }
      },
      error: function (xhr) {
        alert(
          "Error deleting review: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  $(document).on("click", ".delete-product", function () {
    const productId = $(this).closest(".product").data("id");
    $.ajax({
      url: `/shop/seller/product/delete/${productId}/`,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          location.reload();
        }
      },
      error: function (xhr) {
        alert(
          "Error deleting product: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  $(document).on("click", ".edit-product", function () {
    const productId = $(this).closest(".product").data("id");
    if (!productId) {
      console.error("Product ID is undefined");
      alert("Error: Product ID not found. Please try again.");
      return;
    }
    window.location.href = `/shop/seller/product/edit/${productId}/`;
  });

  function capitalizeFirst(text) {
    if (!text) return '';
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  }

  $(document).on("change", ".order-status", function () {
    const orderId = $(this).closest(".order").data("id");
    const status = $(this).val();
    $.ajax({
      url: `/shop/seller/order/update/${orderId}/`,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ status: status }),
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          location.reload();
        }
      },
      error: function (xhr) {
        alert(
          "Error updating order status: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  function decodeDescription(description) {
    if (!description) return "No description available.";
    
    try {
      // Decode Unicode escape sequences
      const decoded = description.replace(/\\u([0-9A-Fa-f]{4})/g, function(match, code) {
        return String.fromCharCode(parseInt(code, 16));
      });
      
      // Replace newlines with <br> tags for HTML display
      return decoded.replace(/\n/g, '<br>');
    } catch (error) {
      console.error('Error decoding description:', error);
      return description;
    }
  }

  $(document).on("click", ".item", function () {
    const item = $(this);
    const productId = item.data("id");
    const name = item.data("name");
    const price = item.data("price");
    const description = item.data("description");
    const material = item.data("material");
    const type = item.data("type");
    const image = item.data("image");
    const sellerName = item.data("seller-name");
    const sellerRating = item.data("seller-rating");
    const sellerProducts = item.data("seller-products");
    const sellerFollowers = item.data("seller-followers");
    const sellerproductsSold = item.data("products-sold");
    const sellerSold = item.data("seller-sold");
    const shopId = item.data("shop-id");
    const rating = item.data("rating");
    const isInCart = item.data('is-in-cart') === 'True' ? true : false;
    const isAvailable = item.data('is-available') === 'True' ? true : false;

    $("#item-id").val(productId);
    $("#item-info-modal .name").text(name || "Unknown Product");
    $("#item-info-modal .price").text(`₱${price || "0"}`);
    $("#item-info-modal .rating span").text(rating || "4.6");
    $("#item-info-modal .details").html(
      decodeDescription(description || "No description available.")
    );
    $("#item-info-modal .material").text(capitalizeFirst(material) || "Unknown Material");
    $("#item-info-modal .type").text(capitalizeFirst(type) || "Unknown Type");
    $("#item-info-modal .seller-name").text(sellerName || "Unknown Seller");
    $("#item-info-modal .seller .rating span").text(sellerRating || "0");
    $("#item-info-modal .products span").text(sellerProducts || "0");
    $("#item-info-modal .followers span").text(sellerFollowers || "0");
    $("#item-info-modal .products-sold span").text(sellerproductsSold || "0");
    $("#item-info-modal .sold span").text(sellerSold || "0");
    $("#item-info-modal .item-img img").attr("src", image);
    $("#item-info-modal .seller .wrap").attr(
      "href",
      shopId ? `/shop/shop_info/${shopId}/` : "#"
    );
    $("#item-info-modal .add-to-cart").prop('disabled', isInCart || !isAvailable);

    // Check if product is in wishlist
    const inWishlist = wishlistProducts.some(product => product.id === productId);
    const wishlistBtn = $("#item-info-modal .wishlist-btn");
    wishlistBtn.text(inWishlist ? "Remove from Wish list" : "Add to Wish list");
    wishlistBtn.toggleClass("in-wishlist", inWishlist);
    wishlistBtn.data("in-wishlist", inWishlist);
  });

  // Buy now
  $(document).on("click", ".buy-now", function () {
    const productId = $("#item-id").val();
    $.ajax({
      url: `/shop/api/buy-now/${productId}/`,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          window.location.href = data.redirect;
        }
      },
      error: function (xhr) {
        alert(
          "Error processing buy now: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  // Wishlist toggle
  $(document).on("click", ".wishlist-btn", function () {
    const productId = parseInt($("#item-id").val());
    const inWishlist = $(this).data("in-wishlist");
    const url = inWishlist
      ? `/shop/api/wishlist/delete/${productId}/`
      : `/shop/api/wishlist/add/${productId}/`;
    $.ajax({
      url: url,
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      success: function (data) {
        if (data.success) {
          const newInWishlist = !inWishlist;
          $(this).text(
            newInWishlist ? "Remove from Wishlist" : "Add to Wishlist"
          );
          $(this).toggleClass("in-wishlist", newInWishlist);
          $(this).data("in-wishlist", newInWishlist);

          appendNotification(newInWishlist ? "Item added to wish list!" : "Item removed from wish list!", "success");
          location.reload();

          // Update wishlistProducts array
          if (newInWishlist) {
            wishlistProducts.push(productId);
          } else {
            wishlistProducts.splice(wishlistProducts.indexOf(productId), 1);
          }
        }
      }.bind(this),
      error: function (xhr) {
        alert(
          "Error updating wishlist: " +
          (xhr.responseJSON?.error || "Unknown error")
        );
      },
    });
  });

  // Category filter
  $("#category-filter").change(function () {
    const categoryId = $(this).val();
    $(".item").each(function () {
      const productCategory = $(this).data("category-id");
      if (!categoryId || productCategory == categoryId) {
        $(this).show();
      } else {
        $(this).hide();
      }
    });
  });

  // Function to get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
