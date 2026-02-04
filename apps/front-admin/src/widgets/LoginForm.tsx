import { useState, ChangeEvent, FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import "@/resources/scss/widgets/Login.scss";

import { ROUTES } from "@/constants";
import { ILoginCredentials } from "@/interfaces/Auth";
import { login } from "@/services/Auth";
import FormInput from "@/components/form/FormInput";
import FormSubmit from "@/components/form/FormSubmit";


export default function LoginForm() {
    const [ dataForm, setDataForm ] = useState<ILoginCredentials>({
        login: "",
        password: "",
    });
    const [ error, setError ] = useState<String | null>(null);
    const [ loading, setLoading ] = useState(false);

    const navigate = useNavigate();

    const handleChangeField = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setDataForm(prev => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            if (await login(dataForm))
                navigate(ROUTES.DASHBOARD);
            else
                setError("Неверное имя пользователя или пароль");
        } catch (e) {
            setError("Неизвестная ошибка: " + e);
        }

        setLoading(false);
    };

    return (
        <form onSubmit={ handleSubmit } className="form">
            <h2 className="form-header">Авторизация</h2>
            <FormInput
                type="text"
                name="login"
                value={ dataForm.login }
                placeholder="Пользователь"
                onChange={ handleChangeField }
                className="form-input"
                required
            />
            <FormInput
                type="password"
                name="password"
                value={ dataForm.password }
                placeholder="Пароль"
                onChange={ handleChangeField }
                className="form-input"
                required
            />
            <FormSubmit className="form-submit" disabled={ loading }>Войти</FormSubmit>
            <div className="error-message">{ error }</div>
        </form>
    );
}
