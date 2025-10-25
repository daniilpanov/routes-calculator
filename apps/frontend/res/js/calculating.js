const dispatchDateInput = document.getElementById('dispatchDate');
const departureInput = document.getElementById('departure');
const destinationInput = document.getElementById('destination');
const departureHiddenInput = document.getElementById('departureId');
const destinationHiddenInput = document.getElementById('destinationId');
const cargoWeightInput = document.getElementById('cargoWeight');
const containerTypeInput = document.getElementById('containerType');

dispatchDateInput.valueAsDate = dispatchDateInput.valueAsDate || new Date();
dispatchDateInput.min = dispatchDateInput.min || dispatchDateInput.value;

const departures = { data: {} };

async function updateDepartures() {
    if (!dispatchDateInput.validity.valid) return;
    const date = dispatchDateInput.value;
    const resp = await fetch(`/api/points/departures?date=${date}`);
    if (resp.ok) {
        const data = await resp.json();
        departures.data = {};
        for (const loc in data)
            departures.data[loc] = JSON.stringify(data[loc]);
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
    const resp = await fetch(`/api/points/destinations?date=${date}&departure_point_id=${departureId}`);
    if (resp.ok) {
        const data = await resp.json();
        destinations.data = {};
        for (const loc in data)
            destinations.data[loc] = JSON.stringify(data[loc]);
    }
}, () => {
    destinationInput.disabled = true;
    destinationInput.value = '';
});
setupAutocomplete('destination', 'destinationList', destinations, 'destinationId');

async function calculateAndRender(icons) {
    const payload = {
        dispatchDate: dispatchDateInput.value,
        departureId: JSON.parse(departureHiddenInput.value),
        destinationId: JSON.parse(destinationHiddenInput.value),
        cargoWeight: cargoWeightInput.value,
        containerType: containerTypeInput.value,
    };

    const response = await fetch('/api/routes/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });
    if (!response.ok)
        throw new Error(`[${response.status} ${response.statusText}]<p>` + await response.text());

    const responseData = await response.json();
    const wrappers = [document.getElementById('results-direct'), document.getElementById('results-other')];
    const dataEls = [responseData.one_service_routes, responseData.multi_service_routes];

    for (let i = 0; i < dataEls.length; ++i) {
        const data = dataEls[i];
        if (!data)
            continue;

        const container = wrappers[i];
        container.innerHTML = '';

        data.forEach(route => {
            const routeEl = document.createElement('div');
            routeEl.className = 'p-3 mb-4 border rounded shadow-sm result-item';

            const segmentsHTML = route.map(segment => {
                let svg = icons[segment.type] || '';

                const roundedPrice = Math.round((segment.price + Number.EPSILON) * 100) / 100;
                return `
                    <div class="align-items-center my-2 result-segment" data-bs-price="${roundedPrice}" data-bs-currency="${segment.currency}">
                        <div class="route-icon">${svg} &emsp; ${segment.company}</div>
                        <div class="mb-2">${segment.beginCond ? `Условия: ${segment.beginCond} - ${segment.finishCond}` : ''}</div>
                        <div class="mb-2">Ставка действует: ${new Date(segment.effectiveFrom).toLocaleDateString()} — ${new Date(segment.effectiveTo).toLocaleDateString()}</div>
                        <div class="mb-3">Контейнер: ${segment.container.name}</div>
                        <div>
                            <div>
                                <strong>${segment.startPointCountry.toUpperCase()}, ${segment.startPointName}</strong>
                                 →
                                 <strong>${segment.endPointCountry.toUpperCase()}, ${segment.endPointName}</strong>
                             </div>
                            <div class="text-muted">${roundedPrice} ${segment.currency}</div>
                        </div>
                    </div>
                `;
            }).join('<div class="text-center mb-3 col-md-2">↓</div>');

            routeEl.innerHTML = `
                <div class="segments">
                    ${segmentsHTML}
                </div>
                <div class="mb-3 sum-price"></div>
            `;

            container.appendChild(routeEl);
        });
    }

    updateResults(document.getElementById('currencySwitcher').value);
}
