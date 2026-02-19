import { ref } from "vue";
import { defineStore } from "pinia";

export const useLang = defineStore("lang", () => {
    const lang = ref("ru");
    const setLang = (newLang: string) => (lang.value = newLang);

    return { lang, setLang };
});
