const dispatchDateInput = document.getElementById("dispatchDate");
const showAllRoutesCheckbox = document.getElementById("showAllRoutes");
const departureInput = document.getElementById("departure");
const destinationInput = document.getElementById("destination");
const departureHiddenInput = document.getElementById("departureId");
const destinationHiddenInput = document.getElementById("destinationId");
const cargoWeightInput = document.getElementById("cargoWeight");
const containerTypeInput = document.getElementById("containerType");

dispatchDateInput.valueAsDate = dispatchDateInput.valueAsDate || new Date();

const departures = { data: {} };

function getCurrencySymbol(currName, defaultCur = undefined) {
    const currMap = {RUB: "₽", USD: "$"};
    return currMap[currName] ?? defaultCur;
}

async function updateDepartures() {
    if (!dispatchDateInput.validity.valid) return;
    const date = dispatchDateInput.value;
    const resp = await fetch(`/api/points/departures?date=${date}`);
    if (resp.ok) {
        const data = await resp.json();
        departures.data = {};
        for (const loc in data)
            departures.data[loc] = JSON.stringify(data[loc]);
        destinationInput.value = "";
        destinationHiddenInput.value = "";
        destinationInput.disabled = true;
    }
}

dispatchDateInput.addEventListener("input", updateDepartures);

const destinations = { data: {} };

setupAutocomplete("departure", "departureList", departures, "departureId", async () => {
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
    destinationInput.value = "";
});
setupAutocomplete("destination", "destinationList", destinations, "destinationId");

async function calculateAndRender(icons, selectedCurrency) {
    const payload = {
        dispatchDate: dispatchDateInput.value,
        onlyInSelectedDateRange: !showAllRoutesCheckbox.checked ?? false,
        departureId: JSON.parse(departureHiddenInput.value),
        destinationId: JSON.parse(destinationHiddenInput.value),
        cargoWeight: cargoWeightInput.value,
        containerType: containerTypeInput.value,
    };

    const response = await fetch("/api/routes/calculate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
    if (!response.ok)
        throw new Error(`[${response.status} ${response.statusText}]<p>` + await response.text());

    const responseData = await response.json();
    const wrappers = [document.getElementById("results-direct"), document.getElementById("results-other")];
    const dataEls = [responseData.one_service_routes, responseData.multi_service_routes];

    for (let i = 0; i < dataEls.length; ++i) {
        const data = dataEls[i];
        if (!data)
            continue;

        const container = wrappers[i];
        container.innerHTML = "";

        container.append(...data.map(([route, drop, mayRouteBeInvalid]) =>
            _buildRoute(route, drop, mayRouteBeInvalid, icons, selectedCurrency)
        ));
    }

    updateResults(document.getElementById("currencySwitcher").value);
}

function _buildRoute(route, drop, mayRouteBeInvalid, icons, selectedCurrency) {
    const routeEl = document.createElement("div");
    routeEl.className = "p-3 mb-4 border rounded shadow-sm result-item";

    if (mayRouteBeInvalid)
        routeEl.innerHTML = renderRouteMayBeInvalidHint();

    const segmentsEl = document.createElement("div");
    segmentsEl.className = "segments";

    segmentsEl.innerHTML = route
        .map(segment => {
            const icon = segment.type === "SEA_RAIL"
                ? "Море+ЖД"
                : icons[segment.type.toLowerCase()] || segment.type;

            return segment.price
                ? renderSinglePrice(icon, segment)
                : renderMultiPrice(icon, segment, segment.type === "SEA_RAIL", selectedCurrency);
        })
        .join("<div class='text-center mb-3 col-md-2'>↓</div>");

    routeEl.appendChild(segmentsEl);
    routeEl.appendChild(document.createElement("hr"));
    routeEl.appendChild(renderDrop(drop));

    const sumPriceEl = document.createElement("div");
    sumPriceEl.classList.add("sum-price", "mb-3");
    routeEl.appendChild(sumPriceEl);

    return routeEl;
}
