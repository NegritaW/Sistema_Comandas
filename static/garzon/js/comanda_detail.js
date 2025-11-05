// --- static/garzon/js/comanda_detail.js ---
document.addEventListener("DOMContentLoaded", () => {
    const MENU = window.MENU || {};
    const comandaId = window.COMANDA_ID;
    const csrf = window.CSRF_TOKEN;

    const tabs = document.querySelectorAll('.tab-btn');
    const itemsList = document.getElementById('items-list');
    const totalDisplay = document.getElementById('total-display');
    const modal = document.getElementById('modal');
    const resumenDiv = document.getElementById('resumen-items');

    let cart = {}; // id -> {id, nombre, precio, cantidad, ...}

    // --- Formato de dinero ---
    const formatMoney = (num) =>
        `$${num.toLocaleString('es-CL')}`;

    // --- Renderizar categoría ---
    function renderCategory(cat) {
        itemsList.innerHTML = '';
        const items = MENU[cat] || [];
        items.forEach(it => {
            const div = document.createElement('div');
            div.className = 'menu-item';
            div.dataset.id = it.id;

            div.innerHTML = `
                <img src="${it.imagen || '/static/img/ejemplo.png'}" class="plate-img" onerror="this.src='/static/img/ejemplo.png'">
                <div class="item-info">
                    <h4>${it.nombre}</h4>
                    <p class="ingred">${it.ingredientes}</p>
                    <p class="precio">${formatMoney(it.precio)}</p>
                </div>
                <div class="item-actions">
                    <button class="minus-btn" data-id="${it.id}" style="display:none;">−</button>
                    <div class="cantidad" data-id="${it.id}" style="display:none;">Cantidad: <span>0</span></div>
                    <button class="plus-btn" data-id="${it.id}">+</button>
                </div>
            `;

            div.addEventListener('click', (e) => {
                if (e.target.classList.contains('plus-btn') || e.target.classList.contains('minus-btn')) return;
                div.classList.toggle('selected');
            });

            itemsList.appendChild(div);
        });
        attachButtons();
    }

    // --- Botones + y − ---
    function attachButtons() {
        document.querySelectorAll('.plus-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                e.stopPropagation();
                const id = btn.dataset.id;
                const item = findItemById(id);
                if (!cart[id]) cart[id] = {...item, cantidad: 0};
                cart[id].cantidad += 1;
                refreshItemUI(id);
                updateTotal();
            });
        });
        document.querySelectorAll('.minus-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                e.stopPropagation();
                const id = btn.dataset.id;
                if (!cart[id]) return;
                cart[id].cantidad = Math.max(0, cart[id].cantidad - 1);
                if (cart[id].cantidad === 0) delete cart[id];
                refreshItemUI(id);
                updateTotal();
            });
        });
    }

    // --- Actualizar visualización de ítems ---
    function refreshItemUI(id) {
        const cantidadDiv = document.querySelector(`.cantidad[data-id="${id}"]`);
        const minus = document.querySelector(`.minus-btn[data-id="${id}"]`);
        const item = document.querySelector(`.menu-item[data-id="${id}"]`);

        if (cart[id] && cart[id].cantidad > 0) {
            if (minus) minus.style.display = 'inline-block';
            if (cantidadDiv) {
                cantidadDiv.style.display = 'block';
                cantidadDiv.querySelector('span').textContent = cart[id].cantidad;
            }
            if (item) item.classList.add('in-cart');
        } else {
            if (minus) minus.style.display = 'none';
            if (cantidadDiv) cantidadDiv.style.display = 'none';
            if (item) item.classList.remove('in-cart');
        }
    }

    // --- Actualizar total general ---
    function updateTotal() {
        let total = 0;
        for (const id in cart) total += cart[id].precio * cart[id].cantidad;
        totalDisplay.textContent = `Total: ${formatMoney(total)}`;
    }

    // --- Buscar ítem por id ---
    function findItemById(id) {
        for (const cat in MENU) {
            const item = MENU[cat].find(i => i.id == id);
            if (item) return item;
        }
        return null;
    }

    // --- Enviar comanda ---
    document.getElementById('enviar-btn').addEventListener('click', () => {
        resumenDiv.innerHTML = '';
        let total = 0;

        if (Object.keys(cart).length === 0) {
            resumenDiv.innerHTML = '<p>No hay ítems seleccionados.</p>';
        } else {
            Object.values(cart).forEach(it => {
                const subtotal = it.precio * it.cantidad;
                total += subtotal;
                const p = document.createElement('p');
                p.textContent = `${it.nombre} x ${it.cantidad} - ${formatMoney(subtotal)}`;
                resumenDiv.appendChild(p);
            });

            // Línea de separación y total final
            const hr = document.createElement('hr');
            const totalP = document.createElement('p');
            totalP.style.fontWeight = 'bold';
            totalP.textContent = `Total: ${formatMoney(total)}`;
            resumenDiv.appendChild(hr);
            resumenDiv.appendChild(totalP);
        }

        modal.style.display = 'flex';
    });

    document.getElementById('cancel-send').addEventListener('click', () => modal.style.display = 'none');

    document.getElementById('confirm-send').addEventListener('click', () => {
        const payload = {items: Object.values(cart)};
        fetch(`/garzon/enviar_comanda/${comandaId}/`, {
            method: 'POST',
            headers: {'Content-Type':'application/json','X-CSRFToken': csrf},
            body: JSON.stringify(payload)
        }).then(r => r.json()).then(res => {
            if (res.ok) {
                window.location.href = res.redirect;
            } else alert('Error al enviar comanda.');
        });
    });

    // --- Tabs ---
    tabs.forEach((tab, i) => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderCategory(tab.dataset.cat);
        });
        if (i === 0) { tab.classList.add('active'); renderCategory(tab.dataset.cat); }
    });
});