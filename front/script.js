document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const productsDiv = document.getElementById('products');
    const averagePriceDiv = document.getElementById('average-price');
    const productValueDiv = document.getElementById('product-value');

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const city = document.getElementById('city').value;
        const product = document.getElementById('product').value;

        // ارسال درخواست به بک‌اند
        fetchData(city, product);
    });

    function fetchData(city, product) {
        const backendUrl = 'http://0.0.0.0:8080/http://localhost:5000';

        // درخواست به بک‌اند
        fetch(`${backendUrl}/${city}/${product}`, {
            method: 'POST',
            headers : {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // نمایش اطلاعات محصولات
            productsDiv.innerHTML = '';
            data.forEach(product => {
                const productElement = document.createElement('div');
                productElement.classList.add('product');
                productElement.innerHTML = `
                    <h2>${product.title}</h2>
                    <p>${product.description}</p>
                    <img src="${product.img}" alt="${product.title}">
                    <p>قیمت: ${product.price}</p>
                    <p>زمان انتشار: ${product.posted}</p>
                    <a href="${product.link}" target="_blank">لینک</a>
                `;
                productsDiv.appendChild(productElement);
            });
        })
        .catch(error => console.error('Error:', error));
    }
});

