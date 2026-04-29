import { useUser } from "@/stores/user";
import { useRouter } from "@/stores/router";
import { gotoAuthForm, gotoHome } from "@/services/redirects";
import { updateUser } from "@/services/auth";
import { watch } from "vue";

import type { IUser } from "@/interfaces/User";
import type { RouteRecordNameGeneric } from "vue-router";

export function mountAuthProvider() {
    watch(
        [
            () => useUser().user,
            () => useRouter().getCurrentRoute()?.value?.name,
        ],
        (
            [newUser, newRouteName]
        ) => provideUser(newUser, newRouteName),
        { immediate: true },
    );
}

async function provideUser(newUser: IUser | null, newRouteName?: RouteRecordNameGeneric) {
    if (!newRouteName)
        return;

    if (newRouteName === "calculator" && !newUser)
        try {
            await updateUser();
        } catch (e) {
            console.log(e);
            gotoAuthForm();
        }
    else if (newRouteName === "login" && newUser)
        gotoHome();
}
