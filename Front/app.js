const API_BASE_URL = 'http://localhost:3000'; 
const API_NOTIFICATION_URL = 'redis://localhost:6379/0'
const PRODUCTS_API = `${API_BASE_URL}/produtos`;
const ESTOQUE_API = `${API_BASE_URL}/estoque`;
const CARRINHO_API = `${API_BASE_URL}/carrinho`;

const listaProdutos = document.getElementById('lista-produtos');
const listaPedidos  = document.getElementById('lista-pedidos');
const listaCarrinho = document.getElementById('lista-carrinho');
const listaNotificacoes = document.getElementById('lista-notificacoes');
const checkoutBtn = document.getElementById('checkout-btn');

async function carregaProdutos() {
    const response = await fetch(PRODUCTS_API);
    const produtos = await response.json();
    listaProdutos.innerHTML = '';
    produtos.forEach(produto => {
        const li = document.createElement('li');
        li.textContent = `${produto.nome} - $${produto.preco} - Estoque: ${produto.estoque}`;
        const addButton = document.createElement('button');
        addButton.textContent = 'Adicionar';
        addButton.onclick = () => adicionaCarrinho(produto.id);
        li.appendChild(addButton);
        listaProdutos.appendChild(li);
    });
}
async function carregaPedidos() {
    const response = await fetch(`${API_BASE_URL}/pedidos`);
    const pedidos = await response.json();
    listaPedidos.innerHTML = '';
    pedidos.forEach(pedido => {
        const id =pedido.id
        const li = document.createElement('li');
        li.textContent = `${pedido.id} - ${pedido.status}`;
        const removePedidoButton = document.createElement('button');       
        listaPedidos.appendChild(li);
        if(pedido.status == 'Pedido Criado' ){
            removePedidoButton.textContent = 'Remover'; 
            li.appendChild(removePedidoButton);
            removePedidoButton.onclick = () => removePedido(pedido.id);
        }
    });
}
async function removePedido(pedidoId) {
    console.log(pedidoId)
    await fetch(`${API_BASE_URL}/pedidos/excluir`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id:pedidoId })
    });
    alert('Pedido removido com sucesso!');
    carregaProdutos();
}

async function adicionaCarrinho(produtoId) {
    await fetch(`${CARRINHO_API}/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ produtoId })
    });
    carregaCarrinho();
}

async function carregaCarrinho() {
    const response = await fetch(CARRINHO_API);
    const carrinho = await response.json();
    listaCarrinho.innerHTML = '';
    carrinho.items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.nome} - $${item.preco} x ${item.quantidade}`;
        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remover';
        removeButton.onclick = () => removeCarrinho(item.produtoId);
        li.appendChild(removeButton);
        listaCarrinho.appendChild(li);
    });
}

async function removeCarrinho(produtoId) {
    await fetch(`${CARRINHO_API}/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ produtoId })
    });
    carregaCarrinho();
}

checkoutBtn.onclick = async () => {
    await fetch(`${CARRINHO_API}/checkout`, { method: 'POST' });
    carregaCarrinho();
    alert('Pedido realizado com sucesso!');
    carregaPedidos();
    carregaProdutos();
};

function setupSSE() {
    const listaNotificacoes = document.getElementById('lista-notificacoes'); 
    const eventSource = new EventSource("http://localhost:3006/stream");
    console.log(eventSource)
    eventSource.addEventListener('publish',function(event) {
        let notificacao = JSON.parse(event.data).message;
        console.log(notificacao)
        const li = document.createElement('li');
        if(notificacao){
            li.textContent = `${notificacao}`;
            listaNotificacoes.appendChild(li);
            carregaPedidos()
            carregaProdutos()
        }
    })
    eventSource.onmessage = event => {
        console.log(event)
    };

    eventSource.onerror = error => {
        console.log('Erro na conexão SSE:', error);
    };
}


carregaProdutos();
carregaPedidos();
carregaCarrinho();
setupSSE();
