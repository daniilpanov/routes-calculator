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

function _renderComment(text) {
    return text ? `<blockquote><p>Комментарий: <i>${text}</i></p></blockquote>` : "";
}

function _renderOnePriceOfSegment(priceVariant) {
    const roundedPrice = Math.round((priceVariant.value + Number.EPSILON) * 100) / 100;
    const needConversationPercents = priceVariant.conversation_percents
        && ["RUB", "РУБ"].indexOf(priceVariant.currency) === -1;

    const [ attrInsertion, contentInsertion ] = (
        () => needConversationPercents ? [
            `data-bs-conversation-percents="${priceVariant.conversation_percents}"`,
            ` + ${priceVariant.conversation_percents}% конвертация в РУБ`,
        ] : ["", ""]
    )();

    return `<div class="col-md">
        <div class="segment--price-variant" data-bs-price="${roundedPrice}" data-bs-currency="${priceVariant.currency}"${attrInsertion}>
            <div class="mb-2">Условия: ${priceVariant.cond}</div>
            <div class="mb-2">${priceVariant.container.name}</div>
            <div class="text-muted">${roundedPrice} ${priceVariant.currency}${contentInsertion}</div>
        </div>
    </div>`;
}

function _renderMultiPrice(icon, segment, isMixed, selectedCurrency) {
    return `
        <div class="align-items-center my-2 result-segment" data-bs-price="${isMixed ? "X" : "M"}">
            <div class="route-icon">${icon} &emsp; ${segment.company}</div>
            <div class="mb-2">
                Ставка действует:
                ${new Date(segment.effectiveFrom).toLocaleDateString()} — ${new Date(segment.effectiveTo).toLocaleDateString()}
            </div>
            <div class="mb-3 row">
                ${
                    segment.prices
                        .map(priceVariant => _renderOnePriceOfSegment(priceVariant, selectedCurrency))
                        .join("\n")
                }
            </div>
            <div>
                <div>
                    <strong>${segment.startPointCountry?.toUpperCase() || ""}, ${segment.startPointName}</strong>
                     →
                     <strong>${segment.endPointCountry?.toUpperCase() || ""}, ${segment.endPointName}</strong>
                 </div>
            </div>
            ${_renderComment(segment.comment)}
        </div>
    `;
}

function _renderSinglePrice(icon, segment) {
    const roundedPrice = Math.round((segment.price + Number.EPSILON) * 100) / 100;
    return `
        <div class="align-items-center my-2 result-segment" data-bs-price="${roundedPrice}" data-bs-currency="${segment.currency}">
            <div class="route-icon">${icon} &emsp; ${segment.company}</div>
            <div class="mb-2">${segment.beginCond ? `Условия: ${segment.beginCond} - ${segment.finishCond}` : ""}</div>
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
            ${_renderComment(segment.comment)}
        </div>
    `;
}

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

        data.forEach(([route, drop, mayRouteBeInvalid]) => {
            const routeEl = document.createElement("div");
            routeEl.className = "p-3 mb-4 border rounded shadow-sm result-item";

            if (mayRouteBeInvalid) {
                routeEl.innerHTML = `
                <div class="alert alert-warning d-flex align-items-center" role="alert">
                  <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Warning:"><use xlink:href="#exclamation-triangle-fill"/></svg>
                  <div>
                    Маршрут может быть неактуален
                  </div>
                </div>
                `;
            }

            const segmentsEl = document.createElement("div");
            segmentsEl.className = "segments";

            segmentsEl.innerHTML = route
                .map(segment => {
                    const icon = segment.type === "SEA_RAIL"
                        ? "Море+ЖД"
                        : icons[segment.type.toLowerCase()] || segment.type;

                    return segment.price
                        ? _renderSinglePrice(icon, segment)
                        : _renderMultiPrice(icon, segment, segment.type === "SEA_RAIL", selectedCurrency);
                })
                .join("<div class='text-center mb-3 col-md-2'>↓</div>");

            routeEl.appendChild(segmentsEl);

            routeEl.appendChild(document.createElement("hr"));

            let dropEl = document.createElement("div");
            dropEl.className = "drop-off row";
            dropEl.innerHTML = "<div class='col-md-7'>Drop off:</div>";

            const dropPriceEl = document.createElement("div");
            dropPriceEl.className = "col-md-5";

            if (drop?.price) {
                const priceSpan = document.createElement("b");
                priceSpan.className = "drop-off-price";
                priceSpan.innerHTML = drop.price;

                const currencySpan = document.createElement("b");
                currencySpan.className = "drop-off-currency";
                currencySpan.setAttribute("data-bs-currency", drop.currency);
                const currencySymbol = getCurrencySymbol(drop.currency);
                currencySpan.innerHTML = currencySymbol ?? drop.currency;

                if (currencySymbol) {
                    dropPriceEl.appendChild(currencySpan);
                    dropPriceEl.appendChild(priceSpan);
                } else {
                    dropPriceEl.appendChild(priceSpan);
                    dropPriceEl.appendChild(currencySpan);
                }

                if (drop.conversation_percents) {
                    const conversationPercentsEl = document.createElement("span");
                    conversationPercentsEl.className = "text-muted drop-off-conversation";
                    conversationPercentsEl.setAttribute("data-bs-conversation", drop.conversation_percents);
                    conversationPercentsEl.innerHTML = `+ ${drop.conversation_percents}% конвертация в рубли`;
                    dropPriceEl.appendChild(document.createTextNode(" "));
                    dropPriceEl.appendChild(conversationPercentsEl);
                }
            } else
                dropPriceEl.innerHTML = "<b>включен</b>";

            dropEl.appendChild(dropPriceEl);
            routeEl.appendChild(dropEl);

            const sumPriceEl = document.createElement("div");
            sumPriceEl.classList.add("sum-price", "mb-3");
            routeEl.appendChild(sumPriceEl);

            container.appendChild(routeEl);
        });
    }

    updateResults(document.getElementById("currencySwitcher").value);
}
