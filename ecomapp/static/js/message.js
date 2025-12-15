$(document).ready(function () {
  const container = $(".message-page .page-container");
  const listOfMessages = $(".message-page .left-section .message-list-item");
  const messageContainer = $('.message-page .right-section .message-content-wrap');

  listOfMessages.click(function () {
    if (!container.hasClass('is-selected-message')) container.addClass('is-selected-message');

    listOfMessages.removeClass('selected');
    $(this).addClass('selected');
    messageContainer.scrollTop(messageContainer[0].scrollHeight);
  });

  $(".message-page .left-section .top-wrap").click(() => container.hasClass('is-selected-message') ? container.removeClass('is-selected-message') : console.log('meow'))
});
