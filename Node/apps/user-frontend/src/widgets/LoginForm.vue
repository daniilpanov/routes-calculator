<script setup lang="ts">
import { login as userLogin } from "@/services/auth";

import { ref } from "vue";

const error = ref<string | undefined>();
const username = ref<string>("");
const password = ref<string>("");

async function login(e: Event) {
    e.preventDefault();

    await userLogin({
        login: username.value,
        password: password.value,
    });
}
</script>

<template>
    <form class="form absolute-centered bg-body">
        <h2 class="form-header">Авторизация</h2>
        <input
            type="text"
            name="login"
            placeholder="Пользователь"
            class="form-input outline"
            v-model="username"
            required
        />
        <input
            type="password"
            name="password"
            placeholder="Пароль"
            class="form-input outline"
            v-model="password"
            required
        />
        <button class="form-submit outline" type="submit" @click.stop="login">Войти</button>
        <div class="error-message" v-if="error">{{ error }}</div>
    </form>
</template>

<style scoped>
.form {
    max-width: max-content;

    padding: 3rem 3rem 4rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px var(--bs-body-color);
    display: flex;
    flex-direction: column;
}

.absolute-centered {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;
    height: fit-content;
}

.form-input {
    display: block;
    height: 3rem;
    margin-top: 1rem;
    padding: 0 0.75rem;
    border-radius: 5px;
    font-size: medium;
}

.outline {
    outline: none;
    border: transparent 3px solid;

    &:hover, &:focus-visible {
        border-color: var(--bs-primary);
    }

    transition: border-color ease-out 0.25s;
}

.form-submit {
    --bs-primary: var(--bs-success);

    background-color: transparent;
    font-weight: bold;
    display: block;
    height: 3rem;
    padding: 0 0.75rem;
    margin-top: 1rem;
    border-radius: 0.5rem;
    text-decoration: none;
    cursor: pointer;
}

.form-header {
    text-align: center;
    font-size: larger;
    margin-top: 0.25rem;
    text-transform: uppercase;
    font-weight: bold;
}

.error-message {
    color: red;
    font-size: smaller;
}
</style>
