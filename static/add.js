document.addEventListener("DOMContentLoaded", function () {
    const addForm = document.getElementById("add-form");

    addForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const product_name = document.getElementById("product_name").value;
        const description = document.getElementById("description").value;
        const price = document.getElementById("price").value;
        const photo = document.getElementById("photo").files[0];
        const category = document.getElementById("category").value;

        const requestBody = new URLSearchParams();
        requestBody.append("product_name", product_name);
        requestBody.append("description", description);
        requestBody.append("price", price);
        requestBody.append("photo", photo);
        requestBody.append("category", category);

        fetch("/add", {
            method: "POST",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: requestBody
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log("Server response:", data);
            // После успешного ответа, перенаправляем на другую страницу (например, на главную)
            window.location.replace("/");
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    });
});
