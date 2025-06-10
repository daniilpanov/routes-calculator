const dispatchDateInput = document.getElementById('dispatchDate');
const departureInput = document.getElementById('departure');
const destinationInput = document.getElementById('destination');
const departureHiddenInput = document.getElementById('departureId');
const destinationHiddenInput = document.getElementById('destinationId');
const cargoWeightInput = document.getElementById('cargoWeight');
const containerTypeInput = document.getElementById('containerType');
const currencyInput = document.getElementById('currency');

dispatchDateInput.valueAsDate = dispatchDateInput.valueAsDate || new Date();
dispatchDateInput.min = dispatchDateInput.min || dispatchDateInput.value;

const departures = { data: null };

async function updateDepartures() {
    if (!dispatchDateInput.validity.valid) return;
    const date = dispatchDateInput.value;
    const resp = await fetch(`${window.baseUrl}/v1/points/departures?date=${date}`);
    if (resp.ok) {
        departures.data = await resp.json();
        destinationInput.value = '';
        destinationHiddenInput.value = '';
        destinationInput.disabled = true;
    }
}

dispatchDateInput.addEventListener('input', updateDepartures);

const destinations = { data: {} };

setupAutocomplete('departure', 'departureList', departures, 'departureId', async () => {
    destinationInput.disabled = false;
    const date = dispatchDateInput.value;
    const departureId = departureHiddenInput.value;
    const resp = await fetch(`${window.baseUrl}/v1/points/destinations?date=${date}&departure_point_id=${departureId}`);
    if (resp.ok) destinations.data = await resp.json();
}, () => {
    destinationInput.disabled = true;
    destinationInput.value = '';
});
setupAutocomplete('destination', 'destinationList', destinations, 'destinationId');

async function calculateAndRender(payload, icons) {
    const response = await fetch(window.baseUrl + '/v1/routes/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });
    if (!response.ok)
        throw new Error(`[${response.status} ${response.statusText}]<p>` + await response.text());

    const data = await response.json();
    const container = document.getElementById('results');
    container.innerHTML = '';

    data.forEach(route => {
        const routeEl = document.createElement('div');
        routeEl.className = 'p-3 mb-4 border rounded shadow-sm';

        const segmentsHTML = route.segments.map(segment => {
            let svg = icons[segment.type] || '';

            const price = segment.containers.reduce((accumulator, p) => accumulator + p.price, 0);
            const roundedPrice = Math.round((price + Number.EPSILON) * 100) / 100;
            const currency = segment.containers[0]?.currency || '';
            return `
                <div class="d-flex align-items-center my-2">
                    <div class="route-icon" style="width:30px;height:30px;margin-right:10px;">${svg}</div>
                    <div>
                        <div><strong>${segment.from.name}</strong> → <strong>${segment.to.name}</strong></div>
                        <div class="text-muted">${roundedPrice} ${currency}</div>
                    </div>
                </div>
            `;
        }).join('');

        routeEl.innerHTML = `
            <h5 class="mb-2">Ставка действует: ${new Date(route.dateFrom).toLocaleDateString()} — ${new Date(route.dateTo).toLocaleDateString()}</h5>
            <div class="mb-2">Условия: ${route.beginCond} - ${route.finishCond}</div>
            <div class="mb-3">Контейнер: ${route.containers.map(c => c.name).join(', ')}</div>
            ${segmentsHTML}
            <div class="mb-3">Суммарная стоимость: ${Math.round((route.price + Number.EPSILON) * 100) / 100} ${route.currency}</div>
        `;

        container.appendChild(routeEl);
    });
}
