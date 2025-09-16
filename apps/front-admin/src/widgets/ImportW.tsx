import React, { useEffect, useState } from "react";
import { CreateSample, FormData } from "./modals/CreateSample";
import { TooltipItem } from "../components/TooltipItem";
import { UploadFile } from "./modals/UploadFile";
import { timestampToDateStringRU } from "../utils/DateFormater";
import "../resources/scss/index.scss";
import trashcan from "../resources/images/trashcan.png";

export function ImportW() {
    const [ isModalOpen, setIsModalOpen ] = useState(false);
    const [ uploadModalOpen, setUploadModalOpen ] = useState(false);
    const [ selectedSample, setSelectedSample ] = useState<FormData | null>(null);

    const [ samples, setSamples ] = useState<FormData[]>(() => {
        try {
            const stored = localStorage.getItem("samples");
            if (!stored) return [];
            const parsed = JSON.parse(stored);
            return Array.isArray(parsed) ? parsed : [ parsed ];
        } catch {
            return [];
        }
    });

    const handleSelectSample = (sample: FormData) => {
        setSelectedSample(sample);
        setUploadModalOpen(true);
    };

    const handleDeleteSample = (idx: number) => {
        const updatedSamples = samples.filter((_, i) => i !== idx);
        setSamples(updatedSamples);
        localStorage.setItem("samples", JSON.stringify(updatedSamples));
    };

    return (
        <div className="import_page">
            <div className="heading_div">
                <h1>Загрузка данных</h1>
            </div>

            <div>
                <p className="text_like_btn">Выберите шаблон данных или создайте новый</p>
            </div>

            <div className="samples_list">
                <button
                    onClick={ () => setIsModalOpen(true) }
                    className="control_btn"
                >
                    +
                </button>

                {samples.map((sample, idx) => (
                    <div
                        key={ idx }
                        className="sample_wrapper"
                    >
                        <TooltipItem
                            label={ sample.nameSample }
                            onClick={ () => handleSelectSample(sample) }
                        >
                            <div>
                                <p>
                                    {sample.company.type === "name" ? (
                                        <>
                                            <strong>Название компании:</strong>{" "}
                                            {sample.company.value || "не указано"}
                                        </>
                                    ) : (
                                        <>
                                            <strong>Колонка с названием компании:</strong>{" "}
                                            {sample.company.value || "не указано"}
                                        </>
                                    )}
                                </p>
                                <p>
                                    {sample.date.type === "range" ? (
                                        <>
                                            <strong>Диапазон дат:</strong>{" "}
                                            {timestampToDateStringRU(sample.date.start) || "не указано"} по{" "}
                                            {timestampToDateStringRU(sample.date.end) || "не указано"}
                                        </>
                                    ) : (
                                        <>
                                            <strong>Столбцы с датами:</strong>{" "}
                                            {sample.date.start || "не указано"} / {sample.date.end || "не указано"}
                                        </>
                                    )}
                                </p>
                                <p>
                                    <strong>Маршрут:</strong>{" "}
                                    {sample.route.type === "Морские" || sample.route.type === "Железнодорожные"
                                        ? sample.route.type
                                        : sample.route.type === "Железнодорожные + drop"
                                            ? `Железнодорожные + drop — колонка с ценой: ${sample.route.additionalData || "не указано"}`
                                            : sample.route.type === "Только DROP"
                                                ? `Только DROP — колонка с ценой: ${sample.route.additionalData || "не указано"}`
                                                : sample.route.type === "Указан в колонке"
                                                    ? `Указан в колонке: ${sample.route.additionalData || "не указано"}`
                                                    : "не указано"}
                                </p>
                                <p>
                                    <strong>Название шаблона:</strong> {sample.nameSample || "не указано"}
                                </p>
                            </div>
                        </TooltipItem>

                        <button
                            className="actions_btn cancel"
                            onClick={ () => handleDeleteSample(idx) }
                        >
                            <img src={ trashcan } alt="удалить" className="actions_img" />
                        </button>
                    </div>
                ))}
            </div>

            <CreateSample
                isOpen={ isModalOpen }
                onClose={ () => setIsModalOpen(false) }
            />

            {selectedSample && (
                <UploadFile
                    isOpen={ uploadModalOpen }
                    onClose={ () => setUploadModalOpen(false) }
                    formSample={ selectedSample }
                />
            )}
        </div>
    );
}
