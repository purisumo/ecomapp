$(document).ready(function () {
  // Add to Cart button click
  $(".border-btn-primary2[data-modal='add-cart']").click(function () {
    $(".modal").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay

    // Update the submit button to Add to Cart
    const submitBtn = $(".modal button.primary-btn");
    submitBtn.html('<i class="bi bi-cart-plus"></i>Add to cart');
    submitBtn.attr("name", "add-cart");
    submitBtn.attr("value", "add-cart");
    submitBtn.attr("type", "submit");
  });

  // Buy Now button click
  $(".primary-btn[data-modal='buy-now']").click(function () {
    $(".modal").addClass("show-modal"); // Show modal
    $(".overlay").addClass("show-modal"); // Show overlay

    // Update the submit button to Buy Now
    const submitBtn = $(".modal button.primary-btn");
    submitBtn.html('<i class="bi bi-wallet2"></i>Buy now');
    submitBtn.attr("name", "buy-now");
    submitBtn.attr("value", "buy-now");
    submitBtn.attr("type", "submit");
  });

  // Overlay click to close modal
  $(".overlay").click(function () {
    $(".modal").removeClass("show-modal"); // Hide modal
    $(".overlay").removeClass("show-modal"); // Hide overlay

    const submitBtn = $(".modal button.primary-btn");
    submitBtn.attr("name", "");
    submitBtn.attr("type", "button");
  });

  // Close button click to close modal
  $("form .close").click(function () {
    $(".modal").removeClass("show-modal"); // Hide modal
    $(".overlay").removeClass("show-modal"); // Hide overlay

    const submitBtn = $(".modal button.primary-btn");
    submitBtn.attr("name", "");
    submitBtn.attr("type", "button");
  });

  // Quantity increment/decrement logic
  $(".quantity-input button").click(function () {
    const input = $("#quantity");
    const totalElement = $(".total.row p");
    const maxStock = parseInt($(".stock.row p").text(), 10); // Get the available stock from the DOM
    const itemPrice = parseFloat($(".price.row p").text().replace('₱', '')); // Get the item price from the DOM
    let value = parseInt(input.val(), 10);

    if ($(this).text() === "+") {
      if (value < maxStock) {
        value += 1;
      }
    } else if (value > 1) {
      value -= 1;
    }

    input.val(value);    
    totalElement.text(`$${(value * itemPrice).toFixed(2)}`); // Update the total price
  });
});
