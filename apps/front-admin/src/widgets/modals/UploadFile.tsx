import React, { useState, useEffect } from "react";
import { Modal } from "../../components/Modal";
import "../../resources/scss/index.scss";
import { uploadSample } from "../../api/Import";
import { ShowResponse } from "../../widgets/modals/ShowResponse";
import { types } from "sass";
import String = types.String;

interface CreateSampleProps {
    isOpen: boolean;
    onClose: () => void;
    formSample: FormData;
}

interface FormData {
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
}

export function UploadFile({ isOpen, onClose, formSample }: CreateSampleProps) {
    const [ dragActive, setDragActive ] = useState(false);
    const [ file, setFile ] = useState<File | null>(null);
    const [ uploading, setUploading ] = useState(false);
    const [ progress, setProgress ] = useState<number>(0);
    const [ error, setError ] = useState<string | null>(null);
    const [ isModalOpenResopnse, setIsModalOpenResopnse ] = useState(false);
    const [ answer, setAnswer ] = useState(null);

    const allowedTypes = [
        "text/plain",
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ];

    useEffect(() => {
        const handlePaste = (e: ClipboardEvent) => {
            if (e.clipboardData?.files && e.clipboardData.files.length > 0) {
                const pastedFile = e.clipboardData.files[0];
                handleFile(pastedFile);
            }
        };
        document.addEventListener("paste", handlePaste);
        return () => document.removeEventListener("paste", handlePaste);
    }, []);

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setProgress(0);

        try {
            const company_name =
                formSample.company.type === "name" ? formSample.company.value : null;
            const company_col =
                formSample.company.type === "column" ? formSample.company.value : null;

            const dates =
                formSample.date.type === "range"
                    ? `${formSample.date.start}-${formSample.date.end}`
                    : null;
            const dates_col =
                formSample.date.type === "columns"
                    ? `${formSample.date.start};${formSample.date.end}`
                    : null;

            const response = await uploadSample(
                {
                    route_type: formSample.route.type === "Морские" ? "sea" : "rail",
                    type_data: formSample.route.type === "Железнодорожные + drop"
                        ? (formSample.route.additionalData ? `drop;${formSample.route.additionalData}` : null)
                        : null,

                    company_col,
                    company_name,
                    dates_col,
                    dates,
                    file,
                },
            );

            console.log("Файл успешно загружен:", response);
            setAnswer(response);
            setProgress(100);
        } catch (err: any) {
            setError(err.message || "Ошибка при загрузке");
        } finally {
            setUploading(false);
            setIsModalOpenResopnse(true);
        }
    };

    const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file: File) => {
        if (!allowedTypes.includes(file.type)) {
            setError("Неверный тип файла. Допустимы: TXT, CSV, Excel.");
            return;
        }
        setFile(file);
        setError(null);
        setProgress(0);
    };

    const handleReset = () => {
        setFile(null);
        setProgress(0);
        setError(null);
        setUploading(false);
    };

    return (
        <Modal isOpen={ isOpen } onClose={ onClose } className="modal-wrapper">
            <div
                className={ `upload-dropzone ${dragActive ? "active" : ""}` }
                onDragEnter={ handleDrag }
                onDragOver={ handleDrag }
                onDragLeave={ handleDrag }
                onDrop={ handleDrop }
            >
                {file ? (
                    <div className="file-info">
                        <p>
                            Выбран файл: <strong>{file.name}</strong>
                        </p>
                        <div className="actions">
                            {!uploading ? (
                                <>
                                    <button
                                        onClick={ handleUpload }
                                        className="control_btn accept"
                                    >
                                        Отправить
                                    </button>
                                    <button
                                        onClick={ handleReset }
                                        className="control_btn cancel"
                                    >
                                        Сбросить
                                    </button>
                                </>
                            ) : (
                                <p>Загрузка... {progress}%</p>
                            )}
                        </div>
                    </div>
                ) : (
                    <>
                        <p>
                            Перетащите файл сюда, выберите или вставьте его (Ctrl+V /
                            CMD+V)
                        </p>
                        <label className="control_accept_btn">
                            Выберите файл
                            <input
                                type="file"
                                accept=".txt, .csv, .xls, .xlsx"
                                onChange={ handleChange }
                                hidden
                            />
                        </label>
                    </>
                )}
                {error && <p className="error">{error}</p>}
            </div>
            <ShowResponse
                isOpen={ isModalOpenResopnse }
                onClose={ () => setIsModalOpenResopnse(false) }
                answer={ answer }
            />
        </Modal>
    );
}
