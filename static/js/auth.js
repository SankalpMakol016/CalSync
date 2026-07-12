// ================================
// ELEMENTS
// ================================

const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");

const loginContainer = document.getElementById("loginContainer");
const registerContainer = document.getElementById("registerContainer");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");


// ================================
// TAB SWITCHING
// ================================

function showLogin() {

    loginContainer.classList.remove("auth-hidden");
    registerContainer.classList.add("auth-hidden");

    loginTab.classList.add("active");
    registerTab.classList.remove("active");

    document.getElementById("loginError").classList.add("hidden");
    document.getElementById("registerError").classList.add("hidden");

}

function showRegister() {

    registerContainer.classList.remove("auth-hidden");
    loginContainer.classList.add("auth-hidden");

    registerTab.classList.add("active");
    loginTab.classList.remove("active");

    document.getElementById("loginError").classList.add("hidden");
    document.getElementById("registerError").classList.add("hidden");

}

loginTab.addEventListener("click", showLogin);
registerTab.addEventListener("click", showRegister);


// ================================
// LOGIN
// ================================

loginForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const btn = document.getElementById("loginBtn");
    const errorDiv = document.getElementById("loginError");

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    btn.disabled = true;
    btn.textContent = "Signing In...";

    errorDiv.classList.add("hidden");

    try {

        const response = await fetch("/api/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email,
                password
            })

        });

        const data = await response.json();

        if (data.success) {

            window.location.href = "/dashboard";
            return;

        }

        errorDiv.textContent = data.message;
        errorDiv.classList.remove("hidden");

    }

    catch {

        errorDiv.textContent = "Unable to connect to the server.";
        errorDiv.classList.remove("hidden");

    }

    btn.disabled = false;
    btn.textContent = "Sign In";

});


// ================================
// REGISTER
// ================================

registerForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const btn = document.getElementById("registerBtn");
    const errorDiv = document.getElementById("registerError");

    const name = document.getElementById("registerName").value.trim();

    const email = document.getElementById("registerEmail").value.trim();

    const password = document.getElementById("registerPassword").value;

    const confirm_password =
        document.getElementById("confirmPassword").value;

    btn.disabled = true;
    btn.textContent = "Creating Account...";

    errorDiv.classList.add("hidden");

    try {

        const response = await fetch("/api/register", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                name,
                email,
                password,
                confirm_password

            })

        });

        const data = await response.json();

        if (data.success) {

            window.location.href = "/dashboard";
            return;

        }

        errorDiv.textContent = data.message;
        errorDiv.classList.remove("hidden");

    }

    catch {

        errorDiv.textContent = "Unable to connect to the server.";
        errorDiv.classList.remove("hidden");

    }

    btn.disabled = false;
    btn.textContent = "Create Account";

});