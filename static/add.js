document.addEventListener("DOMContentLoaded", function () {
    const addForm = document.getElementById("add-form");

    // Функции displayNotification и hideNotification определены вне обработчика события
    function displayNotification(message, isError) {
        const notificationDiv = document.createElement('div');
        notificationDiv.classList.add('notification', isError ? 'error' : 'success');
        notificationDiv.textContent = message;

        // Вставляем уведомление перед формой ввода
        addForm.parentNode.insertBefore(notificationDiv, addForm);

        // Скрыть уведомление через 3 секунды
        setTimeout(() => {
            hideNotification();
        }, 3000);
    }

    function hideNotification() {
        const notificationDiv = document.querySelector('.notification');

        if (notificationDiv) {
            // Удаляем уведомление из DOM
            notificationDiv.parentNode.removeChild(notificationDiv);
        }
    }

    addForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const product_name = document.getElementById("product_name").value;
        const description = document.getElementById("description").value;
        const price = document.getElementById("price").value;
        const photo = document.getElementById("photo").files[0];
        const category = document.getElementById("category").value;

        // Проверка на пустые поля
        if (!product_name || !description || !price || !photo || !category) {
            displayNotification("Все поля должны быть заполнены (даже фото!)", true);
            return;
        }

        const requestBody = new FormData();
        requestBody.append("product_name", product_name);
        requestBody.append("description", description);
        requestBody.append("price", price);
        requestBody.append("photo", photo);
        requestBody.append("category", category);

        fetch("/add", {
            method: "POST",
            body: requestBody
        })
        .then(response => {
            console.log("Received response from server:", response);

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            return response.json(); 
        })
        .then(jsonData => {
            console.log("Server response:", jsonData);

            if (jsonData.redirect) {
                window.location.href = jsonData.redirect;
            } else {
                const tempContainer = document.createElement('div');
                tempContainer.innerHTML = jsonData;

                const registrationElement = tempContainer.querySelector('.registration-cssave');

                if (registrationElement) {
                    const registrationContent = registrationElement.outerHTML;
                    console.log('Content of .registration-cssave:', registrationContent);
                } else {
                    console.error('.registration-cssave not found in the server response');
                }
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);

            displayNotification("Ошибка при добавлении продукта", true);

            setTimeout(() => {
                hideNotification();
            }, 3000);
        });
    });
});
