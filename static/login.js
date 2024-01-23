document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");

    function displayNotification(message, isError) {
        const notificationDiv = document.createElement('div');
        notificationDiv.classList.add('notification', isError ? 'error' : 'success');
        notificationDiv.textContent = message;

        loginForm.parentNode.insertBefore(notificationDiv, loginForm);

        setTimeout(() => {
            hideNotification();
        }, 3000);
    }

    function hideNotification() {
        const notificationDiv = document.querySelector('.notification');

        if (notificationDiv) {
            notificationDiv.parentNode.removeChild(notificationDiv);
        }
    }

    loginForm.addEventListener("submit", function (e) {
        e.preventDefault();

        console.log("Form submitted");

        const usernameInput = document.getElementById("username");
        const passwordInput = document.getElementById("password");

        const username = usernameInput.value;
        const password = passwordInput.value;

        console.log("Username input (login.html):", username);
        console.log("Password input (login.html):", password);

        if (!username || !password) {
            displayNotification("Все поля должны быть заполнены", true);
            return;
        }

        const requestBody = new URLSearchParams({ username, password });
        console.log("Request body:", requestBody);

        console.log("Sending login request with username:", username);

        fetch("/login", {
            method: "POST",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: requestBody
        })
        .then(response => {
            console.log("Received response from server:", response);

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            return response.json();
        })
        .then(data => {
            console.log("Server response:", data);
            sessionStorage.setItem('username', username);

            if (data.redirect) {
                console.log("Redirecting to:", data.redirect);
                window.location.replace(data.redirect);
            } else if (data.error) {
                localStorage.setItem('username', username);
                console.log("Username saved to localStorage:", username);

                displayNotification(data.error, true);

                setTimeout(() => {
                    hideNotification();
                }, 3000);
            } else {
                if (data.user_id && data.user_id !== 'null') {
                    localStorage.setItem('username', username);
                    getUserId(username);
                } else {
                    console.error("User ID is undefined, empty, or 'null'. Cannot proceed.");
                    localStorage.setItem('username', username);
                }
            }
        })
        .catch(error => {
            console.error("There was a problem with the fetch operation:", error);

            displayNotification("Ошибка входа: Неверное имя пользователя или пароль", true);

            setTimeout(() => {
                hideNotification();
            }, 3000);
        });
    });

    function getUserId(username) {
        fetch('/get_user_id')
            .then(response => response.json())
            .then(data => {
                console.log("After fetching user_id. Current user_id:", data.user_id, "nick:", username);
                localStorage.setItem('username', username);
                console.log("User ID and username saved to localStorage:", username);
            })
            .catch(error => {
                console.error("Error fetching user_id:", error);

                displayNotification("Ошибка получения идентификатора пользователя", true);

                setTimeout(() => {
                    hideNotification();
                }, 3000);
            });
    }
});
