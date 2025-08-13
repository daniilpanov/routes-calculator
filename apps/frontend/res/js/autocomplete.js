function setupAutocomplete(inputId, listId, dataObj, hiddenInputId, callbackOnCompleted, callbackOnUncompleted) {
    const input = document.getElementById(inputId);
    const hiddenInput = hiddenInputId ? document.getElementById(hiddenInputId) : null;
    const list = document.getElementById(listId);

    function autocompleteProcess() {
        const data = dataObj.data;
        const val = this.value.trim().toLowerCase();
        list.innerHTML = '';

        const filtered = Object.keys(data).filter(item => item.toLowerCase().includes(val));
        if (!filtered.length) {
            list.classList.add('d-none');
            if (callbackOnUncompleted) callbackOnUncompleted();
            return;
        }

        let selectedVal = null;

        filtered.forEach(item => {
            if (item.toLowerCase() === val.toLowerCase()) selectedVal = item;
            const div = document.createElement('div');
            div.textContent = item;
            div.setAttribute('data-item-id', data[item]);
            div.classList.add('autocomplete-item');
            div.addEventListener('mousedown', () => {
                input.value = item;
                if (hiddenInput)
                    hiddenInput.value = data[item];
                input.classList.remove('is-invalid');
                list.classList.add('d-none');
                if (callbackOnCompleted) callbackOnCompleted(item);
            });
            list.appendChild(div);
        });
        if (selectedVal) {
            input.value = selectedVal;
            if (hiddenInput)
                hiddenInput.value = data[selectedVal];
            if (callbackOnCompleted) callbackOnCompleted(selectedVal);
        } else {
            if (hiddenInput)
                hiddenInput.value = '';
            if (callbackOnUncompleted) callbackOnUncompleted();
        }

        list.classList.remove('d-none');
    }

    input.addEventListener('input', autocompleteProcess);
    input.addEventListener('focus', autocompleteProcess);

    input.addEventListener('blur', () => {
        setTimeout(() => list.classList.add('d-none'), 50);
    });
}
