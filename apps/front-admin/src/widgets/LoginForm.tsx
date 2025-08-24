import React, { useState } from "react";
import FormInput from "../components/form/FormInput";
import FormSubmit from "../components/form/FormSubmit";
import "../resources/scss/login_style.scss";
import { authService } from "../services/Auth";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "../services/RoutesConst";

interface LoginFormData {
    login: string;
    password: string;
}


export function LoginForm() {
    const [ dataForm, setDataForm ] = useState<LoginFormData>({
        login: "",
        password: "",
    });
    const [ error, setError ] = useState<String | null>(null);
    const [ loading, setLoading ] = useState(false);

    const navigate = useNavigate();

    const handleChangeField = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setDataForm(prev => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        try {
            const response = await authService.login(dataForm); //todo вернуть обратно, только для локальной разработки
            //const response = { "status": "OK" };
            if (response.status === "OK") {
                localStorage.setItem("username", dataForm.login);
            }

            navigate(ROUTES.DASHBOARD);
        } catch (err) {
            setError("Неверное имя пользователя или пароль");
            console.error("Login error:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login_page_container">
            <div className="form_div">
                <form onSubmit={ handleSubmit } className="forma_login">
                    <p className="form_p">Авторизация</p>
                    <FormInput
                        type="text"
                        name="login"
                        value={ dataForm.login }
                        placeholder="Пользователь"
                        onChange={ handleChangeField }
                        className="form_input"
                        required
                    />
                    <FormInput
                        type="password"
                        name="password"
                        value={ dataForm.password }
                        placeholder="Пароль"
                        onChange={ handleChangeField }
                        className="form_input"
                        required
                    />
                    <FormSubmit className="form_submit" disabled={ loading }>Войти</FormSubmit>
                </form>
            </div>
        </div>
    );
}
