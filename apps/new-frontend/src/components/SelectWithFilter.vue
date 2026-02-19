<script setup lang="ts" generic="OT">
import { computed, ref, onMounted, onBeforeUnmount, useId, watch } from "vue";

type Option = { value: OT; label: string };

interface Props {
    options: Option[];
    label: string;
    filterFn?: (option: Option, searchText: string) => boolean;
    required?: boolean;
    disabled?: boolean;
    placeholder?: string;
}

const props = withDefaults(defineProps<Props>(), {
    required: false,
    disabled: false,
    placeholder: undefined,
});
const selectedModel = defineModel<OT | undefined>({ required: false, default: undefined });

const inputId = useId();

const searchText = ref("");
const isOpen = ref(false);
const autocompleteRef = ref<HTMLElement | null>(null);

const filteredOptions = computed(() => {
    if (!searchText.value) return props.options;

    const search = searchText.value.toLowerCase();
    const filter =
        props.filterFn ??
        ((option, text) => option.label.toLowerCase().includes(text.toLowerCase()));

    return props.options.filter((option) => filter(option, search));
});

const selectOption = (option: Option) => {
    selectedModel.value = option.value;
    searchText.value = option.label;
    isOpen.value = false;
};

const clearInput = () => {
    searchText.value = "";
    isOpen.value = true;
};

const handleClickOutside = (event: MouseEvent) => {
    if (autocompleteRef.value && !autocompleteRef.value.contains(event.target as Node))
        isOpen.value = false;
};

watch(
    selectedModel,
    (newVal: OT | undefined) => {
        if (newVal === null) searchText.value = "";
        else {
            const selectedOption = props.options.find((opt) => opt.value === newVal);

            if (selectedOption) searchText.value = selectedOption.label;
        }
    },
    { immediate: true },
);

onMounted(() => {
    window.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
    window.removeEventListener("click", handleClickOutside);
});
</script>

<template>
    <div ref="autocompleteRef" class="autocomplete" :class="{ 'is-open': isOpen }">
        <!-- Label -->
        <label :for="inputId" class="form-label">{{ label }}</label>

        <!-- Input -->
        <div class="autocomplete-input-wrapper">
            <input
                :id="inputId"
                type="text"
                class="form-control"
                :placeholder="placeholder ?? label"
                v-model="searchText"
                @focus="isOpen = true"
                @input="isOpen = true"
                :required="required"
                :disabled="disabled"
                autocomplete="off"
            />
            <button
                v-show="searchText && !disabled"
                class="autocomplete-clear-button"
                type="button"
                @click.stop="clearInput"
                aria-label="Очистить"
            >
                ×
            </button>
        </div>

        <!-- Dropdown list -->
        <div v-show="isOpen && filteredOptions.length" class="autocomplete-items">
            <div
                v-for="(option, index) in filteredOptions"
                :key="index"
                class="autocomplete-item"
                @click="selectOption(option)"
            >
                <slot name="option" :option="option" :searchText="searchText">
                    {{ option.label }}
                </slot>
            </div>
        </div>
    </div>
</template>

<style scoped>
.autocomplete {
    position: relative;
    width: 100%;
}

.autocomplete-items {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    border: 1px solid #ced4da;
    border-top: none;
    max-height: 200px;
    overflow-y: auto;
    background: white;
    z-index: 1000;
}

.autocomplete-item {
    padding: 8px 12px;
    cursor: pointer;

    &:hover {
        background-color: #e9ecef;
    }
}

.autocomplete-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.autocomplete-input-wrapper .form-control {
    padding-right: 30px;
}

.autocomplete-clear-button {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 1.5rem;
    line-height: 1;
    color: #6c757d;
    cursor: pointer;
    padding: 0 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;

    &:hover {
        color: #495057;
    }

    &:focus {
        outline: none;
    }
}
</style>
