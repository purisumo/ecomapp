$(document).ready(function () {
  const $allBtns = $('.computations .container-box');
  const $weeklySelect = $('#weekly-select');
  const $monthlySelect = $('#monthly-select');

  const $invoiceSection = $('#invoice-section');
  const $itemsSection = $('#items-section');

  const $sectionTitle = $('#section-title');
  const $statsDetails = $('#stats-details');
  const $ordersList = $('#orders-list');
  const $productItems = $('.items-section .item');

  const allOrders = JSON.parse(document.getElementById('all-orders-data')?.textContent || '[]');
  const currentYear = new Date().getFullYear();

  // Initial hide dropdowns
  $weeklySelect.hide();
  $monthlySelect.hide();

  // Initial: show invoice, hide items
  $invoiceSection.addClass('show-section');
  $itemsSection.removeClass('show-section');

  function getDateRange(type, options = {}) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    if (type === 'today') {
      return { start: today, end: new Date(today.getTime() + 86400000), name: 'Today' };
    } else if (type === 'weekly') {
      const monday = new Date(options.startDate || $weeklySelect.val());
      return { start: monday, end: new Date(monday.getTime() + 7 * 86400000), name: $weeklySelect.find('option:selected').text() };
    } else if (type === 'monthly') {
      const month = options.month || parseInt($monthlySelect.val());
      return {
        start: new Date(currentYear, month - 1, 1),
        end: new Date(currentYear, month, 1),
        name: $monthlySelect.find('option:selected').text()
      };
    } else {
      return { start: new Date(0), end: new Date(9999, 0, 1), name: 'All Time' };
    }
  }

  function renderInvoice(type, options = {}) {
    const { start, end, name } = getDateRange(type, options);

    $sectionTitle.text(`${name}'s Invoice`);

    const filteredOrders = allOrders.filter(order => {
      const orderDate = new Date(order.created_at);
      return orderDate >= start && orderDate < end;
    });

    // Items Ordered by type
    const typeSales = { necklace: 0, bangle: 0, earings: 0, ring: 0 };
    filteredOrders.forEach(order => {
      if (order.product_type) {
        const t = order.product_type.toLowerCase().trim();
        if (t in typeSales) typeSales[t]++;
      }
    });

    const itemsHtml = ['necklace', 'bangle', 'earings', 'ring']
      .map(t => `<p class="info">${t.charAt(0).toUpperCase() + t.slice(1)}: ${typeSales[t]}</p>`)
      .join('');

    const statusCounts = { pending: 0, shipped: 0, completed: 0, cancelled: 0 };
    filteredOrders.forEach(o => statusCounts[o.status]++);

    const totalOrders = filteredOrders.length;
    const totalCustomers = new Set(filteredOrders.map(o => o.customer_id)).size;
    const revenue = filteredOrders.filter(o => o.status === 'completed').reduce((sum, o) => sum + o.total_amount, 0);

    $statsDetails.html(`
      <div class="container">
        <p class="sub-title">Items Ordered</p>
        ${itemsHtml}
      </div>
      <div class="container">
        <p class="sub-title">Orders</p>
        <p class="info">Pending: ${statusCounts.pending}</p>
        <p class="info">Shipped: ${statusCounts.shipped}</p>
        <p class="info">Completed: ${statusCounts.completed}</p>
        <p class="info">Cancelled: ${statusCounts.cancelled}</p>
      </div>
      <div class="container">
        <p class="sub-title">Total</p>
        <p class="info">Total Orders: ${totalOrders}</p>
        <p class="info">Total Customers: ${totalCustomers}</p>
        <p class="info">Total Revenue: <span class="currency">₱</span>${revenue.toFixed(2)}</p>
      </div>
    `);

    if (filteredOrders.length === 0) {
      $ordersList.html(`
        <div class="empty-content" style="margin:20% 0; text-align:center;">
          <p>You have no orders ${name.toLowerCase()}.</p>
        </div>
      `);
    } else {
      const ordersHtml = filteredOrders.map(order => `
        <div class="order-item">
          <div class="image-container" style="height:fit-content; margin:auto 0;">
            ${order.product_image
          ? `<img src="${order.product_image}" width="150" height="150" alt="${order.product_name}">`
          : `<div style="width:150px;height:150px;background:#eee;display:flex;align-items:center;justify-content:center;">No Image</div>`
        }
          </div>

          <div class="item-info">
            <p class="item-name">${order.product_name}</p>
            <a href="/shop/info/${order.customer_id}/" class="seller">
              <div class="seller-img"><i class="bi bi-person-circle"></i></div>
              <div>
                <p class="seller-name">${order.customer_name || 'Customer'}</p>
                <p class="user-role">Customer</p>
              </div>
            </a>
          </div>

          <div class="mid-item-section">
            <div class="label-with-value"><p class="label">Order no.:</p> <p class="value">${order.order_number}</p></div>
            <div class="label-with-value"><p class="label">Order placed:</p> <p class="value">${new Date(order.created_at).toLocaleString()}</p></div>
            <div class="label-with-value estimated-cont">
              <p class="label">Estimated arrival:</p>
              <p class="value">${order.estimated_time_arrival || 'Not set'}</p>
            </div>
          </div>

          <div class="more-info-wrap">
            <p class="status ${order.status}">${order.status.charAt(0).toUpperCase() + order.status.slice(1)}</p>
            <div class="computation-cont">
              <div class="label-with-value"><p class="label">Price:</p> <p class="price"><span class="currency">₱</span>${order.unit_price.toFixed(2)}</p></div>
              <div class="label-with-value"><p class="label">Delivery fee:</p> <p class="price"><span class="currency">₱</span>${order.delivery_fee.toFixed(2)}</p></div>
              <div class="label-with-value total"><p class="label">Total:</p> <p class="price"><span class="currency">₱</span>${order.total_amount.toFixed(2)}</p></div>
            </div>
          </div>
        </div>
        <hr class="line-separator">
      `).join('');

      $ordersList.html(ordersHtml);
    }
  }

  function filterItems(type) {
    $productItems.hide();

    if (type === 'available') {
      $productItems.has('.item-not-available').hide();
      $productItems.not(':has(.item-not-available)').show();
      $sectionTitle.text('Items Available');
    } else if (type === 'sold') {
      $productItems.has('.item-not-available').show();
      $productItems.not(':has(.item-not-available)').hide();
      $sectionTitle.text('Items Sold Out');
    } else {
      $productItems.show();
      $sectionTitle.text('Total Items Listed');
    }
  }

  $allBtns.click(function () {
    $allBtns.removeClass('selected');
    $(this).addClass('selected');

    $weeklySelect.hide();
    $monthlySelect.hide();

    const label = $(this).find('.label').text().trim();

    if (['Items Available', 'Items Sold', 'Total Items Listed'].includes(label)) {
      $invoiceSection.removeClass('show-section');
      $itemsSection.addClass('show-section');

      let type = 'total';
      if (label === 'Items Available') type = 'available';
      else if (label === 'Items Sold') type = 'sold';

      filterItems(type);
    } else {
      $itemsSection.removeClass('show-section');
      $invoiceSection.addClass('show-section');

      const view = $(this).data('view');
      let type = view || 'today';

      if (type === 'weekly') $weeklySelect.show();
      if (type === 'monthly') $monthlySelect.show();

      renderInvoice(type);
    }
  });

  $weeklySelect.change(function () {
    renderInvoice('weekly', { startDate: $(this).val() });
  });

  $monthlySelect.change(function () {
    renderInvoice('monthly', { month: parseInt($(this).val()) });
  });

  // Initial load
  renderInvoice('today');
});