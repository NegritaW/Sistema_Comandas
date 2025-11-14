document.addEventListener("DOMContentLoaded", () => {
    const list = document.getElementById("clientes-list");
    const input = document.getElementById("nombre-cliente");
    const btnAdd = document.getElementById("add-cliente-btn");

    // Clic en card → ir a su comanda
    list.addEventListener("click", (e) => {
        const card = e.target.closest(".cliente-card");
        if (!card) return;
        const id = card.dataset.id;
        window.location.href = `/garzon/comanda_cliente/${id}/`;
    });

    // Añadir cliente nuevo
    btnAdd.addEventListener("click", () => {
        const nombre = input.value.trim();
        if (!nombre) {
            alert("Debe ingresar un nombre válido.");
            return;
        }

        fetch("/garzon/agregar_cliente_externo/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf,
            },
            body: JSON.stringify({ nombre }),
        })
            .then((r) => r.json())
            .then((res) => {
                if (res.ok) {
                    const nuevo = document.createElement("div");
                    nuevo.className = "cliente-card";
                    nuevo.dataset.id = res.id;
                    nuevo.innerHTML = `
                        <div class="cliente-info">
                            <h3>${res.nombre}</h3>
                            <p class="fecha">Hace unos segundos</p>
                        </div>
                        <img src="/static/img/ejemplo.png" class="cliente-img" alt="Cliente">
                    `;
                    list.prepend(nuevo);
                    input.value = "";
                } else {
                    alert("Error al crear cliente externo.");
                }
            });
    });
});