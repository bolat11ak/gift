
function toggleMenu() {
    const menu = document.querySelector(".dropdown-menu");
    menu.classList.toggle("open");
}


function redirectToDashboard() {
    window.location.href = "dashboard.html";
}

function redirectToWelcome() {
    window.location.href = "dashboard.html";
}


document.addEventListener("DOMContentLoaded", () => {
    const signUpForm = document.getElementById("signup-form");

    if (signUpForm) {
        signUpForm.addEventListener("submit", function(event) {
            event.preventDefault();

            let formData = {
                username: document.getElementById("username").value,
                password: document.getElementById("password").value
            };

            fetch("http://127.0.0.1:8000/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Sign-up failed. Username might be taken.");
                }
                return response.json();
            })
            .then(data => {
                console.log("Success:", data);
                alert("User registered successfully!");
                window.location.href = "sign_in.html";
            })
            .catch(error => {
                console.error("Error:", error);
                alert(error.message);
            });
        });
    }
});


document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");

    if (loginForm) {
        loginForm.addEventListener("submit", function(event) {
            event.preventDefault();

            let formData = {
                username: document.getElementById("login-username").value,
                password: document.getElementById("login-password").value
            };

            fetch("http://127.0.0.1:8000/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Invalid username or password.");
                }
                return response.json();
            })
            .then(data => {
                if (data.access_token) {
                    localStorage.setItem("access_token", data.access_token);
                    alert("Login successful!");
                    window.location.href = "dashboard.html";
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert(error.message);  // Show login error
            });
        });
    }
});


function loadWishlists() {
    fetch("http://127.0.0.1:8000/wishlists", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("access_token"),
            "Content-Type": "application/json"
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch wishlists.");
        }
        return response.json();
    })
    .then(data => {
        console.log("Wishlists:", data);
        const wishlistContainer = document.getElementById("wishlist-container");
        wishlistContainer.innerHTML = "";
        data.forEach(wishlist => {
            const div = document.createElement("div");
            div.textContent = wishlist.name;
            wishlistContainer.appendChild(div);
        });
    })
    .catch(error => {
        console.error("Error:", error);
        alert(error.message);
    });
}


function loadCelebrations() {
    fetch("http://127.0.0.1:8000/celebrations", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("access_token"),
            "Content-Type": "application/json"
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch celebrations.");
        }
        return response.json();
    })
    .then(data => {
        console.log("Celebrations:", data);
        const celebrationContainer = document.getElementById("celebration-container");
        celebrationContainer.innerHTML = "";
        data.forEach(celebration => {
            const div = document.createElement("div");
            div.textContent = `${celebration.title} - ${celebration.date}`;
            celebrationContainer.appendChild(div);
        });
    })
    .catch(error => {
        console.error("Error:", error);
        alert(error.message);
    });
}

function logout() {
    localStorage.removeItem("access_token");
    alert("Logged out successfully!");
    window.location.href = "sign_in.html";
}

document.addEventListener("DOMContentLoaded", () => {
    if (window.location.pathname.includes("dashboard.html")) {
        loadWishlists();
        loadCelebrations();
    }
});


