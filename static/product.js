document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('product_id');

    if (productId) {
        fetch(`/get_product_info?product_id=${productId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('product-name').innerText = data.product_name;
                document.getElementById('product-description').innerText = data.description;
                document.getElementById('product-price').innerText = data.price;
                document.getElementById('product-photo').src = data.photo;
                document.getElementById('product-category').innerText = data.category;
            })
            .catch(error => console.error('Error fetching product info:', error));
    } else {
        console.error('Product ID is missing in the URL');
    }
});
