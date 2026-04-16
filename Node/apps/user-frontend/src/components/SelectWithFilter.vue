<script setup lang="ts" generic="OT">
import { computed, onMounted, onBeforeUnmount, ref, useId, watch } from "vue";

type Option = { value: OT; label: string };

interface Props {
    options: Option[];
    pinnedOptions?: Option[];
    label: string;
    filterFn?: (option: Option, searchText: string) => boolean;
    keyFn?: (option: Option) => string;
    required?: boolean;
    disabled?: boolean;
    placeholder?: string;
    clearSignal?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    pinnedOptions: () => [],
    filterFn: ((opt: Option, text: string) => opt.label.toLowerCase().includes(text)),
    keyFn: ((opt: Option) => String(opt.value)),
    required: false,
    disabled: false,
    placeholder: undefined,
    clearSignal: false,
});

const selectedModel = defineModel<OT | undefined>({ required: false, default: undefined });
const searchText = defineModel<string>("searchText", { required: false, default: "" });

const emit = defineEmits(["update:clearSignal"]);

const inputId = useId();

const isOpen = ref(false);
const innerElementRef1 = ref<HTMLElement | undefined>();
const innerElementRef2 = ref<HTMLElement | undefined>();

const allOptions = computed<Option[]>(() => [...props.pinnedOptions, ...props.options]);

const indexedPinnedOptionsByLabel = computed<Record<string, OT>>(() => {
    const res: Record<string, OT> = {};
    for (const { value, label } of props.pinnedOptions)
        res[label] = value;

    return res;
});

const filteredOptions = computed<Option[]>(() => {
    if (!searchText.value) return props.options;

    const search = searchText.value.toLowerCase();
    return props.options.filter((opt: Option) => props.filterFn(opt, search));
});

const displayOptions = computed<Option[]>(() => [...props.pinnedOptions, ...filteredOptions.value]);

const selectOption = (option: Option) => {
    selectedModel.value = option.value;
    searchText.value = option.label;
    isOpen.value = false;
};

const clearInput = () => {
    selectedModel.value = undefined;
    isOpen.value = true;
};

const handleClickOutside = (event: MouseEvent) => {
    if (
        (!innerElementRef1.value || !innerElementRef1.value.contains(event.target as Node)) &&
        (!innerElementRef2.value || !innerElementRef2.value.contains(event.target as Node))
    ) isOpen.value = false;
}

watch(
    selectedModel,
    (newVal?: OT) => {
        if (!newVal) {
            searchText.value = "";
            return;
        }

        const serializedNewVal = props.keyFn({ value: newVal, label: "" });
        const selectedOption = allOptions.value.find((opt: Option) => props.keyFn(opt) === serializedNewVal);

        if (selectedOption) searchText.value = selectedOption.label;
    },
    { immediate: true },
);

watch(searchText, (newText: string) => (
    selectedModel.value = filteredOptions.value?.length === 1 && filteredOptions.value[0]!.label === newText
        ? filteredOptions.value[0]!.value
        : indexedPinnedOptionsByLabel.value[newText]
));

watch(() => props.clearSignal, (needClear: boolean) => {
    if (needClear) {
        clearInput();
        emit("update:clearSignal", false);
    }
});

onMounted(() => {
    window.addEventListener("click", handleClickOutside);
});

onBeforeUnmount(() => {
    window.removeEventListener("click", handleClickOutside);
});
</script>

<template>
    <div class="autocomplete" :class="{ 'is-open': isOpen }">
        <!-- Label -->
        <label :for="inputId" class="form-label">{{ label }}</label>

        <!-- Input -->
        <div ref="innerElementRef1" class="autocomplete-input-wrapper">
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
        <div ref="innerElementRef2" v-show="isOpen && displayOptions.length" class="autocomplete-items">
            <div
                v-for="option in pinnedOptions"
                :key="props.keyFn(option)"
                class="autocomplete-item pinned-item"
                @click="selectOption(option)"
            >
                <slot name="option" :option="option" :searchText="searchText">
                    {{ option.label }}
                </slot>
            </div>
            <div class="autocomplete-divider" v-show="filteredOptions.length" />
            <div
                v-for="option in filteredOptions"
                :key="props.keyFn(option)"
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
    background: var(--bs-body-bg);
    z-index: 1000;
}

.autocomplete-item {
    padding: 8px 12px;
    cursor: pointer;
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
    color: var(--bs-body-color);
    cursor: pointer;
    padding: 0 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;

    &:hover {
        color: var(--bs-red);
    }
}

.pinned-item {
    background-color: var(--bs-body-bg);
    font-weight: bolder;
}
.autocomplete-divider {
    height: 1px;
    background-color: var(--bs-body-color);
    margin: 4px 0;
}
</style>
