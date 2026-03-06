<script setup lang="ts">
import type { IPrice } from "@/interfaces/Routes";

import PriceWithCurrency from "@/components/PriceWithCurrency.vue";
import { isConversationNeeded } from "@/services/rates";
import { computed } from "vue";

const props = withDefaults(defineProps<{
    priceVariant: IPrice,
    editable?: boolean,
}>(), { editable: false });

const needConversation = computed(
    () => isConversationNeeded(props.priceVariant.currency)
);

defineEmits(["update:price"]);
</script>

<template>
    <div>
        <div class="segment--price-variant">
            <div class="mb-2">Условия: {{ priceVariant.cond }}</div>
            <div class="mb-2">Контейнер: {{ priceVariant.container.name }}</div>
            <div>
                <PriceWithCurrency
                    :editable="editable"
                    :price="priceVariant.value"
                    :currency="priceVariant.currency"
                    @update:price="(val: number) => $emit('update:price', val)"
                />
                <span v-if="priceVariant.conversation_percents && needConversation" class="text-muted">
                    + {{ priceVariant.conversation_percents }}% конвертация в рубли
                </span>
            </div>
        </div>
    </div>
</template>

<style scoped>
.segment--price-variant {
    padding: 1rem;
    margin: 1rem;
    border-radius: 0.25rem;
    border: 1px solid var(--bs-border-color);
}
</style>
