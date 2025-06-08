const dispatchDateInput = document.getElementById('dispatchDate');
const departureInput = document.getElementById('departure');
const destinationInput = document.getElementById('destination');
const departureHiddenInput = document.getElementById('departureId');
const destinationHiddenInput = document.getElementById('destinationId');
const cargoWeightInput = document.getElementById('cargoWeight');
const containerTypeInput = document.getElementById('containerType');
const currencyInput = document.getElementById('currency');
const calculateButton = document.getElementById('calculate');

dispatchDateInput.valueAsDate = dispatchDateInput.valueAsDate || new Date();
dispatchDateInput.min = dispatchDateInput.min || dispatchDateInput.value;

const departures = { data: null };

async function updateDepartures() {
    if (!dispatchDateInput.validity.valid) return;
    const date = dispatchDateInput.value;
    const resp = await fetch(`${window.baseUrl}/get_departures?date=${date}`);
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
    const resp = await fetch(`${window.baseUrl}/get_destinations?date=${date}&departure_point_id=${departureId}`);
    if (resp.ok) destinations.data = await resp.json();
}, () => {
    destinationInput.disabled = true;
    destinationInput.value = '';
});
setupAutocomplete('destination', 'destinationList', destinations, 'destinationId');

async function calculateAndRender(payload, icons) {
    calculateButton.disabled = true;
    const response = await fetch(window.baseUrl + '/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        calculateButton.disabled = false;
        return showGlobalAlert(`[${response.status} ${response.statusText}]<p>` + await response.text());
    }
    const data = transformResponseData(await response.json());
    const container = document.getElementById('results');
    container.innerHTML = '';

    data.forEach(route => {
        const routeEl = document.createElement('div');
        routeEl.className = 'p-3 mb-4 border rounded shadow-sm';

        const segmentsHTML = route.segments.map(segment => {
            let svg = icons[segment.type] || '';

            const price = segment.price.map(p => `${p.sum.toLocaleString()} ${p.currency}`).join(', ');
            return `
                <div class="d-flex align-items-center my-2">
                    <div class="route-icon" style="width:30px;height:30px;margin-right:10px;">${svg}</div>
                    <div>
                        <div><strong>${segment.from.name}</strong> → <strong>${segment.to.name}</strong></div>
                        <div class="text-muted">${price}</div>
                    </div>
                </div>
            `;
        }).join('');

        const servicesHTML = route.services
            .filter(s => s.checked || s.isRequired)
            .map(service => {
                const price = service.price.map(p => `${p.sum.toLocaleString()} ${p.currency}`).join(', ');
                return `<div class="text-muted">• ${service.name}: ${price}</div>`;
            }).join('');

        routeEl.innerHTML = `
            <h5 class="mb-2">Ставка действует: ${new Date(route.dateFrom).toLocaleDateString()} — ${new Date(route.dateTo).toLocaleDateString()}</h5>
            <div class="mb-2">Условия: ${route.beginCond} - ${route.finishCond}</div>
            <div class="mb-3">Контейнер: ${route.containers.map(c => c.name).join(', ')}</div>
            ${segmentsHTML}
            <h6 class="mt-3">Дополнительные услуги</h6>
            ${servicesHTML}
            <button class="btn btn-primary mt-3">Оформить заявку</button>
        `;

        container.appendChild(routeEl);
    });
    calculateButton.disabled = false;
}
