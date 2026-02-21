const FIREBASE_API_KEY = "AIzaSyBsMtguwaPW5ueM0Kqpm9lqLx9SdL8EsLk";

document.addEventListener('DOMContentLoaded', () => {
    const loginView = document.getElementById('loginView');
    const loggedInView = document.getElementById('loggedInView');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const errorMsg = document.getElementById('errorMsg');
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const userEmailDisplay = document.getElementById('userEmailDisplay');

    // Check if already logged in
    chrome.storage.local.get(['synapse_token', 'synapse_email'], (result) => {
        if (result.synapse_token && result.synapse_email) {
            showLoggedIn(result.synapse_email);
        } else {
            showLogin();
        }
    });

    loginBtn.addEventListener('click', async () => {
        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
            errorMsg.textContent = "Please enter both email and password.";
            return;
        }

        loginBtn.textContent = "Logging in...";
        loginBtn.disabled = true;
        errorMsg.textContent = "";

        try {
            const response = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${FIREBASE_API_KEY}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    returnSecureToken: true
                })
            });

            const data = await response.json();

            if (!response.ok) {
                let err = data.error.message || "Login failed";
                // Friendly error messages
                if (err === "INVALID_LOGIN_CREDENTIALS") {
                    err = "Invalid email or password.";
                }
                throw new Error(err);
            }

            // Save to Chrome storage
            chrome.storage.local.set({
                synapse_token: data.idToken,
                synapse_email: data.email
            }, () => {
                showLoggedIn(data.email);
            });

        } catch (error) {
            errorMsg.textContent = error.message;
            loginBtn.textContent = "Log In";
            loginBtn.disabled = false;
        }
    });

    logoutBtn.addEventListener('click', () => {
        chrome.storage.local.remove(['synapse_token', 'synapse_email'], () => {
            showLogin();
        });
    });

    function showLoggedIn(email) {
        // We have to set display styles explicitly because 'flex' is used for loginView
        loginView.style.display = 'none';
        loggedInView.style.display = 'block';
        userEmailDisplay.textContent = email;

        loginBtn.textContent = "Log In";
        loginBtn.disabled = false;
        passwordInput.value = "";
    }

    function showLogin() {
        loginView.style.display = 'flex';
        loggedInView.style.display = 'none';
        errorMsg.textContent = "";
    }
});
