import { Modal } from "../../components/Modal";
import React, { useState } from "react";
import FormInput from "../../components/form/FormInput";
import FormSubmit from "../../components/form/FormSubmit";
import { Dropdown } from "../../components/Dropdown";
import "../../resources/scss/index.scss";

interface CreatePointModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface CreatePointValues {
    locatePoint: string;
    rusMainName: string;
    engMainName: string;
    engAdditionalName: string;
    rueAdditionalName: string;
}

export function CreatePoint({ isOpen, onClose }: CreatePointModalProps) {
    const [ selectedOption, setSelectedOption ] = useState(""); //todo поменять на настоящие значения
    const [ pointValues, setPointValues ] = useState<CreatePointValues>(
        {
            locatePoint: "",
            rusMainName: "",
            engMainName: "",
            rueAdditionalName: "",
            engAdditionalName: "",
        },
    );
    const handleChangeField = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setPointValues(prev => ({
            ...prev,
            [name]: value,
        }));
    };
    const handleSubmitSave = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            //todo Добавить рычаг для сохранения точки
        } catch (err) {
            console.error("Login error:", err);
        }
    };
    const handleSubmitCancel = () => {
        setSelectedOption("");
        setPointValues({
            locatePoint: "",
            rusMainName: "",
            engMainName: "",
            rueAdditionalName: "",
            engAdditionalName: "",
        });
        onClose();
    };
    return (
        <Modal
            isOpen={ isOpen }
            onClose={ onClose }
            className="modal-wrapper"
        >
            <form onSubmit={ handleSubmitSave }>
                <h2>Где находится точка?</h2>
                <Dropdown
                    options={ [ "1", "2", "3" ] } //todo Поменять на настоящие значения
                    selected={ selectedOption }
                    onSelect={ setSelectedOption }
                    placeholder="Точка..."
                    className = "dropdown-container"
                />

                <h2>Наименование точки</h2>
                <p>Русское</p>
                <FormInput
                    type="text"
                    name="rusMainName"
                    value={ pointValues.rusMainName }
                    placeholder=""
                    onChange={ handleChangeField }
                    className="input"
                    required={ true }></FormInput>

                <p>Английское</p>
                <FormInput
                    type="text"
                    name="engMainName"
                    value={ pointValues.engMainName }
                    placeholder=""
                    onChange={ handleChangeField }
                    className="input"
                    required={ true }></FormInput>

                <p>Перечислите через символ ; русские названия-синомимы</p>
                <FormInput
                    type="text"
                    name="rueAdditionalName"
                    value={ pointValues.rueAdditionalName }
                    placeholder=""
                    onChange={ handleChangeField }
                    className="input"
                    required={ true }></FormInput>

                <p>Перечислите через символ ; английские названия-синомимы</p>
                <FormInput
                    type="text"
                    name="engAdditionalName"
                    value={ pointValues.engAdditionalName }
                    placeholder=""
                    onChange={ handleChangeField }
                    className="input"
                    required={ true }></FormInput>

                <FormSubmit className="form_submit" disabled={ false } type="button" onclick={ handleSubmitCancel }>Отменить</FormSubmit>
                <FormSubmit className="form_submit" disabled={ false } type="button">Создать</FormSubmit>
            </form>
        </Modal>
    );
}
