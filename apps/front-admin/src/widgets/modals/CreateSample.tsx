import React, { useState } from "react";
import { Modal } from "../../components/Modal";
import "../../resources/scss/index.scss";
import { Dropdown } from "../../components/Dropdown";
import { UploadFile } from "./UploadFile";
import { dateStringToTimestamp, timestampToDateString } from "../../utils/DateFormater";

interface CreateSampleProps {
    isOpen: boolean;
    onClose: () => void;
}
export interface FormData {
    company: {
        type: "name" | "column";
        value: string;
    };
    date: {
        type: "range" | "columns";
        start: string | number;
        end: string | number;
    };
    route: {
        type: string;
        additionalData?: string | number;
    };
    nameSample: string;
}
export function CreateSample({ isOpen, onClose }: CreateSampleProps) {
    const [ isModalOpenUF, setIsModalOpenUF ] = useState(false);
    const [ onlyDropFlag, setOnlyDropFlag ] = useState(true);
    const [ optionsTypesRoute ] = useState([
        "Морские",
        "Железнодорожные",
        "Железнодорожные + drop",
        "Только DROP",
        "Указан в колонке",
    ]);
    const [ formSample, setFormSample ] = useState<FormData>({
        company: {
            type: "name",
            value: "",
        },
        date: {
            type: "range",
            start: "",
            end: "",
        },
        route: {
            type: "",
        },
        nameSample: "",
    });
    const validateForm = (form: FormData, checkNameSample: boolean) => {
        if (form.company.type === "name" && !form.company.value.trim()) {
            alert("Введите название компании!");
            return false;
        }
        if (form.company.type === "column" && !form.company.value.trim()) {
            alert("Введите название столбца компании!");
            return false;
        }

        if (form.date.type === "range") {
            if (!form.date.start || !form.date.end) {
                alert("Заполните диапазон дат!");
                return false;
            }
        } else {
            if (!form.date.start || !form.date.end) {
                alert("Заполните столбцы с датами!");
                return false;
            }
        }

        if (!form.route.type) {
            alert("Выберите тип маршрута!");
            return false;
        }
        if (
            (form.route.type === "Железнодорожные + drop" ||
                form.route.type === "Указан в колонке") &&
            (!form.route.additionalData || form.route.additionalData === "")
        ) {
            alert("Заполните дополнительное поле маршрута!");
            return false;
        }

        if (checkNameSample && !form.nameSample.trim()) {
            alert("Введите название шаблона!");
            return false;
        }

        return true;
    };

    // Для сохранения шаблона
    const saveSample = () => {
        if (!validateForm(formSample, true)) return; // проверяем nameSample

        try {
            const stored = localStorage.getItem("samples");
            let currentSamples: FormData[] = [];
            if (stored) {
                const parsed = JSON.parse(stored);
                currentSamples = Array.isArray(parsed) ? parsed : [ parsed ];
            }

            const updatedSamples = [ ...currentSamples, formSample ];
            localStorage.setItem("samples", JSON.stringify(updatedSamples));
            setIsModalOpenUF(true);
        } catch (e) {
            console.error("Failed to save sample:", e);
        }
    };

    const useOnce = () => {
        if (!validateForm(formSample, false)) return;
        setIsModalOpenUF(true);
    };


    const handleChangeForm = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        const [ namee, se ] = name.split("-");
        setFormSample(prev => {
            if (name === "company") {
                return {
                    ...prev,
                    company: {
                        ...prev.company,
                        value: value,
                    },
                };
            }
            if (namee === "date") {
                if (prev.date.type === "range") {
                    return {
                        ...prev,
                        date: {
                            ...prev.date,
                            [se]: dateStringToTimestamp(value),
                        },
                    };
                }
                else {
                    return {
                        ...prev,
                        date: {
                            ...prev.date,
                            [se]: value,
                        },
                    };
                }
            }
            return prev;
        });
    };
    const handleActiveInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, checked } = e.target;
        setFormSample(prev => {
            if (name === "company") {
                return {
                    ...prev,
                    company: {
                        ...prev.company,
                        type: checked ? "column" : "name",
                        value: "",
                    },
                };
            }
            if (name === "date") {
                return {
                    ...prev,
                    date: {
                        ...prev.date,
                        type: checked ? "columns" : "range",
                        start: "",
                        end: "",
                    },
                };
            }

            return prev;
        });
        console.log(formSample);
    };
    const handleChangeTypeRoute = (type: string) => {
        setFormSample(prev => {
            let additionalData: string | number | undefined;

            switch (type) {
            case "Железнодорожные + drop":
            case "Указан в колонке":
                additionalData = "";
                break;
            case "Только DROP":
                additionalData = "";
                break;
            case "Морские":
            case "Железнодорожные":
            default:
                additionalData = undefined;
            }

            return {
                ...prev,
                route: {
                    ...prev.route,
                    type: type,
                    additionalData: additionalData,
                },
            };
        });
        setOnlyDropFlag(true);
        console.log(formSample);
    };
    return (
        <>
            <Modal
                isOpen={ isOpen }
                onClose={ onClose }
                className="modal-wrapper"
            >
                <div className="modal_div">
                    <div className="section_div">
                        <div className="name_div">
                            <p>Название шаблона (Если многоразовый)</p>
                            <input
                                className="input"
                                type="text"
                                name="nameSample"
                                onChange ={ (e) => setFormSample(prev => ({
                                    ...prev,
                                    nameSample: e.target.value,
                                })) }
                            />
                        </div>
                    </div>
                    <div className="section_div">
                        <div className="name_div">
                            <p>Название компании</p>
                            <input
                                className="input"
                                type="text"
                                name="company"
                                value={ formSample.company.type === "name" ? formSample.company.value : "" }
                                onChange={ handleChangeForm }
                                disabled={ formSample.company.type !== "name" }
                            />
                        </div>
                        <div className="section_div">
                            <label className="switch">
                                <input
                                    type="checkbox"
                                    name="company"
                                    onChange={ handleActiveInput }
                                />
                                <span className="slider"></span>
                            </label>
                        </div>
                        <div className="name_div">
                            <p>Название столбца с наименованием</p>
                            <input
                                className="input"
                                type="text"
                                name="company"
                                value={ formSample.company.type === "column" ? formSample.company.value : "" }
                                onChange={ handleChangeForm }
                                disabled={ formSample.company.type !== "column" }
                            />
                        </div>
                    </div>

                    <div className="section_div">
                        <div className="name_div">
                            <p>Диапазон эффективных дат</p>
                            <div className="date_div">
                                <input
                                    className="date-input"
                                    type="date"
                                    name="date-start"
                                    onChange={ handleChangeForm }
                                    value={
                                        formSample.date.type === "range" && typeof formSample.date.start === "number"
                                            ? timestampToDateString(formSample.date.start)
                                            : ""
                                    }
                                    disabled={ formSample.date.type !== "range" }
                                />
                                -
                                <input
                                    className="date-input"
                                    type="date"
                                    name="date-end"
                                    onChange={ handleChangeForm }
                                    value={
                                        formSample.date.type === "range" && typeof formSample.date.end === "number"
                                            ? timestampToDateString(formSample.date.end)
                                            : ""
                                    }
                                    disabled={ formSample.date.type !== "range" }
                                />
                            </div>
                        </div>
                        <div className="section_div">
                            <label className="switch">
                                <input
                                    type="checkbox"
                                    name="date"
                                    onChange={ handleActiveInput }
                                />
                                <span className="slider"></span>
                            </label>
                        </div>
                        <div className="name_div">
                            <p>Столбец/столбцы с эффективной датой</p>
                            <div className="date_div">
                                <input
                                    className="input"
                                    name="date-start"
                                    type="text"
                                    value={
                                        formSample.date.type === "columns" && typeof formSample.date.start === "string"
                                            ? formSample.date.start
                                            : ""
                                    }
                                    onChange={ handleChangeForm }
                                    disabled={ formSample.date.type !== "columns" }
                                />
                                -
                                <input
                                    className="input"
                                    name="date-end"
                                    type="text"
                                    value={
                                        formSample.date.type === "columns" && typeof formSample.date.end === "string"
                                            ? formSample.date.end
                                            : ""
                                    }
                                    onChange={ handleChangeForm }
                                    disabled={ formSample.date.type !== "columns" }
                                />
                            </div>
                        </div>
                    </div>
                    <div className="section_div">
                        <Dropdown
                            options={ optionsTypesRoute }
                            selected={ formSample.route.type }
                            onSelect={ handleChangeTypeRoute }
                            placeholder="Выберите тип маршрута"
                        />
                    </div>
                    <div className="section_div">
                        {
                            formSample.route.type === "Железнодорожные + drop" && (
                                <>
                                    <p>Колонка с ценой drop'a</p>
                                    <input
                                        className="input"
                                        name="additionalData"
                                        onChange={ (e) => setFormSample(prev => ({
                                            ...prev,
                                            route: {
                                                ...prev.route,
                                                additionalData: e.target.value,
                                            },
                                        })) }
                                    />
                                </>
                            )
                        }
                        {
                            formSample.route.type === "Только DROP" && (
                                <>
                                    <input
                                        type="checkbox"
                                        onChange={ () => {
                                            setOnlyDropFlag(!onlyDropFlag);
                                            setFormSample(prev => ({
                                                ...prev,
                                                route: {
                                                    ...prev.route,
                                                    additionalData: "",
                                                },
                                            }));
                                        } }

                                    />
                                    <input
                                        className="input"
                                        name="additionalData"
                                        onChange={ (e) => setFormSample(prev => ({
                                            ...prev,
                                            route: {
                                                ...prev.route,
                                                additionalData: e.target.value,
                                            },
                                        })) }
                                        value={ onlyDropFlag ? formSample.route.additionalData : undefined }
                                        disabled={ onlyDropFlag }
                                    />
                                </>


                            )
                        }
                        {
                            formSample.route.type === "Указан в колонке" && (
                                <input
                                    className="input"
                                    name="additionalData"
                                    onChange={ (e) => setFormSample(prev => ({
                                        ...prev,
                                        route: {
                                            ...prev.route,
                                            additionalData: e.target.value,
                                        },
                                    })) }
                                />
                            )
                        }
                    </div>
                    <div className="section_div">
                        <button
                            className="control_btn accept"
                            onClick={ saveSample }
                        >Сохранить шаблон</button>
                        <button
                            className="control_btn accept"
                            onClick={ useOnce }
                        >Использовать один раз</button>

                        <button
                            className="control_btn cancel"
                        >Отмена</button>
                    </div>
                </div>
            </Modal>
            <UploadFile
                isOpen={ isModalOpenUF }
                onClose={ () => setIsModalOpenUF(false) }
                formSample={ formSample }
            />
        </>
    );
}
