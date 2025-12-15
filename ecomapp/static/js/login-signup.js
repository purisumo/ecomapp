$(document).ready(function () {
  const loginBtn = $("button.border-btn-primary[data-modal='nav-login-btn']");
  const loginModal = $(".modal.login-modal");
  const signupModal = $(".modal.signup-modal");
  const overlay = $(".overlay");

  loginBtn.click(() => {
    loginModal.addClass("show-modal");
    overlay.addClass("show-modal global-overlay");
  });

  // Open sign up
  loginModal.find("p.signup span").click(() => {
    loginModal.removeClass("show-modal");
    signupModal.addClass("show-modal");
  });

  // Open login
  signupModal.find("p.login span").click(() => {
    signupModal.removeClass("show-modal");
    loginModal.addClass("show-modal");
  });

  // Overlay click to close modal
  overlay.click(() => {
    $(".modal").removeClass("show-modal"); // Hide modal
  });

  // Sign up validation
  const signupForm = $("form.signup-modal");

  signupForm.on("submit", function (e) {
    let isValid = true;

    // clear previous errors
    signupForm.find(".input-cont").removeClass("error-input");
    signupForm.find(".input-error-message").text("");

    // collect input fields and validations
    const fields = [
      { id: "#f-name", msg: "Enter first name" },
      { id: "#l-name", msg: "Enter last name" },
      { id: "#address", msg: "Enter address" },
      { id: "#phone-number", msg: "Enter phone number" },
      { id: "#signup-username", msg: "Enter username" },
      { id: "#signup-email", msg: "Enter email" },
      { id: "#signup-password", msg: "Enter password" },
      { id: "#re-pass", msg: "Re-enter password" }
    ];

    fields.forEach(({ id, msg }) => {
      const field = $(id);
      if (!field.val().trim()) {
        const wrapper = field.closest(".input-cont");
        wrapper.addClass("error-input");
        wrapper.find(".input-error-message").text(msg);
        isValid = false;
      }
    });

    // check if passwords match
    const pass = $("#signup-password").val();
    const rePass = $("#re-pass").val();
    if (pass && rePass && pass !== rePass) {
      const rePassWrap = $("#re-pass").closest(".input-cont");
      rePassWrap.addClass("error-input");
      rePassWrap.find(".input-error-message").text("Passwords do not match");
      isValid = false;
    }

    if (!isValid) e.preventDefault(); // prevent form submission if errors
  });
});
