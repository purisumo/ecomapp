$(document).ready(function () {
  // Toggle password visibility
  const passInput = $("#id_password1");
  const passToggleBtn = passInput.next(".toggle-pass-btn");
  const passIcon = passToggleBtn.find(".toggle-pass-icon");

  passToggleBtn.click(() => {
    if (passIcon.attr("src").includes("eyeslash")) {
      passInput.attr("type", "password");
      passIcon.attr("src", "/static/images/icons/eye.svg");
    } else {
      passInput.attr("type", "text");
      passIcon.attr("src", "/static/images/icons/eyeslash.svg");
    }
  });

  // Initialize current step
  let currentStep = 1;

  // Function to show a step
  const showStep = (step) => {
    $(".form-container").hide(); // Hide all steps
    $(`.form-container[data-step="${step}"]`).fadeIn(); // Show the current step
  };

  // Show initial step
  showStep(currentStep);

  // Handle 'Next' button click
  $(".next-btn").click(function () {
    const targetStep = $(this).data("target");
    if (targetStep) {
      currentStep = targetStep;
      showStep(currentStep);
    }
  });

  // Handle 'Back' link click
  $(".back-text").click(function () {
    const targetStep = $(this).data("target");
    if (targetStep) {
      currentStep = targetStep;
      showStep(currentStep);
    }
  });

  // Add smooth scrolling effect between steps
  $(".next-btn, .back-text").click(function () {
    $("html, body").animate(
      { scrollTop: $(".signup-page").offset().top },
      "slow"
    );
  });
});
