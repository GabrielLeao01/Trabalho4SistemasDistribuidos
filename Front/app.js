const API_BASE_URL = 'http://localhost:3000'; 
const API_NOTIFICATION_URL = 'redis://localhost:6379/0'
const PRODUCTS_API = `${API_BASE_URL}/products`;
const ESTOQUE_API = `${API_BASE_URL}/estoque`;
const CART_API = `${API_BASE_URL}/cart`;

const productList = document.getElementById('product-list');
const pedidosList  = document.getElementById('lista-pedidos');
const cartList = document.getElementById('cart-list');
const notificationList = document.getElementById('notification-list');
const checkoutBtn = document.getElementById('checkout-btn');

async function loadProducts() {
    const response = await fetch(PRODUCTS_API);
    const products = await response.json();
    productList.innerHTML = '';
    products.forEach(product => {
        const li = document.createElement('li');
        li.textContent = `${product.name} - $${product.price}`;
        const addButton = document.createElement('button');
        addButton.textContent = 'Adicionar';
        addButton.onclick = () => addToCart(product.id);
        li.appendChild(addButton);
        productList.appendChild(li);
    });
}
async function loadPedidos() {
    const response = await fetch(`${API_BASE_URL}/pedidos`);
    const pedidos = await response.json();
    pedidosList.innerHTML = '';
    pedidos.forEach(pedido => {
        const li = document.createElement('li');
        li.textContent = `${pedido.id} - ${pedido.status}`;
        pedidosList.appendChild(li);
    });
}

// Adicionar ao carrinho
async function addToCart(productId) {
    await fetch(`${CART_API}/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId })
    });
    loadCart();
}

// Carregar carrinho
async function loadCart() {
    const response = await fetch(CART_API);
    const cart = await response.json();
    cartList.innerHTML = '';
    cart.items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.name} - $${item.price} x ${item.quantity}`;
        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remover';
        removeButton.onclick = () => removeFromCart(item.productId);
        li.appendChild(removeButton);
        cartList.appendChild(li);
    });
}

async function removeFromCart(productId) {
    await fetch(`${CART_API}/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId })
    });
    loadCart();
}

checkoutBtn.onclick = async () => {
    await fetch(`${CART_API}/checkout`, { method: 'POST' });
    loadCart();
    alert('Pedido realizado com sucesso!');
    loadPedidos();
};

// Notificações via SSE
function setupSSE() {
    const notificationList = document.getElementById('notification-list'); // Defina o elemento correto
    const eventSource = new EventSource(`${API_BASE_URL}/stream`);

    eventSource.onmessage = event => {
        const notification = JSON.parse(event.data);
        const li = document.createElement('li');
        li.textContent = `Pedido ${notification.id}: ${notification.status}`;
        notificationList.appendChild(li);
    };

    eventSource.onerror = error => {
        console.log('Erro na conexão SSE:', error);
    };
}


// Inicialização
loadProducts();
loadPedidos();
loadCart();
setupSSE();
