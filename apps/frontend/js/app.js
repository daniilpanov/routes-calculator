class App {
    _currenciesSwitcherInput;
    _currenciesSwitcherInputWrapper;
    _dispatchDateInput;
    _showAllRoutesCheckbox;
    _departureInput;
    _destinationInput;
    _departureHiddenInput;
    _destinationHiddenInput;
    _containerWeightInput;
    _containerTypeInput;

    constructor(
        _currenciesSwitcherInput,
        _currenciesSwitcherInputWrapper,
        _dispatchDateInput,
        _showAllRoutesCheckbox,
        _departureInput,
        _destinationInput,
        _departureHiddenInput,
        _destinationHiddenInput,
        _containerWeightInput,
        _containerTypeInput,
    ) {
        this._currenciesSwitcherInput = _currenciesSwitcherInput;
        this._currenciesSwitcherInputWrapper = _currenciesSwitcherInputWrapper;
        this._dispatchDateInput = _dispatchDateInput;
        this._showAllRoutesCheckbox = _showAllRoutesCheckbox;
        this._departureInput = _departureInput;
        this._destinationInput = _destinationInput;
        this._departureHiddenInput = _departureHiddenInput;
        this._destinationHiddenInput = _destinationHiddenInput;
        this._containerWeightInput = _containerWeightInput;
        this._containerTypeInput = _containerTypeInput;
    }

    async setup() {
        this._setupAutocomplete();

        this._currenciesSwitcherInput.addEventListener("input", this._updateSelectedCurrency.bind(this));
        this._updateSelectedCurrency();

        this._dispatchDateInput.valueAsDate = this._dispatchDateInput.valueAsDate || new Date();

        document.getElementById("currencySwitcherSelect")?.addEventListener("change", e => {
            const val = e?.target?.value;
            if (val === undefined)
                return;

            this._currenciesSwitcherInput.value = val;
            if (val)
                this._currenciesSwitcherInputWrapper.classList.add("inactive");
            else
                this._currenciesSwitcherInputWrapper.classList.remove("inactive");

            this._currenciesSwitcherInput.dispatchEvent(
                new Event("input", { bubbles: true }),
            );
        });

        const rates = await updateRates();

        const currencySelect = document.getElementById("currencySwitcherList");
        for (const rate in rates) {
            const optionEl = document.createElement("option");
            optionEl.value = rate;
            currencySelect.appendChild(optionEl);
        }

        const mappedRates = {};
        for (const rate in rates)
            mappedRates[rate] = rate;

        setupAutocomplete("currencySwitcher", "currencySwitcherList", "rates", null, renderRoutes);

        await this._updateDepartures();

        const iconsMap = {
            "sea": "/res/img/route-icons/sea.svg",
            "rail": "/res/img/route-icons/rail.svg",
            "truck": "/res/img/route-icons/truck.svg",
        };

        store.set("icons", Object.fromEntries(
            (await Promise.allSettled(
                Object.entries(iconsMap).map(this._loadIcon)
            ))
            .map(item => Object.values(item.value))
        ));

        const ctx = this;
        document.getElementById("calcForm").addEventListener("submit", async function (e) {
            if (!this.checkValidity())
                return;

            e.preventDefault();
            await ctx._processCalculation.bind(ctx)();
        });
    }

    _setupAutocomplete() {
        setupAutocomplete(
            "departure",
            "departureList",
            "departures",
            "departureId",
            this._updateDestinations.bind(this),
            () => {
                this._destinationInput.disabled = true;
                this._destinationInput.value = "";
            },
        );

        setupAutocomplete("destination", "destinationList", "destinations", "destinationId");

        this._dispatchDateInput.addEventListener("input", this._updateDepartures.bind(this));
    }

    async _updateDepartures() {
        if (!this._dispatchDateInput.validity.valid)
            return;

        const date = this._dispatchDateInput.value;

        store.lock("departures");
        store.set("departures", await asyncCallOrAlert(getDepartures, date));
        store.unlock("departures");

        this._destinationInput.value = "";
        this._destinationHiddenInput.value = "";
        this._destinationInput.disabled = true;
    }

    async _updateDestinations() {
        const date = this._dispatchDateInput.value;
        const departureId = this._departureHiddenInput.value;

        store.lock("destinations");
        store.set("destinations", await asyncCallOrAlert(getDestinations, date, departureId));
        store.unlock("destinations");

        this._destinationInput.disabled = false;
    }

    _updateSelectedCurrency() {
        store.set("selectedCurrency", this._currenciesSwitcherInput.value);
    }

    async _loadIcon([ key, path ]) {
        return { key, content: await (await fetch(path)).text() };
    }

    async _processCalculation() {
        if (!this._departureHiddenInput.value || !this._destinationHiddenInput.value) {
            showGlobalAlert("Пожалуйста, выберите один из вариантов пункта А и пункта Б.");

            if (!this._departureHiddenInput.value)
                this._departureInput.classList.add("is-invalid");

            if (!this._destinationHiddenInput.value)
                this._destinationInput.classList.add("is-invalid");

            return;
        }

        const selectedCurrency = store.get("selectedCurrency").value;
        if (!selectedCurrency || selectedCurrency.trim() === "") {
            showGlobalAlert("Пожалуйста, выберите валюту.");
            this._currenciesSwitcherInput.classList.add("is-invalid");
            return;
        }

        const rates = store.get("rates").value;
        if (!rates || !rates[selectedCurrency]) {
            showGlobalAlert(`Валюта "${selectedCurrency}" не найдена.`);
            this._currenciesSwitcherInput.classList.add("is-invalid");
            return;
        }

        this._departureInput.classList.remove("is-invalid");
        this._destinationInput.classList.remove("is-invalid");

        const calculateButton = document.getElementById("calculate");
        calculateButton.disabled = true;

        try {
            await updateRoutes(
                this._dispatchDateInput.value,
                this._showAllRoutesCheckbox.checked ?? false,
                JSON.parse(this._departureHiddenInput.value),
                JSON.parse(this._destinationHiddenInput.value),
                this._containerWeightInput.value,
                this._containerTypeInput.value,
            );
            renderRoutes();
        } catch (e) {
            showGlobalAlert(`Error: ${e.message}`);
        } finally {
            calculateButton.disabled = false;
        }
    }
}
